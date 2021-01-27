from RPA.Email.ImapSmtp import ImapSmtp
from src import BOT_DIR
import json, os
from time import sleep
import pandas as pd

email_creds_path = os.path.join(BOT_DIR, 'creds', 'email-creds.json')
with open(email_creds_path, 'r') as creds_file:
    creds = json.load(creds_file)
mail = ImapSmtp(smtp_server='smtp.gmail.com')
mail.authorize(
    account=creds['username'],
    password=creds['password']
)


def send_results(cheapest_products):
    with open(os.path.join(BOT_DIR, 'resultsTemplate.html')) as html_file:
        template = html_file.read()
        header, single_result_template = template.split('+')
    body = header
    writer = pd.ExcelWriter(os.path.join(BOT_DIR, 'searchResults.xlsx'))
    results_df = pd.DataFrame(cheapest_products)
    results_df.to_excel(writer, 'SearchResults')
    writer.save()
    for term, result in cheapest_products.items():
        result_html = single_result_template
        result_html = result_html.replace('{TERM}', term)
        result_html = result_html.replace('{URL}', result['href'])
        result_html = result_html.replace('{PRICE}', f"${result['price']}")
        result_html = result_html.replace('{NAME}', result['name'])
        body += result_html
    try:
        mail.send_message(
            sender=creds['username'],
            recipients=creds['recipients'],
            # cc=creds.get('cc', list()),
            body=body,
            html=True
        )
        sleep(1)
    except Exception:
        pass


if __name__ == '__main__':
    t ={
        '50 pack disposable face masks': {'href': 'https://www.amazon.com/Disposable-Face-Masks-Breathable-Comfortable/dp/B084TQKLCC/ref=sr_1_75?dchild=1&keywords=50+pack+disposable+face+masks&qid=1611714178&sr=8-75',
                                   'name': 'Disposable Face Masks - 50 PCS - '
                                           'For Home & Office - 3-Ply '
                                           'Breathable & Comfortable Filter '
                                           'Safety Mask',
                                   'price': 3.19},
 '85" Flat Screen TV': {'href': 'https://www.amazon.com/Bracket-Built-Spirit-Televisions-Installation/dp/B08TM3M53F/ref=sr_1_84?dchild=1&keywords=85%22+Flat+Screen+TV&qid=1611714146&sr=8-84',
                        'name': '32-85" Tilt TV Wall Mount Bracket with '
                                'Built-in Spirit Level for LED, LCD, 3D, '
                                'Curved, OLED, Plasma, Flat Screen Televisions '
                                'Easy Installation (Color : Black)',
                        'price': 232.82},
 'Mr. Robot Coffee Mug': {'href': 'https://www.amazon.com/Coffee-Tea-Shop-Ceramic-217005/dp/B085HHV6ZV/ref=sr_1_26?dchild=1&keywords=Mr.+Robot+Coffee+Mug&qid=1611713627&sr=8-26',
                          'name': 'Coffee and Tea Shop Mr robot 15Oz Ceramic '
                                  'Coffee Mugs 217005',
                          'price': 12.75},
 'Yeti Ramble 30oz': {'href': 'https://www.amazon.com/Tumbler-Handle-GREEN-STRATA-CUPS/dp/B01HYX2WTW/ref=sr_1_101?dchild=1&keywords=yeti+rambler+30oz&qid=1611714171&sr=8-101',
                      'name': '30oz Tumbler Handle (GREEN) by STRATA CUPS - '
                              'Available For 30oz YETI Tumbler, OZARK TRAIL '
                              'Tumbler, Rambler Tumbler- BPA FREE',
                      'price': 5.95},
 'iRobot Roomba': {'href': 'https://www.amazon.com/gp/slredirect/picassoRedirect.html/ref=pa_sp_btf_aps_sr_pg9_1?ie=UTF8&adId=A0019823DW22IYG8EORN&url=%2FReplacement-Accessories-vacuums-Cleaning-Robots%2Fdp%2FB07RTXVSTX%2Fref%3Dsr_1_150_sspa%3Fdchild%3D1%26keywords%3DiRobot%2BRoomba%26qid%3D1611713551%26sr%3D8-150-spons%26psc%3D1&qualifier=1611713590&id=3687147290647500&widgetName=sp_btf',
                   'name': 'Replacement Accessories for irobot Roomba 500 '
                           'Series \xa0530, 532, 535, 540, 560, 562, 570, 580 '
                           'series vacuums Cleaning Robots. (Except 510 537 '
                           '550 551 555 561 564 575 585 589 595)\xa0',
                   'price': 9.9}}
    send_results(t)
