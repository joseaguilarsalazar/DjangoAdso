import chatbot.orchestrator.flows as flows
from chatbot.orchestrator.clasificator import classify_intent
from ..models import Chat

class Orchestrator:
    def __init__(self):
        # Intent → function map
        self.intent_map = {
            "appointment_lookup": flows.lookup_appointment,
            "patient_registration": flows.register_patient,
            "appointment_registration": flows.register_appointment,
            "default": flows.default_chat,
            "data_confirmation": flows.data_confirmation,
            "lookup_patient": flows.lookup_patient,
            # add new ones here...
        }

    def handle_message(self, text, chat: Chat):
        if chat.current_state != "default":
            intent = chat.current_state
        else:
            intent = classify_intent(text)
            chat.current_state = intent
            chat.save()

        messages = chat.last_messages()

        # Get the right handler, or fallback to default
        handler = self.intent_map.get(intent, flows.default_chat)

        # Execute the flow
        return handler(messages, chat)

