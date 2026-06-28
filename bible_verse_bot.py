import os
import json
import logging
import random
import asyncio
import aiohttp
from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

# Load environment variables from .env file
load_dotenv()

TOKEN = os.environ.get("BOT_TOKEN")
USERS_FILE = "subscribed_users.json"
ETHIOPIAN_TZ = ZoneInfo("Africa/Addis_Ababa")

# ─── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

def load_users() -> set[int]:
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r") as f:
                data = json.load(f)
                return set(data.get("chat_ids", []))
        except (json.JSONDecodeError, IOError):
            return set()
    return set()


def save_users(users: set[int]) -> None:
    with open(USERS_FILE, "w") as f:
        json.dump({"chat_ids": list(users)}, f)


def add_user(chat_id: int) -> None:
    users = load_users()
    users.add(chat_id)
    save_users(users)
    logger.info(f"User {chat_id} subscribed. Total: {len(users)}")


def remove_user(chat_id: int) -> None:
    users = load_users()
    users.discard(chat_id)
    save_users(users)
    logger.info(f"User {chat_id} unsubscribed. Total: {len(users)}")



SUGGESTED_PASSAGES = [
    "John 3:16", "Psalm 23", "Romans 8:28", "Philippians 4:13",
    "Proverbs 3:5-6", "Jeremiah 29:11", "Isaiah 41:10", "Matthew 11:28",
    "Psalm 46:1", "Romans 12:2", "Joshua 1:9", "Psalm 91:1",
    "2 Timothy 1:7", "Hebrews 11:1", "1 Corinthians 13:4-7",
    "Galatians 5:22-23", "Ephesians 2:8", "James 1:5", "Psalm 119:105",
    "Isaiah 40:31", "Lamentations 3:22-23", "Micah 7:8",
    "Nahum 1:7", "2 Corinthians 5:17", "Colossians 3:23",
]


async def fetch_english_verse(passage: str | None = None) -> dict:
    if passage:
        url = f"https://labs.bible.org/api/?passage={passage}&type=json"
    else:
        url = "https://labs.bible.org/api/?passage=random&type=json"

    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
            if resp.status == 200:
                text = await resp.text()
                data = json.loads(text)
                if data and isinstance(data, list) and len(data) > 0:
                    # If multiple verses, pick the first one or combine
                    verse = data[0]
                    # If it's a multiverse passage, combine the text
                    if len(data) > 1:
                        full_text = " ".join(v.get("text", "") for v in data)
                        verse["text"] = full_text
                        first = data[0]
                        last = data[-1]
                        if first.get("chapter") == last.get("chapter"):
                            verse["bookname"] = first.get("bookname", "")
                            verse["chapter"] = first.get("chapter", "")
                            verse["verse_range"] = f"{first.get('verse', '')}-{last.get('verse', '')}"
                        else:
                            verse["bookname"] = first.get("bookname", "")
                            verse["chapter"] = f"{first.get('chapter', '')}-{last.get('chapter', '')}"
                            verse["verse_range"] = ""
                    return verse
            logger.error(f"Failed to fetch English verse: HTTP {resp.status}")
            return {}


# Track recently sent to avoid repeat
RECENT_VERSES: list[str] = []
MAX_RECENT = 10  # remember last 10 verses


def pick_passage() -> str:
    """ random that wasn't recently sent."""
    available = [p for p in SUGGESTED_PASSAGES if p not in RECENT_VERSES]
    if not available:
        # all were recently used, reset and try again
        available = SUGGESTED_PASSAGES
        RECENT_VERSES.clear()
    chosen = random.choice(available)
    RECENT_VERSES.append(chosen)
    if len(RECENT_VERSES) > MAX_RECENT:
        RECENT_VERSES.pop(0)
    return chosen


# Amharic Bible verses database (Kale Birhan / ቃለ ብርሃን translation)
AMHARIC_VERSES = {
    "John 3:16": "እግዚአብሔር አለምን እንዲህ ወደደ ፤ አንድያ ልጁን ሰጠ ፤ በእርሱ የሚያምን ሁሉ እንዳይጠፋ ዘላለማዊ ሕይወት እንዲያገኝ ነው ።",
    "Psalm 23": "እግዚአብሔር እረቴ ነው ፤ ምንም አያስፈልገኝም ። በለመለም ሣር ላይ ያሰማራኛል ፤ ወደ የሰላም ውሃዎች ይመራኛል ። ነፍሴን ያጠናክራል ፤ ስለ ስሙ በትክክል በሚሄድበት መንገድ ይመራኛል ።",
    "Romans 8:28": "እግዚአብሔር ከሚወዱት ጋር ሁሉን ነገር ለመልካም እንደሚሠራ እናውቃለን ።",
    "Philippians 4:13": "በክርስቶስ በሚያበረታኝ ሁሉን ነገር ማድረግ እችላለሁ ።",
    "Proverbs 3:5-6": "በሙሉ ልብህ በእግዚአብሔር ታመን ፤ በራስህ ማስተዋል አትደገፍ ፤ በመንገዶህ ሁሉ እርሱን እወቅ ፤ መንገዶህንም ያቀናልሃል ።",
    "Jeremiah 29:11": "እኔ ስለ እናንተ ያሰትሁትን ሐሳብ አውቃለሁ ፥ እግዚአብሔር ይላል ፤ ሰላምን እንጂ ክፉ ነገር አይደለም ፤ ለናንተም ተስፋን እና የመጨረሻ ዘመን እንድትኖሩ ነው ።",
    "Isaiah 41:10": "አትፍራ ፤ ከአንተ ጋር ነኝ ፤ አትደንግጥ ፤ እኔ አምላክህ ነኝ ፤ አበረታሃለሁ ፤ እረዳሃለሁ ፤ በጻድቅ ቀኝ እጄ አጽናሃለሁ ።",
    "Matthew 11:28": "እናንተ የደከማችሁ እና ከብዳችሁ ሆኖ፣ ወደ እኔ ኑ፤ እኔስ አሳርፋችኋለሁ።",
    "Psalm 46:1": "አምላክ መጠጊያችን እና ኃይላችን ነው ፤ በመከራ ጊዜ በጥብቅ ረዳት ነው ።",
    "Romans 12:2": "ከዚህ ዓለም አትስማሙ ፤ ነገር ግን በአእምሮ መልክም በመለወጥ ለወጡ ፤ የእግዚአብሔር ፈቃድ መልካም እና ደስታ እና ፍጹም መሆኑን ታውቁ ዘንድ ነው ።",
    "Joshua 1:9": "ጽና እንድትበርት እኔ አዝዤሃደላሁ ፤ አትፍራ ፤ አትደንግጥ ፤ አብረሃው ነኝ እንጂ አልተውህም ።",
    "Psalm 91:1": "ልዑል በሚገለው ውስጥ የሚቀመጥ ፤ በሁሉ በላይ በሚጠለልበት ጥላ ይኖራል ።",
    "2 Timothy 1:7": "እግዚአብሔር የፍርሃት መንፈስ አልሰጠንም ፤ ነገር ግን የኃይል እና የፍቅር እና የትምህርት መንፈስ ነው ።",
    "Hebrews 11:1": "እምነት የምንተስፋቸውን ነገሮች እንደምናገኝ ማመን ነው ፤ ያላየነውን ነገር እንደምናውቅ መጠበቅ ነው ።",
    "1 Corinthians 13:4-7": "ፍቅር ትዕግስት ያለው ነው ፤ ቸርነት ያለው ነው ፤ አይቀናም ፤ አይመካም ፤ አይታበይም ፤ አይከብድም ፤ የራሱን አያስብም ፤ አይሆንም ፤ በክፋት አይደሰትም ፤ በእውነት ይደሰታል ።",
    "Galatians 5:22-23": "የመንፈስ ፍሬ ግን ፍቅር ፤ ደስታ ፤ ሰላም ፤ ትዕግስት ፤ ቸርነት ፤ በጎነት ፤ እምነት ፤ የዋህነት ፤ ራስ መግዛት ነው ።",
    "Ephesians 2:8": "በእምነት በጸጋ አድናችኋል ፤ ይህ ከራሳችሁ አይደለም ፤ የእግዚአብሔር ስጦታ ነው ።",
    "James 1:5": "ከእናንተ ጥበብ የጐደለው ቢኖር ፤ ለሁሉ በቸርነት የሰጠ አምላክ ይጠይቅ ፤ ይሰጠዋል ።",
    "Psalm 119:105": "ቃልህ ለእግሬ መብራት ነው ፤ ለመንገዴም ብርሃን ነው ።",
    "Isaiah 40:31": "በእግዚአብሔር የሚታገሱ ግን ኃይላቸውን ያድሳሉ ፤ እንደ ንስር ይወጣሉ ፤ አይደክሙም ።",
    "Lamentations 3:22-23": "የእግዚአብሔር ምሕረት አያልቅም ፤ ርኅራሄው አይጠፋም ፤ በየ ጊዜው አዲስ ነው ፤ ታማኝነትህ ታላቅ ነው ።",
    "Micah 7:8": "ጠላቴ ሆይ በእኔ ላይ አትደሰት ፤ ብወድቅ እነሣለሁ ፤ በጨለማ ብቀመጥ እግዚአብሔር መብራት ሆኖ ያገኘኛል ።",
    "Nahum 1:7": "እግዚአብሔር መልካም ነው ፤ በመከራ ቀን መጠጊያ ነው ፤ በእርሱ የሚታመኑን ያውቃል ።",
    "2 Corinthians 5:17": "በክርስቶስ የሆነ ሰው አዲስ ፍጥረት ነው ፤ አሮጌው ነገር አልፏል ፤ እነሆ አዲስ ሆኗል ።",
    "Colossians 3:23": "የምታደርጉትን ሁሉ በሙሉ ልብ እንደ ለእግዚአብሔር አድርጉ ፤ ለሰው ሳይሆን ነው ።",
}


def get_amharic_verse(passage: str) -> str:
    if passage in AMHARIC_VERSES:
        return AMHARIC_VERSES[passage]

    for key, text in AMHARIC_VERSES.items():
        if passage.lower() in key.lower() or key.lower() in passage.lower():
            return text

    return ""


async def get_random_verse() -> str:
    passage = pick_passage()

    # eng verse
    verse_data = await fetch_english_verse(passage)

    if not verse_data:
        return "please try again later"

    book = verse_data.get("bookname", "")
    chapter = verse_data.get("chapter", "")
    verse_num = verse_data.get("verse_range") or verse_data.get("verse", "")
    text = verse_data.get("text", "").strip()

    reference = f"{book} {chapter}:{verse_num}" if verse_num else f"{book} {chapter}"

    # amh verse
    amharic_text = get_amharic_verse(passage)

    # Amharic book me'eraf
    AMHARIC_BOOKS = {
        "Genesis": "ዘፍጥረት", "Exodus": "ዌግብት", "Leviticus": "ዌሌዎያን",
        "Numbers": "የኆይ", "Deuteronomy": "የዳገት",
        "Joshua": "ኢያሱ", "Judges": "መሳፍንት", "Ruth": "ሩት",
        "1 Samuel": "1 ሳሙኤል", "2 Samuel": "2 ሳሙኤል",
        "1 Kings": "1 ነገስት", "2 Kings": "2 ነገስት",
        "1 Chronicles": "1 ዜና", "2 Chronicles": "2 ዜና",
        "Ezra": "ዕዝራ", "Nehemiah": "ነህምያ", "Esther": "አስቴር",
        "Job": "ኢዮብ", "Psalms": "መዝሙር", "Proverbs": "ምሳሌ",
        "Ecclesiastes": "መክብብ", "Isaiah": "ኢሳይያስ",
        "Jeremiah": "ኤርሚያ", "Lamentations": "ልብ ወለድ",
        "Ezekiel": "ሕዝቅኤል", "Daniel": "ዳንኤል",
        "Hosea": "ሆሴዕ", "Joel": "ኢዮኤል", "Amos": "አሞጽ",
        "Obadiah": "አብድያ", "Jonah": "ኢዮናስ", "Micah": "ሚካ",
        "Nahum": "ናሆም", "Habakkuk": "ሐቁቅ", "Zephaniah": "ሰፊና",
        "Haggai": "ሐጌ", "Zechariah": "ዘካርያ", "Malachi": "ለክብ",
        "Matthew": "ማቴዎስ", "Mark": "ርቆስ", "Luke": "ሉቃስ",
        "John": "ዮሐንስ", "Acts": "ሐዋርያት",
        "Romans": "ሮሜ", "1 Corinthians": "1 ቆሮንቶስ",
        "2 Corinthians": "2 ቆሮንቶስ", "Galatians": "ገላትያ",
        "Ephesians": "ኤስያ", "Philippians": "ፊሊጶስ",
        "Colossians": "ቆላሳውስ", "1 Thessalonians": "1 ተሰሎንቂ",
        "2 Thessalonians": "2 ተሰሎንቂ", "1 Timothy": "1 ሞኵድ",
        "2 Timothy": "2 ሞኵድ", "Titus": "ቲቶስ", "Philemon": "ፊልሞን",
        "Hebrews": "ዕብራውያን", "James": "ያዕቆብ",
        "1 Peter": "1 ጴጥሮስ", "2 Peter": "2 ጴጥሮስ",
        "1 John": "1 ዮሐንስ", "2 John": "2 ዮሐንስ", "3 John": "3 ዮሐንስ",
        "Jude": "ይሁዳ", "Revelation": "ራእይ",
    }

    # reference
    amharic_book = AMHARIC_BOOKS.get(book, book)
    amharic_reference = f"{amharic_book} {chapter}:{verse_num}" if verse_num else f"{amharic_book} {chapter}"

    message = (
        f"*የመጽሐፍ ቅዱስ ጥቅስ*\n"
        f"━━━━━━━━━━━━━━━\n\n"
    )

    if amharic_text:
        message += (
            f"🇪🇹 *Amharic:*\n"
            f"_{amharic_text}_\n\n"
            f"📌 `{amharic_reference}`\n"
        )

    message += (
        f"\n━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🇺🇸 *English:*\n"
        f"_{text}_\n\n"
        f"📌 `{reference}`\n"
        f"\n━━━━━━━━━━━━━━━━━━━━\nሰናይ ቀን ተመኘን 🤲🏾"
    )

    return message



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    chat_id = update.message.chat_id

    add_user(chat_id)

    await update.message.reply_text(
        f"Hellow {user.first_name} 🙌🏽 \n\n"
        f"AVAILABLE COMMANDS:\n"
        f"/verse\n"
        f"/stop\n"
        f"/help\n\n"
        f"የኢየሱስ ክርስቶስ ጸጋ እና ሰላም በሁላችን ላይ ፀንቶ ይሁን ✝️",
        parse_mode="Markdown",
    )


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    remove_user(chat_id)

    await update.message.reply_text(
        "you've been unregistered from daily verses\n"
        "to start you can always come back with /start ",
    )


async def verse(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("fetching a verse...")

    verse_text = await get_random_verse()
    await update.message.reply_text(
        verse_text,
        parse_mode="Markdown",
    )


async def dev(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "If you got error or have any suggestions...feel free to reach out:\n\n"
        "@A13X60 🤛🏽"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        f"*Help*\n\n"
        f"/verse - you will get a random bible verse in both amharic and english\n"
        f"/stop - stop receiving daily verses\n"
        f"/help - show this help message\n"
        f"/dev - contact dev\n"

        f"\n━━━━━━━━━━━━━━━━━━━━\n*እምነት ከመስማት ነው መስማትም በእግዚአብሔር ቃል ነው*\nሮሜ 10:17\n",
        parse_mode="Markdown",
    )



async def send_scheduled_verse(context: ContextTypes.DEFAULT_TYPE) -> None:
    users = load_users()
    if not users:
        logger.info("No subscribed users for scheduled verse.")
        return

    verse_text = await get_random_verse()
    logger.info(f"sending scheduled verse to {len(users)} users...")

    success = 0
    failed = 0

    for chat_id in users:
        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text=verse_text,
                parse_mode="Markdown",
            )
            success += 1
        except Exception as e:
            logger.error(f"failed to send verse to {chat_id}: {e}")
            failed += 1
            if "blocked" in str(e).lower() or "deactivated" in str(e).lower():
                remove_user(chat_id)

    logger.info(f"Scheduled verse sent: {success} success, {failed} failed")



def main() -> None:
    if not TOKEN:
        logger.error("Please set your BOT_TOKEN!")
        print("❌ Please set the BOT_TOKEN variable or use BOT_TOKEN environment variable.")
        return

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("verse", verse))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(CommandHandler("dev", dev))
    app.add_handler(CommandHandler("help", help_command))

    job_queue = app.job_queue

    job_queue.run_daily(
        send_scheduled_verse,
        time=datetime.strptime("00:00:00", "%H:%M:%S").time().replace(tzinfo=ETHIOPIAN_TZ),
        days=(0, 1, 2, 3, 4, 5, 6),  # Every day
        name="morning_verse",
    )

    job_queue.run_daily(
        send_scheduled_verse,
        time=datetime.strptime("12:00:00", "%H:%M:%S").time().replace(tzinfo=ETHIOPIAN_TZ),
        days=(0, 1, 2, 3, 4, 5, 6),  # Every day
        name="evening_verse",
    )

    logger.info("🤖 Bible Verse Bot is starting...")
    app.run_polling()


if __name__ == "__main__":
    main()
