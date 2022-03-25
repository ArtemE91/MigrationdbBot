from pathlib import Path

import yaml
from aiogram import Bot, Dispatcher


def read_config(path):
    if path.exists() is False:
        print(f"WARNING: {path} not found")
        return {}
    else:
        with path.open('r') as f:
            return yaml.safe_load(f)


BAS_DIR = Path(__file__).parent
config = read_config(BAS_DIR / 'config' / 'config.yml')

DB_HOST = config.get('DB_HOST')
DB_PORT = config.get('DB_PORT')
DB_USER = config.get('DB_USER')
DB_NAME = config.get('DB_NAME')
DB_PASSWORD = config.get('DB_PASSWORD')

DB_OLD_HOST = config.get('DB_OLD_HOST')
DB_OLD_PORT = config.get('DB_OLD_PORT')
DB_OLD_USER = config.get('DB_OLD_USER')
DB_OLD_NAME = config.get('DB_OLD_NAME')
DB_OLD_PASSWORD = config.get('DB_OLD_PASSWORD')

DATABASE_URL = f'postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
OLD_DATABASE_URL = f'postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_OLD_NAME}'
DATABASE_URL_SYNC = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

API_TOKEN = config.get('API_TOKEN')

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
