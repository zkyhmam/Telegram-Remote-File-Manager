# -*- coding: utf-8 -*-
"""
Common handler functions used by multiple other handlers (e.g., displaying folder content).
Uses HTML ParseMode.
"""

import logging
from pathlib import Path

from telegram import Update, constants
from telegram.ext import ContextTypes
from telegram.error import BadRequest, Forbidden

# Import config, localization, helpers, and markup generation
from config import UD_KEY_CURRENT_PAGE, START_DIRECTORY_PATH
import localization as loc
# Use escape_html from helpers
from utils.helpers import is_authorized, set_safe_path, get_safe_path, escape_html
from utils.markup import generate_file_list_markup

logger = logging.getLogger(__name__)

async def display_folder_content(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    target_path_str: str | Path,
    page: int = 0,
    edit_message: bool = True
):
    """
    Validates target path, generates markup for the requested page, and updates the message.
    Handles message editing vs. sending new. Uses safe path functions. Uses HTML ParseMode.
    """
    query = update.callback_query
    chat_id = update.effective_chat.id
    message_id = query.message.message_id if query and query.message else None
    user_id = update.effective_user.id

    logger.info(f"--> display_folder_content: User={user_id}, Target='{target_path_str}', ReqPage={page}, Edit={edit_message}")

    target_path = set_safe_path(context, target_path_str)
    logger.info(f"    Validated path: {target_path}")

    # generate_file_list_markup now returns HTML formatted text
    keyboard, message_text = generate_file_list_markup(context, target_path, page=page)

    displayed_page = context.user_data.get(UD_KEY_CURRENT_PAGE, 0)
    logger.info(f"    Generated markup for displayed_page={displayed_page}. Attempting update.")

    try:
        if edit_message and query and message_id:
            logger.debug(f"    Attempting to edit message {message_id} in chat {chat_id}")
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=message_text,
                reply_markup=keyboard,
                parse_mode=constants.ParseMode.HTML # Use HTML
            )
            logger.debug(f"    Successfully edited message {message_id}")
        else:
            logger.debug(f"    Sending new message to chat {chat_id}")
            if query and message_id:
                 try:
                     await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
                     logger.debug(f"    Deleted previous message {message_id} before sending new.")
                 except Exception as del_e:
                      logger.warning(f"    Could not delete previous message {message_id}: {del_e}")

            await context.bot.send_message(
                chat_id=chat_id,
                text=message_text,
                reply_markup=keyboard,
                parse_mode=constants.ParseMode.HTML # Use HTML
            )
            logger.debug(f"    Sent new message.")

    except BadRequest as e:
        if "Message is not modified" in str(e):
            logger.debug(f"    Message {message_id} not modified. Skipping edit.")
            if query:
                try: await query.answer()
                except Exception as answer_e: logger.warning(f"Failed to answer 'not modified' query: {answer_e}")
        elif "Message to edit not found" in str(e):
             logger.warning(f"    Message {message_id} to edit not found. Sending new message instead.")
             await display_folder_content(update, context, target_path, page=displayed_page, edit_message=False)
        else:
            logger.error(f"    BadRequest updating message {message_id} for {target_path}: {e}")
            if query:
                try: await query.answer(loc.ERROR_DISPLAY_UPDATE, show_alert=True)
                except Exception as answer_e: logger.warning(f"Failed to answer BadRequest query: {answer_e}")
    except Forbidden as e:
         logger.error(f"    Forbidden: Cannot edit/send message to chat {chat_id}. Bot blocked or kicked? Error: {e}")
         if query:
             try: await query.answer(loc.ERROR_BOT_PERMISSION, show_alert=True)
             except Exception as answer_e: logger.warning(f"Failed to answer Forbidden query: {answer_e}")
    except Exception as e:
        logger.exception(f"    Unexpected error during display update for {target_path}: {e}")
        if query:
            try: await query.answer(loc.INTERNAL_ERROR, show_alert=True)
            except Exception as answer_e: logger.warning(f"Failed to answer Exception query: {answer_e}")
        try:
            # Error messages in loc are now HTML safe
            await context.bot.send_message(chat_id, loc.ERROR_FATAL_DISPLAY, parse_mode=constants.ParseMode.HTML)
        except Exception as final_e:
            logger.error(f"Failed even to send fatal error message after display update failure: {final_e}")


# Made by: Zaky1million 😊♥️
# For contact or project requests: https://t.me/Zaky1million
# Please keep this credit as a sign of respect and support.
# Keep going, developer!
# Every great project starts with a single line of code.
# Believe in your skills and never stop learning.
# You're not just coding – you're creating magic.
# Your future self will thank you for the effort you put in today.

