# python manage.py shell < test_meta.py
from core.utils.whatsapp_manager import WhatsAppManager
from django.conf import settings

client = WhatsAppManager()

print("🚀 Sending Test Message via Meta API...")

# TEST 1: Plain Text Template (What you have now)
resp = client.send_template(
    to_number="51967244227",  # Your number
    template_name="encuesta_pacientes",
    language_code="es",
    components=[] # No variables
)
print(f"Test 1 Result: {resp}")

# TEST 2: Hello World (Sanity Check)
# resp = client.send_template(
#     to_number="51967244227",
#     template_name="hello_world",
#     language_code="en_US"
# )
# print(f"Test 2 Result: {resp}")