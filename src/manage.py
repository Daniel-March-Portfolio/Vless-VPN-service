#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

import django


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    if len(sys.argv) == 1:
        sys.argv.append('runserver')

    if sys.argv[1] == 'runserver':
        django.setup()
        create_superuser()

    execute_from_command_line(sys.argv)

def create_superuser():
    from django.contrib.auth import get_user_model
    user_model = get_user_model()
    if not user_model.objects.filter(is_superuser=True).exists():
        print("No superuser found. Creating a default superuser.")
        user_model.objects.create_superuser(username='admin', password='admin')


if __name__ == '__main__':
    main()
