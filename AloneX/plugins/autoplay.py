# ━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ʏ_ꜱʜᴀᴅᴏᴡ_ᴍᴜꜱɪᴄ
# ᴀᴅᴠᴀɴᴄᴇᴅ ᴍᴜꜱɪᴄ & ᴠɪᴅᴇᴏ ʙᴏᴛ
# • ᴍᴜꜱɪᴄ • ᴠɪᴅᴇᴏ • ʟɪᴠᴇ
# • ꜰᴀꜱᴛ • ꜱᴛᴀʙʟᴇ • ꜱᴇᴄᴜʀᴇ
# ᴅᴇᴠ : ᴇɴᴀꜰᴜʟ
# ᴠᴇʀ : ᴠ3.0.0
# Year : 2026
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━

# =====================================================================
# Project: X_SHADOW_MUSIC
# Author: ENAFUL
# Year: 2026
# Description: Advanced Telegram Music & Automation Bot
# =====================================================================

# Copyright (c) 2026 OWNER_ENAFUL
# Licensed under the MIT License.
# This file is part of MahiMusic
# DEVELOPER - OWNER_ENAFUL

import asyncio

from pyrogram import filters, types
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import MessageNotModified

from AloneX import app, config, db, lang
from AloneX.helpers import buttons

DELETE_DELAY = 7


async def _delete_later(message: types.Message) -> None:
    try:
        await asyncio.sleep(DELETE_DELAY)
        await message.delete()
    except Exception:
        pass


def autoplay_caption(enabled: bool) -> str:
    status = "🟢 𝐄ɴᴀʙʟᴇᴅ" if enabled else "🔴 𝐃ɪsᴀʙʟᴇᴅ"
    return f"""
**🎵 𝐀ᴜᴛᴏ 𝐏ʟᴀʏ 𝐒ᴇᴛᴛɪɴɢ𝐬**

➻ 𝐌ᴀɴᴀɢᴇ 𝐀ᴜᴛᴏ 𝐏ʟᴀʏ ғᴇᴀᴛᴜʀᴇ ғᴏʀ ᴛʜɪs ɢʀᴏᴜᴘ.

**✦ 𝐂ᴜʀʀᴇɴᴛ 𝐒ᴛᴀᴛᴜ𝐬**
{status}

➻ 𝐖ʜᴇɴ 𝐀ᴜᴛᴏ 𝐏ʟᴀʏ ɪ𝐬 𝐄ɴᴀʙʟᴇᴅ, ᴛʜᴇ ʙᴏᴛ ᴡɪʟʟ
ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ᴘʟᴀʏ ʀᴇᴄᴏᴍᴍᴇɴᴅᴇᴅ ᴛʀᴀᴄᴋ𝐬
ᴡʜᴇɴ ᴛʜᴇ ǫᴜᴇᴜᴇ ᴇɴᴅ𝐬.

━━━━━━━━━━━━━━━
⚡ 𝐏ᴏᴡᴇʀᴇᴅ ʙʏ ➛ 𝐁ᴇᴛᴀ𝐁ᴏᴛ𝐬
"""


@app.on_message(filters.command(["autoplay"]) & filters.group & ~app.bl_users)
@lang.language()
async def _autoplay(_, m: types.Message):
    # Fetch current autoplay status from database
    try:
        enabled = await db.get_autoplay(m.chat.id)
    except AttributeError:
        enabled = False

    mode = m.command[1].lower() if len(m.command) > 1 else None

    # Handle direct commands like /autoplay off
    if mode in ("off", "disable"):
        await db.set_autoplay(m.chat.id, False)
        msg = await m.reply_text("🔴 𝐀ᴜᴛᴏ 𝐏ʟᴀʏ 𝐃ɪsᴀʙʟᴇᴅ")
        asyncio.create_task(_delete_later(msg))
        return

    # Handle direct commands like /autoplay on
    if mode in ("on", "enable"):
        await db.set_autoplay(m.chat.id, True)
        msg = await m.reply_text("🟢 𝐀ᴜᴛᴏ 𝐏ʟᴀʏ 𝐄ɴᴀʙʟᴇᴅ")
        asyncio.create_task(_delete_later(msg))
        return

    # Handle invalid arguments
    if mode is not None and mode not in ("on", "enable", "off", "disable"):
        msg = await m.reply_text(m.lang.get("autoplay_usage", "Usage: /autoplay [on|off]"))
        asyncio.create_task(_delete_later(msg))
        return

    # Get banner image from config (fallback to START_IMG if AUTOPLAY_BANNER is missing)
    banner = getattr(config, "AUTOPLAY_BANNER", getattr(config, "START_IMG", "https://files.catbox.moe/zvziwk.jpg"))

    # Send the new visual panel
    await m.reply_photo(
        photo=banner,
        caption=autoplay_caption(enabled),
        reply_markup=buttons.autoplay_panel_markup(m.chat.id, enabled)
    )


# ==========================================
# 🛠️ CALLBACK HANDLERS FOR AUTOPLAY PANEL 🛠️
# ==========================================

@app.on_callback_query(filters.regex(r"^AUTOPLAY_(ENABLE|DISABLE)\|") & ~app.bl_users)
async def autoplay_callback(_, query: types.CallbackQuery):
    action, chat_id = query.data.split("|")
    chat_id = int(chat_id)

    # Admin verification
    member = await app.get_chat_member(chat_id, query.from_user.id)
    if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
        return await query.answer("❌ You must be an admin to change this setting!", show_alert=True)

    if action == "AUTOPLAY_ENABLE":
        await db.set_autoplay(chat_id, True)
        enabled = True
        await query.answer("🟢 𝐀ᴜᴛᴏ 𝐏ʟᴀʏ 𝐄ɴᴀʙʟᴇᴅ", show_alert=False)
    else:
        await db.set_autoplay(chat_id, False)
        enabled = False
        await query.answer("🔴 𝐀ᴜᴛᴏ 𝐏ʟᴀʏ 𝐃ɪsᴀʙʟᴇᴅ", show_alert=False)

    # Update the panel dynamically
    try:
        await query.message.edit_caption(
            caption=autoplay_caption(enabled),
            reply_markup=buttons.autoplay_panel_markup(chat_id, enabled),
        )
    except MessageNotModified:
        pass


@app.on_callback_query(filters.regex("^AUTOPLAY_STATUS$") & ~app.bl_users)
async def autoplay_status_check(_, query: types.CallbackQuery):
    await query.answer("⚡ 𝐀ᴜᴛᴏ 𝐏ʟᴀʏ 𝐒ᴛᴀᴛᴜ𝐬: Check the panel above 👆", show_alert=True)


@app.on_callback_query(filters.regex("^autoplay_panel close$") & ~app.bl_users)
async def close_autoplay_panel(_, query: types.CallbackQuery):
    try:
        await query.message.delete()
    except Exception:
        pass


# 🆕 YAHAN MUSIC PLAYER WALE BUTTON KO NAYE PANEL SE LINK KIYA HAI
@app.on_callback_query(filters.regex(r"^AUTOPLAY_PANEL_OPEN\|") & ~app.bl_users)
async def autoplay_open_panel_cb(_, query: types.CallbackQuery):
    chat_id = int(query.data.split("|")[1])

    # Get current status
    try:
        enabled = await db.get_autoplay(chat_id)
    except AttributeError:
        enabled = False

    banner = getattr(config, "AUTOPLAY_BANNER", getattr(config, "START_IMG", "https://i.supaimg.com/d8919cc0-dc9c-41e0-9c14-2ff75835e603/b079ee72-66b2-48be-bd64-7ebd61b4d30b.png"))
    # Ek naya panel bhejo jisme saare naye controls honge
    await query.message.reply_photo(
        photo=banner,
        caption=autoplay_caption(enabled),
        reply_markup=buttons.autoplay_panel_markup(chat_id, enabled)
    )
    await query.answer()
