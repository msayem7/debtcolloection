from rest_framework import serializers

from text_to_sql.models import TextToSqlLog, ApiKeyProfile


class TextToSqlRequestSerializer(serializers.Serializer):
    question = serializers.CharField(required=True, max_length=2000)
    api_key_profile = serializers.CharField(required=False, default='primary', max_length=50)
    max_rows = serializers.IntegerField(required=False, default=500, min_value=1, max_value=5000)
    temperature = serializers.FloatField(required=False, default=0.1, min_value=0.0, max_value=1.0)


class TextToSqlResponseSerializer(serializers.Serializer):
    question = serializers.CharField()
    generated_sql = serializers.CharField(allow_null=True)
    executed_sql = serializers.CharField(allow_null=True)
    columns = serializers.ListField(child=serializers.CharField(), allow_null=True)
    rows = serializers.ListField(allow_null=True)
    row_count = serializers.IntegerField(allow_null=True)
    execution_time_ms = serializers.IntegerField(allow_null=True)
    llm_model = serializers.CharField(allow_null=True)
    llm_provider = serializers.CharField(allow_null=True)
    llm_tokens_used = serializers.IntegerField(allow_null=True)
    api_key_profile = serializers.CharField(allow_null=True)
    success = serializers.BooleanField()
    error_message = serializers.CharField(allow_null=True)


class ApiKeyProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApiKeyProfile
        fields = ['profile_name', 'provider', 'base_url', 'model', 'is_active', 'created_at', 'updated_at']


class TextToSqlLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TextToSqlLog
        fields = '__all__'