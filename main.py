import requests
import json
from datetime import datetime
import os


def backup_cat_images(text, yandex_token):
    """
    Резервное копирование картинок котиков на Яндекс.Диск
    """
    # 1. Получаем картинку с текстом от котиков
    cat_api_url = f"https://cataas.com/cat/says/{text}"

    try:
        print("🐱 Получаем картинку с cataas.com...")
        response = requests.get(cat_api_url, timeout=10)
        response.raise_for_status()

        # 2. Сохраняем картинку временно
        image_data = response.content
        image_size = len(image_data)  # Размер в байтах

        print(f"📸 Картинка получена! Размер: {image_size} байт")

        # 3. Создаем папку на Яндекс.Диске
        folder_name = "Fpy-134"
        headers = {
            'Authorization': f'OAuth {yandex_token}',
            'Content-Type': 'application/json'
        }

        # Проверяем и создаем папку
        create_folder_url = "https://cloud-api.yandex.net/v1/disk/resources"
        folder_params = {'path': folder_name}

        folder_response = requests.put(create_folder_url, headers=headers, params=folder_params)

        if folder_response.status_code not in [201, 409]:  # 201 создана, 409 уже exists
            print("❌ Ошибка создания папки на Яндекс.Диске")
            return None

        # 4. Загружаем картинку на Яндекс.Диск
        upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        file_name = f"{text}.jpg"  # Название файла = текст картинки
        file_path = f"{folder_name}/{file_name}"

        upload_params = {
            'path': file_path,
            'overwrite': 'true'
        }

        # Получаем ссылку для загрузки
        upload_response = requests.get(upload_url, headers=headers, params=upload_params)
        upload_data = upload_response.json()

        if 'href' not in upload_data:
            print("❌ Не удалось получить ссылку для загрузки")
            return None

        # Загружаем файл
        put_response = requests.put(upload_data['href'], data=image_data)
        if put_response.status_code == 201:
            print(f"✅ Картинка успешно загружена на Яндекс.Диск!")
            print(f"📁 Папка: {folder_name}")
            print(f"📄 Файл: {file_name}")
        else:
            print("❌ Ошибка загрузки файла")
            return None

        # 5. Сохраняем информацию в JSON
        info_data = {
            'file_name': file_name,
            'file_size_bytes': image_size,
            'file_size_mb': round(image_size / (1024 * 1024), 2),
            'upload_date': datetime.now().isoformat(),
            'source_url': cat_api_url,
            'text_on_image': text,
            'yandex_path': file_path
        }

        json_filename = f"backup_info_{text}.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(info_data, f, ensure_ascii=False, indent=2)

        print(f"📊 Информация сохранена в {json_filename}")

        return info_data

    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка при работе с API: {e}")
        return None
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return None


def main():
    """
    Основная функция для взаимодействия с пользователем
    """
    print("🐱 Резервное копирование картинок котиков!")
    print("=" * 50)

    # Получаем данные от пользователя
    text = input("Введите текст для картинки: ").strip()
    yandex_token = input("Введите токен Яндекс.Диска: ").strip()

    if not text or not yandex_token:
        print("❌ Текст и токен не могут быть пустыми!")
        return

    # Выполняем резервное копирование
    result = backup_cat_images(text, yandex_token)

    if result:
        print("\n🎉 Резервное копирование завершено успешно!")
        print(f"📏 Размер файла: {result['file_size_mb']} MB")
        print(f"📅 Дата загрузки: {result['upload_date']}")
    else:
        print("\n😿 Не удалось выполнить резервное копирование")


if __name__ == "__main__":
    main()