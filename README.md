# 📖 Bible Verse Telegram Bot

A Telegram bot that delivers daily Bible verses in **Amharic** and **English** at scheduled times (12:00 AM & 12:00 PM Ethiopian time). Users can also request instant verses with `/verse`.

## Features

- `/start` — Register for automatic daily & night verses
- `/verse` — Get an instant random Bible verse (Amharic + English)
- `/stop` — Unregister from scheduled verses
- `/dev` — Contact the developer
- `/help` — Show available commands

### Scheduled Verses
- 🌅 **12:00 AM** Ethiopian Time (EAT, UTC+3)
- 🌇 **12:00 PM** Ethiopian Time (EAT, UTC+3)

### Smart Rotation
- 25 curated Bible passages from both Old & New Testament
- Anti-repeat algorithm ensures no duplicate verses within 10 requests
- Amharic reference names (e.g. ምሳሌ for Proverbs, ዮሐንስ for John)

## Setup

### 1. Clone the repository
```bash
git clone https://github.com/Yonas-Wondimagegn/bible-verse-bot.git
cd bible-verse-bot
```

### 2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure your bot token
```bash
cp .env.example .env
```

Then edit `.env` and add your Telegram bot token:
```
BOT_TOKEN=your-a...oken
```

**Get a token:** Message [@BotFather](https://t.me/BotFather) on Telegram, create a new bot, and copy the token.

### 5. Run the bot
```bash
python bible_verse_bot.py
```

## Project Structure

```
bible-verse-bot/
├── bible_verse_bot.py      # Main bot code
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variable template
├── .gitignore             # Git ignore rules
└── README.md              # This file
```

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `BOT_TOKEN` | — | Your Telegram bot token (**required**) |
| `USERS_FILE` | `subscribed_users.json` | File to store subscribed user IDs |
| Schedule | 00:00 & 12:00 EAT | Morning & evening verse times |

## Tech Stack

- **Python 3.11+**
- **python-telegram-bot** (v21+) — Telegram Bot API framework
- **aiohttp** — Async HTTP client for Bible API
- **python-dotenv** — Environment variable management

## API

English verses are fetched live from [labs.bible.org API](https://labs.bible.org/api/?passage=John%203:16&type=json).
Amharic verses use a pre-loaded local database (ቃለ ብርሃን / Kale Birhan translation).

## License

MIT License

## Contact

For issues or suggestions: [@A13X60](https://t.me/A13X60)
