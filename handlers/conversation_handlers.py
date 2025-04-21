# -*- coding: utf-8 -*-
"""
State and fallback functions for the search ConversationHandler. Uses HTML ParseMode.
Includes button-based cancellation helper.
ConversationHandler itself is defined in bot.py to avoid circular imports.
"""

import logging
import os
import re
import html
from pathlib import Path
from stat import S_ISLNK
from typing import List, Dict, Any, Optional

from telegram import Update, constants, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, CommandHandler, CallbackQueryHandler, filters

# Import config, localization, helpers, markup
from config import (
    ASKING_SEARCH_TERM, START_DIRECTORY_PATH, SEARCH_RESULTS_LIMIT,
    UD_KEY_SEARCH_BASE_PATH, UD_KEY_SEARCH_RESULTS,
    CB_PREFIX_SRCH_BACK, CB_PREFIX_SRCH_DIR, CB_PREFIX_SRCH_FILE, CB_PREFIX_NOOP,
    CB_PREFIX_SRCH_START, CB_PREFIX_SRCH_CANCEL,
    UD_KEY_SEARCH_PROMPT_MSG_ID, UD_KEY_SEARCH_FORCE_REPLY_MSG_ID
)
import localization as loc
from utils.helpers import (
    is_authorized, escape_html, truncate_filename, get_file_emoji,
    create_callback_data, store_list_in_context, get_safe_path, set_safe_path
)
from .common_handlers import display_folder_content
# Remove the problematic import:
# from .callback_handlers import main_callback_handler

logger = logging.getLogger(__name__)


# --- Helper for Search Cancellation ---
async def _perform_search_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE, from_callback: bool = False):
    """Core logic to cancel search, clean up messages and context."""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    logger.info(f"User {user_id} requested search cancellation.")

    prompt_cancel_msg_id = context.user_data.pop(UD_KEY_SEARCH_PROMPT_MSG_ID, None)
    force_reply_msg_id = context.user_data.pop(UD_KEY_SEARCH_FORCE_REPLY_MSG_ID, None)
    user_message_id = update.message.message_id if update.message else None

    if prompt_cancel_msg_id:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=prompt_cancel_msg_id)
        except Exception as e:
            logger.debug(f"Could not delete search prompt/cancel message {prompt_cancel_msg_id}: {e}")
    if force_reply_msg_id:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=force_reply_msg_id)
        except Exception as e:
            logger.debug(f"Could not delete search force_reply message {force_reply_msg_id}: {e}")
    if user_message_id and not from_callback:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=user_message_id)
        except Exception as e:
            logger.debug(f"Could not delete user /cancel command message {user_message_id}: {e}")

    original_path_str = context.user_data.pop(UD_KEY_SEARCH_BASE_PATH, str(START_DIRECTORY_PATH))
    context.user_data.pop(UD_KEY_SEARCH_RESULTS, None)

    try:
        await context.bot.send_message(
            chat_id=chat_id,
            text=loc.SEARCH_CANCELLED,
            parse_mode=constants.ParseMode.HTML
        )
    except Exception as e:
        logger.error(f"Failed to send cancel confirmation: {e}")

    try:
        original_path = Path(original_path_str).resolve()
        if not (original_path == START_DIRECTORY_PATH or str(original_path).startswith(str(START_DIRECTORY_PATH) + os.sep)):
             original_path = START_DIRECTORY_PATH
    except Exception:
        original_path = START_DIRECTORY_PATH

    await display_folder_content(
        update=update,
        context=context,
        target_path_str=original_path,
        page=0,
        edit_message=False
    )


# --- Search State and Fallback Handlers ---

async def receive_search_term(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles user's text input for search, performs search, displays results (HTML)."""
    logger.debug(f"receive_search_term entered by user {update.effective_user.id}")
    if not is_authorized(update):
        logger.warning(f"Uɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ sᴇᴀʀᴄʜ ᴛᴇʀᴍ ɪɴᴘᴜᴛ ғʀᴏᴍ {update.effective_user.id}")
        context.user_data.pop(UD_KEY_SEARCH_BASE_PATH, None)
        context.user_data.pop(UD_KEY_SEARCH_PROMPT_MSG_ID, None)
        context.user_data.pop(UD_KEY_SEARCH_FORCE_REPLY_MSG_ID, None)
        return ConversationHandler.END

    search_term_raw = update.message.text
    search_term_escaped = escape_html(search_term_raw)

    user_message_id = update.message.message_id
    prompt_cancel_msg_id = context.user_data.get(UD_KEY_SEARCH_PROMPT_MSG_ID)
    force_reply_msg_id = context.user_data.get(UD_KEY_SEARCH_FORCE_REPLY_MSG_ID)

    search_path_str = context.user_data.get(UD_KEY_SEARCH_BASE_PATH, str(START_DIRECTORY_PATH))
    try:
        search_path = Path(search_path_str).resolve()
        if not (search_path == START_DIRECTORY_PATH or str(search_path).startswith(str(START_DIRECTORY_PATH) + os.sep)):
            search_path = START_DIRECTORY_PATH
            context.user_data[UD_KEY_SEARCH_BASE_PATH] = str(search_path)
    except Exception as e:
        search_path = START_DIRECTORY_PATH
        context.user_data[UD_KEY_SEARCH_BASE_PATH] = str(search_path)

    chat_id = update.message.chat_id
    user_id = update.effective_user.id

    if prompt_cancel_msg_id:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=prompt_cancel_msg_id)
        except Exception as e:
            logger.debug(f"Could not delete search prompt/cancel message {prompt_cancel_msg_id}: {e}")
    if force_reply_msg_id:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=force_reply_msg_id)
        except Exception as e:
            logger.debug(f"Could not delete search force_reply message {force_reply_msg_id}: {e}")
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=user_message_id)
    except Exception as e:
        logger.debug(f"Could not delete user search term reply message {user_message_id}: {e}")

    context.user_data.pop(UD_KEY_SEARCH_PROMPT_MSG_ID, None)
    context.user_data.pop(UD_KEY_SEARCH_FORCE_REPLY_MSG_ID, None)

    logger.info(f"User {user_id} searching for '{search_term_raw}' in '{search_path}'")
    status_msg = None
    try:
        escaped_path_str = escape_html(str(search_path))
        status_msg = await context.bot.send_message(
            chat_id=chat_id,
            text=loc.SEARCH_PERFORMING.format(term=search_term_escaped, path=escaped_path_str),
            parse_mode=constants.ParseMode.HTML,
            disable_notification=True,
        )
        await context.bot.send_chat_action(chat_id=chat_id, action=constants.ChatAction.TYPING)
    except Exception as e:
        logger.error(f"Failed to send 'Searching...' status message: {e}")

    results: List[Dict[str, Any]] = []
    search_error: Optional[str] = None
    processed_inodes = set()
    try:
        safe_term = re.escape(search_term_raw).replace('\\*', '.*')
        pattern = re.compile(safe_term, re.IGNORECASE)
        logger.debug(f"Search regex pattern: '{pattern.pattern}'")

        for root, dirs, files in os.walk(search_path, topdown=True, onerror=lambda e: logger.warning(f"[yellow]Pᴇʀᴍɪssɪᴏɴ ᴏʀ ᴏᴛʜᴇʀ ᴇʀʀᴏʀ ᴅᴜʀɪɴɢ ᴡᴀʟᴋ ɪɴ {escape_html(e.filename)}:[/]", extra={"markup": True}), followlinks=False):
            current_root_path = Path(root)
            if not (current_root_path.resolve() == START_DIRECTORY_PATH or str(current_root_path.resolve()).startswith(str(START_DIRECTORY_PATH) + os.sep)):
                 dirs[:] = []
                 continue

            dirs_to_prune_indices = []
            dirs_copy = list(dirs)
            for i, dirname in enumerate(dirs_copy):
                dirpath = current_root_path / dirname
                try:
                    dir_stat = dirpath.lstat()
                    is_symlink = S_ISLNK(dir_stat.st_mode)
                    if dir_stat.st_ino in processed_inodes and is_symlink:
                        try:
                            dirs_to_prune_indices.append(dirs.index(dirname))
                        except ValueError:
                            pass
                        continue
                    processed_inodes.add(dir_stat.st_ino)

                    if pattern.search(dirname):
                        resolved_path_str = str(dirpath)
                        is_target_dir = False
                        try:
                            resolved_path = dirpath.resolve(strict=True)
                            if resolved_path == START_DIRECTORY_PATH or str(resolved_path).startswith(str(START_DIRECTORY_PATH) + os.sep):
                                is_target_dir = resolved_path.is_dir()
                                resolved_path_str = str(resolved_path)
                            else:
                                is_target_dir = False
                        except (OSError, FileNotFoundError):
                            is_target_dir = False
                        results.append({
                            "name": dirname, "path": resolved_path_str,
                            "is_dir": is_target_dir, "is_file": False, "is_symlink": is_symlink
                        })
                        if len(results) >= SEARCH_RESULTS_LIMIT:
                            break # Exit inner loop

                except OSError as e:
                    logger.warning(f"[yellow]OSError checking directory {escape_html(str(dirpath))}: {e}. Pruning.[/]", extra={"markup": True})
                    try:
                        dirs_to_prune_indices.append(dirs.index(dirname))
                    except ValueError:
                        pass
                except Exception as e:
                    logger.warning(f"[yellow]Unexpected error checking directory {escape_html(str(dirpath))}: {e}. Pruning.[/]", extra={"markup": True})
                    try:
                        dirs_to_prune_indices.append(dirs.index(dirname))
                    except ValueError:
                        pass
            # End inner loop for dirs

            if len(results) >= SEARCH_RESULTS_LIMIT:
                break # Exit outer loop if limit reached in dirs loop

            # Prune dirs after iterating copy
            for index in sorted(set(dirs_to_prune_indices), reverse=True):
                 if 0 <= index < len(dirs):
                    del dirs[index]

            # Process files
            for filename in files:
                filepath = current_root_path / filename
                try:
                    if pattern.search(filename):
                        file_stat = filepath.lstat()
                        is_symlink = S_ISLNK(file_stat.st_mode)
                        resolved_path_str = str(filepath)
                        is_target_file = False
                        try:
                            resolved_path = filepath.resolve(strict=True)
                            if resolved_path == START_DIRECTORY_PATH or str(resolved_path).startswith(str(START_DIRECTORY_PATH) + os.sep):
                                is_target_file = resolved_path.is_file()
                                resolved_path_str = str(resolved_path)
                            else:
                                is_target_file = False
                        except (OSError, FileNotFoundError):
                            is_target_file = False
                        results.append({
                            "name": filename, "path": resolved_path_str,
                            "is_dir": False, "is_file": is_target_file, "is_symlink": is_symlink
                        })
                        if len(results) >= SEARCH_RESULTS_LIMIT:
                            break # Exit files loop
                except OSError as e:
                    logger.warning(f"[yellow]OSError checking file {escape_html(str(filepath))}: {e}. Skipping.[/]", extra={"markup": True})
                except Exception as e:
                    logger.warning(f"[yellow]Unexpected error checking file {escape_html(str(filepath))}: {e}. Skipping.[/]", extra={"markup": True})
            # End files loop

            if len(results) >= SEARCH_RESULTS_LIMIT:
                break # Exit outer loop if limit reached in files loop
        # End outer loop (os.walk)

    except PermissionError as e:
        search_error = loc.SEARCH_ERROR_PERMISSION
        logger.error(f"Pᴇʀᴍɪssɪᴏɴ ᴅᴇɴɪᴇᴅ sᴛᴀʀᴛɪɴɢ os.walk: {e}")
    except Exception as e:
        search_error = loc.SEARCH_ERROR_GENERAL.format(error=escape_html(str(e)))
        logger.exception(f"Eʀʀᴏʀ ᴅᴜʀɪɴɢ search: {e}")

    if status_msg:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=status_msg.message_id)
        except Exception as e:
            logger.warning(f"Could not delete 'Searching...' message {status_msg.message_id}: {e}")

    store_list_in_context(context, UD_KEY_SEARCH_RESULTS, results)
    results_message_text = ""
    results_keyboard = None
    buttons: List[List[InlineKeyboardButton]] = []

    if search_error:
        results_message_text = search_error
    elif not results:
        results_message_text = loc.SEARCH_NO_RESULTS.format(
            term=search_term_escaped, path=escape_html(str(search_path))
        )
    else:
        results.sort(key=lambda x: (not x["is_dir"], x["name"].lower()))
        count_display = f"{len(results)}"
        limit_reached = len(results) >= SEARCH_RESULTS_LIMIT
        escaped_count_display = escape_html(count_display)
        if limit_reached:
            count_display = f"{SEARCH_RESULTS_LIMIT}+"
            escaped_count_display = escape_html(count_display)
        results_message_text = (loc.SEARCH_FOUND_LIMITED_RESULTS if limit_reached else loc.SEARCH_FOUND_RESULTS).format(
            count=escaped_count_display, count_display=escaped_count_display, limit=SEARCH_RESULTS_LIMIT, term=search_term_escaped
        )
        row: List[InlineKeyboardButton] = []
        for index, result in enumerate(results[:SEARCH_RESULTS_LIMIT]):
            display_name = escape_html(truncate_filename(result['name']))
            callback_prefix = CB_PREFIX_NOOP
            emoji = "❓"
            if result["is_dir"]:
                emoji = "🔗" if result["is_symlink"] else "📁"
                callback_prefix = CB_PREFIX_SRCH_DIR
            elif result["is_file"]:
                emoji = "🔗" if result["is_symlink"] else get_file_emoji(result['name'])
                callback_prefix = CB_PREFIX_SRCH_FILE
            elif result["is_symlink"]:
                emoji = "⚠️🔗"
                callback_prefix = CB_PREFIX_NOOP
            button_text = f"{emoji} {display_name}"
            callback_action = create_callback_data(callback_prefix, index)
            if callback_action:
                row.append(InlineKeyboardButton(button_text, callback_data=callback_action))
            else:
                row.append(InlineKeyboardButton(f"⚠️ {display_name}", callback_data=CB_PREFIX_NOOP))
            if len(row) >= 3:
                buttons.append(row)
                row = []
        if row:
            buttons.append(row)

    back_callback = create_callback_data(CB_PREFIX_SRCH_BACK, "")
    if back_callback:
        buttons.append([InlineKeyboardButton(loc.BUTTON_SEARCH_BACK_TO_BROWSER, callback_data=back_callback)])

    if buttons:
        results_keyboard = InlineKeyboardMarkup(buttons)
    elif not search_error and results:
        results_message_text += f"\n{loc.SEARCH_BUTTON_ERROR}"

    try:
        await context.bot.send_message(
            chat_id=chat_id,
            text=results_message_text,
            reply_markup=results_keyboard,
            parse_mode=constants.ParseMode.HTML
        )
    except Exception as e:
         logger.error(f"Failed to send search results message: {e}")
         try:
             await context.bot.send_message(
                 chat_id=chat_id,
                 text=loc.SEARCH_SEND_RESULT_ERROR,
                 parse_mode=constants.ParseMode.HTML
             )
         except Exception:
             pass

    return ConversationHandler.END


async def cancel_search_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles /cancel command during search by calling the helper."""
    logger.debug(f"/cancel command entered by user {update.effective_user.id}")
    if not is_authorized(update):
        return ConversationHandler.END
    await _perform_search_cancel(update, context, from_callback=False)
    return ConversationHandler.END


# --- Conversation Handler Definition Removed ---
# This is now defined in bot.py to avoid circular imports.


# Made by: Zaky1million 😊♥️
# For contact or project requests: https://t.me/Zaky1million
# Please keep this credit as a sign of respect and support.
# Keep going, developer!
# Every great project starts with a single line of code.
# Believe in your skills and never stop learning.
# You're not just coding – you're creating magic.
# Your future self will thank you for the effort you put in today.
