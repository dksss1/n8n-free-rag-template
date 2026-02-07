"""
Конфигурация для работы с Pinecone через n8n webhooks
"""

# URL webhook из n8n
N8N_UPLOAD_WEBHOOK_URL = "https://fondly-assisting-setter.cloudpub.ru/webhook/pinecone-upload"
N8N_SEARCH_WEBHOOK_URL = "https://fondly-assisting-setter.cloudpub.ru/webhook/pinecone-search"

# Настройки по умолчанию
DEFAULT_NAMESPACE = "default"
DEFAULT_DATA_DIR = "./data"

# Таймауты (в секундах)
UPLOAD_TIMEOUT = 300
SEARCH_TIMEOUT = 120

# Настройки чанков для текста
CHUNK_SIZE = 600  # Размер чанка в символах
CHUNK_OVERLAP = 100  # Перекрытие между чанками в символах

# Настройки embeddings
EMBEDDING_MODEL = "text-embedding-3-large"
EMBEDDING_DIMENSION = 1024  # Размерность векторов

# Настройки поиска
SEARCH_TOP_K = 5  # Количество результатов поиска
SEARCH_MIN_SCORE = 0.0  # Минимальный порог релевантности (0.0 - 1.0)

# Настройки обработки файлов
MAX_FILE_SIZE_MB = 50  # Максимальный размер файла в МБ
SUPPORTED_FILE_EXTENSIONS = [".txt"]  # Поддерживаемые расширения файлов

# Настройки логирования
ENABLE_VERBOSE_LOGGING = False  # Подробное логирование
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
