# -*- coding: utf-8 -*-
"""
Global error handler for the bot.
"""
import logging
import html as pyhtml
import traceback

from telegram import Update, constants
from telegram.ext import ContextTypes
from telegram.error import BadRequest, Forbidden, NetworkError

from config import (
    UD_KEY_SEARCH_BASE_PATH, UD_KEY_SEARCH_RESULTS,
    BOT_IMAGE_URL
)
import localization as loc
from utils.helpers import send_or_edit_photo_message # For notifying user with image

logger = logging.getLogger(__name__)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log Errors caused by Updates and notify user if possible."""
    
    tb_lines = traceback.format_exception(context.error.__class__, context.error, context.error.__traceback__)
    tb_text = "".join(tb_lines)
    
    # Log with WARNING or ERROR level based on error type potentially
    log_level = logging.ERROR
    if isinstance(context.error, (NetworkError, BadRequest)): # Less critical often
        log_level = logging.WARNING

    logger.log(
        log_level,
        f"Eʀʀᴏʀ ʜᴀɴᴅʟɪɴɢ ᴜᴘᴅᴀᴛᴇ: {pyhtml.escape(str(update))}\n"
        f"Error Type: {context.error.__class__.__name__}\n"
        f"Error: {pyhtml.escape(str(context.error))}\n"
        f"Traceback:\n{pyhtml.escape(tb_text)}"
    )

    # Ignore common benign errors early
    if isinstance(context.error, BadRequest) and "Message is not modified" in str(context.error):
        logger.debug(f"Benign BadRequest (Message not modified) in global error handler: {context.error}")
        return
    if isinstance(context.error, NetworkError) and "Timed out" in str(context.error):
        logger.warning(f"Network timeout error: {context.error}. User might retry.")
        # No direct user notification for this one to avoid spam on flaky connections.
        return

    if isinstance(update, Update) and update.effective_chat:
        chat_id = update.effective_chat.id
        try:
            await send_or_edit_photo_message(
                update, context, chat_id,
                caption=loc.INTERNAL_ERROR_LOGGED,
                reply_markup=None,
                edit_existing=False # Send as new message for errors
            )
        except Forbidden:
            logger.error(f"Cannot send error message (photo) to chat {chat_id}: Bot forbidden.")
        except Exception as e:
            logger.error(f"Failed to send error notification (photo) to chat {chat_id}: {e}")
            try: # Fallback to simple text
                await context.bot.send_message(
                    chat_id=chat_id, text=loc.INTERNAL_ERROR_LOGGED, parse_mode=constants.ParseMode.HTML
                )
            except Exception as final_e:
                 logger.error(f"Failed to send even text error notification to chat {chat_id}: {final_e}")

    # Clean up any potentially stuck search context data
    if isinstance(context.error, Exception) and context.user_data:
         search_keys_present = any(key in context.user_data for key in [
             UD_KEY_SEARCH_BASE_PATH, UD_KEY_SEARCH_RESULTS
         ])
         if search_keys_present:
              logger.info("Attempting to clean up search context data after error during conversation.")
              context.user_data.pop(UD_KEY_SEARCH_BASE_PATH, None)
              context.user_data.pop(UD_KEY_SEARCH_RESULTS, None)

# Made by: Zaky1million 😊♥️
# For contact or project requests: https://t.me/Zaky1million
