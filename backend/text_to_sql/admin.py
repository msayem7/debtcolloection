from django.contrib import admin

from text_to_sql.models import ApiKeyProfile, TextToSqlLog


@admin.register(ApiKeyProfile)
class ApiKeyProfileAdmin(admin.ModelAdmin):
    list_display = ['profile_name', 'provider', 'model', 'is_active', 'created_at']
    list_filter = ['provider', 'is_active']
    search_fields = ['profile_name', 'provider']


@admin.register(TextToSqlLog)
class TextToSqlLogAdmin(admin.ModelAdmin):
    list_display = ['question', 'user', 'branch', 'success', 'row_count', 'execution_time_ms', 'created_at']
    list_filter = ['success', 'created_at', 'llm_provider']
    search_fields = ['question', 'generated_sql', 'error_message']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'