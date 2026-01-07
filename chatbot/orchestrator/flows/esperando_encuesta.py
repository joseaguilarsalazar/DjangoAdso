import json
import logging
from chatbot.models import Chat
from core.models import Paciente
from chatbot.models import EncuestaSatisfaccion
from .AI_Client import client
from .trascript_history import transcript_history
from .default_chat import default_chat

logger = logging.getLogger(__name__)

def esperando_encuesta(messages, chat: Chat):
    """
    Analyzes the patient's survey response to extract sentiment and actionable insights.
    """
    logger.info(f"📍 [Encuesta] Starting analysis for Chat ID: {chat.id}")

    # 1. Get the text context
    try:
        transcription, history = transcript_history(messages)
        logger.info(f"📝 [Encuesta] Step 1: Transcription extracted. Length: {len(transcription)} chars. Text: '{transcription[:50]}...'")
    except Exception as e:
        logger.error(f"❌ [Encuesta] Step 1 Failed: Error extracting transcript: {e}")
        return "Error procesando su respuesta."

    # 2. Identify the patient (Crucial for linking data)
    paciente = None
    try:
        # NOTE: standard Chat model field is usually 'number', verifying if 'phone_number' exists
        phone_number = getattr(chat, 'number', getattr(chat, 'phone_number', None))
        
        if phone_number:
            clean_phone = str(phone_number).replace('+', '').strip()
            logger.info(f"🔍 [Encuesta] Step 2: Looking for patient with phone: {clean_phone}")
            
            # Trying both field names 'telf_pac' (from previous tasks) and 'telefono' (from your snippet) just in case
            paciente = Paciente.objects.filter(telf_pac__icontains=clean_phone).first() 
            if not paciente:
                 paciente = Paciente.objects.filter(telefono__icontains=clean_phone).first()

            if paciente:
                logger.info(f"✅ [Encuesta] Step 2: Patient found: {paciente} (ID: {paciente.id})")
            else:
                logger.warning(f"⚠️ [Encuesta] Step 2: Patient NOT found for phone {clean_phone}")
        else:
             logger.error("❌ [Encuesta] Step 2: Chat object has no phone number.")
            
    except Exception as e:
        logger.error(f"⚠️ [Encuesta] Step 2 Error: Could not link patient: {e}")
        paciente = None

    # 3. Define the AI Prompt
    logger.info("🧠 [Encuesta] Step 3: Generating AI Prompt...")
    
    prompt = f"""
    You are a Data Analyst for a Dental Clinic. You are analyzing a response from a patient to a satisfaction survey.

    The survey asked 3 things:
    1. What they valued most.
    2. What could be improved.
    3. Suggestions.

    Your task is to analyze the user's input and extract structured data in JSON format.

    ### output_format:
    {{
        "sentiment": "POSITIVE" | "NEUTRAL" | "NEGATIVE",
        "aspectos_positivos": ["list", "of", "things", "liked"],
        "areas_mejora": ["list", "of", "complaints", "or", "improvements"],
        "sugerencias": "Summary of any specific suggestion",
        "requiere_atencion_humana": boolean,
        "response_message": "string",
        "change_logic" : boolean
    }}

    ### Rules for 'response_message':
    - If POSITIVE: Thank them warmly.
    - If NEGATIVE/IMPROVEMENT: Thank them for honesty and apologize if needed.
    - Keep it short and natural (WhatsApp style).
    - If the user answers something unrelated (like scheduling an appointment), set "change_logic": true.

    ### Input Text (Patient Response):
    "{transcription}"
    """

    try:
        # 4. Call LLM
        logger.info("🚀 [Encuesta] Step 4: Sending request to AI Model...")
        response = client.chat.completions.create(
            model="deepseek-chat", # or gpt-4o-mini
            messages=[{"role": "user", "content": prompt}],
            max_tokens=350,
            temperature=0.5,
            response_format={"type": "json_object"},
        )
        logger.info("📥 [Encuesta] Step 5: AI Response received.")

        # 5. Parse JSON
        raw_content = response.choices[0].message.content
        logger.debug(f"📜 [Encuesta] Step 6: Raw Content: {raw_content}")
        
        data = json.loads(raw_content)
        logger.info(f"✅ [Encuesta] Step 6: JSON Parsed successfully. Sentiment: {data.get('sentiment')}")

        # 6. Check Logic Change
        if data.get('change_logic', False):
            logger.info("🔀 [Encuesta] Step 7: 'change_logic' is TRUE. Switching to default flow.")
            chat.current_state = "default"
            chat.save()
            return default_chat(messages, chat)

        # 7. Save Data
        if paciente:
            logger.info("💾 [Encuesta] Step 8: Saving survey data to DB...")
            EncuestaSatisfaccion.objects.create(
                paciente=paciente,
                texto_original=transcription,
                sentimiento=data.get('sentiment', 'NEUTRAL'),
                aspectos_positivos=json.dumps(data.get('aspectos_positivos', [])),
                areas_mejora=json.dumps(data.get('areas_mejora', [])),
                sugerencias=data.get('sugerencias', ''),
                requiere_atencion_humana=data.get('requiere_atencion_humana', False)
            )
            logger.info("✅ [Encuesta] Step 8: Data saved.")
            
            if data.get('requiere_atencion_humana'):
                logger.warning(f"🚨 [Encuesta] URGENT ATTENTION REQUIRED for Patient {paciente.id}")
        else:
            logger.info("ℹ️ [Encuesta] Step 8: Skipping DB save (No Patient linked).")

        # 8. Update State
        logger.info("🔄 [Encuesta] Step 9: Resetting chat state to 'default'.")
        chat.current_state = "default"
        chat.save()

        # 9. Return Response
        final_message = data.get('response_message', "¡Muchas gracias por sus comentarios!")
        logger.info(f"📤 [Encuesta] Step 10: Returning response: '{final_message}'")
        return final_message

    except Exception as e:
        logger.error(f"❌ [Encuesta] CRITICAL ERROR during processing: {e}", exc_info=True)
        # Fallback
        chat.current_state = "default"
        chat.save()
        return "¡Muchas gracias por su respuesta! La hemos registrado correctamente."