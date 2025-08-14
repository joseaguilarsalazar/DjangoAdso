import os
from django.conf import settings

print("DB_NAME repr:", repr(os.getenv('DB_NAME')))
print("DB_USER repr:", repr(os.getenv('DB_USER')))
print("DB_PASSWORD repr (first 64 bytes):", repr(os.getenv('DB_PASSWORD')[:64]))
print("DB_HOST repr:", repr(os.getenv('DB_HOST')))
print("DB_PORT repr:", repr(os.getenv('DB_PORT')))
