from django.apps import AppConfig # type: ignore


class AccountsConfig(AppConfig):
    name = 'accounts'

    def ready(self):
        import sys
import logging

def ready(self):
    try:
        from . import signals
    except Exception as e:
        logging.error(f"فشل استيراد signals: {e}")

