# -*- coding: utf-8 -*-
"""
Handlers for Telegram commands like /start and /help. Uses HTML ParseMode.
"""

import logging

from telegram import Update, constants
from telegram.ext import ContextTypes

# Import config, localization, helpers, and common handlers
from config import START_DIRECTORY_PATH, UD_KEY_CURRENT_PATH
import localization as loc
# Use escape_html from helpers
from utils.helpers import is_authorized, set_safe_path, escape_html
from .common_handlers import display_folder_content

logger = logging.getLogger(__name__)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles /start command. Clears context and shows root directory."""
    if not is_authorized(update):
        # Use HTML parse mode for error messages too
        await update.message.reply_text(loc.ACCESS_DENIED, parse_mode=constants.ParseMode.HTML)
        return

    user = update.effective_user
    user_id = user.id
    # mention_html produces an HTML link
    user_mention = user.mention_html()
    logger.info(f"Aᴜᴛʜᴏʀɪᴢᴇᴅ ᴜsᴇʀ {user_id} ({user.username}) sᴛᴀʀᴛᴇᴅ ɪɴᴛᴇʀᴀᴄᴛɪᴏɴ.")

    context.user_data.clear()
    logger.debug(f"User data cleared for user {user_id}")

    initial_path = set_safe_path(context, START_DIRECTORY_PATH)

    # Construct welcome message using HTML
    welcome_text = loc.WELCOME_MESSAGE.format(user_mention=user_mention)
    # Escape the path for display inside <code> tag
    folder_text = f"{loc.STARTING_FOLDER} <code>{escape_html(str(initial_path))}</code>"
    await update.message.reply_text(
        f"{welcome_text}\n{folder_text}",
        parse_mode=constants.ParseMode.HTML # Use HTML
    )

    await display_folder_content(update, context, initial_path, page=0, edit_message=False)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Shows the help message defined in localization (now HTML)."""
    if not is_authorized(update):
        await update.message.reply_text(loc.ACCESS_DENIED, parse_mode=constants.ParseMode.HTML)
        return

    await update.message.reply_text(loc.HELP_TEXT, parse_mode=constants.ParseMode.HTML) # Use HTML


# Made by: Zaky1million 😊♥️
# For contact or project requests: https://t.me/Zaky1million
# Please keep this credit as a sign of respect and support.
# Keep going, developer!
# Every great project starts with a single line of code.
# Believe in your skills and never stop learning.
# You're not just coding – you're creating magic.
# Your future self will thank you for the effort you put in today.

