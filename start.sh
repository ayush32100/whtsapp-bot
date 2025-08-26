#!/bin/bash

# Install Chromium + ChromeDriver
sudo apt-get update
sudo apt-get install -y chromium-browser chromium-chromedriver

# Run the bot
python3 whatsapp_ai_bot.py
