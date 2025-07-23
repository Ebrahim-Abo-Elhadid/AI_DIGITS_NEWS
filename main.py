import asyncio
import feedparser
import requests
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from aiogram import Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import CallbackQuery, BotCommand
from dotenv import load_dotenv

import os

load_dotenv()
TELEGRAM_BOT_TOKEN  = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
CHAT_ID = os.getenv("CHAT_ID")
GROQ_API_URL = os.getenv("GROQ_API_URL")



bot = Bot(
    token=TELEGRAM_BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()
router = Router()



dp.include_router(router)




# مصادر RSS متعددة
RSS_FEEDS = [
    "https://www.topbots.com/feed/",
    "https://bdtechtalks.com/feed/",
    "https://venturebeat.com/category/ai/feed/",
    "https://syncedreview.com/feed/",
    "https://www.marktechpost.com/feed/",
    "https://www.artificialintelligence-news.com/feed/",
    "https://aitopics.org/rss",
]

AI_KEYWORDS = [
    "ai", "artificial intelligence", "machine learning",
    "deep learning", "neural network", "chatgpt", "gpt", "openai"
]

def filter_ai_news(news_list):
    ai_news = []
    for news in news_list:
        text = (news['title'] + " " + news['content']).lower()
        if any(keyword in text for keyword in AI_KEYWORDS):
            ai_news.append(news)
    return ai_news

def summarize_with_groq(text):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
    "model": "llama3-70b-8192",
    "messages": [
        {"role": "system", "content": "You are an expert assistant who summarizes texts accurately and concisely."},
        {"role": "user", "content": f"Summarize the following news article clearly and in bullet points:\n{text}"}
    ],
    "temperature": 0.4
}

    response = requests.post(GROQ_API_URL, headers=headers, json=data)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

async def daily_summary_task(chat_id: int,include_sources=True):
    news_list = []

    # 1. قراءة الأخبار من RSS
    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries[:5]:  # نأخذ 5 أخبار من كل مصدر
            news_list.append({
                "title": entry.title,
                "content": entry.summary if hasattr(entry, 'summary') else '',
                "link": entry.link
            })

    # 2. تصفية الأخبار المتعلقة بالذكاء الاصطناعي
    ai_news = filter_ai_news(news_list)
    if not ai_news:
        await bot.send_message(chat_id=chat_id, text="❌ No AI news available today.")
        return

    # دمج النصوص
    combined_text = "\n\n".join(
        f"{n['title']} - {n['content']}" for n in ai_news
    )

    # تلخيص
    summary = summarize_with_groq(combined_text)  # بدون await إذا الدالة ليست async

    # تعريف الرسالة الأساسية
    message = f"✅ AI News Summary:\n\n{summary}"

    # إضافة المصادر إذا تم الطلب
    if include_sources:
        sources_text = "\n\n📚 News Sources:\n"
        for i, news in enumerate(ai_news, 1):
            sources_text += f"{i}. {news['title']}\n{news['link']}\n"
        message += sources_text

    # تقسيم الرسالة إذا كانت طويلة وإرسالها
    max_length = 4000
    for i in range(0, len(message), max_length):
        chunk = message[i:i + max_length]
        await bot.send_message(chat_id=chat_id, text=chunk)


@dp.message(Command(commands=["start"]))
async def start_handler(message: Message):
    welcome_text = (
    "Hi there! 👋 Just send /summary and I’ll give you a quick summary of today’s AI news!"
)

    await message.answer(welcome_text)


@router.message(Command("start"))
async def start_handler(message: Message):
    welcome_text = (
    "👋 Welcome!\n\n"
    "Send /summary to get a summary of the latest AI news.\n"
    "Send /help for assistance."
)

    await message.answer(welcome_text)

@router.message(Command("help"))
async def help_handler(message: Message):
    help_text = (
    "<b>🆘 List of Commands:</b>\n\n"
    "/start - Start a conversation with the bot\n"
    "/summary - Get a summary of the latest AI news\n"
    "/help - Show this help message"
)

    await message.answer(help_text)

@router.message(Command("summary"))
async def summary_handler(message: Message):
    keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Show summary only", callback_data="summary_only"),
            InlineKeyboardButton(text="Show summary with sources", callback_data="show_sources"),
        ]
    ],
    row_width=2
)

   
    await message.answer("Please choose how you want the AI news summary:", reply_markup=keyboard)


@router.callback_query(lambda c: c.data in ["show_sources", "summary_only"])
async def process_callback(callback_query: CallbackQuery):
    chat_id = callback_query.message.chat.id
    await callback_query.answer()  # لإخفاء "loading"

    waiting_message = await callback_query.message.answer("⏳ Please wait while we gather and summarize the news...")

    if callback_query.data == "show_sources":
        await daily_summary_task(chat_id, include_sources=True)
    else:
        await daily_summary_task(chat_id, include_sources=False)

    await waiting_message.delete()



async def set_bot_commands(bot: Bot):
    commands = [
    BotCommand(command="start", description="Start conversation with the bot"),
    BotCommand(command="summary", description="Get AI news summary"),
    BotCommand(command="help", description="Show help message"),
]

    await bot.set_my_commands(commands)

# تشغيل البوت
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    dp.startup.register(set_bot_commands)
    dp.run_polling(bot)

