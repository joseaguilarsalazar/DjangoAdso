import requests
import time
import logging
import os
import environ
from requests.exceptions import RequestException, Timeout, ConnectionError, HTTPError
from pathlib import Path

# --- Environment Setup ---
BASE_DIR = Path(__file__).resolve().parent.parent.parent
env_file = os.path.join(BASE_DIR, '.env')

if os.path.exists(env_file):
    environ.Env.read_env(env_file)

env = environ.Env(DEBUG=(bool, False))

logger = logging.getLogger(__name__)

class ChatwootManager:
    """
    Manager to interact with Chatwoot API v1.
    Replaces the previous EvolutionApiManager.
    """
    
    # Load config from env
    base_url = env('CHATWOOT_API_URL', default='https://app.chatwoot.com')
    api_token = env('CHATWOOT_ACCESS_TOKEN')
    account_id = env('CHATWOOT_ACCOUNT_ID')
    default_inbox_id = env('CHATWOOT_INBOX_ID')
    
    def __init__(self, api_token: str = None, base_url: str = None, account_id: str = None):
        if api_token:
            self.api_token = api_token
        if base_url:
            self.base_url = base_url
        if account_id:
            self.account_id = account_id

        # Headers for Chatwoot API
        self.headers = {
            "Content-Type": "application/json",
            "api_access_token": self.api_token
        }

    def _validate_number(self, number: str) -> bool:
        """Ensures number contains only digits and is of sufficient length."""
        if not number:
            return False
        s = str(number).strip().replace('+', '')
        return s.isdigit() and len(s) >= 8

    def _get_or_create_contact(self, number: str, inbox_id: int):
        """
        Internal helper: Search for a contact by phone number. 
        If not found, create a new one.
        """
        # Ensure number has + prefix for Chatwoot
        clean_number = number.strip().replace('+', '')
        formatted_number = f"+{clean_number}"
        
        # 1. Search for existing contact
        search_url = f"{self.base_url}/api/v1/accounts/{self.account_id}/contacts/search"
        try:
            resp = requests.get(search_url, headers=self.headers, params={"q": formatted_number})
            resp.raise_for_status()
            data = resp.json()
            
            # Chatwoot returns { "payload": [ ... ] }
            contacts = data.get("payload", [])
            if contacts:
                logger.debug(f"Contact found for {formatted_number}: ID {contacts[0]['id']}")
                return contacts[0]["id"]
                
        except RequestException as e:
            logger.warning(f"Error searching contact {formatted_number}: {e}")

        # 2. Create new contact if not found
        create_url = f"{self.base_url}/api/v1/accounts/{self.account_id}/contacts"
        payload = {
            "inbox_id": inbox_id,
            "name": formatted_number,
            "phone_number": formatted_number
        }
        try:
            resp = requests.post(create_url, headers=self.headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            contact_id = data.get("payload", {}).get("contact", {}).get("id") or data.get("payload", {}).get("id")
            logger.info(f"Created new contact for {formatted_number}: ID {contact_id}")
            return contact_id
        except RequestException as e:
            logger.error(f"Failed to create contact for {formatted_number}: {e.response.text if e.response else e}")
            raise

    def _get_conversation_id(self, contact_id: int, inbox_id: int):
        """
        Internal helper: Create a conversation or get the existing open one.
        Chatwoot's 'Create Conversation' endpoint automatically returns the existing 
        open conversation if one exists for the contact/inbox pair.
        """
        url = f"{self.base_url}/api/v1/accounts/{self.account_id}/conversations"
        payload = {
            "source_id": contact_id, # Can typically be contact_id for standard API usage
            "contact_id": contact_id,
            "inbox_id": inbox_id,
            "status": "open"
        }
        
        try:
            resp = requests.post(url, headers=self.headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            # ID is usually at the root or inside payload depending on version
            conv_id = data.get("id")
            return conv_id
        except RequestException as e:
            logger.error(f"Failed to get/create conversation: {e.response.text if e.response else e}")
            raise

    def send_message(self, number: str, message: str, timeout: float = 10.0, max_retries: int = 3, message_instance=None):
        """
        Sends a message via Chatwoot.
        
        Flow:
        1. Find/Create Contact
        2. Find/Create Conversation
        3. Send Message
        """
        
        # Use provided instance/inbox or default from env
        inbox_id = message_instance if message_instance else self.default_inbox_id
        
        if not self._validate_number(number):
            return {"ok": False, "error": f"Invalid number: {number}"}

        backoff = 1.0
        attempt = 0
        last_exception = None

        while attempt < max_retries:
            attempt += 1
            try:
                # Step 1 & 2: Resolve Contact and Conversation
                # (We do this inside the loop in case of transient API errors)
                contact_id = self._get_or_create_contact(number, inbox_id)
                conversation_id = self._get_conversation_id(contact_id, inbox_id)
                
                # Step 3: Send Message
                url = f"{self.base_url}/api/v1/accounts/{self.account_id}/conversations/{conversation_id}/messages"
                payload = {
                    "content": message,
                    "message_type": "outgoing",
                    "private": False
                }
                
                logger.debug(f"Sending message attempt {attempt} to conv {conversation_id} (url={url})")
                resp = requests.post(url, json=payload, headers=self.headers, timeout=timeout)
                
                # Check for errors
                if 500 <= resp.status_code < 600:
                    raise HTTPError(f"Server error {resp.status_code}")
                
                resp.raise_for_status()
                
                logger.info(f"Message sent to {number} (Conv {conversation_id}): status={resp.status_code}")
                return {"ok": True, "status_code": resp.status_code, "response": resp.json(), "error": None}

            except (Timeout, ConnectionError, HTTPError, RuntimeError) as e:
                logger.warning(f"Error sending to {number} (attempt {attempt}/{max_retries}): {e}")
                last_exception = e
                time.sleep(backoff)
                backoff *= 2
            except Exception as e:
                logger.exception(f"Unexpected error sending to {number}: {e}")
                return {"ok": False, "error": str(e)}

        err_msg = f"Failed after {max_retries} attempts. Last error: {str(last_exception)}"
        logger.error(err_msg)
        return {"ok": False, "status_code": None, "error": err_msg}

    def check_instance_state(self, timeout: float = 5.0, inbox_id=None):
        """
        Checks the health of the specific Inbox in Chatwoot.
        Replaces 'check_instance_state' from Evolution.
        """
        target_inbox = inbox_id if inbox_id else self.default_inbox_id
        url = f"{self.base_url}/api/v1/accounts/{self.account_id}/inboxes/{target_inbox}"
        
        try:
            resp = requests.get(url, headers=self.headers, timeout=timeout)
            resp.raise_for_status()
            data = resp.json()
            
            # Chatwoot doesn't have a "connecting" state exposed easily via API for the channel itself,
            # but if we get the Inbox details, the API is reachable and the inbox exists.
            name = data.get("name")
            channel_type = data.get("channel_type")
            
            return {
                "ok": True, 
                "status_code": resp.status_code, 
                "result": {"state": "active", "name": name, "type": channel_type}, 
                "error": None
            }
            
        except Exception as e:
            logger.error(f"Failed to check inbox state: {e}")
            return {"ok": False, "error": str(e)}

if __name__ == "__main__":
    # Test execution
    manager = ChatwootManager()
    
    # 1. Send test message
    # Ensure you have your .env set with CHATWOOT_ACCOUNT_ID and INBOX_ID
    print("📨 Sending Message...")
    # Note: Replace with a real test number in your system
    print(manager.send_message(number="51967244237", message="Mensaje de Prueba desde Chatwoot Manager"))

    # 2. Check State
    print("\n🔍 Checking Inbox State...")
    print(manager.check_instance_state())