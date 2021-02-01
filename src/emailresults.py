from src import BOT_DIR
from RPA.Email.ImapSmtp import ImapSmtp
from time import sleep
import pandas as pd
import json, os

email_creds_path = os.path.join(BOT_DIR, 'creds', 'email-creds.json')
with open(email_creds_path, 'r') as creds_file:
    creds = json.load(creds_file)
mail = ImapSmtp(smtp_server='smtp.gmail.com')
mail.authorize_smtp(
    account=creds['username'],
    password=creds['password']
)


class Emailer:
    def __init__(self, mail):
        self.mail = mail

    def send_results(self, cheapest_products, all_products=None):
        with open(os.path.join(BOT_DIR, 'resultsTemplate.html')) as html_file:
            template = html_file.read()
            header, single_result_template = template.split('+')
        body = header
        excel_path = os.path.join(BOT_DIR, 'output', 'searchResults.xlsx')
        writer = pd.ExcelWriter(excel_path)
        excel_products = all_products or cheapest_products
        results_df = pd.DataFrame(excel_products)
        results_df.to_excel(writer, 'SearchResults')
        results_df.transpose()
        writer.save()
        for term, result in cheapest_products.items():
            result_html = single_result_template
            result_html = result_html.replace('{TERM}', term)
            result_html = result_html.replace('{URL}', result['url'])
            result_html = result_html.replace('{PRICE}', f"${result['total']}")
            result_html = result_html.replace('{NAME}', result['title'])
            body += result_html
        self.mail.send_message(
            sender=creds['username'],
            recipients=creds['recipients'],
            body=body,
            html=True,
            attachments=excel_path
        )


if __name__ == '__main__':
    pass
