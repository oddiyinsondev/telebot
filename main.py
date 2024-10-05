import logging
from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.exceptions import TelegramBadRequest
from config import token

logging.basicConfig(level=logging.INFO)


# Majburiy obuna bo'lishi kerak bo'lgan kanallar
CHANNELS = [
    {"id": -1002142798901, "url": "https://t.me/+lOlLCJbWp-k2NGQ6"},
    {"id": -1002024595278, "url": "https://t.me/channel2"}
]

# Router va Dispatcher yaratish
router = Router()
dp = Dispatcher()

# Foydalanuvchi obuna bo'lganligini tekshirish
async def check_subscription(bot: Bot, user_id: int) -> bool:
    for channel in CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=channel['id'], user_id=user_id)
            if member.status in ["left", "kicked", "restricted"]:
                return False
        except TelegramBadRequest:
            logging.error(f"Kanal tekshirishda xatolik: {channel['id']}")
            return False
    return True

# Obuna bo'lish uchun tugmalar yaratish
def get_subscription_keyboard():
    builder = InlineKeyboardBuilder()
    for channel in CHANNELS:
        builder.button(text=f"Obuna bo'lish: {channel['url'].split('/')[-1]}", url=channel['url'])
    builder.button(text="Tekshirish ✅", callback_data="check_subscription")
    builder.adjust(1)  # Har bir qatorda bitta tugma
    return builder.as_markup()

# Start buyrug'i uchun handler
@router.message(Command("start"))
async def cmd_start(message: Message, bot: Bot):
    if await check_subscription(bot, message.from_user.id):
        await message.answer("Xush kelibsiz! Siz barcha kanallarga obuna bo'lgansiz. Botdan foydalanishingiz mumkin.")
    else:
        await message.answer(
            "Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling:",
            reply_markup=get_subscription_keyboard()
        )

# Obunani tekshirish uchun callback
@router.callback_query(F.data == "check_subscription")
async def check_subscription_callback(callback_query: CallbackQuery, bot: Bot):
    await callback_query.answer()
    if await check_subscription(bot, callback_query.from_user.id):
        await callback_query.message.edit_text("Rahmat! Endi siz botdan foydalanishingiz mumkin.")
    else:
        await callback_query.message.edit_text(
            "Siz hali barcha kanallarga obuna bo'lmagansiz. Iltimos, quyidagi kanallarga obuna bo'ling:",
            reply_markup=get_subscription_keyboard()
        )

# Boshqa xabarlarni qayta ishlash
@router.message()
async def process_other_messages(message: Message, bot: Bot):
    if await check_subscription(bot, message.from_user.id):
        await message.answer("Sizning xabaringiz qabul qilindi. Botdan foydalanishingiz mumkin.")
    else:
        await message.answer(
            "Kechirasiz, botdan foydalanish uchun quyidagi kanallarga obuna bo'lishingiz kerak:",
            reply_markup=get_subscription_keyboard()
        )

# Asosiy funksiya
async def main():
    bot = Bot(token=token)
    dp.include_router(router)
    
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())