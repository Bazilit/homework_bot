import os

from dotenv import load_dotenv

load_dotenv()

token = os.getenv('TELEGRAM_TOKEN')
print(token)