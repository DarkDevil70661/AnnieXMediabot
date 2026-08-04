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

import asyncio
import math
from pyrogram import filters, enums
from pyrogram.errors import FloodWait, MessageNotModified

from AloneX import app

try:
    from AloneX import userbot
except ImportError:
    userbot = None

# Progress Bar Generator Function
def get_progress_bar(current, total, length=15):
    if total == 0:
        return "🟩" * length
    percent = current / total
    filled = int(length * percent)
    empty = length - filled
    bar = "🟩" * filled + "⬜️" * empty
    return f"{bar} {int(percent * 100)}%"

# ==========================================
# 🆕 /aleave <number/all> - ASSISTANT LEAVE
# ==========================================
@app.on_message(filters.command(["aleave"]) & app.sudoers)
async def _aleave_cmd(client, message):
    if not userbot:
        return await message.reply_text("<blockquote><b>❌ ᴀssɪsᴛᴀɴᴛ ʙᴏᴛ (ᴜsᴇʀʙᴏᴛ) ᴄᴏɴꜰɪɢᴜʀᴇᴅ ɴᴀʜɪ ʜᴀɪ.</b></blockquote>")
        
    ass_client = getattr(userbot, 'one', None)
    if not ass_client:
        return await message.reply_text("<blockquote><b>❌ ᴀssɪsᴛᴀɴᴛ ᴄʟɪᴇɴᴛ ɴᴏᴛ ꜰᴏᴜɴᴅ.</b></blockquote>")

    if len(message.command) < 2:
        return await message.reply_text(
            "<blockquote><b>⚠️ ɪɴᴠᴀʟɪᴅ ᴜsᴀɢᴇ!</b>\n\n"
            "👉 <code>/aleave 10</code> : ᴛᴏ ʟᴇᴀᴠᴇ 10 ɢʀᴏᴜᴘs\n"
            "👉 <code>/aleave all</code> : ᴛᴏ ʟᴇᴀᴠᴇ ᴀʟʟ ɢʀᴏᴜᴘs</blockquote>"
        )

    arg = message.command[1].lower()
    sent = await message.reply_text("<blockquote><b>⏳ ꜰᴇᴛᴄʜɪɴɢ ᴀssɪsᴛᴀɴᴛ ᴄʜᴀᴛs ʟɪsᴛ...</b></blockquote>")

    # 1. Total groups fetch karna
    groups = []
    try:
        async for dialog in ass_client.get_dialogs():
            if dialog.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
                groups.append(dialog.chat.id)
    except Exception as e:
        return await sent.edit_text(f"<blockquote><b>❌ ᴇʀʀᴏʀ ꜰᴇᴛᴄʜɪɴɢ ᴄʜᴀᴛs :</b> <code>{e}</code></blockquote>")

    if not groups:
        return await sent.edit_text("<blockquote><b>✅ ᴀssɪsᴛᴀɴᴛ ɪs ɴᴏᴛ ɪɴ ᴀɴʏ ɢʀᴏᴜᴘ.</b></blockquote>")

    # 2. Limit set karna (Number ya All)
    if arg == "all":
        limit = len(groups)
        action_text = f"ᴀʟʟ ({limit}) ɢʀᴏᴜᴘs"
    elif arg.isdigit():
        limit = int(arg)
        if limit <= 0:
            return await sent.edit_text("<blockquote><b>⚠️ ᴘʟᴇᴀsᴇ ᴇɴᴛᴇʀ ᴀ ᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ ɢʀᴇᴀᴛᴇʀ ᴛʜᴀɴ 0.</b></blockquote>")
        # Agar bot 15 group me hai aur aapne 50 dala, toh limit 15 hi rahegi
        limit = min(limit, len(groups)) 
        action_text = f"{limit} ɢʀᴏᴜᴘs"
    else:
        return await sent.edit_text("<blockquote><b>⚠️ ɪɴᴠᴀʟɪᴅ ᴀʀɢᴜᴍᴇɴᴛ. ᴜsᴇ 'all' ᴏʀ ᴀ ɴᴜᴍʙᴇʀ.</b></blockquote>")

    await sent.edit_text(f"<blockquote><b>🚀 sᴛᴀʀᴛɪɴɢ ᴛᴏ ʟᴇᴀᴠᴇ {action_text}...</b></blockquote>")

    left_count = 0
    failed_count = 0
    total_to_leave = limit
    
    # Message bar bar edit hone se floodwait na aaye, isliye hum steps me update karenge
    update_step = max(1, total_to_leave // 10)

    # 3. Leave Process
    for i, chat_id in enumerate(groups[:limit]):
        try:
            await ass_client.leave_chat(chat_id)
            left_count += 1
            await asyncio.sleep(1) # Assistant account ki safety ke liye 1 sec delay
            
        except FloodWait as fw:
            await asyncio.sleep(fw.value + 1)
            try:
                await ass_client.leave_chat(chat_id)
                left_count += 1
            except Exception:
                failed_count += 1
        except Exception:
            failed_count += 1
            
        # 4. Progress Bar Update Logic
        if (i + 1) % update_step == 0 or (i + 1) == total_to_leave:
            p_bar = get_progress_bar(i + 1, total_to_leave)
            try:
                await sent.edit_text(
                    f"<blockquote><b>🔄 ʟᴇᴀᴠɪɴɢ ɢʀᴏᴜᴘs ᴘʀᴏɢʀᴇss :</b>\n\n"
                    f"{p_bar}\n\n"
                    f"<b>🚪 ʟᴇꜰᴛ :</b> {left_count} / {total_to_leave}\n"
                    f"<b>❌ ꜰᴀɪʟᴇᴅ :</b> {failed_count}</blockquote>"
                )
            except MessageNotModified:
                pass
            except FloodWait as fw:
                await asyncio.sleep(fw.value + 1)

    # 5. Final Result
    await sent.edit_text(
        f"<blockquote><b>✅ ᴀssɪsᴛᴀɴᴛ ʟᴇꜰᴛ sᴜᴄᴄᴇssꜰᴜʟʟʏ!</b>\n\n"
        f"<b>🎯 ᴛᴀʀɢᴇᴛ :</b> {total_to_leave} ɢʀᴏᴜᴘs\n"
        f"<b>🚪 ʟᴇꜰᴛ :</b> {left_count}\n"
        f"<b>❌ ꜰᴀɪʟᴇᴅ :</b> {failed_count}</blockquote>"
    )
