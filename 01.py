import requests

BASE_URL = "https://evolution-api-evolution-api.4oghcf.easypanel.host"
INSTANCE_NAME = "adso_iquitos_instance"
API_KEY = "429683C4C977415CAAFCCE10F7D57E11"

HEADERS = {
    "Content-Type": "application/json",
    "apikey": API_KEY
}

def check_instance_connection():
    """Check if the WhatsApp instance is connected."""
    url = f"{BASE_URL}/instance/connectionState/{INSTANCE_NAME}"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()
        print("Connection Check Response:", data)
        print(data.get("state"))
        # Adjust key access depending on API structure
        if isinstance(data, dict) and data.get("state") == "open":
            return True
        return False
    except requests.RequestException as e:
        print("Error checking connection:", e)
        return False

def send_message(number, text):
    """Send a WhatsApp text message."""
    url = f"{BASE_URL}/message/sendText/{INSTANCE_NAME}"
    payload = {"number": number, "text": text}
    try:
        response = requests.post(url, json=payload, headers=HEADERS, timeout=10)
        print("Status Code:", response.status_code)
        print("Response JSON:", response.json())
    except requests.RequestException as e:
        print("Error sending message:", e)

if __name__ == "__main__":
    if check_instance_connection():
        print("✅ Instance is connected. Sending message...")
        send_message("51967244227", "Message send started")
    else:
        print("❌ Instance is not connected. Aborting send.")
