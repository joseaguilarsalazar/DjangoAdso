# create_superuser.py
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djangoAdso.settings")
django.setup()

from django.contrib.auth import get_user_model
from chatbot.models import Chat, Message

chatjd = Chat.objects.filter(number='51967244227').first()
if chatjd:
    Message.objects.filter(chat=chatjd).delete()

User = get_user_model()

DEFAULT_EMAIL = "admin@gmail.com"
DEFAULT_PASSWORD = "adso_dental_2025"

try:
    user = User.objects.get(email=DEFAULT_EMAIL)
    # Check if password matches
    if not user.check_password(DEFAULT_PASSWORD):
        user.set_password(DEFAULT_PASSWORD)
        user.save()
        print("✅ Password for admin reset to default.")
    else:
        print("ℹ️ Admin user already exists with correct password.")

except User.DoesNotExist:
    User.objects.create_superuser(
        email=DEFAULT_EMAIL,
        password=DEFAULT_PASSWORD,
        tipo_doc="DNI",
        num_doc="00000001",
        name="Administrador General",
        rol="admin",
        estado="activo",
        clinica_id=1,
    )
    print("✅ Admin user created with default password.")
