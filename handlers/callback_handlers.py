# -*- coding: utf-8 -*-
"""
Handlers for callback queries (button presses). Includes the main dispatcher
and specific handlers for navigation, file actions, pagination, and search results.
Uses HTML ParseMode. Includes button-based search cancellation.
"""

import logging
import time
import os
import html
from pathlib import Path
from typing import Optional

import telegram
from telegram import Update, constants, InlineKeyboardButton, InlineKeyboardMarkup # Import button/markup
from telegram.ext import ContextTypes, ConversationHandler
from telegram.error import BadRequest, TimedOut, NetworkError, Forbidden

# Import config, localization, helpers, markup, and other handlers
from config import (
    START_DIRECTORY_PATH, MIN_CALLBACK_INTERVAL,
    CB_PREFIX_NAV_DIR, CB_PREFIX_NAV_FILE, CB_PREFIX_NAV_PAGE, CB_PREFIX_NAV_PARENT,
    CB_PREFIX_NAV_ROOT, CB_PREFIX_SRCH_START, CB_PREFIX_SRCH_BACK, CB_PREFIX_SRCH_DIR,
    CB_PREFIX_SRCH_FILE, CB_PREFIX_SRCH_CANCEL, # Import cancel prefix
    CB_PREFIX_NOOP, ASKING_SEARCH_TERM,
    UD_KEY_VIEW_ITEMS, UD_KEY_SEARCH_RESULTS, UD_KEY_CURRENT_PATH, UD_KEY_CURRENT_PAGE,
    UD_KEY_LAST_CB_TIME, UD_KEY_SEARCH_BASE_PATH,
    UD_KEY_SEARCH_PROMPT_MSG_ID, UD_KEY_SEARCH_FORCE_REPLY_MSG_ID # Import message ID keys
)
import localization as loc
from utils.helpers import (
    is_authorized, get_safe_path, set_safe_path, get_item_from_context, escape_html,
    create_callback_data # Import create_callback_data
)
from utils.markup import generate_file_list_markup
from .common_handlers import display_folder_content
# Import the cancel helper function
from .conversation_handlers import _perform_search_cancel

logger = logging.getLogger(__name__)


# --- File Sending Logic ---
async def send_file_safe(context: ContextTypes.DEFAULT_TYPE, chat_id: int, file_path: Path):
    """Safely sends a file with status updates and error handling (HTML ParseMode)."""
    try:
        if not file_path.is_file():
            logger.error(f"Aᴛᴛᴇᴍᴘᴛ ᴛᴏ sᴇɴᴅ ɴᴏɴ-ғɪʟᴇ ᴏʀ ɴᴏɴ-ᴇxɪsᴛᴇɴᴛ ᴘᴀᴛʜ: {file_path}")
            await context.bot.send_message(
                chat_id=chat_id,
                text=loc.ERROR_SEND_NOT_A_VALID_FILE,
                parse_mode=constants.ParseMode.HTML
            )
            return
    except OSError as e:
        logger.error(f"OS ᴇʀʀᴏʀ ᴄʜᴇᴄᴋɪɴɢ ғɪʟᴇ ʙᴇғᴏʀᴇ sᴇɴᴅ {file_path}: {e}")
        await context.bot.send_message(
            chat_id=chat_id,
            text=loc.ERROR_OS_CHECK_BEFORE_SEND,
            parse_mode=constants.ParseMode.HTML
        )
        return

    file_name = file_path.name
    escaped_file_name = escape_html(file_name)
    status_message = None

    try:
        await context.bot.send_chat_action(
            chat_id=chat_id,
            action=constants.ChatAction.UPLOAD_DOCUMENT
        )
        status_message = await context.bot.send_message(
            chat_id=chat_id,
            text=f"{loc.SENDING_FILE} <code>{escaped_file_name}</code>\n{loc.PLEASE_WAIT}",
            parse_mode=constants.ParseMode.HTML,
            disable_notification=True
        )
        logger.info(f"Sending file {file_path} to chat {chat_id}")

        with open(file_path, 'rb') as file_to_send:
            await context.bot.send_document(
                chat_id=chat_id,
                document=file_to_send,
                filename=file_name,
                read_timeout=180,
                write_timeout=180,
                connect_timeout=60,
                pool_timeout=180,
            )
        logger.info(f"Successfully sent file {file_path} to chat {chat_id}")

    except FileNotFoundError:
        logger.error(f"Fɪʟᴇ ɴᴏᴛ ғᴏᴜɴᴅ: {file_path}")
        await context.bot.send_message(
            chat_id=chat_id,
            text=loc.ERROR_SEND_NOT_FOUND,
            parse_mode=constants.ParseMode.HTML
        )
    except PermissionError:
        logger.error(f"Pᴇʀᴍɪssɪᴏɴ ᴅᴇɴɪᴇᴅ: {file_path}")
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"{loc.ERROR_SEND_PERMISSION}\n<code>{escape_html(str(file_path))}</code>",
            parse_mode=constants.ParseMode.HTML
        )
    except (TimedOut, NetworkError) as e:
        logger.error(f"Network/Timeout: {e}")
        await context.bot.send_message(
            chat_id=chat_id,
            text=loc.ERROR_SEND_NETWORK,
            parse_mode=constants.ParseMode.HTML
        )
    except BadRequest as e:
        error_message = str(e).lower()
        tg_error_msg = escape_html(e.message)
        if "file is too big" in error_message or "request entity too large" in e.message.lower():
            logger.error(f"File too large: {file_path}")
            await context.bot.send_message(
                chat_id=chat_id,
                text=loc.ERROR_SEND_TOO_LARGE,
                parse_mode=constants.ParseMode.HTML
            )
        elif "wrong file identifier" in error_message or "file reference expired" in error_message:
            logger.error(f"Wrong/Expired File ID: {e}")
            await context.bot.send_message(
                chat_id=chat_id,
                text=loc.ERROR_SEND_TG_INTERNAL,
                parse_mode=constants.ParseMode.HTML
            )
        else:
            logger.error(f"BadRequest: {e}")
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"{loc.ERROR_SEND_TG_BADREQUEST} <code>{escaped_file_name}</code>\n<code>{tg_error_msg}</code>",
                parse_mode=constants.ParseMode.HTML
            )
    except Forbidden as e:
        logger.error(f"Forbidden: {e}. Bot blocked?")
    except Exception as e:
        logger.exception(f"Uɴᴇxᴘᴇᴄᴛᴇᴅ ᴇʀʀᴏʀ sending file: {e}")
        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text=loc.ERROR_SEND_UNEXPECTED.format(filename=escaped_file_name),
                parse_mode=constants.ParseMode.HTML
            )
        except Exception:
            pass # Ignore errors sending the final error message
    finally:
        if status_message:
            try:
                await context.bot.delete_message(
                    chat_id=chat_id,
                    message_id=status_message.message_id
                )
            except Exception as del_e:
                logger.warning(f"Could not delete status msg: {del_e}")


# --- Callback Handler Helpers ---

async def handle_item_click(update: Update, context: ContextTypes.DEFAULT_TYPE, prefix: str, index_str: str):
    """Handles clicks on directory or file items in the browser view (UD_KEY_VIEW_ITEMS)."""
    query = update.callback_query
    chat_id = update.effective_chat.id

    try:
        item_index = int(index_str)
    except ValueError:
        logger.error(f"Iɴᴠᴀʟɪᴅ ɪɴᴅᴇx: {prefix}{index_str}")
        await query.answer(loc.INVALID_INDEX_ERROR, show_alert=True)
        return

    item = get_item_from_context(context, UD_KEY_VIEW_ITEMS, item_index)
    if not item:
        logger.warning(f"Iᴛᴇᴍ ɴᴏᴛ ғᴏᴜɴᴅ index {item_index}")
        await query.answer(loc.STALE_DATA_ERROR, show_alert=True)
        return

    target_path_str = item.get("path")
    if not target_path_str:
        logger.error(f"Iᴛᴇᴍ {item_index} ʜᴀs ɴᴏ ᴘᴀᴛʜ")
        await query.answer(loc.ERROR_ITEM_PATH_MISSING, show_alert=True)
        return

    try:
        target_path = Path(target_path_str)
        if not (target_path.resolve() == START_DIRECTORY_PATH or str(target_path.resolve()).startswith(str(START_DIRECTORY_PATH) + os.sep)):
            raise ValueError("Path outside allowed dir")
    except Exception as path_err:
        logger.error(f"Invalid path index {item_index}: '{target_path_str}'. {path_err}")
        await query.answer(loc.ERROR_ITEM_PATH_MISSING, show_alert=True)
        return

    item_name = item.get('name', 'Unknown')
    escaped_item_name = escape_html(item_name)

    if prefix == CB_PREFIX_NAV_DIR:
        if not item.get('is_dir', False):
            logger.warning(f"Not a dir: {target_path}")
            await query.answer(loc.ERROR_NOT_A_FOLDER, show_alert=True)
            return
        await query.answer(loc.BUTTON_OPENING_FOLDER.format(name=escaped_item_name))
        await display_folder_content(update, context, target_path, page=0, edit_message=True)
    elif prefix == CB_PREFIX_NAV_FILE:
        if not item.get('is_file', False):
            logger.warning(f"Not a file: {target_path}")
            await query.answer(loc.ERROR_NOT_A_FILE, show_alert=True)
            return
        await query.answer(loc.BUTTON_PREPARING_FILE.format(name=escaped_item_name))
        await send_file_safe(context, chat_id, target_path)

async def handle_pagination(update: Update, context: ContextTypes.DEFAULT_TYPE, page_str: str):
    """Handles clicks on pagination buttons (CB_PREFIX_NAV_PAGE)."""
    query = update.callback_query
    try:
        page = int(page_str)
        assert page >= 0
    except (ValueError, AssertionError):
        logger.error(f"Iɴᴠᴀʟɪᴅ ᴘᴀɢᴇ number: {page_str}")
        await query.answer(loc.INVALID_INDEX_ERROR, show_alert=True)
        return

    await query.answer(loc.BUTTON_LOADING_PAGE.format(page=page + 1))
    current_path = get_safe_path(context)
    logger.info(f"Paginating to page {page} for path: {current_path}")
    await display_folder_content(update, context, current_path, page=page, edit_message=True)

async def handle_parent_nav(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles click on the 'Back' (Parent) button (CB_PREFIX_NAV_PARENT)."""
    query = update.callback_query
    current_path = get_safe_path(context)

    if current_path != START_DIRECTORY_PATH:
        await query.answer(loc.BUTTON_GO_UP)
        await display_folder_content(
            update=update,
            context=context,
            target_path_str=current_path.parent,
            page=0,
            edit_message=True
        )
    else:
        logger.debug("Parent nav at root")
        await query.answer(loc.ALERT_ALREADY_ROOT, show_alert=True)

async def handle_root_nav(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles click on the 'Root' button (CB_PREFIX_NAV_ROOT)."""
    query = update.callback_query
    await query.answer(loc.BUTTON_GO_ROOT)
    await display_folder_content(
        update=update,
        context=context,
        target_path_str=START_DIRECTORY_PATH,
        page=0,
        edit_message=True
    )

async def handle_search_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Optional[int]:
    """
    Initiates the search conversation (HTML). Sends two messages:
    1. Prompt with Cancel button (emoji only).
    2. Simple message with ForceReply.
    """
    query = update.callback_query
    current_path = get_safe_path(context)
    chat_id = query.message.chat_id
    user_id = update.effective_user.id

    context.user_data[UD_KEY_SEARCH_BASE_PATH] = str(current_path)
    context.user_data.pop(UD_KEY_SEARCH_PROMPT_MSG_ID, None)
    context.user_data.pop(UD_KEY_SEARCH_FORCE_REPLY_MSG_ID, None)
    logger.info(f"User {user_id} initiated search in {current_path}")

    await query.answer(loc.SEARCH_STARTING)

    cancel_callback_data = create_callback_data(CB_PREFIX_SRCH_CANCEL, "")
    if not cancel_callback_data:
        logger.error("Failed to create callback data for search cancel button!")
        await context.bot.send_message(
            chat_id=chat_id,
            text="Error: Could not create cancel button."
        )
        return ConversationHandler.END # Abort if cancel button fails

    cancel_button = InlineKeyboardButton("⛔️", callback_data=cancel_callback_data)
    cancel_keyboard = InlineKeyboardMarkup([[cancel_button]])

    escaped_path_str = escape_html(str(current_path))
    prompt_text = (
        f"{loc.SEARCH_PROMPT}\n<code>{escaped_path_str}</code>\n"
        f"{loc.SEARCH_PROMPT_HINT}"
    )

    prompt_cancel_msg = None
    force_reply_msg = None

    try:
        try:
            await query.delete_message()
        except Exception as del_e:
            logger.warning(f"Could not delete browser message {query.message.message_id}: {del_e}")

        # Send Message 1: Prompt + Cancel Button
        prompt_cancel_msg = await context.bot.send_message(
            chat_id=chat_id,
            text=prompt_text,
            parse_mode=constants.ParseMode.HTML,
            reply_markup=cancel_keyboard
        )
        context.user_data[UD_KEY_SEARCH_PROMPT_MSG_ID] = prompt_cancel_msg.message_id
        logger.debug(f"Search prompt/cancel message sent, ID: {prompt_cancel_msg.message_id}")

        # Send Message 2: Simple ForceReply prompt
        force_reply_msg = await context.bot.send_message(
            chat_id=chat_id,
            text="↪️ Reply to this message with your search term:",
            reply_markup=telegram.ForceReply(
                selective=True,
                input_field_placeholder=loc.SEARCH_INPUT_PLACEHOLDER
            )
        )
        context.user_data[UD_KEY_SEARCH_FORCE_REPLY_MSG_ID] = force_reply_msg.message_id
        logger.debug(f"Search ForceReply message sent, ID: {force_reply_msg.message_id}")

        return ASKING_SEARCH_TERM # Proceed to wait for user's text reply

    except Forbidden:
        logger.error(f"Cannot send search messages to chat {chat_id}: Forbidden.")
        if prompt_cancel_msg:
            try:
                await context.bot.delete_message(chat_id, prompt_cancel_msg.message_id)
            except Exception:
                pass
        if force_reply_msg:
            try:
                await context.bot.delete_message(chat_id, force_reply_msg.message_id)
            except Exception:
                pass
        await query.answer(loc.SEARCH_ERROR_SEND_PROMPT, show_alert=True)
        return ConversationHandler.END
    except Exception as e:
        logger.error(f"Failed to start search or send prompt messages: {e}", exc_info=True)
        if prompt_cancel_msg:
            try:
                await context.bot.delete_message(chat_id, prompt_cancel_msg.message_id)
            except Exception:
                pass
        if force_reply_msg:
            try:
                await context.bot.delete_message(chat_id, force_reply_msg.message_id)
            except Exception:
                pass
        await query.answer(loc.SEARCH_ERROR_STARTING, show_alert=True)
        return ConversationHandler.END

async def handle_search_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles click on 'Back to Browser' from search results (CB_PREFIX_SRCH_BACK)."""
    query = update.callback_query
    await query.answer(loc.BUTTON_SEARCH_RETURN_BROWSER)
    original_search_path_str = context.user_data.get(UD_KEY_SEARCH_BASE_PATH)
    context.user_data.pop(UD_KEY_SEARCH_RESULTS, None)

    if not original_search_path_str:
        logger.warning("Search base path not found")
        await query.answer(loc.ALERT_SEARCH_CANNOT_FIND_ORIGINAL_PATH, show_alert=True)
        original_search_path = START_DIRECTORY_PATH
    else:
        original_search_path = Path(original_search_path_str)

    await display_folder_content(
        update=update,
        context=context,
        target_path_str=original_search_path,
        page=0,
        edit_message=False
    )

async def handle_search_result_click(update: Update, context: ContextTypes.DEFAULT_TYPE, prefix: str, index_str: str):
    """Handles clicks on items listed in search results (UD_KEY_SEARCH_RESULTS)."""
    query = update.callback_query
    chat_id = update.effective_chat.id

    try:
        result_index = int(index_str)
    except ValueError:
        logger.error(f"Iɴᴠᴀʟɪᴅ search index: {prefix}{index_str}")
        await query.answer(loc.SEARCH_INVALID_INDEX_ERROR, show_alert=True)
        return

    result_item = get_item_from_context(context, UD_KEY_SEARCH_RESULTS, result_index)
    if not result_item:
        logger.warning(f"Search result {result_index} not found")
        await query.answer(loc.SEARCH_STALE_RESULTS_ERROR, show_alert=True)
        try:
            await query.delete_message()
        except Exception:
            pass
        return

    target_path_str = result_item.get("path")
    if not target_path_str:
        logger.error(f"Search result {result_index} ʜᴀs ɴᴏ ᴘᴀᴛʜ")
        await query.answer(loc.SEARCH_RESULT_PATH_MISSING_ERROR, show_alert=True)
        return

    try:
        target_path = Path(target_path_str)
        if not (target_path.resolve() == START_DIRECTORY_PATH or str(target_path.resolve()).startswith(str(START_DIRECTORY_PATH) + os.sep)):
            raise ValueError("Search path outside allowed dir")
    except Exception as path_err:
        logger.error(f"Invalid search path index {result_index}: '{target_path_str}'. {path_err}")
        await query.answer(loc.SEARCH_RESULT_PATH_MISSING_ERROR, show_alert=True)
        return

    item_name = result_item.get('name', 'Unknown')
    escaped_item_name = escape_html(item_name)

    if prefix == CB_PREFIX_SRCH_DIR:
        if not result_item.get('is_dir'):
            logger.warning(f"Search result not dir: {target_path}")
            await query.answer(loc.SEARCH_RESULT_NOT_FOLDER, show_alert=True)
            return
        await query.answer(loc.SEARCH_OPENING_RESULT.format(name=escaped_item_name))
        context.user_data.pop(UD_KEY_SEARCH_RESULTS, None)
        await display_folder_content(
            update=update,
            context=context,
            target_path_str=target_path,
            page=0,
            edit_message=False
        )
    elif prefix == CB_PREFIX_SRCH_FILE:
        if not result_item.get('is_file'):
            logger.warning(f"Search result not file: {target_path}")
            await query.answer(loc.SEARCH_RESULT_NOT_FILE, show_alert=True)
            return
        await query.answer(loc.SEARCH_PREPARING_RESULT.format(name=escaped_item_name))
        context.user_data.pop(UD_KEY_SEARCH_RESULTS, None)
        try:
            await query.delete_message()
        except Exception as del_e:
            logger.warning(f"Could not delete search result msg: {del_e}")
        await send_file_safe(context, chat_id, target_path)

# --- Main Callback Query Dispatcher ---

async def main_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Optional[int]:
    """Handles all button clicks (CallbackQuery). Uses HTML ParseMode."""
    query = update.callback_query
    if not query or not query.data:
        logger.warning("CallbackQuery without data.")
        return None
    if not is_authorized(update):
        logger.warning(f"Unauthorized CBQ from {update.effective_user.id}")
        await query.answer(loc.ACCESS_DENIED, show_alert=True)
        return None

    now = time.monotonic()
    last_cb_time = context.user_data.get(UD_KEY_LAST_CB_TIME, 0)
    is_rapid_click = (now - last_cb_time) < MIN_CALLBACK_INTERVAL
    context.user_data[UD_KEY_LAST_CB_TIME] = now
    callback_data = query.data
    user_id = update.effective_user.id
    logger.debug(f"Callback received: User={user_id}, Data='{callback_data}', Rapid={is_rapid_click}")

    answer_text = None
    answer_show_alert = False
    next_state = None

    try:
        if callback_data == CB_PREFIX_NOOP:
            if is_rapid_click:
                try:
                    current_path = get_safe_path(context)
                    current_page = context.user_data.get(UD_KEY_CURRENT_PAGE, 0)
                    answer_text = loc.ALERT_CALLBACK_CONTEXT.format(
                        name=escape_html(current_path.name), page=current_page + 1
                    )
                    answer_show_alert = True
                except Exception as e:
                    logger.warning(f"Err NOOP ctx: {e}")
                    answer_text = None # Fallback if error getting context
                    answer_show_alert = False
            else:
                answer_text = None # Silent ack for non-rapid click

        elif callback_data == CB_PREFIX_NAV_PARENT:
            await handle_parent_nav(update, context)
            return None # Handler manages answer/display
        elif callback_data == CB_PREFIX_NAV_ROOT:
            await handle_root_nav(update, context)
            return None # Handler manages answer/display
        elif callback_data == CB_PREFIX_SRCH_START:
            next_state = await handle_search_start(update, context)
            return next_state # Handler manages answer/display and returns state
        elif callback_data == CB_PREFIX_SRCH_BACK:
            await handle_search_back(update, context)
            return None # Handler manages answer/display
        elif callback_data == CB_PREFIX_SRCH_CANCEL:
            logger.debug(f"Search cancel button pressed by user {user_id}")
            await query.answer("⛔️ Cancelling...")
            await _perform_search_cancel(update, context, from_callback=True)
            return None # Cancel helper manages display, don't transition state here

        elif ':' in callback_data:
            prefix, payload = callback_data.split(':', 1)
            prefix_with_colon = prefix + ":"
            if prefix_with_colon == CB_PREFIX_NAV_DIR or prefix_with_colon == CB_PREFIX_NAV_FILE:
                await handle_item_click(update, context, prefix_with_colon, payload)
                return None # Handler manages answer/display
            elif prefix_with_colon == CB_PREFIX_NAV_PAGE:
                await handle_pagination(update, context, payload)
                return None # Handler manages answer/display
            elif prefix_with_colon == CB_PREFIX_SRCH_DIR or prefix_with_colon == CB_PREFIX_SRCH_FILE:
                await handle_search_result_click(update, context, prefix_with_colon, payload)
                return None # Handler manages answer/display
            else:
                logger.warning(f"Unhandled CBQ prefix: {prefix_with_colon}")
                answer_text = loc.ACTION_UNKNOWN
                answer_show_alert = True
        else:
            logger.warning(f"Malformed CBQ data: '{callback_data}'")
            answer_text = loc.INVALID_FORMAT
            answer_show_alert = True

        # --- Execute Default/Fallback Answer ---
        if answer_text is not None or answer_show_alert:
            await query.answer(text=answer_text, show_alert=answer_show_alert)
        elif not next_state: # Provide silent ack if not handled and not transitioning state
            try:
                await query.answer()
            except BadRequest: # Ignore "Query is too old" or similar if already answered
                pass
            except Exception as e:
                logger.warning(f"Err fallback answer: {e}")

        return next_state # Return None unless starting search

    except Exception as e:
        logger.exception(f"Eʀʀᴏʀ processing CBQ '{callback_data}': {e}")
        try:
            await query.answer(loc.INTERNAL_ERROR, show_alert=True)
        except Exception as answer_e:
            logger.error(f"Failed answer after CBQ error: {answer_e}")
        return None


# Made by: Zaky1million 😊♥️
# For contact or project requests: https://t.me/Zaky1million
# Please keep this credit as a sign of respect and support.
# Keep going, developer!
# Every great project starts with a single line of code.
# Believe in your skills and never stop learning.
# You're not just coding – you're creating magic.
# Your future self will thank you for the effort you put in today.
