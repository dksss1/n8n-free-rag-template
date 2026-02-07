#!/usr/bin/env python3
"""
CLI клиент для поиска по Pinecone через n8n webhook
"""

import argparse
import sys
from search_client import PineconeSearchAPIClient
from config import N8N_SEARCH_WEBHOOK_URL, DEFAULT_NAMESPACE, SEARCH_TOP_K, SEARCH_MIN_SCORE


def main():
    parser = argparse.ArgumentParser(
        description='Поиск по корпоративной базе знаний через Pinecone'
    )
    parser.add_argument(
        'query',
        help='Поисковый запрос'
    )
    parser.add_argument(
        '--namespace',
        default=DEFAULT_NAMESPACE,
        help=f'Namespace в Pinecone (по умолчанию: {DEFAULT_NAMESPACE})'
    )
    parser.add_argument(
        '--top-k',
        type=int,
        default=SEARCH_TOP_K,
        help=f'Количество результатов (по умолчанию: {SEARCH_TOP_K})'
    )
    parser.add_argument(
        '--min-score',
        type=float,
        default=SEARCH_MIN_SCORE,
        help=f'Минимальный порог релевантности (по умолчанию: {SEARCH_MIN_SCORE})'
    )
    parser.add_argument(
        '--url',
        default=N8N_SEARCH_WEBHOOK_URL,
        help=f'URL webhook (по умолчанию из config.py)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Подробный вывод результатов'
    )

    args = parser.parse_args()

    try:
        client = PineconeSearchAPIClient(args.url)
        
        print(f"🔍 Поиск: {args.query}")
        print(f"📁 Namespace: {args.namespace}")
        print(f"🎯 Top-K: {args.top_k}")
        print(f"⭐ Min Score: {args.min_score}")
        print("=" * 80)

        results = client.search(
            query=args.query,
            namespace=args.namespace,
            top_k=args.top_k,
            min_score=args.min_score
        )

        if results:
            print(f"\n✅ Найдено результатов: {len(results)}")
            print("=" * 80)
            client.print_results(results, show_details=args.verbose)
        else:
            print("\n❌ Результаты не найдены")
            print("Попробуйте:")
            print("- Использовать другие ключевые слова")
            print("- Проверить орфографию")
            print("- Использовать более общие формулировки")

    except KeyboardInterrupt:
        print("\n\n👋 Поиск отменен")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
