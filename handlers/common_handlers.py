# -*- coding: utf-8 -*-
"""
Common handler functions used by multiple other handlers (e.g., displaying folder content).
"""
import logging
from pathlib import Path

from telegram import Update, constants
from telegram.ext import ContextTypes
from telegram.error import BadRequest, Forbidden

from config import UD_KEY_CURRENT_PAGE, BOT_IMAGE_URL, UD_KEY_CURRENT_MESSAGE_ID
import localization as loc
from utils.helpers import (
    # is_authorized, # Authorization handled by caller
    set_safe_path, send_or_edit_photo_message,
    # handle_unauthorized_access # Authorization handled by caller
)
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
    Validates target path, generates markup for the requested page,
    and updates the message by sending/editing a photo with caption.
    Authorization is expected to be handled by the calling function.
    """
    query = update.callback_query
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    logger.info(f"Displaying folder: User={user_id}, Target='{target_path_str}', ReqPage={page}, EditHint={edit_message}")

    target_path = set_safe_path(context, target_path_str) # Updates UD_KEY_CURRENT_PATH
    
    keyboard_markup, caption_text = generate_file_list_markup(context, target_path, page=page)
    # generate_file_list_markup updates UD_KEY_CURRENT_PAGE and UD_KEY_VIEW_ITEMS

    displayed_page = context.user_data.get(UD_KEY_CURRENT_PAGE, 0)
    logger.debug(f"Generated markup for path '{target_path}', effective page {displayed_page}.")

    try:
        await send_or_edit_photo_message(
            update, context, chat_id,
            caption=caption_text,
            reply_markup=keyboard_markup,
            edit_existing=edit_message
        )
        logger.debug(f"Folder content for '{target_path}' displayed/updated.")

    except BadRequest as e:
        if "Message is not modified" in str(e): # This case should ideally be caught by send_or_edit_photo_message
            logger.debug(f"Message not modified for {target_path}. (Handled by helper or this is a fallback)")
            if query:
                try:
                    await query.answer() 
                except Exception as e_ans:
                    logger.debug(f"Query answer failed (likely already answered or old) for 'not modified': {e_ans}")
        else:
            logger.error(f"BadRequest during display_folder_content for {target_path}: {e}")
            if query:
                try:
                    await query.answer(loc.ERROR_DISPLAY_UPDATE, show_alert=True)
                except Exception as e_ans:
                     logger.debug(f"Query answer failed for BadRequest display_folder_content: {e_ans}")
            try:
                # Send a new text message as fallback if editing/sending photo fails with other BadRequest
                await context.bot.send_message(chat_id, loc.ERROR_FATAL_DISPLAY, parse_mode=constants.ParseMode.HTML)
            except Exception as final_err:
                logger.error(f"Failed to send text fallback for BadRequest: {final_err}")

    except Forbidden as e:
         logger.error(f"Forbidden: Cannot update display for {target_path} in chat {chat_id}: {e}")
         if query:
             try:
                 await query.answer(loc.ERROR_BOT_PERMISSION, show_alert=True)
             except Exception as e_ans:
                  logger.debug(f"Query answer failed for Forbidden display_folder_content: {e_ans}")
    except Exception as e:
        logger.exception(f"Unexpected error during display_folder_content for {target_path}: {e}")
        if query:
            try:
                await query.answer(loc.INTERNAL_ERROR, show_alert=True)
            except Exception as e_ans:
                logger.debug(f"Query answer failed for general Exception in display_folder_content: {e_ans}")
        try:
            await context.bot.send_message(chat_id, loc.ERROR_FATAL_DISPLAY, parse_mode=constants.ParseMode.HTML)
        except Exception as final_err:
            logger.error(f"Failed to send text fallback for general Exception: {final_err}")


# Made by: Zaky1million 😊♥️
# For contact or project requests: https://t.me/Zaky1million
