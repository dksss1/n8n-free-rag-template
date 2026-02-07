# n8n Workflows

Эта директория содержит JSON файлы для импорта в n8n.

## Файлы

- `workflow1-pinecone-upload.json` - Загрузка документов в Pinecone
- `workflow2-pinecone-search.json` - Поиск по Pinecone

## Импорт в n8n

1. Откройте n8n: http://localhost:5678
2. Нажмите "Import from file"
3. Выберите JSON файл из этой директории
4. Активируйте workflow

## Настройка Credentials

### Hugging Face API (вместо OpenAI)
- Тип: **Header Auth**
- Name: `Authorization`
- Value: `Bearer hf_xxxxxxxx...` (Ваш токен Hugging Face)

### Pinecone API
- Тип: **Pinecone API**
- Value: Ваш API Key

## Важные настройки

- Модель: `intfloat/multilingual-e5-large`
- Размерность: `1024`
- Префикс запросов: `query: `
