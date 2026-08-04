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

from pyrogram import enums, errors, types

from AloneX import app, config, db, logger, queue, yt
from AloneX.helpers import utils


def checkUB(play):
    async def wrapper(_, m: types.Message):
        if not m.from_user:
            return await m.reply_text(m.lang["play_user_invalid"])

        chat_id = m.chat.id
        if m.chat.type != enums.ChatType.SUPERGROUP:
            await m.reply_text(m.lang["play_chat_invalid"])
            return await app.leave_chat(chat_id)

        if not m.reply_to_message and (
            len(m.command) < 2 or (len(m.command) == 2 and m.command[1] == "-f")
        ):
            return await m.reply_text(m.lang["play_usage"])

        if len(queue.get_queue(chat_id)) >= config.QUEUE_LIMIT:
            return await m.reply_text(m.lang["play_queue_full"].format(config.QUEUE_LIMIT))

        force = m.command[0].endswith("force") or (
            len(m.command) > 1 and "-f" in m.command[1]
        )
        video = m.command[0][0] == "v" and config.VIDEO_PLAY
        url = utils.get_url(m)
        m3u8 = url and not yt.valid(url)

        play_mode = await db.get_play_mode(chat_id)
        if play_mode or force:
            adminlist = await db.get_admins(chat_id)
            if (
                m.from_user.id not in adminlist
                and not await db.is_auth(chat_id, m.from_user.id)
                and not m.from_user.id in app.sudoers
            ):
                return await m.reply_text(m.lang["play_admin"])

        if chat_id not in db.active_calls:
            client = await db.get_client(chat_id)
            
            # --- FIX: Stop gracefully if the assistant client is dead ---
            if not client:
                return await m.reply_text(
                    "**⚠️ Assistant Error:**\nThe assistant account failed to load. Your `SESSION` string has likely expired or is invalid. Please generate a new Pyrogram v2 string session and update your config variables."
                )
            # ------------------------------------------------------------
            
            try:
                member = await app.get_chat_member(chat_id, client.id)
                if member.status in [
                    enums.ChatMemberStatus.BANNED,
                    enums.ChatMemberStatus.RESTRICTED,
                ]:
                    try:
                        await app.unban_chat_member(
                            chat_id=chat_id, user_id=client.id
                        )
                    except:
                        return await m.reply_text(
                            m.lang["play_banned"].format(
                                app.name,
                                client.id,
                                client.mention,
                                f"@{client.username}" if client.username else None,
                            )
                        )
            except errors.ChatAdminRequired:
                return await m.reply_text(m.lang["admin_required"])
            except Exception as e:
                # 🛠️ BULLETPROOF ERROR CATCHING: Catches all variations of UserNotParticipant
                if "USER_NOT_PARTICIPANT" in str(e) or isinstance(e, errors.UserNotParticipant):
                    if m.chat.username:
                        invite_link = m.chat.username
                        try:
                            await client.resolve_peer(invite_link)
                        except:
                            pass
                    else:
                        try:
                            invite_link = (await app.get_chat(chat_id)).invite_link
                            if not invite_link:
                                invite_link = await app.export_chat_invite_link(chat_id)
                        except errors.ChatAdminRequired:
                            return await m.reply_text(m.lang["admin_required"])
                        except Exception as ex:
                            return await m.reply_text(
                                m.lang["play_invite_error"].format(type(ex).__name__)
                            )

                    umm = await m.reply_text(m.lang["play_invite"].format(app.name))
                    await asyncio.sleep(2)
                    try:
                        await client.join_chat(invite_link)
                    except errors.UserAlreadyParticipant:
                        pass
                    except errors.InviteRequestSent:
                        await asyncio.sleep(2)
                        try:
                            await client.approve_chat_join_request(chat_id, client.id)
                        except errors.HideRequesterMissing:
                            pass
                        except Exception as ex:
                            return await umm.edit_text(
                                m.lang["play_invite_error"].format(type(ex).__name__)
                            )
                    except Exception as ex:
                        logger.error(f"Error joining chat - {chat_id}: {ex}")
                        return await umm.edit_text(
                            m.lang["play_invite_error"].format(type(ex).__name__)
                        )

                    await umm.delete()
                    try:
                        await client.resolve_peer(chat_id)
                    except:
                        pass
                else:
                    # Logs other unexpected errors without crashing
                    logger.error(f"Unexpected error in checkUB: {e}")

        if await db.get_cmd_delete(chat_id):
            try:
                await m.delete()
            except:
                pass

        return await play(_, m, force, m3u8, video, url)

    return wrapper
