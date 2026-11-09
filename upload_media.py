"""
Загружает картинки из локальной папки media/ в Supabase Storage
и обновляет пути в базе данных.

Файлы получают латинские имена (по slug), потому что Supabase
не принимает имена файлов с кириллицей.

Запуск (из папки проекта, с активированным venv):
    $env:DATABASE_URL="строка подключения к Supabase"
    python upload_media.py
"""
import os
from pathlib import Path

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings  # noqa: E402
from django.core.files import File  # noqa: E402
from django.core.files.storage import default_storage  # noqa: E402

from products.models import Category, Product  # noqa: E402

MEDIA_DIR = Path(settings.BASE_DIR) / 'media'


def check_setup():
    backend = settings.STORAGES['default']['BACKEND']
    db_host = settings.DATABASES['default'].get('HOST') or 'SQLite (локально)'
    print(f'Хранилище: {backend}')
    print(f'База данных: {db_host}')

    if 's3' not in backend.lower():
        raise SystemExit(
            'Ошибка: картинки сохранятся локально, а не в Supabase.\n'
            'Проверь, что в .env заполнен AWS_STORAGE_BUCKET_NAME.'
        )
    if 'supabase' not in str(db_host):
        raise SystemExit(
            'Ошибка: подключена локальная база, а не Supabase.\n'
            'Сначала выполни: $env:DATABASE_URL="строка из блокнота"'
        )


def upload(obj, folder):
    old_name = obj.image.name
    if not old_name:
        return 'нет картинки'

    local_path = MEDIA_DIR / old_name
    if not local_path.exists():
        return f'ПРОПУЩЕНО: нет файла {local_path}'

    new_name = f'{folder}/{obj.slug}{local_path.suffix.lower()}'
    if default_storage.exists(new_name):
        default_storage.delete(new_name)

    with open(local_path, 'rb') as f:
        saved_name = default_storage.save(new_name, File(f))

    obj.image.name = saved_name
    obj.save(update_fields=['image'])
    return f'OK -> {default_storage.url(saved_name)}'


def main():
    check_setup()
    print()
    for model, folder in [(Category, 'categories'), (Product, 'products')]:
        print(f'=== {model._meta.verbose_name_plural} ===')
        for obj in model.objects.all():
            print(f'{obj}: {upload(obj, folder)}')
        print()
    print('Готово!')


if __name__ == '__main__':
    main()