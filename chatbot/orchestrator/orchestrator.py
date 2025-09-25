import chatbot.orchestrator.flows as flows
from chatbot.orchestrator.router import classify_intent

class Orchestrator:
    def handle_message(self, text, user):
        intent = classify_intent(text)
        if intent == "appointment_lookup":
            return flows.lookup_appointment(text, user)
        elif intent == "patient_registration":
            return flows.register_patient(text, user)
        else:
            return flows.default_chat(text)
