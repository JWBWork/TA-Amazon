from src.amazon import search_shopping_list, close_driver
from src.emailresults import send_results


def main():
    try:
        results = search_shopping_list()
    finally:
        close_driver()

    cheapest = dict()
    for search_term, results in results.items():
        cheapest[search_term] = min(results, key=lambda r: r['price'])

    send_results(cheapest)


if __name__ == '__main__':
    main()

