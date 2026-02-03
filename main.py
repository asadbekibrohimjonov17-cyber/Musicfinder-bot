from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import yt_dlp
import os
import re

API_TOKEN = "8583886315:AAGnfIcraV0L3RuBHLWETi6UDxhQbW_RJoE"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

user_songs = {}

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("🎵 Qo‘shiqchi nomini yozing (masalan: Shahlo Ahmedova)")

@dp.message_handler()
async def search_music(message: types.Message):
    query = message.text.strip()
    await message.answer("🔍 Qidirilyapti...")

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "default_search": "ytsearch10",
        "format": "bestaudio/best",
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)
            entries = info.get("entries", [])

            if not entries:
                await message.answer("❌ Qo‘shiq topilmadi")
                return

            user_songs[message.from_user.id] = []
            keyboard = InlineKeyboardMarkup(row_width=1)

            for i, entry in enumerate(entries[:10]):
                title = entry["title"]
                url = entry["webpage_url"]
                user_songs[message.from_user.id].append(url)
                keyboard.add(
                    InlineKeyboardButton(
                        text=f"{i+1}. {title}",
                        callback_data=str(i)
                    )
                )

            await message.answer("🎶 Qo‘shiqni tanlang:", reply_markup=keyboard)

    except Exception as e:
        await message.answer("❌ Xatolik yuz berdi")
        print(e)

@dp.callback_query_handler()
async def send_mp3(call: types.CallbackQuery):
    user_id = call.from_user.id
    index = int(call.data)

    if user_id not in user_songs:
        await call.message.answer("❌ Qaytadan urinib ko‘ring")
        return

    url = user_songs[user_id][index]

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": "%(title)s.%(ext)s",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "quiet": True,
        "no_warnings": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            name = re.sub(r'[\\/*?:"<>|]', "", info["title"]) + ".mp3"

            if os.path.exists(name):
                await call.message.answer_audio(
                    audio=open(name, "rb"),
                    title=info["title"]
                )
                os.remove(name)
            else:
                await call.message.answer("❌ MP3 xatolik")

    except Exception as e:
        await call.message.answer("❌ MP3 xatolik")
        print(e)

if __name__ == "__main__":
    executor.start_polling(dp)

    import os 
    API_TOKEN = os.getenv("8583886315:AAGnfIcraV0L3RuBHLWETi6UDxhQbW_RJoE")