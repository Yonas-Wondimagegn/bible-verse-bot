# bible verse telegram Bot

delivers daily Bible verses in **Amharic** and **English** at scheduled times (12:00 AM & 12:00 PM)...users can also request instant verses with `/verse`

## Features
 Scheduled Verses
 Smart Rotation
- 25 curated bible passages from both Old & New Testament
- tried to include anti repeat algo to ensures no duplicate verses within 10 requests that came from 1 user
- to ensure same naming as amharic reference names i have had included those to the project (e.g ምሳሌ for Proverbs, ዮሐንስ for John)

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

**to get a token:** Message [@BotFather](https://t.me/BotFather) on telegram and create a new bot then copy the token

### 5. Run the bot
```bash
python bible_verse_bot.py
```

## Project Structure

```
bible-verse-bot/
├── bible_verse_bot.py      # Main bot code
├── requirements.txt        # python dependencies
├── .env.example           # environment variable template
├── .gitignore             # Git ignore rules
└── README.md              # this file
```

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `BOT_TOKEN` | — | Your Telegram bot token (**required**) |
| `USERS_FILE` | `subscribed_users.json` | File to store subscribed user IDs |

## Tech Stack

- **Python 3.11+**
- **python-telegram-bot** (v21+) — telegram Bot API framework
- **aiohttp** — Async HTTP client for bible API
- **python-dotenv** — environment variable management

## API

English verses are fetched live from [labs.bible.org API](https://labs.bible.org/api/?passage=John%203:16&type=json)
Amharic verses use already pre loaded local database (got those from ቃለ ብርሃን)

## License

MIT License

## Contact

for issues or any type of suggestions: [@A13X60](https://t.me/A13X60)
