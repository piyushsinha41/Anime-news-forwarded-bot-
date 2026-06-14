import asyncio
import logging
import re
import os
from telethon import TelegramClient, events
from telethon.errors import FloodWaitError, MediaCaptionTooLongError

# ===== CONFIG =====
API_ID = 30474999
API_HASH = "8efd532fecec093546e8cfe6ced62f19"
SESSION = "userbot_session"

# SOURCE CHANNELS
SOURCE_CHANNELS = [
    -1001127756447,
    -1001981723257,
    -1001070766565,
    -1003868985436,
]

DEST_CHANNEL = -1004300667075
BUTTON_URL = "https://t.me/+bsf0CMUMQPpkODA9"
FORWARD_DELAY = 5
SEPARATOR = "━━━━━━━━━━━━━━━━━━"

# ===== LOGGING =====
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
log = logging.getLogger("userbot")

client = TelegramClient(SESSION, API_ID, API_HASH)

# Remove @mentions
MENTION_RE = re.compile(r"(?<!\w)@[A-Za-z][A-Za-z0-9_]{3,}")

def clean_text(text: str) -> str:
    if not text:
        return ""
    cleaned = MENTION_RE.sub("", text)
    cleaned = re.sub(r"[ \t]{2,}", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
    return cleaned

# Format message with JOIN link
def format_message(text: str) -> str:
    body = clean_text(text) or "<i>(media)</i>"
    return (
        f"{SEPARATOR}\n"
        f"<b>✨ ANIME NEWS UPDATE ✨</b>\n"
        f"{SEPARATOR}\n\n"
        f"{body}\n\n"
        f"{SEPARATOR}\n"
        f"<b>🔥 JOIN OUR COMMUNITY 🔥</b>\n"
        f"<b>👇 <a href='{BUTTON_URL}'>🔘 CLICK HERE TO JOIN</a> 👇</b>\n"
        f"{SEPARATOR}"
    )

async def send_with_retry(coro_factory):
    while True:
        try:
            return await coro_factory()
        except FloodWaitError as e:
            log.warning(f"FloodWait: sleeping {e.seconds}s")
            await asyncio.sleep(e.seconds + 1)
        except MediaCaptionTooLongError:
            log.warning("Caption too long")
            return "CAPTION_TOO_LONG"

@client.on(events.NewMessage(chats=SOURCE_CHANNELS))
async def handler(event):
    msg = event.message
    try:
        caption = format_message(msg.message or "")

        if msg.media:
            result = await send_with_retry(lambda: client.send_file(
                DEST_CHANNEL,
                file=msg.media,
                caption=caption,
                parse_mode="html",
            ))
            if result == "CAPTION_TOO_LONG":
                await send_with_retry(lambda: client.send_file(
                    DEST_CHANNEL, file=msg.media))
                await send_with_retry(lambda: client.send_message(
                    DEST_CHANNEL, caption, parse_mode="html"))
        else:
            await send_with_retry(lambda: client.send_message(
                DEST_CHANNEL, caption, parse_mode="html", link_preview=False))

        log.info(f"Forwarded msg {msg.id}")
        await asyncio.sleep(FORWARD_DELAY)

    except Exception as e:
        log.exception(f"Error: {e}")

async def main():
    while True:
        try:
            await client.start()
            me = await client.get_me()
            log.info(f"✅ Logged in as {me.first_name}")
            log.info(f"📡 Monitoring {len(SOURCE_CHANNELS)} channels")
            log.info(f"🎯 Forwarding to channel {DEST_CHANNEL}")
            await client.run_until_disconnected()
        except Exception as e:
            log.exception(f"❌ Connection lost: {e}")
            log.info("🔄 Reconnecting in 10 seconds...")
            await asyncio.sleep(10)

if __name__ == "__main__":
    print("🚀 Bot Starting...")
    asyncio.run(main())
