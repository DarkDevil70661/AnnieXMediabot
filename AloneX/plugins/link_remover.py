import re
import asyncio
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus, MessageEntityType

from AloneX import app

# Dictionary to track link violations per user per chat
# Structure: {chat_id: {user_id: count}}
link_violations = {}

# Regex pattern for link detection
URL_PATTERN = re.compile(
    r"(https?://(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|"
    r"www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|"
    r"https?://[^\s]+|"
    r"t\.me/[^\s]+|"
    r"telegram\.me/[^\s]+|"
    r"[a-zA-Z0-9-]+\.(com|org|net|io|me|co|info|biz|tk|ml|ga|cf|gq))",
    re.IGNORECASE
)

# Optional domain whitelist
WHITELISTED_DOMAINS = [
    # "youtube.com", "youtu.be"
]

async def is_admin(chat_id: int, user_id: int) -> bool:
    """Check if the user is an administrator or owner in the chat."""
    try:
        member = await app.get_chat_member(chat_id, user_id)
        return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except Exception:
        return False

async def bot_can_ban(chat_id: int) -> bool:
    """Check if the bot has permissions to ban members."""
    try:
        bot_member = await app.get_chat_member(chat_id, "me")
        if bot_member.status == ChatMemberStatus.ADMINISTRATOR:
            return getattr(bot_member.privileges, "can_restrict_members", False)
        return False
    except Exception:
        return False

async def delete_after(msg: Message, delay: int = 10):
    """Helper function to auto-delete notice message after a specified delay."""
    await asyncio.sleep(delay)
    try:
        await msg.delete()
    except Exception:
        pass

@app.on_message(filters.group & ~filters.me, group=-1)
async def auto_link_remover_handler(client, message: Message):
    if not message.from_user:
        return

    chat_id = message.chat.id
    user_id = message.from_user.id
    user_mention = message.from_user.mention

    # Skip checking for admins or chat owners
    if await is_admin(chat_id, user_id):
        return

    text = message.text or message.caption or ""
    has_link = False

    # Check via Telegram message entities (URL & Text URL)
    entities = message.entities or message.caption_entities or []
    for entity in entities:
        if entity.type in [MessageEntityType.URL, MessageEntityType.TEXT_LINK]:
            has_link = True
            break

    # Check via regex search if entity detection missed it
    if not has_link and text:
        found_urls = URL_PATTERN.findall(text)
        if found_urls:
            # Check domain whitelist
            if WHITELISTED_DOMAINS:
                is_whitelisted = any(domain in str(found_urls) for domain in WHITELISTED_DOMAINS)
                if not is_whitelisted:
                    has_link = True
            else:
                has_link = True

    if not has_link:
        return

    # 1. Delete the link message immediately
    try:
        await message.delete()
    except Exception as e:
        print(f"[LinkRemover Error] Failed to delete message in {chat_id}: {e}")

    # Track violation counts
    if chat_id not in link_violations:
        link_violations[chat_id] = {}

    link_violations[chat_id][user_id] = link_violations[chat_id].get(user_id, 0) + 1
    count = link_violations[chat_id][user_id]

    has_ban_perm = await bot_can_ban(chat_id)

    # 2. Threshold action check (3 strikes limit)
    if count >= 3:
        if has_ban_perm:
            try:
                await app.ban_chat_member(chat_id, user_id)
                notice = await app.send_message(
                    chat_id,
                    f"🚫 `[ 𝐀𝐔𝐓𝐎𝐌𝐀𝐓𝐈𝐂 𝐁𝐀𝐍 𝐍𝐎𝐓𝐈𝐂𝐄 ]`\n\n"
                    f"👤 `𝐔𝐬𝐞𝐫:` {user_mention}\n"
                    f"🆔 `𝐈𝐃:` `{user_id}`\n"
                    f"⚠️ `𝐑𝐞𝐚𝐬𝐨𝐧:` `𝐌𝐚𝐱𝐢𝐦𝐮𝐦 𝐥𝐢𝐧𝐤 𝐯𝐢𝐨𝐥𝐚𝐭𝐢𝐨𝐧𝐬 (𝟑/𝟑)`\n"
                    f"⚡ `𝐒𝐭𝐚𝐭𝐮𝐬:` `𝐏𝐞𝐫𝐦𝐚𝐧𝐞𝐧𝐭𝐥𝐲 𝐁𝐚𝐧𝐧𝐞𝐝`"
                )
                link_violations[chat_id][user_id] = 0
                asyncio.create_task(delete_after(notice, 10))
            except Exception as e:
                notice = await app.send_message(
                    chat_id,
                    f"⚠️ `[ 𝐖𝐀𝐑𝐍𝐈𝐍𝐆 𝐅𝐎𝐑` {user_mention} `]`\n\n"
                    f"❌ `𝐋𝐢𝐧𝐤𝐬 𝐚𝐫𝐞 𝐬𝐭𝐫𝐢𝐜𝐭𝐥𝐲 𝐩𝐫𝐨𝐡𝐢𝐛𝐢𝐭𝐞𝐝!`\n"
                    f"📊 `𝐕𝐢𝐨𝐥𝐚𝐭𝐢𝐨𝐧𝐬:` `{count}/𝟑`\n"
                    f"❗ `(𝐅𝐚𝐢𝐥𝐞𝐝 𝐭𝐨 𝐛𝐚𝐧: 𝐌𝐢𝐬𝐬𝐢𝐧𝐠 𝐩𝐞𝐫𝐦𝐢𝐬𝐬𝐢𝐨𝐧𝐬)`"
                )
                asyncio.create_task(delete_after(notice, 10))
        else:
            # Persistent notice mode if bot cannot ban
            notice = await app.send_message(
                chat_id,
                f"🚨 `[ 𝐒𝐏𝐀𝐌 𝐍𝐎𝐓𝐈𝐂𝐄 𝐅𝐎𝐑` {user_mention} `]`\n\n"
                f"❌ `𝐘𝐨𝐮 𝐡𝐚𝐯𝐞 𝐩𝐨𝐬𝐭𝐞𝐝 𝐥𝐢𝐧𝐤𝐬 {count} 𝐭𝐢𝐦𝐞𝐬!`\n"
                f"🗑️ `𝐘𝐨𝐮𝐫 𝐥𝐢𝐧𝐤 𝐰𝐚𝐬 𝐝𝐞𝐥𝐞𝐭𝐞𝐝.`\n"
                f"💡 `(𝐀𝐝𝐦𝐢𝐧𝐬: 𝐆𝐫𝐚𝐧𝐭 '𝐁𝐚𝐧 𝐔𝐬𝐞𝐫𝐬' 𝐩𝐞𝐫𝐦𝐢𝐬𝐬𝐢𝐨𝐧)`"
            )
            asyncio.create_task(delete_after(notice, 10))
    else:
        # Warning notification for 1st & 2nd strikes
        action_note = "𝐲𝐨𝐮 𝐰𝐢𝐥𝐥 𝐛𝐞 𝐛𝐚𝐧𝐧𝐞𝐝 𝐨𝐧 𝟑𝐫𝐝 𝐚𝐭𝐭𝐞𝐦𝐩𝐭!" if has_ban_perm else "𝐚𝐥𝐥 𝐥𝐢𝐧𝐤𝐬 𝐰𝐢𝐥𝐥 𝐛𝐞 𝐝𝐞𝐥𝐞𝐭𝐞𝐝!"
        notice = await app.send_message(
            chat_id,
            f"⚠️ `[ 𝐋𝐈𝐍𝐊 𝐑𝐄𝐌𝐎𝐕𝐄𝐃 ]`\n\n"
            f"👤 `𝐔𝐬𝐞𝐫:` {user_mention}\n"
            f"🚫 `𝐖𝐚𝐫𝐧𝐢𝐧𝐠𝐬:` `{count}/𝟑`\n"
            f"📌 `𝐍𝐨𝐭𝐞:` {action_note}\n\n"
            f"⏱️ `[ 𝐓𝐡𝐢𝐬 𝐦𝐞𝐬𝐬𝐚𝐠𝐞 𝐰𝐢𝐥𝐥 𝐚𝐮𝐭𝐨-𝐝𝐞𝐥𝐞𝐭𝐞 𝐢𝐧 𝟏𝟎𝐬 ]`"
        )
        asyncio.create_task(delete_after(notice, 10))


@app.on_message(filters.command(["resetlinks", "cleanlinkwarns"]) & filters.group)
async def reset_link_warns_handler(client, message: Message):
    """Admin command to clear link warnings manually."""
    if not await is_admin(message.chat.id, message.from_user.id):
        reply = await message.reply_text("❌ `𝐎𝐧𝐥𝐲 𝐚𝐝𝐦𝐢𝐧𝐢𝐬𝐭𝐫𝐚𝐭𝐨𝐫𝐬 𝐜𝐚𝐧 𝐞𝐱𝐞𝐜𝐮𝐭𝐞 𝐭𝐡𝐢𝐬 𝐜𝐨𝐦𝐦𝐚𝐧𝐝.`")
        return asyncio.create_task(delete_after(reply, 10))

    if message.reply_to_message and message.reply_to_message.from_user:
        target_id = message.reply_to_message.from_user.id
        target_mention = message.reply_to_message.from_user.mention
        if message.chat.id in link_violations and target_id in link_violations[message.chat.id]:
            link_violations[message.chat.id][target_id] = 0
        reply = await message.reply_text(f"✅ `𝐋𝐢𝐧𝐤 𝐰𝐚𝐫𝐧𝐢𝐧𝐠𝐬 𝐫𝐞𝐬𝐞𝐭 𝐟𝐨𝐫` {target_mention}.")
    else:
        link_violations[message.chat.id] = {}
        reply = await message.reply_text("✅ `𝐀𝐥𝐥 𝐥𝐢𝐧𝐤 𝐰𝐚𝐫𝐧𝐢𝐧𝐠𝐬 𝐜𝐥𝐞𝐚𝐫𝐞𝐝 𝐟𝐨𝐫 𝐭𝐡𝐢𝐬 𝐠𝐫𝐨𝐮𝐩.`")

    asyncio.create_task(delete_after(reply, 10))
