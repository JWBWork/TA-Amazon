from src.logger import logger
from src.sheets import get_shopping_list
from src import BOT_DIR, CONFIG
from selenium.common.exceptions import NoSuchElementException
import selenium.webdriver
import os, re

cookie_path = os.path.join(BOT_DIR, 'cookies.pkl')
options = selenium.webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument('--no-sandbox')
options.add_argument("window-size=1280,800")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36")
driver = selenium.webdriver.Chrome(options=options)
driver.implicitly_wait(5)


def get_amzn_page_n():
    page_n = re.findall('page=(\d+)', driver.current_url)
    page_n = page_n[0] if page_n else 1
    return int(page_n)


def parse_amzn_search_page(search_str):
    result_divs = driver.find_elements_by_css_selector('.s-result-item.s-asin')
    products = list()
    for div in result_divs:
        try:
            # Implemented to filter out items that don't really match - i.e. tvs of different sizes
            # (Needs smarter implementation)
            name = div.find_element_by_css_selector('.a-link-normal.a-text-normal').get_attribute('innerText')
            split_search_str = [re.sub('[^a-zA-Z0-9 ]', '', s) for s in search_str.split(' ')]
            match_score = sum(1 for s in split_search_str if s.lower() in name.lower())/len(split_search_str)
            if match_score < CONFIG['settings']['match_threshold']:
                continue

            potential_shipping = div.find_elements_by_css_selector('.a-section.a-spacing-none.a-spacing-top-micro')
            shipping = 0
            if potential_shipping:
                potential_shipping_text = potential_shipping[-1].get_attribute('innerText').lower()
                if 'shipping' in potential_shipping_text and 'free' not in potential_shipping_text:
                    shipping = float(re.findall('\$(\d+\.\d+)', potential_shipping_text)[0])

            products.append({
                'name': name,
                'href': div.find_element_by_css_selector('.a-link-normal.a-text-normal').get_attribute('href'),
                'price': float(re.sub(
                    '[,$]', '', div.find_element_by_css_selector('.a-offscreen').get_attribute('innerText')
                )) + shipping
            })
        except NoSuchElementException as e:
            continue
    logger.info(f'{len(products)} found on page {get_amzn_page_n()}')
    return products


def search_amazon(search_str):
    logger.info(f'Searching for {search_str}')
    products = []
    first_page_url = f"https://www.amazon.com/s?k={'+'.join(search_str.split(' '))}"
    driver.get(first_page_url)
    searching = True
    while searching:
        products += parse_amzn_search_page(search_str)
        for next_button_attempt in range(0, 3):
            try:
                next_button = driver.find_elements_by_css_selector('.a-last')[-1]
                next_button_class = next_button.get_attribute('class')
                if get_amzn_page_n() == CONFIG['settings']['page_limit']:
                    logger.info(f'Search for {search_str} - reached page limit')
                    searching = False
                elif len(products) >= CONFIG['settings']['item_limit']:
                    logger.info(f'Search for {search_str} - reached item limit')
                    searching = False
                elif "a-disabled" in next_button_class:
                    logger.info(f'Search for {search_str} - reached last page')
                    searching = False
                else:
                    next_page_url = next_button.find_element_by_tag_name('a').get_attribute('href')
                    driver.get(next_page_url)
                break
            except NoSuchElementException as e:
                if next_button_attempt == 2:
                    logger.warning(f"Max next button attempts - {e}")
                    searching = False
    return products


def search_shopping_list():
    items_search_results = dict()
    for shopping_item in get_shopping_list():
        search_results = search_amazon(shopping_item)
        items_search_results[shopping_item] = search_results
    return items_search_results


def close_driver():
    driver.close()


if __name__ == '__main__':
    try:
        results = search_shopping_list()
        print(results)
    finally:
        close_driver()
