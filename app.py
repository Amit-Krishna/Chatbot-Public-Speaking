import os
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify, session
from dotenv import load_dotenv
import logging
import re

# --- Configuration & Setup ---
load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
app = Flask(__name__)

# --- Secret Key for Session ---
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-replace-in-prod')
if app.secret_key == 'dev-secret-key-replace-in-prod':
    logging.warning("Using default FLASK_SECRET_KEY. Please set a proper secret key in your .env file for production.")

# --- API Client Setup (Gemini Only) ---
google_api_key = os.getenv("GOOGLE_API_KEY")
gemini_model_name = 'gemini-1.5-flash' # Or 'gemini-pro'
gemini_model = None
if not google_api_key:
    logging.error("FATAL: GOOGLE_API_KEY not found in .env file. Cannot run.")
    raise ValueError("GOOGLE_API_KEY not configured.")
else:
    try:
        genai.configure(api_key=google_api_key)
        gemini_model = genai.GenerativeModel(gemini_model_name)
        logging.info(f"Google Gemini client ({gemini_model_name}) configured successfully.")
    except Exception as e:
        logging.error(f"FATAL: Error configuring Google Gemini client: {e}", exc_info=True)
        raise

# --- Chatbot Scope & Configuration ---
BOT_SCOPE = """
Primary Focus: Assisting users with AI tools and techniques specifically for **Public Speaking preparation, practice, and analysis**.
Includes:
- Helping brainstorm, outline, and **write speech content** on user-provided topics (like friendship, technology, etc.).
- Suggesting improvements for clarity, impact, and word choice within a speech context.
- Explaining AI tools for delivery practice (feedback on pace, tone, fillers).
- Discussing AI for presentation analysis (structure, engagement).
- Guiding users on using AI for audience analysis or creating visual aids.
- Offering tips on using AI for managing speaking anxiety.
- Naming or describing specific AI public speaking tools/platforms.
- Discussing trends and ethics of AI *in public speaking*.

Out of Scope: Answering general knowledge questions (e.g., math problems like '9+88', 'what date is today', capitals, history facts unrelated to speech content), coding help, cooking, relationship advice, etc., unless the user is asking how to incorporate such *data* into speech content. The request must clearly relate to creating or improving a speech/presentation.
"""

OUT_OF_SCOPE_MESSAGE = "My expertise is focused on AI for Public Speaking preparation and practice. While that's an interesting question, it seems outside this specific area. Can I help you brainstorm speech ideas, practice delivery with AI tools, or analyze a presentation?"

# History Configuration
MAX_HISTORY_TURNS = 15 # Approx 15 user + 15 bot messages
MAX_HISTORY_MESSAGES = MAX_HISTORY_TURNS * 2

# Model Configuration
MAX_RESPONSE_TOKENS = 700 # Increased significantly for drafting full speeches
TEMPERATURE_RESPONSE = 0.75

# --- Core Chatbot Functions ---

# --- ** REMOVED Relevance Check Function - Scope handled within main generator ---

# --- ** MODIFIED Gemini Response Function (Context-Aware Scope Check) ** ---
def generate_response_gemini(user_query: str, history: list) -> str | None:
    """
    Generates response using Google Gemini chat session.
    Uses history for context, attempts to progress after clarification,
    and applies scope rules intelligently, prioritizing conversational context
    for follow-up commands.
    """
    if not gemini_model:
        logging.error("Gemini model not available during response generation.")
        return None
    logging.info(f"Generating response (Gemini) with history (len={len(history)}) for: '{user_query[:50]}...'")

    gemini_history = []
    for msg in history:
        role = 'user' if msg['role'] == 'user' else 'model'
        gemini_history.append({'role': role, 'parts': [str(msg.get('content', ''))]})

    # --- ** Prompt with Context-Aware Logic ** ---
    prompt_for_current_turn = f"""
INSTRUCTIONS: You are an AI assistant strictly specialized in **AI Public Speaking Assistants**. Your goal is to help users prepare, practice, or analyze speeches.

**Processing Steps:**

1.  **Analyze History & Current Query:** Review the conversation history AND the CURRENT 'USER QUERY' below.
2.  **Check for Follow-up Command:** Determine if the CURRENT query is a short, direct command or confirmation relating to your *immediately preceding* message (e.g., "yes", "do that", "draft that outline", "the above one only", "make the speech now", "use those details").
3.  **Execute Follow-up (If Applicable):** If it IS a direct follow-up (#2 is True) AND your previous message was *on-topic* (e.g., asking for clarification, presenting an outline), then **PRIORITIZE fulfilling the command based on the established context**. Proceed directly to the requested action (e.g., drafting the speech using the details gathered). **DO NOT** trigger the off-topic refusal for valid follow-ups.
4.  **Handle Clarification Answers:** If your *last* message asked for details AND the CURRENT query provides those details (and is not a simple command from #2), acknowledge the input and proceed to the next logical step (brainstorming, outlining, drafting). DO NOT repeat clarification.
5.  **Check New Query Relevance:** If the CURRENT query is *NOT* a follow-up command (#2 is False) AND *NOT* a clarification answer (#4 is False), evaluate if it introduces a **new topic**. If this new topic is clearly outside the Public Speaking SCOPE (e.g., math, date, general facts, cooking), then respond EXACTLY with: '{OUT_OF_SCOPE_MESSAGE}'.
6.  **Handle New On-Topic Query:** If the query introduces a new topic *within* the scope, or continues an existing on-topic discussion, provide a helpful, conversational response.
7.  **Formatting:** Use Markdown (**bold**, *italic*, lists) for clear formatting in your valid, on-topic responses.

SCOPE (Adhere Strictly, except for valid follow-ups per instruction #3):
{BOT_SCOPE}
---
USER QUERY: {user_query}
"""

    try:
        # Start chat session WITH the history context
        chat_session = gemini_model.start_chat(history=gemini_history)

        safety_settings = [ {"category": c, "threshold": "BLOCK_MEDIUM_AND_ABOVE"} for c in ["HARM_CATEGORY_HARASSMENT", "HARM_CATEGORY_HATE_SPEECH", "HARM_CATEGORY_SEXUALLY_EXPLICIT", "HARM_CATEGORY_DANGEROUS_CONTENT"]]
        generation_config = genai.types.GenerationConfig(
            temperature=TEMPERATURE_RESPONSE,
            max_output_tokens=MAX_RESPONSE_TOKENS
        )

        # Send the structured prompt for THIS turn
        response = chat_session.send_message(
            prompt_for_current_turn, # Send the prompt with enhanced context-aware instructions + query
            stream=False,
            safety_settings=safety_settings,
            generation_config=generation_config
            )

        # Handle response (same error/block checks as before)
        generated_text = None
        if hasattr(response, 'text') and response.text: generated_text = response.text.strip()
        elif response.parts: generated_text = "".join(part.text for part in response.parts).strip()

        if response.prompt_feedback and response.prompt_feedback.block_reason:
             logging.warning(f"Gemini response blocked. Reason: {response.prompt_feedback.block_reason}")
             return generated_text if generated_text else "My safety filters prevented processing that request. Please rephrase."

        if not generated_text:
             logging.warning("Gemini returned no usable text content.")
             finish_reason = getattr(response, 'candidates', [{}])[0].get('finish_reason', 'UNKNOWN')
             if finish_reason == 'SAFETY': return "My safety filters prevented processing that request. Please rephrase."
             else: return f"Gemini didn't provide a valid response (Finish reason: {finish_reason}). You could try asking differently."

        # Check if Gemini correctly returned the refusal message
        # Use 'in' check for robustness, but compare exact for logic below
        is_refusal = generated_text == OUT_OF_SCOPE_MESSAGE
        if is_refusal:
            logging.info("Gemini correctly refused query based on current turn instructions.")
            return OUT_OF_SCOPE_MESSAGE

        # If it wasn't the refusal message, assume it's an on-topic response (drafting, brainstorming, etc.)
        return generated_text

    except Exception as e:
        logging.error(f"Google Gemini API Error during response generation: {e}", exc_info=True)
        return "I encountered an issue connecting to my knowledge base. Please try again shortly."


# --- Flask Routes ---
@app.route("/")
def index():
    """Serves the main HTML page."""
    return render_template("index.html")

# --- ** /chat Route (No changes needed here from previous version) ** ---
@app.route("/chat", methods=["POST"])
def chat():
    """Handles messages, manages history, calls Gemini (which handles scope/progression)."""
    try:
        user_message = request.json.get("message")
        if not user_message:
            return jsonify({"response": "Please enter a message."}), 400

        chat_history = session.get('chat_history', [])
        logging.info(f"Received message (History len: {len(chat_history)}): {user_message[:100]}...")

        # Add user message to history
        current_turn_user_message = {"role": "user", "content": user_message}
        chat_history.append(current_turn_user_message)

        # Generate Response (using history before current message)
        logging.info("Generating Gemini response (scope/context check internal).")
        # Pass history *before* this turn's message for context for the generator
        bot_response = generate_response_gemini(user_message, chat_history[:-1])

        # Process Response & Update History
        final_bot_message = ""
        history_needs_update = True
        is_refusal = False

        if bot_response is None or "encountered an issue connecting" in (bot_response or ""):
            # Generation failed entirely (e.g., API error)
            logging.error(f"Gemini response generation failed or returned error: {bot_response}")
            final_bot_message = bot_response or "I'm having trouble generating a response right now."
            # Remove the user message since it wasn't answered
            if chat_history: chat_history.pop()
            history_needs_update = False
        # Check if the response IS the refusal message
        elif bot_response == OUT_OF_SCOPE_MESSAGE: # Check for exact match now
            logging.info("Gemini response matched OUT_OF_SCOPE_MESSAGE.")
            final_bot_message = OUT_OF_SCOPE_MESSAGE # Use the standard message
            is_refusal = True
            # Add the refusal to history.
            chat_history.append({"role": "assistant", "content": final_bot_message})
        else:
            # Assume valid, on-topic response
            final_bot_message = bot_response
            chat_history.append({"role": "assistant", "content": final_bot_message})

        # History Management: Limit Size & Save
        if len(chat_history) > MAX_HISTORY_MESSAGES:
            chat_history = chat_history[-MAX_HISTORY_MESSAGES:]
            logging.info(f"History truncated to {len(chat_history)} messages.")

        if history_needs_update:
            session['chat_history'] = chat_history
        else:
             # Save potentially popped history if update failed
            session['chat_history'] = chat_history


        return jsonify({"response": final_bot_message})

    except Exception as e:
        logging.error(f"Critical error in /chat endpoint: {e}", exc_info=True)
        return jsonify({"response": "An critical server error occurred. Please try again later."}), 500


# --- Run the App ---
if __name__ == "__main__":
    app.run(debug=True, host='127.0.0.1', port=5000)