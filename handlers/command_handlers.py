# -*- coding: utf-8 -*-
"""
Handlers for Telegram commands like /start, /help, and /cancel.
"""
import logging
import os # Needed for os.sep for path construction
from pathlib import Path

from telegram import Update, constants
from telegram.ext import ContextTypes

from config import START_DIRECTORY_PATH, UD_KEY_CURRENT_PATH, UD_KEY_SEARCH_RESULTS, UD_KEY_SEARCH_BASE_PATH, BOT_IMAGE_URL, UD_KEY_CURRENT_PAGE
import localization as loc
from utils.auth_utils import is_authorized # <<<--- مصدر is_authorized الصحيح
from utils.helpers import (
    set_safe_path, escape_html,
    send_or_edit_photo_message, handle_unauthorized_access, get_safe_path
)
from .common_handlers import display_folder_content

logger = logging.getLogger(__name__)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles /start command. Clears context and shows root directory."""
    if not await is_authorized(update, context):
        await handle_unauthorized_access(update, context)
        return

    user = update.effective_user
    logger.info(f"User {user.id} ({user.username}) used /start.")

    context.user_data.clear()
    initial_path = set_safe_path(context, START_DIRECTORY_PATH) # Sets UD_KEY_CURRENT_PATH

    welcome_text_formatted = loc.WELCOME_MESSAGE.format(user_mention=user.mention_html())
    folder_text_formatted = f"{loc.STARTING_FOLDER} <code>{escape_html(str(initial_path))}</code>"
    
    caption = f"{welcome_text_formatted}\n{folder_text_formatted}"
    
    # This will send a new photo message and store its ID in UD_KEY_CURRENT_MESSAGE_ID
    await send_or_edit_photo_message(
        update, context, update.effective_chat.id,
        caption=caption,
        reply_markup=None, # Markup will be added by display_folder_content
        edit_existing=False # /start always creates a new message context
    )
    
    # display_folder_content will now edit the message sent above
    await display_folder_content(update, context, initial_path, page=0, edit_message=True)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Shows the help message with the bot's image."""
    if not await is_authorized(update, context):
        await handle_unauthorized_access(update, context)
        return
    
    logger.info(f"User {update.effective_user.id} used /help.")
    # Send help as a new message, doesn't affect current browsing message_id
    await send_or_edit_photo_message(
        update, context, update.effective_chat.id,
        caption=loc.HELP_TEXT,
        reply_markup=None,
        edit_existing=False # Send as new message
    )

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles /cancel.
    - If search results are in context, clears them and returns to the search base path.
    - Otherwise, refreshes the current folder view.
    """
    if not await is_authorized(update, context):
        await handle_unauthorized_access(update, context)
        return

    logger.info(f"User {update.effective_user.id} used /cancel.")
    # chat_id = update.effective_chat.id # Not directly used here anymore

    if UD_KEY_SEARCH_RESULTS in context.user_data:
        context.user_data.pop(UD_KEY_SEARCH_RESULTS, None)
        original_search_path_str = context.user_data.pop(UD_KEY_SEARCH_BASE_PATH, None)
        
        target_path_for_display = START_DIRECTORY_PATH # Default
        if original_search_path_str:
            try:
                resolved_path = Path(original_search_path_str).resolve()
                # Ensure it's safe (within START_DIRECTORY_PATH)
                if resolved_path == START_DIRECTORY_PATH or \
                   str(resolved_path).startswith(str(START_DIRECTORY_PATH) + os.sep):
                    target_path_for_display = resolved_path
            except Exception as e:
                logger.warning(f"Error resolving original search path '{original_search_path_str}' for cancel: {e}. Defaulting to root.")
        
        set_safe_path(context, target_path_for_display) # Update current path in context
        # Display folder content as a new message, replacing the search results view
        await display_folder_content(update, context, target_path_for_display, page=0, edit_message=False)
        # User sees the folder browser, loc.CANCEL_SEARCH_CLEARED can be part of that message if desired,
        # or a separate small text message. For now, just show the browser.

    else:
        # No active search context, just refresh current view
        current_path = get_safe_path(context) # Get current path or default to root
        current_page = context.user_data.get(UD_KEY_CURRENT_PAGE, 0)
        # Refresh current view, send as a new message to ensure clean state
        await display_folder_content(update, context, current_path, page=current_page, edit_message=False)
        # Similar to above, loc.CANCEL_NO_ACTIVE_OP message can be integrated or sent separately.

# Made by: Zaky1million 😊♥️
# For contact or project requests: https://t.me/Zaky1million
