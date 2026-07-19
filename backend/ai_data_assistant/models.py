from django.db import models
from django.contrib.auth.models import User
from cheques.models import Branch


class ApiKeyProfile(models.Model):
    PROVIDER_CHOICES = [
        ('openrouter', 'OpenRouter'),
        ('google-ai-studio', 'Google AI Studio'),
        ('groq', 'Groq'),
    ]

    profile_name = models.CharField(max_length=50, unique=True)
    provider = models.CharField(max_length=50, choices=PROVIDER_CHOICES)
    api_key_hash = models.CharField(max_length=512)
    base_url = models.CharField(max_length=512, blank=True, null=True)
    model = models.CharField(max_length=100, blank=True, null=True,
                             help_text="Model identifier, e.g. 'gemini-2.0-flash', 'gpt-4o'")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ai_data_assistant_api_key_profile'
        verbose_name = 'API Key Profile'
        verbose_name_plural = 'API Key Profiles'

    def __str__(self):
        return f"{self.profile_name} ({self.provider})"


class AIDataAssistantLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True)
    question = models.TextField()
    generated_sql = models.TextField(blank=True, null=True)
    executed_sql = models.TextField(blank=True, null=True)
    sql_params = models.JSONField(blank=True, null=True)
    columns = models.JSONField(blank=True, null=True)
    row_count = models.IntegerField(null=True)
    execution_time_ms = models.IntegerField(null=True)
    api_key_profile = models.CharField(max_length=50, blank=True, null=True)
    llm_model = models.CharField(max_length=100, blank=True, null=True)
    llm_provider = models.CharField(max_length=50, blank=True, null=True)
    llm_tokens_used = models.IntegerField(null=True)
    llm_cost_estimate = models.DecimalField(max_digits=12, decimal_places=8, null=True)
    success = models.BooleanField(default=False)
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ai_data_assistant_log'
        verbose_name = 'AI Data Assistant Log'
        verbose_name_plural = 'AI Data Assistant Logs'
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['branch', '-created_at']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"[{'OK' if self.success else 'FAIL'}] {self.question[:60]}"