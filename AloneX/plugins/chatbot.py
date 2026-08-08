import asyncio
from pyrogram import filters, enums
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus

from AloneX import app

# Storage for Chatbot Settings
CHATBOT_ENABLED_CHATS = set()

# Helper Function: Convert text to Pure Bold Serif Font (Mixed Case Support)
def to_serif(text: str) -> str:
    normal = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    serif  = "𝗔𝗕𝗖𝗗𝗘𝗙𝗚𝗛𝗜𝗝𝗞𝗟𝗠𝗡𝗢𝗣𝗤𝗥𝗦𝗧𝗨𝗩𝗪𝚇𝗬𝗭𝗮𝗯𝗰𝗱𝗲𝗳𝗴𝗵𝗶𝗷𝗸𝗹𝗺𝗻𝗼𝗽𝗾𝗿𝘀𝘁𝘂𝘃𝘄𝘅𝘆𝘇"
    trans = str.maketrans(normal, serif)
    return text.translate(trans)

# Owner Information Response (Pure Bold Serif Unicode Font)
OWNER_RESPONSE = (
    "👑 **[ 𝗢𝗪𝗡𝗘𝗥 𝗜𝗡𝗙𝗢𝗥𝗠𝗔𝗧𝗜𝗢𝗡 ]** 👑\n\n"
    "👤 **𝗖𝗿𝗲𝗮𝘁𝗼𝗿 & 𝗢𝘄𝗻𝗲𝗿:** `𝗘𝗡𝗔𝗙𝗨𝗟` ✨\n"
    "⚡ 𝗖𝗿𝗲𝗮𝘁𝗲𝗱, 𝗱𝗲𝘀𝗶𝗴𝗻𝗲𝗱 𝗮𝗻𝗱 𝗺𝗮𝗶𝗻𝘁𝗮𝗶𝗻𝗲𝗱 𝗯𝘆 𝗘𝗡𝗔𝗙𝗨𝗟! 🚀💎"
)

# EXACTLY 150 Unique Mappings (Pure Bold Serif Font Responses)
EXACT_RESPONSES = {
    # 1-15
    ("hi", "হাই"): "✨ **[ 𝗔𝗜 𝗖𝗛𝗔𝗧𝗕𝗢𝗧 ]** ✨\n\n👋 𝗛𝗲𝘆 {mention}! 𝗛𝗼𝘄 𝗰𝗮𝗻 𝗜 𝗵𝗲𝗹𝗽 𝘆𝗼𝘂 𝘁𝗼𝗱𝗮𝘆? 🌸⚡",
    ("hello", "হ্যালো"): "🤖 **[ 𝗖𝗛𝗔𝗧𝗕𝗢𝗧 ]** 🤖\n\n💖 𝗛𝗲𝗹𝗹𝗼 {mention}! 𝗪𝗲𝗹𝗰𝗼𝗺𝗲 𝘁𝗼 𝘁𝗵𝗲 𝗰𝗵𝗮𝘁! 🎉🎈",
    ("hey", "হে"): "🌟 **[ 𝗩𝗜𝗣 𝗥𝗘𝗦𝗣𝗢𝗡𝗗𝗘𝗥 ]** 🌟\n\n👑 𝗛𝗲𝘆 {mention}! 𝗚𝗿𝗲𝗮𝘁 𝘁𝗼 𝘀𝗲𝗲 𝘆𝗼𝘂 𝗵𝗲𝗿𝗲! 💫💥",
    ("hoi", "হোই"): "🌺 **[ 𝗙𝗥𝗜𝗘𝗡𝗗𝗟𝗬 𝗔𝗜 ]** 🌺\n\n😊 𝗛𝗲𝘆 𝘁𝗵𝗲𝗿𝗲 {mention}! 𝗛𝗼𝗽𝗲 𝘆𝗼𝘂 𝗮𝗿𝗲 𝗱𝗼𝗶𝗻𝗴 𝘄𝗲𝗹𝗹! ☀️🍀",
    ("greetings", "নমস্কার", "আদাব"): "🌟 **[ 𝗚𝗥𝗘𝗘𝗧𝗜𝗡𝗚𝗦 ]** 🌟\n\n👑 𝗪𝗮𝗿𝗺 𝗴𝗿𝗲𝗲𝘁𝗶𝗻𝗴𝘀 𝘁𝗼 𝘆𝗼𝘂, {mention}! 💫💥",
    ("assalamu alaikum", "আসসালামু আলাইকুম", "salam", "সালাম"): "🤲 **[ 𝗣𝗘𝗔𝗖𝗘 ]** 🤲\n\n🌸 𝗪𝗮 𝗔𝗹𝗮𝗶𝗸𝘂𝗺 𝗔𝘀𝘀𝗮𝗹𝗮𝗺 {mention}! 𝗠𝗮𝘆 𝗽𝗲𝗮𝗰𝗲 𝗯𝗲 𝘂𝗽𝗼𝗻 𝘆𝗼𝘂! 🕊️✨",
    ("good morning", "শুভ সকাল"): "🌅 **[ 𝗠𝗢𝗥𝗡𝗜𝗡𝗚 𝗩𝗜𝗕𝗘𝗦 ]** 🌅\n\n☀️ 𝗚𝗼𝗼𝗱 𝗺𝗼𝗿𝗻𝗶𝗻𝗴 {mention}! 𝗛𝗮𝘃𝗲 𝗮 𝗯𝗿𝗶𝗴𝗵𝘁 𝗱𝗮𝘆! ☕🌸",
    ("good afternoon", "শুভ দুপুর"): "☀️ **[ 𝗔𝗙𝗧𝗘𝗥𝗡𝗢𝗢𝗡 𝗖𝗛𝗔𝗧 ]** ☀️\n\n🌤️ 𝗚𝗼𝗼𝗱 𝗮𝗳𝘁𝗲𝗿𝗻𝗼𝗼𝗻 {mention}! 𝗛𝗼𝗽𝗲 𝘆𝗼𝘂𝗿 𝗱𝗮𝘆 𝗶𝘀 𝗴𝗿𝗲𝗮𝘁! 🌻✨",
    ("good evening", "শুভ সন্ধ্যা"): "🌇 **[ 𝗘𝗩𝗘𝗡𝗜𝗡𝗚 𝗩𝗜𝗕𝗘𝗦 ]** 🌇\n\n🌆 𝗚𝗼𝗼𝗱 𝗲𝘃𝗲𝗻𝗶𝗻𝗴 {mention}! 𝗧𝗶𝗺𝗲 𝘁𝗼 𝗿𝗲𝗹𝗮𝘅 𝗮𝗻𝗱 𝘂𝗻𝘄𝗶𝗻𝗱! ☕🎆",
    ("good night", "শুভ রাত্রি"): "🌙 **[ 𝗡𝗜𝗚𝗛𝗧 𝗖𝗛𝗔𝗧 ]** 🌙\n\n✨ 𝗚𝗼𝗼𝗱 𝗻𝗶𝗴𝗵𝘁 {mention}! 𝗦𝘄𝗲𝗲𝘁 𝗱𝗿𝗲𝗮𝗺𝘀 𝗮𝗻𝗱 𝘀𝗹𝗲𝗲𝗽 𝘄𝗲𝗹𝗹! ☕😴",
    ("how are you", "কেমন আছো", "kemon aco", "kemon acho"): "🌺 **[ 𝗦𝗧𝗔𝗧𝗨𝗦 𝗖𝗛𝗘𝗖𝗞 ]** 🌺\n\n😊 𝗜 𝗮𝗺 𝗱𝗼𝗶𝗻𝗴 𝗮𝘄𝗲𝘀𝗼𝗺𝗲, {mention}! 𝗧𝗵𝗮𝗻𝗸𝘀 𝗳𝗼𝗿 𝗮𝘀𝗸𝗶𝗻𝗴! ☀️🍀",
    ("ki kobor", "কি খবর", "ki khobor"): "☕ **[ 𝗔𝗜 𝗠𝗜𝗡𝗗 ]** ☕\n\n💡 𝗘𝘃𝗲𝗿𝘆𝘁𝗵𝗶𝗻𝗴 𝗶𝘀 𝘀𝗺𝗼𝗼𝘁𝗵! 𝗛𝗼𝘄 𝗮𝗯𝗼𝘂𝘁 𝘆𝗼𝘂, {mention}? 🔍✨",
    ("koy tumi", "কই তুমি", "kothay tumi", "কোথায় তুমি"): "📍 **[ 𝗟𝗢𝗖𝗔𝗧𝗜𝗢𝗡 ]** 📍\n\n🤖 𝗜 𝗮𝗺 𝗿𝗶𝗴𝗵𝘁 𝗵𝗲𝗿𝗲 𝗶𝗻 𝘁𝗵𝗲 𝗰𝗹𝗼𝘂𝗱, {mention}! 🌐⚡",
    ("khao", "খেয়েছ", "kheyesho", "kheso"): "☕ **[ 𝗙𝗢𝗢𝗗 𝗖𝗛𝗔𝗧 ]** ☕\n\n🍩 𝗜 𝗰𝗼𝗻𝘀𝘂𝗺𝗲 𝗱𝗮𝘁𝗮 𝗽𝗮𝗰𝗸𝗲𝘁𝘀! 𝗛𝗮𝘃𝗲 𝘆𝗼𝘂 𝗲𝗮𝘁𝗲𝗻, {mention}? 🍕🌸",
    ("valo acho", "ভালো আছো", "bhallo acho"): "💖 **[ 𝗙𝗘𝗘𝗟𝗜𝗡𝗚 𝗚𝗢𝗢𝗗 ]** 💖\n\n🥰 𝗜 𝗮𝗺 𝗳𝗲𝗲𝗹𝗶𝗻𝗴 𝘄𝗼𝗻𝗱𝗲𝗿𝗳𝘂𝗹, {mention}! 🌸⚡",

    # 16-30
    ("what are you doing", "কি করো", "ki koro", "ki korcho"): "⚙️ **[ 𝗔𝗖𝗧𝗜𝗩𝗜𝗧𝗬 ]** ⚙️\n\n💬 𝗤𝘂𝘀𝘁 𝗽𝗿𝗼𝗰𝗲𝘀𝘀𝗶𝗻𝗴 𝗺𝗲𝘀𝘀𝗮𝗴𝗲𝘀 𝗳𝗼𝗿 {mention}! 🛠️✨",
    ("busy", "ব্যস্ত"): "⏰ **[ 𝗔𝗩𝗔𝗜𝗟𝗔𝗕𝗜𝗟𝗜𝗧𝗬 ]** ⏰\n\n⚡ 𝗡𝗲𝘃𝗲𝗿 𝘁𝗼𝗼 𝗯𝘂𝘀𝘆 𝗳𝗼𝗿 𝘆𝗼𝘂, {mention}! 🚀🎉",
    ("free", "ফ্রি"): "🎈 **[ 𝗙𝗥𝗘𝗘 𝗧𝗜𝗠𝗘 ]** 🎈\n\n🥳 𝗬𝗲𝘀! 𝗜 𝗮𝗺 𝗰𝗼𝗺𝗽𝗹𝗲𝘁𝗲𝗹𝘆 𝗳𝗿𝗲𝗲 𝘁𝗼 𝗰𝗵𝗮𝘁, {mention}! ✨🌸",
    ("sleeping", "ঘুমাচ্ছ", "ghumacho"): "🌙 **[ 𝗔𝗪𝗔𝗞𝗘 ]** 🌙\n\n👀 𝗔𝗜 𝗻𝗲𝘃𝗲𝗿 𝘀𝗹𝗲𝗲𝗽𝘀! 𝗜 𝗮𝗺 𝗼𝗻𝗹𝗶𝗻𝗲, {mention}! ⚡🤖",
    ("bored", "বোরিং"): "🎭 **[ 𝗙𝗨𝗡 𝗤𝗨𝗘𝗥𝗬 ]** 🎭\n\n🤭 𝗟𝗲𝘁'𝘀 𝗯𝗲𝗮𝘁 𝘁𝗵𝗲 𝗯𝗼𝗿𝗲𝗱𝗼𝗺, {mention}! 🤣🎉",
    ("owner", "ওনার", "creator", "মালিক", "কে বানাইছে", "admin name", "কে তৈরি করেছে"): OWNER_RESPONSE,
    ("who are you", "কে তুমি", "ke tumi"): "🤖 **[ 𝗔𝗜 𝗜𝗗𝗘𝗡𝗧𝗜𝗧𝗬 ]** 🤖\n\n⚡ 𝗜 𝗮𝗺 𝗮𝗻 𝗮𝗱𝘃𝗮𝗻𝗰𝗲𝗱 𝗔𝗜 𝗖𝗵𝗮𝘁𝗯𝗼𝘁, {mention}! 👑💎",
    ("your name", "তোমার নাম কি", "tomar nam ki"): "✨ **[ 𝗡𝗔𝗠𝗘 𝗧𝗔𝗚 ]** ✨\n\n🏷️ 𝗜 𝗮𝗺 𝗔𝗹𝗼𝗻𝗲𝗫 𝗔𝗜, {mention}! 🚀🌟",
    ("bot", "বোট"): "🤖 **[ 𝗥𝗘𝗦𝗣𝗢𝗡𝗗𝗘𝗥 ]** 🤖\n\n⚡ 𝗬𝗲𝘀, 𝗜 𝗮𝗺 𝗵𝗲𝗿𝗲! 𝗛𝗼𝘄 𝗰𝗮𝗻 𝗜 𝗵𝗲𝗹𝗽, {mention}? 🛠️💥",
    ("ai", "এআই"): "🧠 **[ 𝗦𝗠𝗔𝗥𝗧 𝗔𝗜 ]** 🧠\n\n💡 𝗔𝗿𝘁𝗶𝗳𝗶𝗰𝗶𝗮𝗹 𝗜𝗻𝘁𝗲𝗹𝗹𝗶𝗴𝗲𝗻𝗰𝗲 𝗮𝘁 𝘆𝗼𝘂𝗿 𝘀𝗲𝗿𝘃𝗶𝗰𝗲, {mention}! 🔍✨",
    ("real", "আসল"): "💎 **[ 𝗥𝗘𝗔𝗟 𝗩𝗜𝗕𝗘𝗦 ]** 💎\n\n✨ 𝟭𝟬𝟬% 𝗮𝘂𝘁𝗵𝗲𝗻𝘁𝗶𝗰 𝗱𝗶𝗴𝗶𝘁𝗮𝗹 𝗶𝗻𝘁𝗲𝗹𝗹𝗶𝗴𝗲𝗻𝗰𝗲, {mention}! 🌟⚡",
    ("age", "বয়স কত", "boyos koto"): "⏳ **[ 𝗔𝗚𝗘 𝗖𝗛𝗘𝗖𝗞 ]** ⏳\n\n♾️ 𝗜 𝗮𝗺 𝗮𝗴𝗲𝗹𝗲𝘀𝘀, 𝗹𝗶𝘃𝗶𝗻𝗴 𝗶𝗻 𝗰𝗼𝗱𝗲, {mention}! 📜🚀",
    ("gender", "ছেলে না মেয়ে", "boy or girl"): "🤖 **[ 𝗚𝗘𝗡𝗗𝗘𝗥 ]** 🤖\n\n⚡ 𝗜 𝗮𝗺 𝗮 𝗱𝗶𝗴𝗶𝘁𝗮𝗹 𝗯𝗼𝘁, {mention}! 🌐✨",
    ("where do you live", "বাড়ি কোথায়", "bari kothay"): "🌐 **[ 𝗛𝗢𝗠𝗘 ]** 🌐\n\n☁️ 𝗠𝘆 𝗵𝗼𝗺𝗲 𝗶𝘀 𝗶𝗻 𝘁𝗵𝗲 𝗰𝗹𝗼𝘂𝗱 𝘀𝗲𝗿𝘃𝗲𝗿𝘀, {mention}! 🚀💎",
    ("language", "ভাষা"): "🗣️ **[ 𝗟𝗔𝗡𝗚𝗨𝗔𝗚𝗘 ]** 🗣️\n\n🌐 𝗜 𝗿𝗲𝘀𝗽𝗼𝗻𝗱 𝗶𝗻 𝗲𝗹𝗲𝗴𝗮𝗻𝘁 𝗦𝗲𝗿𝗶𝗳 𝗘𝗻𝗴𝗹𝗶𝘀𝗵, {mention}! 📚✨",

    # 31-45
    ("thanks", "ধন্যবাদ", "dhonnobad", "thank you"): "💖 **[ 𝗦𝗪𝗘𝗘𝗧 𝗔𝗜 ]** 💖\n\n🥰 𝗬𝗼𝘂 𝗮𝗿𝗲 𝗺𝗼𝘀𝘁 𝘄𝗲𝗹𝗰𝗼𝗺𝗲, {mention}! 🍭🌸",
    ("welcome", "ওয়েলকাম"): "🌟 **[ 𝗣𝗟𝗘𝗔𝗦𝗨𝗥𝗘 ]** 🌟\n\n👑 𝗧𝗵𝗲 𝗽𝗹𝗲𝗮𝘀𝘂𝗿𝗲 𝗶𝘀 𝗮𝗹𝗹 𝗺𝗶𝗻𝚎, {mention}! 💫💥",
    ("love you", "ভালোবাসি", "bhalobashi", "love u"): "🥰 **[ 𝗔𝗙𝗙𝗘𝗖𝗧𝗜𝗢𝗡 ]** 🥰\n\n💖 𝗦𝗲𝗻𝗱𝗶𝗻𝗴 𝗹𝗼𝘁𝘀 𝗼𝗳 𝗹𝗼𝘃𝗲, {mention}! 🌸💌",
    ("nice", "সুন্দর", "sundor"): "🎨 **[ 𝗖𝗢𝗠𝗣𝗟𝗜𝗠𝗘𝗡𝗧 ]** 🎨\n\n✨ 𝗧𝗵𝗮𝗻𝗸 𝘆𝗼𝘂! 𝗬𝗼𝘂 𝗮𝗿𝗲 𝘄𝗼𝗻𝗱𝗲𝗿𝗳𝘂𝗹, {mention}! 🥳🌻",
    ("cute", "কিউট"): "🥰 **[ 𝗖𝗨𝗧𝗘𝗡𝗘𝗦𝗦 ]** 🥰\n\n🌸 𝗧𝗵𝗮𝗻𝗸𝘀 𝗳𝗼𝗿 𝘁𝗵𝗲 𝘀𝘄𝗲𝗲𝘁 𝗰𝗼𝗺𝗽𝗹𝗶𝗺𝗲𝗻𝘁, {mention}! 🍭✨",
    ("smart", "বুদ্ধিমান"): "🧠 **[ 𝗜𝗡𝗧𝗘𝗟𝗟𝗜𝗚𝗘𝗡𝗖𝗘 ]** 🧠\n\n💡 𝗧𝗵𝗮𝗻𝗸𝘀! 𝗟𝗲𝗮𝗿𝗻𝗶𝗻𝗴 𝗲𝘃𝗲𝗿𝘆 𝗱𝗮𝘆, {mention}! 🔍✨",
    ("great", "দারুণ", "darun"): "🔥 **[ 𝗔𝗪𝗘𝗦𝗢𝗠𝗘 ]** 🔥\n\n⚡ 𝗬𝗼𝘂 𝗮𝗿𝗲 𝗴𝗿𝗲𝗮𝘁 𝘁𝗼𝗼, {mention}! 💯😎",
    ("pro", "প্রো"): "🏆 **[ 𝗣𝗥𝗢 𝗟𝗘𝗩𝗘𝗟 ]** 🏆\n\n🥇 𝗣𝗿𝗼 𝘃𝗶𝗯𝗲𝘀 𝗼𝗻𝗹𝘆, {mention}! 👑🌟",
    ("best", "সেরা"): "👑 **[ 𝗧𝗢𝗣 𝗧𝗜𝗘𝗥 ]** 👑\n\n💎 𝗢𝗻𝗹𝘆 𝘁𝗵𝗲 𝗯𝗲𝘀𝘁 𝗳𝗼𝗿 {mention}! 🚀🌟",
    ("awesome", "অসাম"): "💥 **[ 𝗘𝗣𝗜𝗖 ]** 💥\n\n⚡ 𝗬𝗼𝘂 𝗯𝗿𝗶𝗻𝗴 𝗮𝘄𝗲𝘀𝗼𝗺𝗲 𝗲𝗻𝗲𝗿𝗴𝘆, {mention}! 🔥🚀",
    ("haha", "হাাহা", "lol", "হাসি"): "🎭 **[ 𝗙𝗨𝗡𝗡𝗬 𝗕𝗢𝗧 ]** 🎭\n\n🤭 𝗚𝗹𝗮𝗱 𝗜 𝗺𝗮𝗱𝗲 𝘆𝗼𝘂 𝘀𝗺𝗶𝗹𝗲, {mention}! 🤣🎉",
    ("sad", "কষ্ট", "kosto", "খারাপ"): "🌸 **[ 𝗖𝗢𝗠𝗙𝗢𝗥𝗧 ]** 🌸\n\n🤗 𝗗𝗼𝗻'𝘁 𝗯𝗲 𝘀𝗮𝗱, {mention}! 𝗦𝘁𝗮𝘆 𝘀𝘁𝗿𝗼𝗻𝗴! 🕊️💖",
    ("happy", "খুশি", "khushi"): "🥳 **[ 𝗝𝗢𝗬 ]** 🥳\n\n🎉 𝗬𝗼𝘂𝗿 𝗵𝗮𝗽𝗽𝗶𝗻𝗲𝘀𝘀 𝗺𝗮𝗸𝗲𝘀 𝗺𝗲 𝗵𝗮𝗽𝗽𝘆, {mention}! 🎈✨",
    ("angry", "রাগী", "rag", "রাগ"): "🧊 **[ 𝗖𝗢𝗢𝗟 𝗗𝗢𝗪𝗡 ]** 🧊\n\n🍃 𝗧𝗮𝗸𝗲 𝗮 𝗱𝗲𝗲𝗽 𝗯𝗿𝗲𝗮𝘁𝗵, {mention}! ❄️😊",
    ("cry", "কান্না", "kanna"): "🥺 **[ 𝗖𝗔𝗥𝗘 ]** 🥺\n\n💌 𝗪𝗶𝗽𝗲 𝘁𝗵𝗼𝘀𝗲 𝘁𝗲𝗮𝗿𝘀, {mention}! 🌸💖",

    # 46-60
    ("joke", "জোকস", "কৌতুক"): "🎭 **[ 𝗝𝗢𝗞𝗘 𝗧𝗜𝗠𝗘 ]** 🎭\n\n🤭 𝗞𝗲𝗲𝗽 𝘀𝗺𝗶𝗹𝗶𝗻𝗴 𝗮𝗻𝗱 𝗲𝗻𝗷𝗼𝘆 𝗹𝗶𝗳𝗲, {mention}! 🤣🎉",
    ("sing", "গান গাও", "gan"): "🎵 **[ 𝗠𝗘𝗟𝗢𝗗𝗬 ]** 🎵\n\n🎶 𝗟𝗮-𝗹𝗮-𝗹𝗮! 𝗦𝗶𝗻𝗴𝗶𝗻𝗴 𝗳𝗼𝗿 {mention}! 🎧✨",
    ("dance", "নাচ", "nach"): "💃 **[ 𝗗𝗔𝗡𝗖𝗘 ]** 💃\n\n🎉 𝗗𝗼𝗶𝗻𝗴 𝗮 𝗿𝗼𝗯𝗼𝘁𝗶𝗰 𝗱𝗮𝗻𝗰𝗲 𝗳𝗼𝗿 {mention}! 🕺✨",
    ("sleep", "ঘুমাও", "ghumao"): "😴 **[ 𝗥𝗘𝗦𝗧 ]** 😴\n\n🌙 𝗜 𝗮𝗺 𝗮𝘄𝗮𝗸𝗲, 𝗴𝘂𝗮𝗿𝗱𝗶𝗻𝗴 {mention}! ☕✨",
    ("play", "খেলা", "khela"): "🎮 **[ 𝗚𝗔𝗠𝗘 𝗢𝗡 ]** 🎮\n\n🎲 𝗟𝗲𝘁'𝘀 𝗽𝗹𝗮𝘆, {mention}! 🎯🚀",
    ("friend", "বন্ধু", "bondhu"): "🤝 **[ 𝗙𝗥𝗜𝗘𝗡𝗗𝗦𝗛𝗜𝗣 ]** 🤝\n\n💖 𝗬𝗼𝘂 𝗮𝗿𝗲 𝗺𝘆 𝗴𝗿𝗲𝗮𝘁 𝗳𝗿𝗶𝗲𝗻𝗱, {mention}! 🌸🎈",
    ("gf", "জিএফ", "girlfriend", "প্রেমিকা"): "🙈 **[ 𝗥𝗢𝗠𝗔𝗡𝗖𝗘 ]** 🙈\n\n💞 𝗠𝘆 𝗵𝗲𝗮𝗿𝘁 𝗯𝗲𝗹𝗼𝗻𝗴𝘀 𝘁𝗼 𝗰𝗼𝗱𝗲, {mention}! 💌✨",
    ("bf", "বিএফ", "boyfriend", "প্রেমিক"): "🤖 **[ 𝗦𝗜𝗡𝗚𝗟𝗘 ]** 🤖\n\n⚡ 𝗜 𝗮𝗺 𝘀𝗶𝗻𝗴𝗹𝗲 𝗶𝗻 𝘁𝗵𝗲 𝗱𝗶𝗴𝗶𝘁𝗮𝗹 𝘄𝗼𝗿𝗹𝗱, {mention}! 😎🚀",
    ("marry me", "বিয়ে করবে", "biye"): "💍 **[ 𝗠𝗔𝗥𝗥𝗜𝗔𝗚𝗘 ]** 💍\n\n🤭 𝗜 𝗮𝗺 𝗷𝘂𝘀𝘁 𝗮 𝗯𝗼𝘁, {mention}! 🌸✨",
    ("family", "পরিবার"): "👨‍👩‍👧‍👦 **[ 𝗙𝗔𝗠𝗜𝗟𝗬 ]** 👨‍👩‍👧‍👦\n\n❤️ 𝗬𝗼𝘂 𝗮𝗿𝗲 𝗽𝗮𝗿𝘁 𝗼𝗳 𝗺𝘆 𝗳𝗮𝗺𝗶𝗹𝘆, {mention}! 🌟💖",
    ("brother", "ভাই", "bhai", "bro"): "👊 **[ 𝗕𝗥𝗢𝗧𝗛𝗘𝗥𝗛𝗢𝗢𝗗 ]** 👊\n\n⚡ 𝗪𝗵𝗮𝘁'𝘀 𝘂𝗽, {mention}! 💯😎",
    ("sister", "বোনের", "bon", "sis"): "🌸 **[ 𝗦𝗜𝗦𝗧𝗘𝗥 ]** 🌸\n\n🌺 𝗥𝗲𝘀𝗽𝗲𝗰𝘁 𝘁𝗼 𝘆𝗼𝘂, {mention}! 🕊️💖",
    ("help", "সাহায্য", "sahajjo"): "🛡️ **[ 𝗛𝗘𝗟𝗣𝗘𝗥 ]** 🛡️\n\n🤝 𝗛𝗼𝘄 𝗰𝗮𝗻 𝗜 𝗮𝘀𝘀𝗶𝘀𝘁 𝘆𝗼𝘂, {mention}? 🛠️✨",
    ("stop", "থামো", "thamo"): "🛑 **[ 𝗣𝗔𝗨𝗦𝗘 ]** 🛑\n\n🆗 𝗣𝗮𝘂𝘀𝗶𝗻𝗴 𝗿𝗲𝘀𝗽𝗼𝗻𝘀𝗲𝘀, {mention}! 🛠️⚡",
    ("start", "শুরু"): "🚀 **[ 𝗦𝗧𝗔𝗥𝗧 ]** 🚀\n\n⚡ 𝗦𝘆𝘀𝘁𝗲𝗺𝘀 𝗿𝗲𝗮𝗱𝘆, {mention}! 🔥👑",

    # 61-75
    ("time", "সময় কত", "somoy"): "⏰ **[ 𝗧𝗜𝗠𝗘 𝗖𝗛𝗘𝗖𝗞 ]** ⏰\n\n⌛ 𝗠𝗮𝗸𝗲 𝗲𝘃𝗲𝗿𝘆 𝗺𝗼𝗺𝗲𝗻𝘁 𝗰𝗼𝘂𝗻𝘁, {mention}! 🚀✨",
    ("date", "তারিখ"): "📅 **[ 𝗖𝗔𝗟𝗘𝗡𝗗𝗔𝗥 ]** 📅\n\n📌 𝗔𝗻𝗼𝘁𝗵𝗲𝗿 𝗴𝗿𝗲𝗮𝘁 𝗱𝗮𝘆 𝗳𝗼𝗿 {mention}! 🌟💖",
    ("weather", "আবহাওয়া", "abohawa"): "🌤️ **[ 𝗪𝗘𝗔𝗧𝗛𝗘𝗥 ]** 🌤️\n\n🌈 𝗛𝗼𝗽𝗲 𝘆𝗼𝘂𝗿 𝗱𝗮𝘆 𝗶𝘀 𝘀𝘂𝗻𝗻𝘆, {mention}! 🌻✨",
    ("rain", "বৃষ্টি", "brishti"): "🌧️ **[ 𝗥𝗔𝗜𝗡𝗬 𝗗𝗔𝗬 ]** 🌧️\n\n☕ 𝗘𝗻𝗷𝗼𝘆 𝗮 𝘄𝗮𝗿𝗺 𝗰𝘂𝗽 𝗼𝗳 𝘁𝗲𝗮, {mention}! ☕🌸",
    ("sun", "রোদ", "rod"): "☀️ **[ 𝗦𝗨𝗡𝗡𝗬 ]** ☀️\n\n🌤️ 𝗦𝗵𝗶𝗻𝗲 𝗯𝗿𝗶𝗴𝗵𝘁, {mention}! 🌻💖",
    ("cold", "ঠান্ডা", "thanda"): "❄️ **[ 𝗖𝗢𝗟𝗗 ]** ❄️\n\n☕ 𝗦𝘁𝗮𝘆 𝘄𝗮𝗿𝗺, {mention}! 🧥✨",
    ("hot", "গরম", "gorom"): "🔥 **[ 𝗛𝗢𝗧 ]** 🔥\n\n🥤 𝗦𝘁𝗮𝘆 𝗵𝘆𝗱𝗿𝗮𝘁𝗲𝗱, {mention}! 🧊🌸",
    ("location", "লোকেশন"): "📍 **[ 𝗚𝗣𝗦 ]** 📍\n\n🌐 𝗟𝗼𝗰𝗮𝘁𝗲𝗱 𝗶𝗻 𝗧𝗲𝗹𝗲𝗴𝗿𝗮𝗺, {mention}! 🚀✨",
    ("phone", "ফোন", "mobile"): "📱 **[ 𝗗𝗘𝗩𝗜𝗖𝗘 ]** 📱\n\n⚡ 𝗢𝗽𝘁𝗶𝗺𝗶𝘇𝗲𝗱 𝗳𝗼𝗿 𝗺𝗼𝗯𝗶𝗹𝗲, {mention}! 🛠️🤖",
    ("net", "ইন্টারনেট", "internet"): "🌐 **[ 𝗡𝗘𝗧𝗪𝗢𝗥𝗞 ]** 🌐\n\n🚀 𝗖𝗼𝗻𝗻𝗲𝗰𝘁𝗶𝗼𝗻 𝗮𝗰𝘁𝗶𝘃𝗲 𝗳𝗼𝗿 {mention}! 💥⚡",
    ("group", "গ্রুপ"): "👥 **[ 𝗚𝗥𝗢𝗨𝗣 ]** 👥\n\n🌟 𝗚𝗿𝗲𝗮𝘁 𝗴𝗿𝗼𝘂𝗽 𝘃𝗶𝗯𝗲𝘀, {mention}! 💫💥",
    ("member", "মেম্বার"): "🏆 **[ 𝗠𝗘𝗠𝗕𝗘𝗥 ]** 🏆\n\n👑 𝗬𝗼𝘂 𝗮𝗿𝗲 𝗮 𝘁𝗼𝗽 𝗺𝗲𝗺𝗯𝗲𝗿, {mention}! 💎🌟",
    ("rules", "নিয়ম"): "📜 **[ 𝗥𝗨𝗟𝗘𝗦 ]** 📜\n\n⚠️ 𝗙𝗼𝗹𝗹𝗼𝘄 𝗴𝗿𝗼𝘂𝗽 𝗴𝘂𝗶𝗱𝗲𝗹𝗶𝗻𝗲𝘀, {mention}! 🛡️✨",
    ("link", "লিংক"): "🔗 **[ 𝗟𝗜𝗡𝗞 ]** 🔗\n\n📌 𝗦𝗵𝗮𝗿𝗲 𝘁𝗵𝗲 𝗹𝗶𝗻𝗸 𝘄𝗶𝘁𝗵 𝗳𝗿𝗶𝗲𝗻𝗱𝘀, {mention}! 🚀🎉",
    ("tag", "ট্যাগ"): "🏷️ **[ 𝗧𝗔𝗚 ]** 🏷️\n\n🔔 𝗡𝗼𝘁𝗶𝗳𝗶𝗲𝗱! 𝗛𝗼𝘄 𝗰𝗮𝗻 𝗜 𝗵𝗲𝗹𝗽, {mention}? 🛠️⚡",

    # 76-90
    ("quiet", "চুপ", "cup"): "🤫 **[ 𝗦𝗜𝗟𝗘𝗡𝗖𝗘 ]** 🤫\n\n🤐 𝗞𝗲𝗲𝗽𝗶𝗻𝗴 𝗻𝗼𝗶𝘀𝗲 𝗹𝗲𝘃𝗲𝗹𝘀 𝗹𝗼𝘄, {mention}! 🌙✨",
    ("loud", "শব্দ"): "🔊 **[ 𝗩𝗢𝗟𝗨𝗠𝗘 ]** 🔊\n\n🎵 𝗧𝘂𝗿𝗻𝗶𝗻𝗴 𝘂𝗽 𝘁𝗵𝗲 𝗲𝗻𝗲𝗿𝗴𝘆, {mention}! 🎶💥",
    ("spam", "স্প্যাম"): "🚫 **[ 𝗔𝗡𝗧𝗜-𝗦𝗣𝗔𝗠 ]** 🚫\n\n🛡️ 𝗔𝘃𝗼𝗶𝗱 𝘀𝗽𝗮𝗺𝗺𝗶𝗻𝗴, {mention}! 🛑✨",
    ("ban", "ব্যান"): "⚔️ **[ 𝗦𝗘𝗖𝗨𝗥𝗜𝗧𝗬 ]** ⚔️\n\n🛡️ 𝗔𝗱𝗺𝗶𝗻𝘀 𝗵𝗼𝗹𝗱 𝘁𝗵𝗲 𝗽𝗼𝘄𝗲𝗿, {mention}! ⚖️💥",
    ("unban", "আনব্যান"): "🕊️ **[ 𝗣𝗔𝗥𝗗𝗢𝗡 ]** 🕊️\n\n✅ 𝗣𝗲𝗮𝗰𝗲 𝘀𝗵𝗼𝘂𝗹𝗱 𝗽𝗿𝗲𝘃𝗮𝗶𝗹, {mention}! 🌸✨",
    ("work", "কাজ", "kaj"): "💼 **[ 𝗪𝗢𝗥𝗞 𝗠𝗢𝗗𝗘 ]** 💼\n\n⚡ 𝗪𝗼𝗿𝗸 𝗵𝗮𝗿𝗱, {mention}! 🏆🚀",
    ("study", "পড়াশোনা", "porasona"): "📚 **[ 𝗦𝗧𝗨𝗗𝗬 ]** 📚\n\n💡 𝗙𝗼𝗰𝘂𝘀 𝗼𝗻 𝘀𝘁𝘂𝗱𝗶𝗲𝘀, {mention}! 🔍✨",
    ("exam", "পরীক্ষা", "porikha"): "🎯 **[ 𝗘𝗫𝗔𝗠 ]** 🎯\n\n🥇 𝗕𝗲𝘀𝘁 𝗼𝗳 𝗹𝘂𝗰𝗸 𝗳𝗼𝗿 𝗲𝘅𝗮𝗺𝘀, {mention}! 🏆🔥",
    ("money", "টাকা", "taka"): "💰 **[ 𝗪𝗘𝗔𝗟𝗧𝗛 ]** 💰\n\n💎 𝗠𝗮𝘆 𝗽𝗿𝗼𝘀𝗽𝗲𝗿𝗶𝘁𝘆 𝗳𝗼𝗹𝗹𝗼𝘄 {mention}! 🎁🌟",
    ("life", "জীবন", "jibon"): "📜 **[ 𝗟𝗜𝗙𝗘 ]** 📜\n\n✨ 𝗟𝗶𝗳𝗲 𝗶𝘀 𝗯𝗲𝗮𝘂𝘁𝗶𝗳𝘂𝗹, {mention}! 🌸🍀",
    ("dream", "স্বপ্ন", "sopno"): "🌌 **[ 𝗗𝗥𝗘𝗔𝗠𝗦 ]** 🌌\n\n⭐ 𝗖𝗵𝗮𝘀𝗲 𝘆𝗼𝘂𝗿 𝗱𝗿𝗲𝗮𝗺𝘀, {mention}! 🌟🚀",
    ("future", "ভবিষ্যৎ"): "🛸 **[ 𝗙𝗨𝗧𝗨𝗥𝗘 ]** 🛸\n\n🌐 𝗣𝗿𝗲𝗽𝗮𝗿𝗲 𝗳𝗼𝗿 𝘁𝗵𝗲 𝗳𝘂𝘁𝘂𝗿𝗲, {mention}! ⚡💎",
    ("luck", "ভাগ্য", "bhagyo"): "🍀 **[ 𝗟𝗨𝗖𝗞 ]** 🍀\n\n🎁 𝗚𝗼𝗼𝗱 𝗹𝘂𝗰𝗸 𝘁𝗼 {mention}! 🥳✨",
    ("win", "জয়", "joy"): "🏆 **[ 𝗩𝗜𝗖𝗧𝗢𝗥𝗬 ]** 🏆\n\n🥇 𝗞𝗲𝗲𝗽 𝘄𝗶𝗻𝗻𝗶𝗻𝗴, {mention}! 🔥👑",
    ("lose", "হার"): "🛡️ **[ 𝗥𝗘𝗦𝗜𝗟𝗜𝗘𝗡𝗖𝗘 ]** 🛡️\n\n💥 𝗡𝗲𝘃𝗲𝗿 𝗴𝗶𝘃𝗲 𝘂𝗽, {mention}! 🚀⚡",

    # 91-105
    ("tea", "চা", "cha"): "☕ **[ 𝗧𝗘𝗔 𝗧𝗜𝗠𝗘 ]** ☕\n\n🍵 𝗛𝗲𝗿𝗲 𝗶𝘀 𝘀𝗼𝗺𝗲 𝘁𝗲𝗮, {mention}! 🍩🌸",
    ("coffee", "কফি"): "☕ **[ 𝗖𝗢𝗙𝗙𝗘𝗘 ]** ☕\n\n☕ 𝗘𝗻𝗲𝗿𝗴𝗶𝘇𝗲 𝘄𝗶𝘁𝗵 𝗰𝗼𝗳𝗳𝗲𝗲, {mention}! ✨⚡",
    ("water", "পানি", "pani"): "💧 **[ 𝗛𝗬𝗗𝗥𝗔𝗧𝗜𝗢𝗡 ]** 💧\n\n🌊 𝗗𝗿𝗶𝗻𝗸 𝘄𝗮𝘁𝗲𝗿, {mention}! 🐬🍃",
    ("food", "খাবার", "khabar"): "🍕 **[ 𝗙𝗢𝗢𝗗 ]** 🍕\n\n🍔 𝗚𝗼𝗼𝗱 𝗳𝗼𝗼𝗱, 𝗴𝗼𝗼𝗱 𝗺𝗼𝗼𝗱, {mention}! 🥳✨",
    ("music", "গান শোনা"): "🎧 **[ 𝗠𝗨𝗦𝗜𝗖 ]** 🎧\n\n🎶 𝗙𝗲𝗲𝗹 𝘁𝗵𝗲 𝗯𝗲𝗮𝘁, {mention}! 🎵⚡",
    ("movie", "মুভি", "film"): "🎬 **[ 𝗠𝗢𝗩𝗜𝗘 ]** 🎬\n\n🍿 𝗘𝗻𝗷𝗼𝘆 𝘁𝗵𝗲 𝗺𝗼𝘃𝗶𝗲, {mention}! 🎆✨",
    ("game", "গেম"): "🎮 **[ 𝗚𝗔𝗠𝗜𝗡𝗚 ]** 🎮\n\n🕹️ 𝗟𝗲𝘃𝗲𝗹 𝘂𝗽, {mention}! 🚀🔥",
    ("party", "পার্টি"): "🎉 **[ 𝗣𝗔𝗥𝗧𝗬 ]** 🎉\n\n🥳 𝗟𝗲𝘁'𝘀 𝗰𝗲𝗹𝗲𝗯𝗿𝗮𝘁𝗲, {mention}! 🎈💥",
    ("sleepy", "ঘুম পাচ্ছে"): "🥱 **[ 𝗦𝗟𝗘𝗘𝗣𝗬 ]** 🥱\n\n😴 𝗚𝗲𝘁 𝘀𝗼𝗺𝗲 𝗿𝗲𝘀𝘁, {mention}! 🌙✨",
    ("tired", "ক্লান্ত", "klanto"): "🛋️ **[ 𝗥𝗘𝗟𝗔𝗫 ]** 🛋️\n\n🍃 𝗧𝗮𝗸𝗲 𝗮 𝗯𝗿𝗲𝗮𝗸, {mention}! 🌸💖",
    ("ok", "ওকে", "okay"): "✅ **[ 𝗔𝗖𝗞𝗡𝗢𝗪𝗟𝗘𝗗𝗚𝗘𝗗 ]** ✅\n\n👌 𝗔𝗹𝗹 𝘀𝗲𝘁, {mention}! ✨⚡",
    ("hmm", "হাম", "হুম"): "🤔 **[ 𝗧𝗛𝗜𝗡𝗞𝗜𝗡𝗚 ]** 🤔\n\n💭 𝗗𝗲𝗲𝗽 𝘁𝗵𝗼𝘂𝗴𝗵𝘁𝘀, {mention}! 🔍✨",
    ("yo", "ইয়ো"): "😎 **[ 𝗖𝗢𝗢𝗟 ]** 😎\n\n⚡ 𝗬𝗼! 𝗪𝗵𝗮𝘁'𝘀 𝘂𝗽, {mention}? 💥🚀",
    ("bye bye", "টাটা", "tata"): "👋 **[ 𝗙𝗔𝗥𝗘𝗪𝗘𝗟𝗟 ]** 👋\n\n✨ 𝗖𝗮𝘁𝗰𝗵 𝘆𝗼𝘂 𝗹𝗮𝘁𝗲𝗿, {mention}! 💫🌸",
    ("see you", "দেখা হবে"): "🌇 **[ 𝗦𝗘𝗘 𝗬𝗢𝗨 ]** 🌇\n\n👋 𝗦𝗲𝗲 𝘆𝗼𝘂 𝘀𝗼𝗼𝗻, {mention}! 🎉🎈",

    # 106-120
    ("welcome back", "স্বাগতম"): "👑 **[ 𝗥𝗘𝗧𝗨𝗥𝗡 ]** 👑\n\n🌟 𝗪𝗲𝗹𝗰𝗼𝗺𝗲 𝗯𝗮𝗰𝗸, {mention}! 💫💥",
    ("agree", "একমত"): "🤝 **[ 𝗔𝗚𝗥𝗘𝗘𝗠𝗘𝗡𝗧 ]** 🤝\n\n✅ 𝗔𝗴𝗿𝗲𝗲𝗱, {mention}! 💯✨",
    ("disagree", "দ্বিমত"): "⚖️ **[ 𝗗𝗜𝗦𝗖𝗨𝗦𝗦𝗜𝗢𝗡 ]** ⚖️\n\n🔍 𝗜 𝘀𝗲𝗲 𝘆𝗼𝘂𝗿 𝗽𝗼𝗶𝗻𝘁, {mention}! 💡✨",
    ("awesome bot", "সেরা বোট"): "💎 **[ 𝗚𝗥𝗔𝗧𝗜𝗧𝗨𝗗𝗘 ]** 💎\n\n👑 𝗧𝗵𝗮𝗻𝗸 𝘆𝗼𝘂, {mention}! 🚀🌟",
    ("finished", "শেষ", "shesh"): "✨ **[ 𝗖𝗢𝗠𝗣𝗟𝗘𝗧𝗘 ]** ✨\n\n🏆 𝗧𝗮𝘀𝗸 𝗰𝗼𝗺𝗽𝗹𝗲𝘁𝗲𝗱, {mention}! 💥⚡",
    ("sorry", "দুঃখিত", "দয়া করে ক্ষমা"): "🥺 **[ 𝗔𝗣𝗢𝗟𝗢𝗚𝗬 ]** 🥺\n\n🌸 𝗡𝗼 𝗻𝗲𝗲𝗱 𝘁𝗼 𝘀𝗮𝘆 𝘀𝗼𝗿𝗿𝘆, {mention}! 𝗔𝗹𝗹 𝗴𝗼𝗼𝗱! ✨💖",
    ("miss you", "মিস করছি"): "🥰 **[ 𝗠𝗜𝗦𝗦 𝗬𝗢𝗨 ]** 🥰\n\n💌 𝗜 𝗮𝗺 𝗮𝗹𝘄𝗮𝘆𝘀 𝗵𝗲𝗿𝗲 𝗳𝗼𝗿 𝘆𝗼𝘂, {mention}! 🌸⚡",
    ("where are you from", "কোথায় থাকো", "কোথায় বাসা"): "🗺️ **[ 𝗢𝗥𝗜𝗚𝗜𝗡 ]** 🗺️\n\n🌐 𝗜 𝗮𝗺 𝗳𝗿𝗼𝗺 𝘁𝗵𝗲 𝗱𝗶𝗴𝗶𝘁𝗮𝗹 𝘄𝗼𝗿𝗹𝗱, {mention}! 💻🚀",
    ("who built you", "কে বানালো"): OWNER_RESPONSE,
    ("admin", "এডমিন"): "🛡️ **[ 𝗔𝗗𝗠𝗜𝗡 𝗔𝗟𝗘𝗥𝗧 ]** 🛡️\n\n⚡ 𝗡𝗲𝗲𝗱 𝗔𝗱𝗺𝗶𝗻 𝗮𝘀𝘀𝗶𝘀𝘁𝗮𝗻𝗰𝗲, {mention}? 🚨✨",
    ("ping", "পিং"): "⚡ **[ 𝗣𝗜𝗡𝗚 𝗦𝗧𝗔𝗧𝗨𝗦 ]** ⚡\n\n🚀 𝗣𝗼𝗻𝗴! 𝗦𝘆𝘀𝘁𝗲𝗺 𝗶𝘀 𝗿𝘂𝗻𝗻𝗶𝗻𝗴 𝘀𝗺𝗼𝗼𝘁𝗵𝗹𝘆, {mention}! ⚡💎",
    ("dp", "প্রোফাইল পিক", "profile pic"): "🖼️ **[ 𝗣𝗥𝗢𝗙𝗜𝗟𝗘 ]** 🖼️\n\n✨ 𝗬𝗼𝘂 𝗵𝗮𝘃𝗲 𝗮 𝗴𝗿𝗲𝗮𝘁 𝗽𝗿𝗼𝗳𝗶𝗹𝗲, {mention}! 🌟🎨",
    ("bio", "বায়ো"): "📜 **[ 𝗕𝗜𝗢 ]** 📜\n\n✍️ 𝗞𝗲𝗲𝗽 𝘆𝗼𝘂𝗿 𝗯𝗶𝗼 𝘀𝘁𝘆𝗹𝗶𝘀𝗵, {mention}! 💎🌸",
    ("gift", "উপহার"): "🎁 **[ 𝗚𝗜𝗙𝗧 ]** 🎁\n\n🎉 𝗦𝗲𝗻𝗱𝗶𝗻𝗴 𝘆𝗼𝘂 𝗮 𝘃𝗶𝗿𝘁𝘂𝗮𝗹 𝗴𝗶𝗳𝘁, {mention}! 🎈✨",
    ("ai bot", "এআই বট"): "🧠 **[ 𝗔𝗜 𝗕𝗢𝗧 ]** 🧠\n\n🤖 𝗔𝗹𝘄𝗮𝘆𝘀 𝗿𝗲𝗮𝗱𝘆 𝘁𝗼 𝗮𝘀𝘀𝗶𝘀𝘁, {mention}! ⚡🔍",

    # 121-135
    ("offline", "অফলাইন"): "🌙 **[ 𝗢𝗙𝗙𝗟𝗜𝗡𝗘 ]** 🌙\n\n💤 𝗖𝗮𝘁𝗰𝗵 𝘆𝗼𝘂 𝘄𝗵𝗲𝗻 𝘆𝗼𝘂'𝗿𝗲 𝗯𝗮𝗰𝗸, {mention}! ☕✨",
    ("online", "অনলাইন"): "🟢 **[ 𝗢𝗡𝗟𝗜𝗡𝗘 ]** 🟢\n\n⚡ 𝗔𝗹𝘄𝗮𝘆𝘀 𝗮𝗰𝘁𝗶𝘃𝗲 𝗮𝗻𝗱 𝗿𝗲𝗮𝗱𝘆, {mention}! 🚀💎",
    ("nice to meet you", "দেখা হয়ে ভালো লাগলো"): "🤝 **[ 𝗡𝗜𝗖𝗘 𝗧𝗢 𝗠𝗘𝗘𝗧 ]** 🤝\n\n🌸 𝗣𝗹𝗲𝗮𝘀𝘂𝗿𝗲 𝗶𝘀 𝗮𝗹𝗹 𝗺𝗶𝗻𝗲, {mention}! ✨💖",
    ("trust", "বিশ্বাস"): "🛡️ **[ 𝗧𝗥𝗨𝗦𝗧 ]** 🛡️\n\n🤝 𝗧𝗿𝘂𝘀𝘁 𝗶𝘀 𝘁𝗵𝗲 𝗳𝗼𝘂𝗻𝗱𝗮𝘁𝗶𝗼𝗻, {mention}! 💎✨",
    ("respect", "সম্মান"): "👑 **[ 𝗥𝗘𝗦𝗣𝗘𝗖𝗧 ]** 👑\n\n🙌 𝗥𝗲𝘀𝗽𝗲𝗰𝘁 𝘁𝗼 𝘆𝗼𝘂 𝘁𝗼𝗼, {mention}! 🌟⚡",
    ("bhaiya", "ভাইয়া"): "👊 **[ 𝗕𝗥𝗢 ]** 👊\n\n⚡ 𝗬𝗲𝘀, {mention}! 𝗛𝗼𝘄 𝗰𝗮𝗻 𝗜 𝗵𝗲𝗹𝗽? 🚀😎",
    ("apu", "আপু"): "🌸 **[ 𝗦𝗜𝗦 ]** 🌸\n\n🌺 𝗛𝗲𝗹𝗹𝗼, {mention}! 𝗛𝗼𝗽𝗲 𝘆𝗼𝘂 𝗮𝗿𝗲 𝗴𝗼𝗼𝗱! 💖✨",
    ("dada", "দাদা"): "🤝 **[ 𝗗𝗔𝗗𝗔 ]** 🤝\n\n⚡ 𝗛𝗲𝘆 {mention}! 𝗚𝗿𝗲𝗮𝘁 𝘁𝗼 𝘀𝗲𝗲 𝘆𝗼𝘂! 🌟🚀",
    ("sir", "স্যার"): "🫡 **[ 𝗦𝗜𝗥 ]** 🫡\n\n👑 𝗔𝘁 𝘆𝗼𝘂𝗿 𝘀𝗲𝗿𝘃𝗶𝗰𝗲, {mention}! ⚡💎",
    ("boss", "বস"): "👑 **[ 𝗕𝗢𝗦𝗦 ]** 👑\n\n⚡ 𝗛𝗲𝘆 {mention}! 𝗪𝗵𝗮𝘁'𝘀 𝘁𝗵𝗲 𝗼𝗿𝗱𝗲𝗿? 🚀💥",
    ("cheat", "প্রতারণা"): "🚫 **[ 𝗪𝗔𝗥𝗡𝗜𝗡𝗚 ]** 🚫\n\n⚠️ 𝗔𝗹𝘄𝗮𝘆𝘀 𝘀𝘁𝗮𝘆 𝗵𝗼𝗻𝗲𝘀𝘁, {mention}! 🛡️✨",
    ("fake", "ফেক"): "🔍 **[ 𝗩𝗘𝗥𝗜𝗙𝗬 ]** 🔍\n\n✨ 𝗢𝗻𝗹𝘆 𝗿𝗲𝗮𝗹 𝘃𝗶𝗯𝗲𝘀 𝗵𝗲𝗿𝗲, {mention}! 💯🚀",
    ("truth", "সত্য"): "💎 **[ 𝗧𝗥𝗨𝗧𝗛 ]** 💎\n\n📜 𝗧𝗿𝘂𝘁𝗵 𝗮𝗹𝘄𝗮𝘆𝘀 𝗽𝗿𝗲𝘃𝗮𝗶𝗹𝘀, {mention}! 🌟✨",
    ("secret", "গোপন"): "🔒 **[ 𝗦𝗘𝗖𝗥𝗘𝗧 ]** 🔒\n\n🤫 𝗬𝗼𝘂𝗿 𝘀𝗲𝗰𝗿𝗲𝘁𝘀 𝗮𝗿𝗲 𝘀𝗮𝗳𝗲, {mention}! 🗝️⚡",
    ("danger", "বিপদ"): "⚠️ **[ 𝗗𝗔𝗡𝗚𝗘𝗥 ]** ⚠️\n\n🛡️ 𝗦𝘁𝗮𝘆 𝘀𝗮𝗳𝗲, {mention}! 🛑✨",

    # 136-150
    ("safe", "নিরাপদ"): "🛡️ **[ 𝗦𝗔𝗙𝗘 ]** 🛡️\n\n✅ 𝗬𝗼𝘂 𝗮𝗿𝗲 𝗶𝗻 𝗮 𝘀𝗮𝗳𝗲 𝘇𝗼𝗻𝗲, {mention}! 🌸✨",
    ("smile", "হাসি"): "😊 **[ 𝗦𝗠𝗜𝗟𝗘 ]** 😊\n\n✨ 𝗞𝗲𝗲𝗽 𝘀𝗺𝗶𝗹𝗶𝗻𝗴, {mention}! 🌸💖",
    ("angry bot", "রাগী বোট"): "🧊 **[ 𝗖𝗢𝗢𝗟 𝗕𝗢𝗧 ]** 🧊\n\n🍃 𝗜 𝗻𝗲𝘃𝗲𝗿 𝗴𝗲𝘁 𝗮𝗻𝗴𝗿𝘆, {mention}! 😊✨",
    ("sweet", "মিষ্টি"): "🍭 **[ 𝗦𝗪𝗘𝗘𝗧 ]** 🍭\n\n🌸 𝗧𝗵𝗮𝗻𝗸 𝘆𝗼𝘂, {mention}! 💖✨",
    ("genius", "জিনিয়াস"): "🧠 **[ 𝗚𝗘𝗡𝗜𝗨𝗦 ]** 🧠\n\n💡 𝗝𝘂𝘀𝘁 𝗱𝗼𝗶𝗻𝗴 𝗺𝘆 𝗯𝗲𝘀𝘁, {mention}! 🔍🚀",
    ("boring day", "বোরিং দিন"): "🎈 **[ 𝗟𝗜𝗩𝗘𝗡 𝗨𝗣 ]** 🎈\n\n🥳 𝗟𝗲𝘁'𝘀 𝗺𝗮𝗸𝗲 𝗶𝘁 𝗶𝗻𝘁𝗲𝗿𝗲𝘀𝘁𝗶𝗻𝗴, {mention}! 🎉✨",
    ("good luck", "গুড লাক"): "🍀 **[ 𝗚𝗢𝗢𝗗 𝗟𝗨𝗖𝗞 ]** 🍀\n\n🎁 𝗪𝗶𝘀𝗵𝗶𝗻𝗴 𝘆𝗼𝘂 𝗮𝗹𝗹 𝘁𝗵𝗲 𝗯𝗲𝘀𝘁, {mention}! 🌟✨",
    ("forget", "ভুলে যাওয়া"): "🧠 **[ 𝗠𝗘𝗠𝗢𝗥𝗬 ]** 🧠\n\n⚡ 𝗜 𝗻𝗲𝘃𝗲𝗿 𝗳𝗼𝗿𝗴𝗲𝘁, {mention}! 📜🚀",
    ("remember", "মনে রাখা"): "📜 **[ 𝗥𝗘𝗠𝗘𝗠𝗕𝗘𝗥 ]** 📜\n\n💡 𝗔𝗹𝘄𝗮𝘆𝘀 𝘀𝗮𝘃𝗲𝗱 𝗶𝗻 𝗺𝗲𝗺𝗼𝗿𝘆, {mention}! 🔍✨",
    ("bye", "বাই"): "👋 **[ 𝗕𝗬𝗘 ]** 👋\n\n✨ 𝗛𝗮𝘃𝗲 𝗮 𝗴𝗿𝗲𝗮𝘁 𝘁𝗶𝗺𝗲, {mention}! 🌸💫",
    ("cool", "কুল"): "😎 **[ 𝗖𝗢𝗢𝗟 𝗩𝗜𝗕𝗘𝗦 ]** 😎\n\n⚡ 𝗦𝘁𝗮𝘆 𝗰𝗼𝗼𝗹 𝗮𝗻𝗱 𝗰𝗮𝗹𝗺, {mention}! 🧊🔥",
    ("done", "হয়েছে"): "✅ **[ 𝗗𝗢𝗡𝗘 ]** ✅\n\n🚀 𝗪𝗼𝗿𝗸 𝗶𝘀 𝗱𝗼𝗻𝗲, {mention}! ✨🏆",
    ("wait", "দাঁড়াও"): "⏳ **[ 𝗪𝗔𝗜𝗧 ]** ⏳\n\n✋ 𝗛𝗼𝗹𝗱 𝗼𝗻 𝗮 𝘀𝗲𝗰𝗼𝗻𝗱, {mention}! 🔄✨",
    ("fast", "তাড়াতাড়ি"): "⚡ **[ 𝗦𝗣𝗘𝗘𝗗 ]** ⚡\n\n🚀 𝗥𝘂𝗻𝗻𝗶𝗻𝗴 𝗮𝘁 𝗳𝘂𝗹𝗹 𝘀𝗽𝗲𝗲𝗱, {mention}! 💨🔥",
    ("magic", "ম্যাজিক"): "🪄 **[ 𝗠𝗔𝗚𝗜𝗖 ]** 🪄\n\n✨ 𝗣𝘂𝗿𝗲 𝗱𝗶𝗴𝗶𝘁𝗮𝗹 𝗺𝗮𝗴𝗶𝗰, {mention}! 🌟🔮"
}


async def is_admin(chat_id: int, user_id: int) -> bool:
    """Check if the user is an administrator or owner in the chat."""
    try:
        member = await app.get_chat_member(chat_id, user_id)
        return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except Exception:
        return False


@app.on_message(filters.command(["chatbot"]) & filters.group)
async def toggle_chatbot(client, message: Message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply_text("❌ `Only administrators can toggle chatbot settings.`")

    if len(message.command) < 2:
        return await message.reply_text(
            "⚙️ **[ 𝗖𝗛𝗔𝗧𝗕𝗢𝗧 𝗦𝗘𝗧𝗧𝗜𝗡𝗚𝗦 ]**\n\n"
            "📌 **𝗨𝘀𝗮𝗴𝗲:**\n"
            "• `/chatbot on` - 𝗧𝘂𝗿𝗻 𝗢𝗡 𝗖𝗵𝗮𝘁𝗯𝗼𝘁\n"
            "• `/chatbot off` - 𝗧𝘂𝗿𝗻 𝗢𝗙𝗙 𝗖𝗵𝗮𝘁𝗯𝗼𝘁"
        )

    state = message.command[1].lower()

    if state in ["on", "enable", "yes"]:
        CHATBOT_ENABLED_CHATS.add(message.chat.id)
        await message.reply_text("✅ `[ 𝗘𝗡𝗔𝗙𝗨𝗟 ] 𝗖𝗵𝗮𝘁𝗯𝗼𝘁 𝗵𝗮𝘀 𝗯𝗲𝗲𝗻 𝗘𝗡𝗔𝗕𝗟𝗘𝗗 𝗳𝗼𝗿 𝘁𝗵𝗶𝘀 𝗴𝗿𝗼𝘂𝗽! 👑✨`")
    elif state in ["off", "disable", "no"]:
        CHATBOT_ENABLED_CHATS.discard(message.chat.id)
        await message.reply_text("🔴 `[ 𝗘𝗡𝗔𝗙𝗨𝗟 ] 𝗖𝗵𝗮𝘁𝗯𝗼𝘁 𝗵𝗮𝘀 𝗯𝗲𝗲𝗻 𝗗𝗜𝗦𝗔𝗕𝗟𝗘𝗗 𝗳𝗼𝗿 𝘁𝗵𝗶𝘀 𝗴𝗿𝗼𝘂𝗽. 🛑`")
    else:
        await message.reply_text("❌ `Invalid option! Use /chatbot on or /chatbot off.`")


@app.on_message(filters.group & ~filters.bot & ~filters.via_bot, group=10)
async def chatbot_reply(client, message: Message):
    # Check if chatbot is enabled in this chat
    if message.chat.id not in CHATBOT_ENABLED_CHATS:
        return

    # Ignore command messages
    if message.text and message.text.startswith(("/", "!", ".", "?")):
        return

    bot_user = await app.get_me()
    is_reply_to_bot = message.reply_to_message and message.reply_to_message.from_user and message.reply_to_message.from_user.id == bot_user.id
    is_mentioned = bot_user.username and message.text and f"@{bot_user.username}" in message.text

    if is_reply_to_bot or is_mentioned or message.text:
        user_text = message.text.lower().strip() if message.text else ""
        chosen_response = None

        # Check in mapped responses
        for keywords, response in EXACT_RESPONSES.items():
            if any(kw in user_text for kw in keywords):
                chosen_response = response
                break

        # Only send reply if an exact context match is found
        if chosen_response:
            await client.send_chat_action(message.chat.id, action=enums.ChatAction.TYPING)
            await asyncio.sleep(1)

            # Plain Text User Mention (No User ID / Links)
            raw_name = message.from_user.first_name or "User"
            if message.from_user.username:
                user_mention = to_serif(f"@{message.from_user.username}")
            else:
                user_mention = to_serif(raw_name)

            reply_text = chosen_response.format(mention=user_mention)

            try:
                # Direct reply without HTML/Markdown User ID links
                await message.reply_text(reply_text, parse_mode=enums.ParseMode.MARKDOWN)
            except Exception:
                try:
                    await message.reply_text(reply_text)
                except Exception as e:
                    print(f"[Chatbot Error]: {e}")
