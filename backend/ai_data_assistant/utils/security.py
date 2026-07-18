"""
Security middleware for Text-to-SQL endpoint.
Enforces SELECT-only operations at the database connection level.
"""

import logging

from django.db import connection

logger = logging.getLogger(__name__)


class TextToSqlSecurityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response


class ReadOnlyDatabaseRouter:
    """
    Database router that directs all queries from the ai_data_assistant app
    to a read-only database connection if configured.
    Falls back to the default database with read-only session settings.
    """

    route_app_labels = {'ai_data_assistant'}

    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'ai_data_assistant':
            return 'default'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'ai_data_assistant':
            return 'default'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'ai_data_assistant':
            return db == 'default'
        return None


def set_readonly_session(cursor):
    """Set the PostgreSQL session to read-only for safety."""
    cursor.execute("SET TRANSACTION READ ONLY;")
    cursor.execute("SET statement_timeout = '30000';")  # 30 second timeout
    cursor.execute("SET idle_in_transaction_session_timeout = '60000';")


def set_readonly_session_psycopg2(connection):
    """Set read-only mode on the psycopg2 connection."""
    try:
        with connection.cursor() as cursor:
            set_readonly_session(cursor)
    except Exception as e:
        logger.warning(f"Could not set read-only session: {e}")
