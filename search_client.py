#!/usr/bin/env python3
"""
Python клиент для поиска по Pinecone через n8n webhook
"""

import requests
import json
from typing import Dict, List, Optional
from config import (
    N8N_SEARCH_WEBHOOK_URL, DEFAULT_NAMESPACE, SEARCH_TIMEOUT,
    SEARCH_TOP_K, SEARCH_MIN_SCORE, ENABLE_VERBOSE_LOGGING, LOG_LEVEL
)


class PineconeSearchAPIClient:
    def __init__(self, webhook_url: str = N8N_SEARCH_WEBHOOK_URL):
        """
        Инициализация клиента для работы с Pinecone Search API через n8n webhook.
        
        Args:
            webhook_url: URL webhook из n8n (по умолчанию из config.py)
        """
        self.webhook_url = webhook_url
    
    def search(self, query: str, namespace: str = DEFAULT_NAMESPACE, top_k: int = SEARCH_TOP_K, min_score: float = SEARCH_MIN_SCORE) -> List[Dict]:
        """
        Выполняет поиск в Pinecone по текстовому запросу.
        
        Args:
            query: Текстовый запрос для поиска
            namespace: Namespace в Pinecone (по умолчанию из config.py)
            top_k: Количество результатов поиска (по умолчанию из config.py)
            min_score: Минимальный порог релевантности (по умолчанию из config.py)
        
        Returns:
            Список словарей с результатами поиска:
            [
                {
                    "text": "текст чанка",
                    "score": 0.95,
                    "source": "document1",
                    "chunk_index": 0,
                    "id": "chunk_1234567890_0"
                },
                ...
            ]
        """
        # ВАЖНОЕ ИЗМЕНЕНИЕ: Добавляем префикс "query: "
        # Модель E5 требует "query: " для запросов и "passage: " для документов.
        # Если этого не сделать, вектор запроса будет "смотреть" не туда.
        formatted_query = f"query: {query}" if not query.startswith("query: ") else query

        payload = {
            "query": formatted_query,  # <-- Отправляем с префиксом
            "namespace": namespace,
            "topK": top_k,
            "minScore": min_score
        }
        
        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=SEARCH_TIMEOUT
            )
            response.raise_for_status()
            
            results = response.json()
            
            if isinstance(results, list):
                # Фильтруем результаты по минимальному скору
                filtered_results = [r for r in results if r.get('score', 0) >= min_score]
                return filtered_results[:top_k]  # Ограничиваем количество результатов
            elif isinstance(results, dict) and "data" in results:
                filtered_results = [r for r in results["data"] if r.get('score', 0) >= min_score]
                return filtered_results[:top_k]
            else:
                return [results] if results else []
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"Ошибка при запросе к API: {e}")
        except json.JSONDecodeError as e:
            raise Exception(f"Ошибка при парсинге JSON ответа: {e}")
    
    def print_results(self, results: List[Dict], show_details: bool = ENABLE_VERBOSE_LOGGING):
        """
        Красиво выводит результаты поиска.
        
        Args:
            results: Список результатов поиска
            show_details: Показывать детальную информацию
        """
        if not results:
            print("Результаты не найдены.")
            return
        
        print(f"\nНайдено результатов: {len(results)}\n")
        print("=" * 80)
        
        for i, result in enumerate(results, 1):
            print(f"\nРезультат #{i}:")
            print(f"  Score: {result.get('score', 0):.4f}")
            print(f"  Source: {result.get('source', 'unknown')}")
            print(f"  Chunk Index: {result.get('chunk_index', -1)}")
            print(f"  ID: {result.get('id', 'N/A')}")
            
            if show_details:
                print(f"  Text: {result.get('text', '')}")
            else:
                print(f"  Text: {result.get('text', '')[:200]}...")
            print("-" * 80)
