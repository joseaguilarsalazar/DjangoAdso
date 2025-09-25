import chatbot.orchestrator.flows as flows
from chatbot.orchestrator.router import classify_intent
from ..models import Chat

class Orchestrator:
    def __init__(self):
        # Intent → function map
        self.intent_map = {
            "appointment_lookup": flows.lookup_appointment,
            "patient_registration": flows.register_patient,
            "default": flows.default_chat
            # add new ones here...
        }

    def handle_message(self, text, chat: Chat):
        intent = classify_intent(text)

        messages = chat.last_messages()

        # Get the right handler, or fallback to default
        handler = self.intent_map.get(intent, flows.default_chat)

        # Execute the flow
        return handler(messages, chat)

