from src.amazon import search_shopping_list, close_driver
from src.emailresults import mail, Emailer
from src.amzn_playwrite import Amazon
from src.sheets import get_shopping_list
from RPA.Browser.Playwright import Playwright


def main():
    browser = Playwright()
    amazon = Amazon(browser)
    emailer = Emailer(mail)
    try:
        # search_terms = get_shopping_list()
        search_terms = ['cat fighting toys']
        cheapest = dict()
        for term in search_terms:
            results = amazon.search(term)
            min_price = min(
                r['total'] for r in results
            )
            cheapest[term] = next(
                r for r in results if r['total'] == min_price
            )
        emailer.send_results(cheapest)
    finally:
        browser.close_browser()


if __name__ == '__main__':
    main()

