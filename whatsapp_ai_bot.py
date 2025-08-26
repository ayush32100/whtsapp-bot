import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# 🔑 SambaNova API Key
API_KEY = "36dc67e2-f51e-4213-b6e3-fe4121acc601"  # replace with your key
MODEL_NAME = "Meta-Llama-3.1-8B-Instruct"

# 🧑‍🤝‍🧑 Define behavior per contact
contact_behaviors = {
    "Apeksha Dwivedi": "friendly and flirty",
    "Suyash": "casual and short",
    "Mammi": "polite and respectful"
}

# 🚀 Setup headless Chrome options
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
options.add_experimental_option("excludeSwitches", ["enable-logging"])  # suppress warnings

# 🚀 Start Chrome & WhatsApp Web
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get("https://web.whatsapp.com")
print("📱 Scan the QR code to log in (first time)...")
time.sleep(20)  # scan QR code manually once

print("🤖 Bot started...")

def get_ai_reply(message, contact_name):
    """Send message to SambaNova API and return reply"""
    behavior = contact_behaviors.get(contact_name, "friendly and helpful")  # default
    system_prompt = f"You are a WhatsApp assistant. Reply in a {behavior} style."

    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    data = {
        'model': MODEL_NAME,
        'messages': [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ]
    }
    try:
        response = requests.post("https://api.sambanova.ai/v1/chat/completions", headers=headers, json=data)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            print("⚠️ SambaNova API error:", response.text)
            return "[AI Disabled] Message received."
    except Exception as e:
        print("⚠️ Error calling SambaNova:", e)
        return "[AI Disabled] Message received."

last_replied = {}  # store last replied message per contact

while True:
    try:
        print("\n🔎 Checking chats...")

        # --- Get all chats ---
        all_chats = driver.find_elements(By.XPATH, '//div[@role="gridcell"]')
        print("📌 Chats detected:", len(all_chats))

        # --- Find unread chats ---
        unread_chats = driver.find_elements(By.XPATH, '//span[@dir="auto" and normalize-space(text())!=""]')
        print("📌 Unread found:", len(unread_chats))

        target_chat = None
        mode = ""

        if unread_chats:
            # ✅ Click parent chat row
            target_chat = unread_chats[0].find_element(By.XPATH, "./ancestor::div[@role='gridcell']")
            mode = "unread"
        elif all_chats:
            target_chat = all_chats[0]
            mode = "fallback"

        if target_chat:
            driver.execute_script("arguments[0].scrollIntoView(true);", target_chat)
            time.sleep(1)
            target_chat.click()
            time.sleep(2)

            # Get contact name
            contact_name = driver.find_element(By.XPATH, '//header//span[@title]').text

            # Get last incoming message
            messages = driver.find_elements(By.XPATH, '//div[contains(@class,"message-in")]//span[@dir="ltr"]')
            if messages:
                last_msg = messages[-1].text

                # Prevent duplicate replies per contact
                if last_replied.get(contact_name) != last_msg:
                    print(f"📩 ({mode}) {contact_name}:", last_msg)

                    reply = get_ai_reply(last_msg, contact_name)
                    print("💬 Replying:", reply)

                    # Chat box (editable input area)
                    chat_box = driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]')
                    chat_box.send_keys(reply)

                    # Send button
                    send_btn = driver.find_element(By.XPATH, '//button[@aria-label="Send"]')
                    send_btn.click()

                    # Save last replied message
                    last_replied[contact_name] = last_msg
                else:
                    print("⏩ Skipped (already replied to this message)")

        time.sleep(10)  # check every 10 seconds
    except Exception as e:
        print("⚠️ Error:", e)
        time.sleep(5)
