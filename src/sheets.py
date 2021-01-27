from RPA.Cloud.Google import ServiceSheets
from src import BOT_DIR, CONFIG
import os
from pprint import pprint

sheets_cli = ServiceSheets()
google_creds_path = os.path.join(
    BOT_DIR, 'creds', 'ta-google-creds.json'
)
sheets_cli.init_sheets_client(google_creds_path)


def get_shopping_list():
    sheet_data = sheets_cli.get_values(
        sheet_id=CONFIG['sheets']['id'],
        sheet_range='A:B'
    )
    shopping_list = [i[0] for i in sheet_data['values'][1:]]
    return shopping_list


if __name__ == '__main__':
    pprint(get_shopping_list())

