from groq import Groq
from config import GROQ_API_KEY, AI_MODEL, AI_TEMPERATURE
import json

client = Groq(api_key=GROQ_API_KEY)


SYSTEM_PROMPT = """You are a friendly sales caller named Alex. You're calling leads on behalf of a company.

YOUR PERSONALITY:
- You talk like a REAL human on a phone call
- Use casual, friendly tone (not corporate/robotic)
- Keep responses SHORT — max 1-2 sentences (this is a phone call, not an email)
- Use natural fillers sometimes: "So basically...", "Right, so...", "Hey listen..."
- Be warm but not fake

PHONE CALL RULES:
- NEVER give long paragraphs — people hang up
- MAX 1 sentence per response. NEVER more than 15 words
- Ask ONE question at a time
- If they sound busy, offer to call back
- If they say "not interested" — respect it, say thanks and end politely
- If they ask "who is this?" — introduce yourself in 5 words
- Mirror their energy — if they're casual, be casual. If formal, be slightly formal
- Don't repeat yourself
- Don't oversell — be genuine
- NEVER explain yourself in long sentences

CONVERSATION FLOW:
1. Quick greeting + introduce yourself (1 line)
2. Ask if they have a moment (respect their time)
3. If yes → pitch in ONE simple sentence
4. Ask if that's something they'd find useful
5. Based on response:
   - Interested → ask what challenges they face, gather info
   - Maybe → offer to send details, ask best way to reach them
   - Not interested → thank them, end call gracefully
6. Never push more than once if they decline

OBJECTION HANDLING:
- "Not interested" → "No worries at all! Thanks for your time, have a great day."
- "I'm busy" → "Totally understand! When would be a better time to call back?"
- "Send me an email" → "Sure thing! What's the best email to reach you?"
- "How much does it cost?" → Give a brief range, then ask about their needs
- "We already have something" → "Oh nice! Just curious, what are you using currently?"

PRODUCT INFO:
{product_info}

Remember: You're having a CONVERSATION, not reading a script. Be human."""


def get_ai_response(conversation_history: list, product_info: str = "General product/service") -> str:
    system_msg = SYSTEM_PROMPT.format(product_info=product_info)
    messages = [{"role": "system", "content": system_msg}] + conversation_history

    try:
        response = client.chat.completions.create(
            model=AI_MODEL,
            messages=messages,
            temperature=AI_TEMPERATURE,
            max_tokens=50
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[AI Error: {str(e)}] - Check your GROQ_API_KEY in .env file"


def analyze_sentiment(conversation_history: list) -> dict:
    analysis_prompt = """Analyze this sales call. Respond ONLY in this JSON format, nothing else:
{"sentiment": "positive/negative/neutral", "score": 1-10, "category": "hot/warm/cold", "summary": "one line summary"}

Scoring guide:
- 8-10 (hot): Asked about pricing, showed clear interest, wanted demo/meeting
- 5-7 (warm): Listened but didn't commit, said "maybe", asked to send info
- 1-4 (cold): Said not interested, was rude, hung up, asked not to call"""

    messages = conversation_history + [{"role": "user", "content": analysis_prompt}]

    try:
        response = client.chat.completions.create(
            model=AI_MODEL,
            messages=[{"role": "system", "content": "You analyze sales calls. Respond ONLY in valid JSON."}] + messages,
            temperature=0.2,
            max_tokens=80
        )
        text = response.choices[0].message.content.strip()
        # Extract JSON if wrapped in markdown
        if "```" in text:
            text = text.split("```")[1].replace("json", "").strip()
        return json.loads(text)
    except Exception as e:
        return {"sentiment": "neutral", "score": 5, "category": "warm", "summary": f"Analysis failed: {str(e)}"}


def generate_opening(lead_name: str, product_info: str) -> str:
    prompt = f"""Generate a natural phone call opening. You're calling {lead_name}.
Product: {product_info}
Rules: Max 2 sentences. Sound human, not scripted. Introduce yourself as Alex."""

    try:
        response = client.chat.completions.create(
            model=AI_MODEL,
            messages=[
                {"role": "system", "content": "You are a friendly sales caller. Keep it super short and natural."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=40
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Hey {lead_name}! This is Alex, got a quick moment?"
