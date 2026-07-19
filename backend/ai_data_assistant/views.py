import time
import logging
from decimal import Decimal

from django.db import connection
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from cheques.models import Branch
from ai_data_assistant.models import AIDataAssistantLog
from ai_data_assistant.serializers import AIDataAssistantRequestSerializer, AIDataAssistantResponseSerializer
from ai_data_assistant.utils.prompt_builder import build_prompt
from ai_data_assistant.utils.llm_client import LlmClient, LlmClientError
from ai_data_assistant.utils.sql_validator import validate_sql, inject_tenant_filter, enforce_row_limit, strip_parameters
from ai_data_assistant.utils.security import set_readonly_session

logger = logging.getLogger(__name__)


class AIDataAssistantView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        start_time = time.time()

        serializer = AIDataAssistantRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        question = serializer.validated_data['question']
        api_key_profile = serializer.validated_data['api_key_profile']
        max_rows = serializer.validated_data['max_rows']
        temperature = serializer.validated_data['temperature']

        user = request.user
        branch_id = None
        branch_alias_id = None

        branch_param = request.query_params.get('branch')
        if branch_param:
            branch_obj = get_object_or_404(Branch, alias_id=branch_param)
            branch_id = branch_obj.id
            branch_alias_id = branch_obj.alias_id

        log_entry = AIDataAssistantLog(
            user=user,
            branch_id=branch_id,
            question=question,
            api_key_profile=api_key_profile,
        )

        try:
            messages = build_prompt(question)

            client = LlmClient(profile_name=api_key_profile)
            generated_sql, tokens_used, cost = client.generate_sql(messages, temperature=temperature)

            log_entry.generated_sql = generated_sql
            log_entry.llm_model = client.model
            log_entry.llm_provider = client.provider
            log_entry.llm_tokens_used = tokens_used
            if cost:
                log_entry.llm_cost_estimate = Decimal(str(cost))

            is_valid, error_msg = validate_sql(generated_sql)
            if not is_valid:
                log_entry.success = False
                log_entry.error_message = error_msg
                log_entry.execution_time_ms = int((time.time() - start_time) * 1000)
                log_entry.save()
                return Response(
                    AIDataAssistantResponseSerializer({
                        'question': question,
                        'generated_sql': generated_sql,
                        'success': False,
                        'error_message': error_msg,
                    }).data,
                    status=status.HTTP_400_BAD_REQUEST
                )

            safe_sql = enforce_row_limit(generated_sql, max_rows)

            safe_sql = strip_parameters(safe_sql)

            if branch_id:
                _, safe_sql = inject_tenant_filter(safe_sql, branch_id, branch_alias_id)
            else:
                raise ValueError("A branch/office must be selected. Query cannot be executed without tenant isolation.")

            log_entry.executed_sql = safe_sql

            with connection.cursor() as cursor:
                set_readonly_session(cursor)
                cursor.execute(safe_sql)
                columns = [col[0] for col in cursor.description]
                rows = [dict(zip(columns, row)) for row in cursor.fetchall()]

            execution_time = int((time.time() - start_time) * 1000)

            log_entry.columns = columns
            log_entry.row_count = len(rows)
            log_entry.execution_time_ms = execution_time
            log_entry.success = True
            log_entry.save()

            return Response(AIDataAssistantResponseSerializer({
                'question': question,
                'generated_sql': generated_sql,
                'executed_sql': safe_sql,
                'columns': columns,
                'rows': rows,
                'row_count': len(rows),
                'execution_time_ms': execution_time,
                'llm_model': client.model,
                'llm_provider': client.provider,
                'llm_tokens_used': tokens_used,
                'api_key_profile': api_key_profile,
                'success': True,
                'error_message': None,
            }).data)

        except LlmClientError as e:
            execution_time = int((time.time() - start_time) * 1000)
            log_entry.success = False
            log_entry.error_message = str(e)
            log_entry.execution_time_ms = execution_time
            log_entry.save()
            return Response(
                AIDataAssistantResponseSerializer({
                    'question': question,
                    'generated_sql': None,
                    'success': False,
                    'error_message': f"LLM error: {str(e)}",
                }).data,
                status=status.HTTP_502_BAD_GATEWAY
            )

        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            log_entry.success = False
            log_entry.error_message = str(e)
            log_entry.execution_time_ms = execution_time
            log_entry.save()
            logger.exception("AI Data Assistant execution error")
            return Response(
                AIDataAssistantResponseSerializer({
                    'question': question,
                    'generated_sql': generated_sql,
                    'success': False,
                    'error_message': f"Execution error: {str(e)}",
                }).data,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


