import random
import json
import os
from captcha.image import ImageCaptcha
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from colorama import Fore, Style

# Configuration for the bot
API_ID = "<YOUR_API_ID>" # https://my.telegram.org/auth
API_HASH = "<YOUR_API_HASH>" # https://my.telegram.org/auth
BOT_TOKEN = "<YOUR_BOT_TOKEN>" # https://t.me/BotFather
CHANNEL_ID = -1000000000000  # Replace with your actual channel ID https://t.me/username_to_id_bot

# Database setup using SQLAlchemy
engine = create_engine("sqlite:///captcha_bot.db")
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

class Captcha(Base):
    """Database model to store captcha information."""
    __tablename__ = "captchas"
    user_id = Column(Integer, primary_key=True)
    captcha_answer = Column(String, nullable=False)

Base.metadata.create_all(engine)

# Bot setup using Pyrogram
bot = Client("captcha_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def generate_captcha():
    """Generates a CAPTCHA image and returns the answer and file path."""
    answer = str(random.randint(1000, 9999))
    image = ImageCaptcha()
    image_path = f"captcha_{answer}.png"
    image.write(answer, image_path)
    return answer, image_path

@bot.on_message(filters.command("start"))
def start(client, message):
    """Handler for the /start command."""
    message.reply_text("Welcome! Solve the CAPTCHA to join the channel.")

@bot.on_callback_query()
async def handle_callback_query(client, callback_query: CallbackQuery):
    """Handler for CAPTCHA verification callbacks."""
    user_id = callback_query.from_user.id
    captcha = session.query(Captcha).filter_by(user_id=user_id).first()

    if not captcha:
        await callback_query.answer("No CAPTCHA found. Please try again.", show_alert=True)
        return

    user_chosen_number = callback_query.data
    if user_chosen_number == captcha.captcha_answer:
        session.delete(captcha)
        session.commit()
        print(f"{Fore.GREEN}User {user_id} solved the CAPTCHA correctly.{Style.RESET_ALL}")
        await callback_query.answer("Correct! You may now join the channel.")
        await client.approve_chat_join_request(chat_id=CHANNEL_ID, user_id=user_id)
        await client.send_message(chat_id=user_id, text="Welcome to the channel!")
        await callback_query.message.delete()
    else:
        await callback_query.answer("Incorrect CAPTCHA. Please try again.", show_alert=True)
        print(f"{Fore.RED}User {user_id} entered an incorrect CAPTCHA.{Style.RESET_ALL}")
        await send_new_captcha(client, user_id, captcha)

async def send_new_captcha(client, user_id, captcha):
    """Generates and sends a new CAPTCHA to the user."""
    captcha_answer, image_path = generate_captcha()
    captcha.captcha_answer = captcha_answer
    session.commit()

    options = [captcha_answer, str(random.randint(1000, 9999)), str(random.randint(1000, 9999))]
    random.shuffle(options)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(text=opt, callback_data=opt)] for opt in options
    ])

    await client.send_photo(
        chat_id=user_id,
        photo=image_path,
        caption="Solve the CAPTCHA to join the channel.",
        reply_markup=keyboard
    )
    try:
        os.remove(image_path)
    except Exception as e:
        print(f"Error removing image file: {e}")

@bot.on_raw_update()
async def handle_raw_update(client, update, users, chats):
    """Handles raw updates to catch chat join requests."""
    data = json.loads(str(update))

    if data.get("_") == "types.UpdateBotChatInviteRequester":
        user_id = data["user_id"]
        captcha_answer, image_path = generate_captcha()

        existing_captcha = session.query(Captcha).filter_by(user_id=user_id).first()
        if existing_captcha:
            session.delete(existing_captcha)

        new_captcha = Captcha(user_id=user_id, captcha_answer=captcha_answer)
        session.add(new_captcha)
        session.commit()

        print(f"{Fore.YELLOW}Generated CAPTCHA for user {user_id}: {captcha_answer}{Style.RESET_ALL}")

        options = [captcha_answer, str(random.randint(1000, 9999)), str(random.randint(1000, 9999))]
        random.shuffle(options)

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(text=opt, callback_data=opt)] for opt in options
        ])

        await client.send_photo(
            chat_id=user_id,
            photo=image_path,
            caption="Solve the CAPTCHA to join the channel.",
            reply_markup=keyboard
        )
        try:
            os.remove(image_path)
        except Exception as e:
            print(f"Error removing image file: {e}")

if __name__ == "__main__":
    print("Bot is running")
    bot.run()
