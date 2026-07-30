"""
Call Simulator
- Simulates a full AI phone call in terminal
- No real phone needed - just type responses
- Perfect for demo and testing
"""
import time
import random
from ai_agent import get_ai_response, analyze_sentiment, generate_opening
from lead_scorer import score_lead_from_keywords, get_lead_recommendation
from text_to_speech import speak_text
from speech_to_text import DEMO_RESPONSES


def simulate_call(lead_name: str, phone: str, product_info: str, use_voice: bool = False):
    """Simulate a complete AI sales call"""

    print("\n" + "=" * 60)
    print(f"📞 CALLING: {lead_name} ({phone})")
    print(f"📦 Product: {product_info}")
    print("=" * 60)

    # Simulate ringing
    print("\n🔔 Ringing...")
    time.sleep(1)
    print("✅ Call Connected!\n")
    print("-" * 40)
    print("Type your responses as the LEAD (human)")
    print("Type 'hangup' to end the call")
    print("-" * 40 + "\n")

    # Conversation history for AI
    conversation_history = []

    # AI opens the call
    opening = generate_opening(lead_name, product_info)
    print(f"🤖 AI Agent: {opening}\n")
    conversation_history.append({"role": "assistant", "content": opening})

    if use_voice:
        speak_text(opening)

    # Conversation loop
    turn_count = 0
    max_turns = 10  # Max 10 back-and-forth exchanges

    while turn_count < max_turns:
        # Human (lead) responds
        human_input = input(f"👤 {lead_name}: ").strip()

        if human_input.lower() in ['hangup', 'bye', 'end', 'quit']:
            print("\n📴 Call Ended by lead")
            break

        if not human_input:
            continue

        conversation_history.append({"role": "user", "content": human_input})

        # AI responds
        ai_response = get_ai_response(conversation_history, product_info)
        print(f"\n🤖 AI Agent: {ai_response}\n")
        conversation_history.append({"role": "assistant", "content": ai_response})

        if use_voice:
            speak_text(ai_response)

        turn_count += 1

        # Check if AI naturally ended the call
        end_signals = ["thank you for your time", "have a great day", "goodbye", "talk soon"]
        if any(signal in ai_response.lower() for signal in end_signals):
            print("\n📴 Call Ended by AI Agent")
            break

    # Post-call analysis
    print("\n" + "=" * 60)
    print("📊 POST-CALL ANALYSIS")
    print("=" * 60)

    # Get AI-powered analysis
    analysis = analyze_sentiment(conversation_history)
    print(f"\n🎯 Sentiment: {analysis.get('sentiment', 'unknown')}")
    print(f"📈 Lead Score: {analysis.get('score', 0)}/10")
    print(f"🏷️  Category: {analysis.get('category', 'unknown')}")
    print(f"📝 Summary: {analysis.get('summary', 'N/A')}")
    print(f"\n💡 Recommendation: {get_lead_recommendation(analysis.get('category', 'cold'))}")
    print("=" * 60)

    return {
        "lead_name": lead_name,
        "phone": phone,
        "conversation": conversation_history,
        "analysis": analysis,
        "turns": turn_count
    }


def run_demo():
    """Run a quick demo with sample data"""
    print("\n" + "🚀" * 20)
    print("\n   AI CALL FILTRATION + LEAD GENERATION SYSTEM")
    print("   ============================================")
    print("   Demo Mode - Type responses as the lead\n")
    print("🚀" * 20)

    # Sample lead
    lead_name = input("\n📋 Enter lead name (or press Enter for 'Rahul Sharma'): ").strip()
    if not lead_name:
        lead_name = "Rahul Sharma"

    phone = input("📱 Enter phone number (or press Enter for demo): ").strip()
    if not phone:
        phone = "+91-9876543210"

    product = input("📦 What product/service to pitch? (or press Enter for default): ").strip()
    if not product:
        product = "AI-powered CRM software that helps businesses manage leads and increase sales by 40%"

    # Run the simulated call
    result = simulate_call(lead_name, phone, product, use_voice=False)

    # Ask if want to run another
    again = input("\n\n🔄 Run another call? (yes/no): ").strip().lower()
    if again in ['yes', 'y']:
        run_demo()


if __name__ == "__main__":
    run_demo()
