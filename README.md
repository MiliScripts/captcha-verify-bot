# Captcha Verify Bot

Captcha Verify Bot is a Python-based Telegram bot that helps manage channel join requests by verifying users through CAPTCHA challenges. This ensures that only genuine users are allowed to join the channel while preventing bots and spammers.

## Features
- Automatically generates CAPTCHA challenges for new join requests.
- Verifies user responses in real-time.
- Deletes solved CAPTCHA data to keep the database clean.
- Customizable to suit your channel's needs.

## Prerequisites
- Python 3.7+
- A Telegram bot token (obtainable from [BotFather](https://core.telegram.org/bots#botfather)).
- Basic knowledge of Python to configure and run the bot.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/captcha-verify-bot.git
   cd captcha-verify-bot
