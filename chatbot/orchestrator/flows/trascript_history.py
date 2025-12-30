from chatbot.models import Message


def transcript_history(messages: list[Message]):
    # Convert chat history to plain text transcript
    history = []
    for msg in messages:
        speaker = "paciente" if msg.from_user else "tu"
        history.append(f"-{speaker}: {msg.text}")

    history = history[::-1]

    transcript = "\n".join(history)

    return transcript, history