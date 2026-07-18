"""
LLM Client — abstracts API calls to multiple LLM providers.
Supports OpenRouter, Google AI Studio, and Groq.
"""

import logging
from typing import Optional, Dict, Any, Tuple
from decimal import Decimal

import requests
from django.conf import settings

from ai_data_assistant.models import ApiKeyProfile

logger = logging.getLogger(__name__)


class LlmClientError(Exception):
    pass


class LlmClient:
    PROVIDER_CONFIGS = {
        'openrouter': {
            'base_url': 'https://openrouter.ai/api/v1/chat/completions',
            'auth_header': 'Authorization',
            'auth_prefix': 'Bearer ',
            'model_key': 'model',
        },
        'google-ai-studio': {
            'base_url': 'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent',
            'auth_header': 'x-goog-api-key',
            'auth_prefix': '',
            'model_key': None,
        },
        'groq': {
            'base_url': 'https://api.groq.com/openai/v1/chat/completions',
            'auth_header': 'Authorization',
            'auth_prefix': 'Bearer ',
            'model_key': 'model',
        },
    }

    def __init__(self, profile_name: str = 'primary'):
        try:
            self.profile = ApiKeyProfile.objects.get(
                profile_name=profile_name,
                is_active=True
            )
        except ApiKeyProfile.DoesNotExist:
            raise LlmClientError(f"API key profile '{profile_name}' not found or inactive")

        self.profile_name = profile_name
        self.provider = self.profile.provider
        self.api_key = self._decrypt_key(self.profile.api_key_hash)
        self.model = self.profile.model or self._get_default_model()
        self.base_url = self.profile.base_url or self.PROVIDER_CONFIGS[self.provider]['base_url']

    def _get_default_model(self) -> str:
        defaults = {
            'openrouter': 'openai/gpt-4o',
            'google-ai-studio': 'gemini-2.0-flash',
            'groq': 'llama-3.3-70b-versatile',
        }
        return defaults.get(self.provider, 'gpt-4o')

    def _decrypt_key(self, hashed: str) -> str:
        if hashed.startswith('enc:'):
            return hashed[4:]
        return hashed

    def _build_request_data(self, messages: list, temperature: float = 0.1) -> Dict[str, Any]:
        config = self.PROVIDER_CONFIGS[self.provider]

        if self.provider == 'google-ai-studio':
            contents = []
            for msg in messages:
                role = 'user' if msg['role'] in ('user', 'system') else 'model'
                contents.append({
                    'role': role,
                    'parts': [{'text': msg['content']}]
                })
            return {
                'contents': contents,
                'generationConfig': {
                    'temperature': temperature,
                    'maxOutputTokens': 1024,
                }
            }
        else:
            data = {
                'messages': messages,
                'temperature': temperature,
                'max_tokens': 1024,
            }
            data[config['model_key']] = self.model
            return data

    def _build_headers(self) -> Dict[str, str]:
        config = self.PROVIDER_CONFIGS[self.provider]
        headers = {
            'Content-Type': 'application/json',
        }
        auth_value = f"{config['auth_prefix']}{self.api_key}"
        headers[config['auth_header']] = auth_value

        if self.provider == 'openrouter':
            headers['HTTP-Referer'] = settings.BASE_URL if hasattr(settings, 'BASE_URL') else 'http://localhost:8000'
            headers['X-Title'] = 'Debt Collection AI Data Assistant'

        return headers

    def _build_url(self) -> str:
        if self.provider == 'google-ai-studio':
            return self.base_url.format(model=self.model)
        return self.base_url

    def _parse_response(self, response_json: dict) -> Tuple[str, Optional[int], Optional[Decimal]]:
        if self.provider == 'google-ai-studio':
            candidates = response_json.get('candidates', [])
            if not candidates:
                raise LlmClientError("No candidates in response")
            content = candidates[0].get('content', {}).get('parts', [{}])[0].get('text', '')
            tokens_used = None
            cost = None
        else:
            choices = response_json.get('choices', [])
            if not choices:
                raise LlmClientError("No choices in response")
            content = choices[0].get('message', {}).get('content', '')
            usage = response_json.get('usage', {})
            tokens_used = usage.get('total_tokens')
            cost = None

        sql = content.strip()
        if sql.startswith('```sql'):
            sql = sql[6:]
        elif sql.startswith('```'):
            sql = sql[3:]
        if sql.endswith('```'):
            sql = sql[:-3]
        sql = sql.strip()

        return sql, tokens_used, cost

    def generate_sql(self, messages: list, temperature: float = 0.1) -> Tuple[str, Optional[int], Optional[Decimal]]:
        url = self._build_url()
        headers = self._build_headers()
        data = self._build_request_data(messages, temperature)

        logger.info(f"LLM request: profile={self.profile_name}, provider={self.provider}, model={self.model}")

        try:
            response = requests.post(
                url,
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            response_json = response.json()
            return self._parse_response(response_json)
        except requests.exceptions.RequestException as e:
            error_detail = ""
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.text[:500]
                except Exception:
                    pass
            raise LlmClientError(f"LLM API error: {str(e)} {error_detail}")

