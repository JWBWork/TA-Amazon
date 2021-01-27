from src import BOT_DIR
import os, json

config_path = os.path.join(BOT_DIR, 'config.json')
with open(config_path, 'r') as config_file:
    CONFIG = json.load(config_file)