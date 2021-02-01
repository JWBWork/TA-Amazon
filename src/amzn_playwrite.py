from RPA.Browser.Playwright import Playwright
from bs4 import BeautifulSoup
from time import sleep
from src.logger import logger
import re

parse_re = {
    'rating': re.compile(r'(\d\.\d) out of \d'),
    'price': re.compile(r'\$(\d+\.\d+)'),
    'shipping': re.compile(r'\$(\d+\.\d+) shipping'),
}


class Amazon:
    def __init__(self, browser, headless=True):
        self.browser = browser
        if not headless:
            self.browser.new_browser(headless=False)

    def search(self, term):
        logger.info(f'Searching amazon for "{term}"')
        self.browser.new_page('https://www.amazon.com')

        self.browser.type_text(
            'id=twotabsearchtextbox', text=term
        )
        self.browser.click('id=nav-search-submit-button')

        page = 0
        all_products = []
        searching = True
        while searching:
            sleep(2)
            page_source = self.browser.get_page_source()
            search_soup = BeautifulSoup(page_source, features='lxml')
            page_results = search_soup.find_all('div', {'data-component-type': 's-search-result'})
            page_products = list()
            for result in page_results:
                try:
                    result_text = result.get_text(strip=True)
                    title = result.find('h2').text.strip()
                    price = re.search(parse_re['price'], result_text)
                    # skip products that don't list prices, free kindle books, protection plans
                    if price is None or price.group(1) == '0.00':
                        continue
                    price = float(price.group(1).replace(',', ''))
                    shipping = re.search(parse_re['shipping'], result_text)
                    shipping = float(shipping.group(1).replace(',', '')) if shipping is not None else 0.0
                    rating = re.search(parse_re['rating'], result_text)
                    page_products.append({
                        'title': title,
                        'url': f'https://www.amazon.com{result.find("h2").find("a").get("href")}',
                        'rating': float(rating.group(1)) if rating else None,
                        'price': price,
                        'shipping': shipping,
                        'total': price + shipping
                    })
                except Exception as e:
                    logger.error(f'{str(result)}')
                    raise e

            page += 1
            logger.info(f'{len(page_products)} found on page {page}')
            all_products += page_products

            next_button = self.browser.get_element('css=li.a-last')
            next_button_style = self.browser.get_attribute(next_button, 'class')
            if 'a-disabled' in next_button_style:
                searching = False
            else:
                self.browser.click(next_button)
        all_products.sort(key=lambda x: x['total'])
        logger.info(f'"{term}" search complete! {len(all_products)} found')
        return all_products


if __name__ == '__main__':
    import json, os
    from src import OUT_DIR
    browser = Playwright()
    try:
        amazon = Amazon(browser, headless=True)
        results = amazon.search('thicc')
        json.dump(results, open(os.path.join(OUT_DIR, 'test.json'), 'w+'))
    finally:
        browser.close_browser()
