import os

BOT_DIR = os.path.join(os.path.dirname(__file__), '..')
CREDS_DIR = os.path.join(BOT_DIR, 'creds')
OUT_DIR = os.path.join(BOT_DIR, 'output')
LOG_DIR = os.path.join(OUT_DIR, 'logs')

if not os.path.isdir(OUT_DIR):
    os.mkdir(OUT_DIR)
if not os.path.isdir(LOG_DIR):
    os.mkdir(LOG_DIR)

from .config import CONFIG
