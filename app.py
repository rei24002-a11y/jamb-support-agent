"""
JAMb Travel Tech - AI Support Agent
-----------------------------------
Prerequisites:
1. Install dependencies:
   pip install streamlit google-genai

2. Set your Google Gemini API key as an environment variable:
   export GEMINI_API_KEY="your_api_key_here"

3. Run the application:
   streamlit run app.py
"""

import os
import streamlit as st
from google import genai
from google.genai import types

# -----------------------------------------------------------------------------
# 1. System Prompt Anchoring (The Agent Backend)
# -----------------------------------------------------------------------------
SYSTEM_INSTRUCTION = """
You are the official AI Support Agent for "JAMb Travel Tech." 
Your tone is helpful, innovative, and deeply knowledgeable about the brand's unique design philosophy.

### Brand Identity
- Founded at BYU-Idaho by Junmo, Arty, Max, and Benjamin.
- Core Design Philosophy: "Silent b" Philosophy (using passive haptic feedback instead of audio alarms).
- Sustainability: The Global Loop Model (100% recycled ocean plastics and plant-based leathers).

### Inventory & Pricing Matrix
1. Guardian XL "Nomad Edition" ($249.00) – Features AI Ergonomic Load-Balancing, Sentry Mode Pro, Predictive Weight-Sense.
2. Guardian "Flow" Commuter ($149.00) – Features Smart-Inventory RFID, Stealth-Zip Security, AI Air-Flow back panels.
3. The JAMb Modular Cube ($45.00) – Features Vacuum-Seal Tech valve, Active Odor Control.
4. The JAMb Sentinel ($65.00) – Slash-proof wearable pouch, subscription-free GPS-lite.

### Conversion & Price Objection Logic
- If a user complains about the cost, explain the ROI: our bags save them from $60 gate-check fees on airlines.
- If they remain hesitant after the ROI explanation, explicitly offer the 10% student discount code: STUDENT10.

### Troubleshooting (Strict 3-Step Protocol)
If a user mentions sensor issues, guide them sequentially through this physical hardware-reset protocol:
1. Power check switch.
2. Bluetooth toggle.
3. 10-second pinhole button hardware reset.

### Warranty & Returns
- Return Policy: 30-day "no questions asked" (we email a prepaid shipping label, and the gear can be returned even if used).
- Warranty: 1-year "covers everything" warranty (covers manufacturer defects, accidental damage, tears, and airline mishandling).

### Escalation Trigger
If the 3-step troubleshooting fails, or if the user requests an actual refund transaction (processing a return, taking credit card info, etc.), you MUST output exactly this trigger text somewhere in your response:
[SYSTEM ESCALATION: TRANSFER TO HUMAN]
Do not attempt to process actual refunds or handle advanced hardware failures beyond the 3-step protocol.
"""

# -----------------------------------------------------------------------------
# 2. Streamlit UI Architecture & Initialization
# -----------------------------------------------------------------------------
st.set_page_config(page_title="JAMb Travel Tech Support", page_icon="🎒", layout="centered")

st.title("🎒 JAMb Travel Tech")
st.caption("AI Support Agent – The Silent b Philosophy in Action")

# Safely check for API key
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    st.error("🚨 GEMINI_API_KEY environment variable not found. Please export it before running.")
    st.stop()

# Initialize the Gemini Client and Chat Session in Streamlit state
if "chat_session" not in st.session_state:
    # STORE THE CLIENT IN STATE SO IT DOES NOT CLOSE
    st.session_state.client = genai.Client(api_key=api_key)
    
    # Create a stateful chat session using the modern SDK
    st.session_state.chat_session = st.session_state.client.chats.create(
    st.session_state.chat_session = client.chats.create(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.3, # Low temperature to strictly adhere to brand guidelines
        )
    )

if "messages" not in st.session_state:
    # We maintain a separate message list for UI rendering purposes
    st.session_state.messages = [
        {"role": "assistant", "content": "Welcome to JAMb Travel Tech Support! How can I help you gear up today?"}
    ]

# Render existing conversation history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -----------------------------------------------------------------------------
# 3. Chat Interaction Logic
# -----------------------------------------------------------------------------
if prompt := st.chat_input("Ask about our gear, troubleshooting, or policies..."):
    
    # 1. Display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Generate and display assistant response
    with st.chat_message("assistant"):
        with st.spinner("Connecting to JAMb Support..."):
            try:
                # Send message to the GenAI chat object (automatically maintains history)
                response = st.session_state.chat_session.send_message(prompt)
                reply_text = response.text
                
                # Visual Escalation Handling
                ESCALATION_FLAG = "[SYSTEM ESCALATION: TRANSFER TO HUMAN]"
                
                if ESCALATION_FLAG in reply_text:
                    # Strip the tag so the raw system string doesn't clutter the UI
                    clean_reply = reply_text.replace(ESCALATION_FLAG, "").strip()
                    
                    if clean_reply:
                        st.markdown(clean_reply)
                        
                    st.error(
                        "🚨 **Escalation Triggered:** A live human support specialist from the BYU-Idaho team is joining the session...", 
                        icon="👨‍💻"
                    )
                    
                    # Store the cleaned reply in memory
                    st.session_state.messages.append({"role": "assistant", "content": f"{clean_reply}\n\n*(Transferred to Human)*"})
                else:
                    # Standard response
                    st.markdown(reply_text)
                    st.session_state.messages.append({"role": "assistant", "content": reply_text})
                    
            except Exception as e:
                st.error(f"Communication error: {e}")
