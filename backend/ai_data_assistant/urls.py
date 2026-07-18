from django.urls import path
from ai_data_assistant.views import AIDataAssistantView

urlpatterns = [
    path('ai-data-assistant/', AIDataAssistantView.as_view(), name='ai-data-assistant'),
]

