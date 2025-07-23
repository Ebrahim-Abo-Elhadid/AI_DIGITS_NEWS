# AI Digits News Bot 🤖📰

A Telegram bot that collects and summarizes artificial intelligence news from various sources using the Groq API.

---

## Features

- Aggregates AI news from multiple RSS feeds  
- Filters news related to artificial intelligence  
- Summarizes news into clear bullet points using Groq API  
- Easy commands: `/start`, `/summary`, `/help`  
- Interactive buttons to choose summary only or summary with sources  

---

## How to Run the Bot

1. Install the required libraries:  
```bash
pip install aiogram feedparser requests python-dotenv
Create a .env file in your project folder with the following content:
BOT_TOKEN=your_telegram_bot_token_here
GROQ_API_KEY=your_groq_api_key_here
GROQ_API_URL=your_groq_api_url_here (e.g., https://api.groq.ai/v1/chat/completions)
CHAT_ID=your_chat_id (optional)

python main.py


Bot Commands
/start — Start a conversation with the bot

/summary — Get a summary of the latest AI news

/help — Show help message

Important Notes
Do NOT upload your .env file to GitHub as it contains sensitive keys

Use .gitignore to exclude .env from your repository

If GitHub blocks your push due to secrets, remove them from Git history before pushing

News Sources
https://www.topbots.com/feed/

https://bdtechtalks.com/feed/

https://venturebeat.com/category/ai/feed/

https://syncedreview.com/feed/

https://www.marktechpost.com/feed/

https://www.artificialintelligence-news.com/feed/

https://aitopics.org/rss

License
MIT License

Support & Contact
If you have any questions, please open an issue on GitHub.

Thank you for using AI Digits News Bot! 🚀

