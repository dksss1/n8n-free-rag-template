#!/usr/bin/env python3
"""
Скрипт для загрузки файлов в Pinecone через n8n webhook
"""

import os
import requests
import json
from pathlib import Path
from typing import List, Dict
from config import (
    N8N_UPLOAD_WEBHOOK_URL, DEFAULT_NAMESPACE, DEFAULT_DATA_DIR, UPLOAD_TIMEOUT,
    CHUNK_SIZE, CHUNK_OVERLAP, MAX_FILE_SIZE_MB, SUPPORTED_FILE_EXTENSIONS,
    ENABLE_VERBOSE_LOGGING, LOG_LEVEL
)

def read_txt_files_from_directory(directory: str = DEFAULT_DATA_DIR) -> List[Dict]:
    """
    Читает все поддерживаемые файлы из указанной директории.
    
    Args:
        directory: Путь к директории с файлами
    
    Returns:
        Список словарей с данными файлов
    """
    files_data = []
    
    if not os.path.exists(directory):
        raise FileNotFoundError(f"Directory {directory} does not exist")
    
    # Фильтруем файлы по поддерживаемым расширениям
    all_files = os.listdir(directory)
    supported_files = [f for f in all_files 
                      if any(f.lower().endswith(ext) for ext in SUPPORTED_FILE_EXTENSIONS)]
    
    if not supported_files:
        raise FileNotFoundError(f"No supported files found in {directory}. "
                              f"Supported extensions: {SUPPORTED_FILE_EXTENSIONS}")
    
    for filename in supported_files:
        filepath = os.path.join(directory, filename)
        
        # Проверяем размер файла
        file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
        if file_size_mb > MAX_FILE_SIZE_MB:
            print(f"✗ Файл {filename} слишком большой ({file_size_mb:.1f}MB > {MAX_FILE_SIZE_MB}MB)")
            continue
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Проверяем, что файл не пустой
                if not content.strip():
                    print(f"⚠ Файл {filename} пуст, пропускаем")
                    continue
                
                files_data.append({
                    "fileName": filename,
                    "text": content,
                    "chunkSize": CHUNK_SIZE,
                    "chunkOverlap": CHUNK_OVERLAP
                })
                
                if ENABLE_VERBOSE_LOGGING:
                    print(f"✓ Прочитан файл: {filename} ({len(content)} символов)")
                else:
                    print(f"✓ Прочитан файл: {filename}")
                    
        except Exception as e:
            print(f"✗ Ошибка чтения файла {filename}: {e}")
    
    return files_data


def upload_to_pinecone(files_data: List[Dict], webhook_url: str, namespace: str = DEFAULT_NAMESPACE) -> Dict:
    """
    Загружает файлы в Pinecone через n8n webhook.
    
    Args:
        files_data: Список словарей с данными файлов
        webhook_url: URL webhook из n8n
        namespace: Namespace в Pinecone
    
    Returns:
        Ответ от API
    """
    payload = {
        "files": files_data,
        "namespace": namespace,
        "chunkSize": CHUNK_SIZE,
        "chunkOverlap": CHUNK_OVERLAP
    }
    
    print(f"\n📤 Отправка {len(files_data)} файлов в Pinecone...")
    print(f"   Webhook URL: {webhook_url}")
    print(f"   Namespace: {namespace}")
    if ENABLE_VERBOSE_LOGGING:
        print(f"   Chunk size: {CHUNK_SIZE}")
        print(f"   Chunk overlap: {CHUNK_OVERLAP}")
        print(f"   Max file size: {MAX_FILE_SIZE_MB}MB")
    
    try:
        response = requests.post(
            webhook_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=UPLOAD_TIMEOUT
        )
        response.raise_for_status()
        
        result = response.json()
        print(f"\n✅ Успешно загружено!")
        print(f"   Обработано файлов: {result.get('totalFiles', 0)}")
        print(f"   Векторов загружено: {result.get('totalUpserted', 0)}")
        
        return result
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Ошибка при запросе к API: {e}")
    except json.JSONDecodeError as e:
        raise Exception(f"Ошибка при парсинге JSON ответа: {e}")


def main():
    """
    Основная функция для загрузки файлов из /data в Pinecone.
    """
    # Настройки из config.py
    DATA_DIR = os.getenv("DATA_DIR", DEFAULT_DATA_DIR)
    WEBHOOK_URL = os.getenv("N8N_UPLOAD_WEBHOOK_URL", N8N_UPLOAD_WEBHOOK_URL)
    NAMESPACE = os.getenv("PINECONE_NAMESPACE", DEFAULT_NAMESPACE)
    
    print("=" * 80)
    print("📁 Загрузка файлов из директории в Pinecone")
    print("=" * 80)
    print(f"Директория: {DATA_DIR}")
    print(f"Webhook URL: {WEBHOOK_URL}")
    print(f"Namespace: {NAMESPACE}")
    print("=" * 80)
    
    try:
        # Читаем файлы
        files_data = read_txt_files_from_directory(DATA_DIR)
        
        if not files_data:
            print("❌ Нет файлов для загрузки")
            return
        
        # Загружаем в Pinecone
        result = upload_to_pinecone(files_data, WEBHOOK_URL, NAMESPACE)
        
        # Выводим детальную статистику
        if result.get('fileResults'):
            print("\n📊 Детальная статистика по файлам:")
            for file_result in result['fileResults']:
                print(f"   Файл #{file_result['fileIndex']}: {file_result['upserted']} векторов")
        
        print("\n✅ Все файлы успешно обработаны!")
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())

