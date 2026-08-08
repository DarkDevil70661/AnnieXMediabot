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
                    f"🚫 `[ 𝙰𝚄𝚃𝙾𝙼𝙰𝚃𝙸𝙲 𝙱𝙰𝙽 𝙽𝙾𝚃𝙸𝙲𝙴 ]`\n\n"
                    f"👤 `𝚄𝚜𝚎𝚛:` {user_mention}\n"
                    f"🆔 `𝙸𝙳:` `{user_id}`\n"
                    f"⚠️ `𝚁𝚎𝚊𝚜𝚘𝚗:` `𝙼𝚊𝚡𝚒𝚖𝚞𝚖 𝚕𝚒𝚗𝚔 𝚟𝚒𝚘𝚕𝚊𝚝𝚒𝚘𝚗𝚜 (𝟹/𝟹)`\n"
                    f"⚡ `𝚂𝚝𝚊𝚝𝚞𝚜:` `𝙿𝚎𝚛𝚖𝚊𝚗𝚎𝚗𝚝𝚕𝚢 𝙱𝚊𝚗𝚗𝚎𝚍`"
                )
                link_violations[chat_id][user_id] = 0
                asyncio.create_task(delete_after(notice, 10))
            except Exception as e:
                notice = await app.send_message(
                    chat_id,
                    f"⚠️ `[ 𝚆𝙰𝚁𝙽𝙸𝙽𝙶 𝙵𝙾𝚁` {user_mention} `]`\n\n"
                    f"❌ `𝙻𝚒𝚗𝚔𝚜 𝚊𝚛𝚎 𝚜𝚝𝚛𝚒𝚌𝚝𝚕𝚢 𝚙𝚛𝚘𝚑𝚒𝚋𝚒𝚝𝚎𝚍!`\n"
                    f"📊 `𝚅𝚒𝚘𝚕𝚊𝚝𝚒𝚘𝚗𝚜:` `{count}/3`\n"
                    f"❗ `(𝙵𝚊𝚒𝚕𝚎𝚍 𝚝𝚘 𝚋𝚊𝚗: 𝙼𝚒𝚜𝚜𝚒𝚗𝚐 𝚙𝚎𝚛𝚖𝚒𝚜𝚜𝚒𝚘𝚗𝚜)`"
                )
                asyncio.create_task(delete_after(notice, 10))
        else:
            # Persistent notice mode if bot cannot ban
            notice = await app.send_message(
                chat_id,
                f"🚨 `[ 𝚂𝙿𝙰𝙼 𝙽𝙾𝚃𝙸𝙲𝙴 𝙵𝙾𝚁` {user_mention} `]`\n\n"
                f"❌ `𝚈𝚘𝚞 𝚑𝚊𝚟𝚎 𝚙𝚘𝚜𝚝𝚎𝚍 𝚕𝚒𝚗𝚔𝚜 {count} 𝚝𝚒𝚖𝚎𝚜!`\n"
                f"🗑️ `𝚈𝚘𝚞𝚛 𝚕𝚒𝚗𝚔 𝚠𝚊𝚜 𝚍𝚎𝚕𝚎𝚝𝚎𝚍.`\n"
                f"💡 `(𝙰𝚍𝚖𝚒𝚗𝚜: 𝙶𝚛𝚊𝚗𝚝 '𝙱𝚊𝚗 𝚄𝚜𝚎𝚛𝚜' 𝚙𝚎𝚛𝚖𝚒𝚜𝚜𝚒𝚘𝚗)`"
            )
            asyncio.create_task(delete_after(notice, 10))
    else:
        # Warning notification for 1st & 2nd strikes
        action_note = "𝚢𝚘𝚞 𝚠𝚒𝚕𝚕 𝚋𝚎 𝚋𝚊𝚗𝚗𝚎𝚍 𝚘𝚗 𝟹𝚛𝚍 𝚊𝚝𝚝𝚎𝚖𝚙𝚝!" if has_ban_perm else "𝚊𝚕𝚕 𝚕𝚒𝚗𝚔𝚜 𝚠𝚒𝚕𝚕 𝚋𝚎 𝚍𝚎𝚕𝚎𝚝𝚎𝚍!"
        notice = await app.send_message(
            chat_id,
            f"⚠️ `[ 𝙻𝙸𝙽𝙺 𝚁𝙴𝙼𝙾𝚅𝙴𝙳 ]`\n\n"
            f"👤 `𝚄𝚜𝚎𝚛:` {user_mention}\n"
            f"🚫 `𝚆𝚊𝚛𝚗𝚒𝚗𝚐𝚜:` `{count}/3`\n"
            f"📌 `𝙽𝚘𝚝𝚎:` {action_note}\n\n"
            f"⏱️ `[ 𝚃𝚑𝚒𝚜 𝚖𝚎𝚜𝚜𝚊𝚐𝚎 𝚠𝚒𝚕𝚕 𝚊𝚞𝚝𝚘-𝚍𝚎𝚕𝚎𝚝𝚎 𝚒𝚗 𝟷𝟶𝚜 ]`"
        )
        asyncio.create_task(delete_after(notice, 10))


@app.on_message(filters.command(["resetlinks", "cleanlinkwarns"]) & filters.group)
async def reset_link_warns_handler(client, message: Message):
    """Admin command to clear link warnings manually."""
    if not await is_admin(message.chat.id, message.from_user.id):
        reply = await message.reply_text("❌ `𝙾𝚗𝚕𝚢 𝚊𝚍𝚖𝚒𝚗𝚒𝚜𝚝𝚛𝚊𝚝𝚘𝚛𝚜 𝚌𝚊𝚗 𝚎𝚡𝚎𝚌𝚞𝚝𝚎 𝚝𝚑𝚒𝚜 𝚌𝚘𝚖𝚖𝚊𝚗𝚍.`")
        return asyncio.create_task(delete_after(reply, 10))

    if message.reply_to_message and message.reply_to_message.from_user:
        target_id = message.reply_to_message.from_user.id
        target_mention = message.reply_to_message.from_user.mention
        if message.chat.id in link_violations and target_id in link_violations[message.chat.id]:
            link_violations[message.chat.id][target_id] = 0
        reply = await message.reply_text(f"✅ `𝙻𝚒𝚗𝚔 𝚠𝚊𝚛𝚗𝚒𝚗𝚐𝚜 𝚛𝚎𝚜𝚎𝚝 𝚏𝚘𝚛` {target_mention}.")
    else:
        link_violations[message.chat.id] = {}
        reply = await message.reply_text("✅ `𝙰𝚕𝚕 𝚕𝚒𝚗𝚔 𝚠𝚊𝚛𝚗𝚒𝚗𝚐𝚜 𝚌𝚕𝚎𝚊𝚛𝚎𝚍 𝚏𝚘𝚛 𝚝𝚑𝚒𝚜 𝚐𝚛𝚘𝚞𝚙.`")

    asyncio.create_task(delete_after(reply, 10))
