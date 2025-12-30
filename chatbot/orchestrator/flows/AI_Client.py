from pathlib import Path
import os
import environ
from openai import OpenAI

env = environ.Env(
    DEBUG=(bool, False)
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env_file = os.path.join(BASE_DIR, '.env')

client = OpenAI(
    api_key=env('deepseek_key'),
    base_url=env('deepseek_url')
)