import asyncio
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus

from AloneX import app

# Storage for Welcome Settings
WELCOME_SETTINGS = {}

async def is_admin(chat_id: int, user_id: int) -> bool:
    """Check if the user is an administrator or owner in the chat."""
    try:
        member = await app.get_chat_member(chat_id, user_id)
        return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except Exception:
        return False

def safe_format(text: str, **kwargs) -> str:
    """Safely replace placeholders without crashing on unescaped brackets."""
    if not text:
        return ""
    for key, value in kwargs.items():
        text = text.replace(f"{{{key}}}", str(value))
    return text

@app.on_message(filters.new_chat_members & filters.group, group=-1)
async def welcome_new_member(client, message: Message):
    chat_id = message.chat.id
    
    default_text = (
        "👋 [ WELCOME TO THE GROUP ]\n\n"
        "👤 Hey {mention}, welcome to **{title}**!\n"
        "🎉 You are member number: `{count}`"
    )

    custom_data = WELCOME_SETTINGS.get(chat_id)

    if custom_data:
        photo_id = custom_data.get("photo_id")
        raw_text = custom_data.get("text", "")
    else:
        photo_id = None
        raw_text = default_text

    for new_member in message.new_chat_members:
        if new_member.is_self:
            continue

        first_name = new_member.first_name or "User"
        username = f"@{new_member.username}" if new_member.username else first_name
        mention = new_member.mention
        chat_title = message.chat.title or "Group"

        try:
            members_count = await app.get_chat_members_count(chat_id)
        except Exception:
            members_count = 0

        # Safe String Formatting
        formatted_text = safe_format(
            raw_text,
            first=first_name,
            username=username,
            mention=mention,
            title=chat_title,
            count=members_count
        )

        try:
            # Send Photo Welcome
            if photo_id:
                await app.send_photo(
                    chat_id,
                    photo=photo_id,
                    caption=formatted_text if formatted_text else None
                )
            # Send Text-Only Welcome
            elif formatted_text:
                await app.send_message(
                    chat_id,
                    text=formatted_text,
                    disable_web_page_preview=True
                )
        except Exception as e:
            print(f"[Welcome Error] Failed to send welcome in {chat_id}: {e}")


@app.on_message(filters.command(["setwelcome"]) & filters.group)
async def set_welcome_msg(client, message: Message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply_text("❌ Only administrators can set welcome message.")

    reply = message.reply_to_message
    raw_text = ""
    photo_id = None

    if reply:
        if reply.photo:
            photo_id = reply.photo.file_id
            raw_text = reply.caption or ""
        elif reply.text:
            raw_text = reply.text
    elif len(message.command) > 1:
        raw_text = message.text.split(None, 1)[1]

    if not raw_text and not photo_id:
        usage = (
            "📝 [ HOW TO SET WELCOME ]\n\n"
            "📌 Usage:\n"
            "• `/setwelcome <your message>`\n"
            "• Reply `/setwelcome` to any photo, caption or text.\n\n"
            "💡 Formatting Variables:\n"
            "• `{first}` - User's first name\n"
            "• `{username}` - User's username\n"
            "• `{mention}` - Mention user\n"
            "• `{title}` - Group Title\n"
            "• `{count}` - Group Member Count"
        )
        return await message.reply_text(usage)

    WELCOME_SETTINGS[message.chat.id] = {
        "text": raw_text,
        "photo_id": photo_id
    }

    await message.reply_text("✅ Custom welcome message successfully set!")


@app.on_message(filters.command(["welcome"]) & filters.group)
async def get_welcome_msg(client, message: Message):
    custom_data = WELCOME_SETTINGS.get(message.chat.id)
    if not custom_data:
        return await message.reply_text("ℹ️ No custom welcome message set. Using default.")

    photo_id = custom_data.get("photo_id")
    raw_text = custom_data.get("text", "")

    if photo_id:
        await message.reply_photo(
            photo=photo_id,
            caption=f"📌 [ CURRENT WELCOME ]\n\n{raw_text}" if raw_text else None
        )
    elif raw_text:
        await message.reply_text(f"📌 [ CURRENT WELCOME ]\n\n{raw_text}")


@app.on_message(filters.command(["resetwelcome", "clearwelcome", "remwelcome", "removewelcome"]) & filters.group)
async def reset_welcome_msg(client, message: Message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply_text("❌ Only administrators can reset welcome message.")

    if message.chat.id in WELCOME_SETTINGS:
        del WELCOME_SETTINGS[message.chat.id]
        await message.reply_text("✅ Welcome message has been removed.")
    else:
        await message.reply_text("ℹ️ No custom welcome message was set.")
