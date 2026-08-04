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
import importlib

from pyrogram import idle

from AloneX import (anon, app, db,
                    logger, stop, userbot)
from AloneX.plugins import all_modules

# ✅ Auto-clean function ko yahan import kiya gaya hai
from AloneX.core.dir import auto_clean_downloads


async def main():
    await db.connect()
    await app.boot()
    await userbot.boot()
    await anon.boot()

    for module in all_modules:
        importlib.import_module(f"AloneX.plugins.{module}")
    logger.info(f"Loaded {len(all_modules)} modules.")

    sudoers = await db.get_sudoers()
    app.sudoers.update(sudoers)
    app.bl_users.update(await db.get_blacklisted())
    logger.info(f"Loaded {len(app.sudoers)} sudo users.")

    # ✅ Yahan par auto-clean task ko background mein start kar diya gaya hai
    asyncio.create_task(auto_clean_downloads())
    logger.info("Auto-clean storage monitor started.")

    await idle()
    await stop()


if __name__ == "__main__":
    try:
        asyncio.get_event_loop().run_until_complete(main())
    except KeyboardInterrupt:
        pass
