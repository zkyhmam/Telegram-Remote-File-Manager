# -*- coding: utf-8 -*-
"""
Global error handler for the bot. Uses HTML ParseMode for user messages.
"""

import logging

from telegram import Update, constants
from telegram.ext import ContextTypes
from telegram.error import BadRequest, Forbidden

# Import config, localization, and constants
from config import (
    UD_KEY_SEARCH_BASE_PATH, UD_KEY_SEARCH_RESULTS,
    UD_KEY_SEARCH_PROMPT_MSG_ID, UD_KEY_SEARCH_FORCE_REPLY_MSG_ID # Import both msg IDs
)
import localization as loc # Localization uses HTML now

logger = logging.getLogger(__name__)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log Errors caused by Updates and notify user if possible (HTML ParseMode)."""
    logger.error(f"Eʀʀᴏʀ ʜᴀɴᴅʟɪɴɢ ᴜᴘᴅᴀᴛᴇ: {update}\nError: {context.error}", exc_info=context.error)

    if isinstance(context.error, BadRequest) and "Message is not modified" in str(context.error):
        logger.debug(f"Iɢɴᴏʀɪɴɢ ʙᴇɴɪɢɴ BᴀᴅRᴇǫᴜᴇsᴛ ɪɴ ᴇʀʀᴏʀ ʜᴀɴᴅʟᴇʀ: {context.error}")
        return

    if isinstance(update, Update) and update.effective_chat:
        chat_id = update.effective_chat.id
        try:
            await context.bot.send_message(
                chat_id=chat_id, text=loc.INTERNAL_ERROR_LOGGED, parse_mode=constants.ParseMode.HTML
            )
        except Forbidden: logger.error(f"Cannot send error message to chat {chat_id}: Bot forbidden.")
        except Exception as e: logger.error(f"Failed to send error notification message to chat {chat_id}: {e}")

    # Clean up conversation state if an error occurred within the search conversation
    if isinstance(context.error, Exception) and context.user_data:
         search_keys_present = any(key in context.user_data for key in [
             UD_KEY_SEARCH_BASE_PATH, UD_KEY_SEARCH_PROMPT_MSG_ID,
             UD_KEY_SEARCH_FORCE_REPLY_MSG_ID, # Check for force reply ID too
             UD_KEY_SEARCH_RESULTS
         ])
         if search_keys_present:
              logger.info("Attempting to clean up search context data after error during conversation.")
              context.user_data.pop(UD_KEY_SEARCH_BASE_PATH, None)
              context.user_data.pop(UD_KEY_SEARCH_PROMPT_MSG_ID, None)
              context.user_data.pop(UD_KEY_SEARCH_FORCE_REPLY_MSG_ID, None) # Pop force reply ID
              context.user_data.pop(UD_KEY_SEARCH_RESULTS, None)


# Made by: Zaky1million 😊♥️
# For contact or project requests: https://t.me/Zaky1million
# Please keep this credit as a sign of respect and support.
# Keep going, developer!
# Every great project starts with a single line of code.
# Believe in your skills and never stop learning.
# You're not just coding – you're creating magic.
# Your future self will thank you for the effort you put in today.

