import asyncio
import datetime
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus, ChatAction
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from AloneX import app

# ডেসপাচ প্রসেস ট্র্যাক করার ডিকশনারি (মেনশন থামানোর জন্য)
active_mentions = {}

# এডমিন চেক করার হেল্পার ফাংশন
async def is_admin(chat_id: int, user_id: int) -> bool:
    try:
        member = await app.get_chat_member(chat_id, user_id)
        return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except Exception:
        return False

# ট্যাগ অল / মেনশন অল কমান্ড হ্যান্ডলার (সকল ফরম্যাট এবং কমান্ডের জন্য কার্যকর)
@app.on_message(filters.command(["all", "mention", "tagall", "hallo", "slashall", "hashall", "@all", "#all"]) & filters.group)
async def tag_all_handler(client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id if message.from_user else 0

    # শুধুমাত্র এডমিনরা ব্যবহার করতে পারবে
    if not await is_admin(chat_id, user_id):
        reply = await message.reply_text("❌ `𝐎𝐧𝐥𝐲 𝐚𝐝𝗺𝐢𝐧𝐢𝐬𝐭𝐫𝐚𝐭𝐨𝐫𝐬 𝐜𝐚𝐧 𝐮𝐬𝐞 𝐭𝐡𝐢𝐬 𝐜𝐨𝐦𝗺𝐚𝐧𝐝.`")
        await asyncio.sleep(10)
        try:
            await reply.delete()
        except Exception:
            pass
        return

    # কমান্ডের সাথে লেখা কাস্টম টেক্সট বা ক্যাপশন বের করা
    custom_text = message.text.partition(" ")[2]
    if not custom_text and message.reply_to_message:
        custom_text = message.reply_to_message.text or message.reply_to_message.caption or ""

    if not custom_text:
        custom_text = "none"

    await client.send_chat_action(chat_id, ChatAction.TYPING)

    # মেনশন শুরু হওয়ার স্টার্টিং মেসেজ
    start_msg = await message.reply_text(
        f"⚡ ᴍᴇɴᴛɪᴏɴɪɴɢ sᴛᴀʀ𝘁ᴇ𝗱...\n\n"
        f"💬 ʀᴇᴀsᴏɴ: `{custom_text}`\n"
        f"⏳ ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ ᴡʜɪʟᴇ ɪ ᴛᴀɢ ᴛʜᴇ ᴍᴇᴍʙᴇʀs."
    )

    # মেম্বারদের সংগ্রহ করা (সরাসরি ইউজারনেম `@username` ফরম্যাটে, লাইনে লাইনে তীরের দাগ সহ)
    users = []
    try:
        async for member in client.get_chat_members(chat_id):
            if not member.user.is_bot and not member.user.is_deleted:
                username = member.user.username
                if username:
                    users.append(f"> @{username}")
    except Exception as e:
        await message.reply_text(f"❌ `𝐅𝐚𝐢𝐥𝐞𝐝 𝐭𝐨 𝐟𝐞𝘁𝐜𝐡 𝐦𝐞𝐦𝐛𝐞𝐫𝐬:` `{e}`")
        return

    if not users:
        await message.reply_text("❌ `𝐍𝐨 𝐮sᴇ𝐫ɴᴀᴍ𝐞 ᴍ𝐞𝗺𝗯𝗲𝗿𝘀 𝐟𝐨𝐮𝐧𝗱 𝐭𝐨 ᴍ𝐞𝐧𝐭𝐢𝐨𝐧!`")
        return

    active_mentions[chat_id] = True
    total_users = len(users)
    batch_size = 5  
    chunks = [users[i:i + batch_size] for i in range(0, len(users), batch_size)]

    # প্রতিটি ব্যাচে একদম উপরে কাস্টম টেক্সট এবং নিচে ৫টি করে ইউজারনেম লাইন বাই লাইন সাজিয়ে পাঠানো
    for chunk in chunks:
        if chat_id not in active_mentions or not active_mentions[chat_id]:
            break

        batch_count_len = len(chunk)
        names_list = "\n".join(chunk)
        
        # এখানে প্রথমে কাস্টম টেক্সট বা ক্যাপশন বসানো হয়েছে, তারপর ইউজারদের লিস্ট এবং ব্যাচ স্ট্যাটিস্টিক্স দেওয়া হয়েছে
        msg_text = (
            f"🔥 **{custom_text}**\n\n"
            f"{names_list}\n\n"
            f"📊 ᴍᴇɴᴛɪᴏɴᴇᴅ ɪɴ ᴛ𝐡ɪs ʙᴀᴛᴄʜ: {batch_count_len}\n"
            f"🔢 ᴛᴏᴛᴀʟ ᴍᴇɴᴛɪᴏɴᴇᴅ: {total_users}"
        )

        # স্টপ করার জন্য একটিমাত্র বাটন
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    text="🛑 𝐒𝐭𝐨𝐩 𝐌𝐞𝐧𝐭𝐢𝐨𝐧 🛑", 
                    callback_data="help_stop_mention"
                )
            ]
        ])

        try:
            await client.send_message(
                chat_id,
                msg_text,
                reply_markup=keyboard
            )
            await asyncio.sleep(4) 
        except Exception:
            pass

    if chat_id in active_mentions:
        active_mentions[chat_id] = False

    try:
        await start_msg.delete()
    except Exception:
        pass

# মেনশন স্টপ করার জন্য কমান্ড হ্যান্ডলার (/stop, #stop, @stop, stop ইত্যাদি)
@app.on_message(filters.command(["stop", "cancel", "end", "halt", "#stop", "@stop"]) & filters.group)
async def stop_command_handler(client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id if message.from_user else 0
    user_mention = message.from_user.mention if message.from_user else "Admin"

    if not await is_admin(chat_id, user_id):
        reply = await message.reply_text("❌ `𝐎𝐧𝐥𝐲 𝐚𝐝𝗺𝐢𝐧𝐢𝐬𝐭𝐫𝐚𝐭𝐨𝐫𝐬 𝐜𝐚𝐧 𝐬𝐭𝐨𝐩 𝐭𝐡𝚒𝐬!`")
        await asyncio.sleep(5)
        try:
            await reply.delete()
        except Exception:
            pass
        return

    active_mentions[chat_id] = False
    bot_username = app.username if app.username else "Bot"
    
    stop_text = (
        f"🛑 ᴛᴀɢɢɪɴɢ sᴛᴏ𝗽𝗽ᴇᴅ ʙʏ ʙᴜᴛ𝘁𝗼𝗻!\n\n"
        f"👤 ʙʏ: {user_mention}\n"
        f"🤖 ʙᴏᴛ: @{bot_username}"
    )
    await message.reply_text(stop_text)

# বাটনে ক্লিক করলে মেনশন স্টপ করা এবং কে স্টপ করেছে তা সহ দেখানো
@app.on_callback_query(filters.regex("help_stop_mention"))
async def stop_mention_callback(client, callback_query):
    chat_id = callback_query.message.chat.id
    user_id = callback_query.from_user.id
    user_mention = callback_query.from_user.mention if callback_query.from_user else "Admin"

    if not await is_admin(chat_id, user_id):
        await callback_query.answer("❌ 𝙾𝚗𝚕𝚢 𝚊𝚍𝚖𝚒𝚗𝚜 𝚌𝚊𝚗 𝚜𝚝𝚘𝚙 𝚝𝚑𝚒𝚜!", show_alert=True)
        return

    active_mentions[chat_id] = False
    await callback_query.answer("🛑 𝙼𝚎𝚗𝚝𝚒𝚘𝚗 𝚙𝚛𝚘𝚌𝚎𝚜𝚜 𝚑𝚊𝚜 𝚋𝚎𝚎𝚗 𝚜𝚝𝚘𝚙𝚙𝚎𝚍!", show_alert=True)
    
    bot_username = app.username if app.username else "Bot"
    
    stop_text = (
        f"🛑 ᴛᴀɢɢɪɴɢ sᴛᴏ𝗽𝗽ᴇᴅ ʙʏ ʙᴜᴛ𝘁𝗼𝗻!\n\n"
        f"👤 ʙʏ: {user_mention}\n"
        f"🤖 ʙᴏᴛ: @{bot_username}"
    )
    
    try:
        await callback_query.message.edit_text(stop_text, reply_markup=None)
    except Exception:
        await client.send_message(chat_id, stop_text)
