from django.urls import path
from text_to_sql.views import TextToSqlView

urlpatterns = [
    path('text-to-sql/', TextToSqlView.as_view(), name='text-to-sql'),
]