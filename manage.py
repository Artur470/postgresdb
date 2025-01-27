#!/usr/bin/env python
"""Django's management-line utility for administrative tasks."""
import os
import sys
import cloudinary
import cloudinary.api
from decouple import config

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

    # Настройка Cloudinary
    cloudinary.config(
        cloud_name=config('CLOUDINARY_CLOUD_NAME'),
        api_key=config('CLOUDINARY_API_KEY'),
        api_secret=config('CLOUDINARY_API_SECRET')
    )

    # Проверка работы Cloudinary
    try:
        resources = cloudinary.api.resources()  # Попытка получить ресурсы
        print("Cloudinary работает корректно.")
    except Exception as e:
        print("Ошибка при обращении к Cloudinary:", e)

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
