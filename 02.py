import requests
import os
import environ
from pathlib import Path
from djangoAdso.settings import env

headers = {
    "api_access_token": env('CHATWOOT_ACCESS_TOKEN'),
    "Content-Type": "application/json"
}

account_id = env('CHATWOOT_ACCOUNT_ID')
base_url = env('CHATWOOT_API_URL').rstrip('/')

# 1. Search for the conversation to get the ID
phone_number = "+51967244227" 
print(f"🔍 Searching for conversation with {phone_number}...")

search_url = f"{base_url}/api/v1/accounts/{account_id}/contacts/search?q={phone_number}"
resp = requests.get(search_url, headers=headers)
data = resp.json()

if not data['payload']:
    print("❌ Contact not found!")
    exit()

contact_id = data['payload'][0]['id']
print(f"✅ Contact ID: {contact_id}")

# 2. Get Conversations for this contact
conv_url = f"{base_url}/api/v1/accounts/{account_id}/conversations?contact_id={contact_id}"
resp = requests.get(conv_url, headers=headers)
conv_data = resp.json()

if not conv_data['data']['payload']:
    print("❌ No conversations found for this contact.")
    exit()

# Get the most recent conversation
conversation = conv_data['data']['payload'][0]
conv_id = conversation['id']
inbox_id = conversation['inbox_id']

print(f"✅ Found Conversation ID: {conv_id}")
print(f"📦 Inside Inbox ID: {inbox_id}") 
print(f"⚠️ EXPECTED INBOX ID: {env('CHATWOOT_INBOX_ID')}")

if str(inbox_id) != str(env('CHATWOOT_INBOX_ID')):
    print("🚨 MISMATCH! You are sending messages to the wrong inbox.")

# 3. List Messages in that conversation
msg_url = f"{base_url}/api/v1/accounts/{account_id}/conversations/{conv_id}/messages"
resp = requests.get(msg_url, headers=headers)
messages = resp.json()['payload']

print("\nRecent Messages in Chatwoot DB:")
for msg in messages[-3:]: # Show last 3
    print(f"- [{msg['status']}] {msg['message_type']}: {msg['content']}")
    if msg['status'] == 'failed':
        print("  ❌ STATUS IS FAILED. Check Sidekiq logs!")