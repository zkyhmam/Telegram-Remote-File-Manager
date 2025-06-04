# -*- coding: utf-8 -*-
"""
Handlers for general text messages (automatic search) and unauthorized access.
"""
import logging
import time # Not directly used, can be removed if not needed elsewhere in future
from pathlib import Path
from typing import List, Dict, Any

from telegram import Update, constants, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from config import (
    START_DIRECTORY_PATH, UD_KEY_SEARCH_BASE_PATH, UD_KEY_SEARCH_RESULTS,
    CB_PREFIX_SRCH_BACK, CB_PREFIX_SRCH_DIR, CB_PREFIX_SRCH_FILE, CB_PREFIX_NOOP,
    SEARCH_RESULTS_LIMIT, BOT_IMAGE_URL, UD_KEY_CURRENT_MESSAGE_ID
)
import localization as loc
from utils.auth_utils import is_authorized # <<<--- مصدر is_authorized الصحيح
from utils.helpers import (
    # is_authorized removed from here
    escape_html, truncate_filename, get_file_emoji,
    create_callback_data, store_list_in_context, get_safe_path,
    send_or_edit_photo_message, handle_unauthorized_access
)
from utils.search_utils import perform_search
from .common_handlers import display_folder_content # Not used directly in handle_text_search

logger = logging.getLogger(__name__)

MIN_SEARCH_TERM_LENGTH = 1

async def handle_text_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles user's text input for automatic search, performs search, displays results."""
    if not await is_authorized(update, context): # <<<--- يستخدم is_authorized
        await handle_unauthorized_access(update, context)
        return

    search_term_raw = update.message.text
    if not search_term_raw or len(search_term_raw) < MIN_SEARCH_TERM_LENGTH:
        if search_term_raw:
             logger.info(f"Search term '{search_term_raw}' too short, ignoring.")
        return

    search_term_escaped = escape_html(search_term_raw)
    chat_id = update.message.chat_id
    user_id = update.effective_user.id

    search_path = get_safe_path(context)
    context.user_data[UD_KEY_SEARCH_BASE_PATH] = str(search_path)

    logger.info(f"User {user_id} (auth) auto-searching for '{search_term_raw}' in '{search_path}'")

    context.user_data.pop(UD_KEY_SEARCH_RESULTS, None)
    # For search results, always send a new message, so no need to manage UD_KEY_CURRENT_MESSAGE_ID here before sending.
    # send_or_edit_photo_message will store the new message's ID.

    status_msg_text = loc.SEARCH_PERFORMING.format(term=search_term_escaped, path=escape_html(str(search_path)))
    status_message_obj = None
    try:
        status_message_obj = await context.bot.send_message(
            chat_id=chat_id, text=status_msg_text,
            parse_mode=constants.ParseMode.HTML, disable_notification=True
        )
        await context.bot.send_chat_action(chat_id=chat_id, action=constants.ChatAction.TYPING)
    except Exception as e:
        logger.error(f"Failed to send 'Searching...' status message: {e}")

    results, search_error_msg = perform_search(search_term_raw, search_path)
    
    if status_message_obj:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=status_message_obj.message_id)
        except Exception as e:
            logger.warning(f"Could not delete 'Searching...' message: {e}")

    store_list_in_context(context, UD_KEY_SEARCH_RESULTS, results)

    results_caption_text = ""
    results_keyboard_buttons: List[List[InlineKeyboardButton]] = []

    if search_error_msg:
        results_caption_text = search_error_msg
    elif not results:
        results_caption_text = loc.SEARCH_NO_RESULTS.format(
            term=search_term_escaped, path=escape_html(str(search_path))
        )
    else: # results has content
        count_actual = len(results) # results is already limited by SEARCH_RESULTS_LIMIT in perform_search
        limit_was_hit = count_actual >= SEARCH_RESULTS_LIMIT 
        
        count_display_text = f"{count_actual}{'+' if limit_was_hit else ''}"
        escaped_count_display = escape_html(count_display_text)

        results_caption_text = (loc.SEARCH_FOUND_LIMITED_RESULTS if limit_was_hit else loc.SEARCH_FOUND_RESULTS).format(
            count=escaped_count_display, 
            count_display=escaped_count_display, # For older loc string compatibility
            limit=SEARCH_RESULTS_LIMIT,
            term=search_term_escaped
        )
        
        row: List[InlineKeyboardButton] = []
        for index, result_item in enumerate(results):
            item_display_name = escape_html(truncate_filename(result_item['name']))
            callback_prefix_item = CB_PREFIX_NOOP
            item_emoji = "❓"

            if result_item["is_dir"]:
                item_emoji = "🔗" if result_item["is_symlink"] else "📁"
                callback_prefix_item = CB_PREFIX_SRCH_DIR
            elif result_item["is_file"]:
                item_emoji = "🔗" if result_item["is_symlink"] else get_file_emoji(result_item['name'])
                callback_prefix_item = CB_PREFIX_SRCH_FILE
            elif result_item["is_symlink"]:
                item_emoji = "⚠️🔗"
            
            button_text_item = f"{item_emoji} {item_display_name}"
            callback_action_item = create_callback_data(callback_prefix_item, index)

            if callback_action_item:
                row.append(InlineKeyboardButton(button_text_item, callback_data=callback_action_item))
            else:
                row.append(InlineKeyboardButton(f"⚠️ {item_display_name}", callback_data=CB_PREFIX_NOOP))

            if len(row) >= 3:
                results_keyboard_buttons.append(row)
                row = []
        if row:
            results_keyboard_buttons.append(row)

    back_cb_data = create_callback_data(CB_PREFIX_SRCH_BACK, "")
    if back_cb_data:
        # Add as the last row of buttons, or if no item buttons, it's the only row.
        results_keyboard_buttons.append([InlineKeyboardButton(loc.BUTTON_SEARCH_BACK_TO_BROWSER, callback_data=back_cb_data)])
    
    final_results_markup = InlineKeyboardMarkup(results_keyboard_buttons) if results_keyboard_buttons else None
    if not final_results_markup and not search_error_msg and results :
         results_caption_text += f"\n{loc.SEARCH_BUTTON_ERROR}"

    await send_or_edit_photo_message(
        update, context, chat_id,
        caption=results_caption_text,
        reply_markup=final_results_markup,
        edit_existing=False # Search results are always a new message context
    )

async def handle_unauthorized_catch_all(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    This handler is less critical now as authorization is checked at the start of primary handlers.
    It can serve as a final fallback.
    """
    if not await is_authorized(update, context): # <<<--- يستخدم is_authorized
        await handle_unauthorized_access(update, context)

# Made by: Zaky1million 😊♥️
# For contact or project requests: https://t.me/Zaky1million
