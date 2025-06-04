# -*- coding: utf-8 -*-
"""
Handlers for callback queries (button presses).
"""
import logging
import time
import os
import html as pyhtml
from pathlib import Path
from typing import Optional

from telegram import Update, constants, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.error import BadRequest, TimedOut, NetworkError, Forbidden

from config import (
    START_DIRECTORY_PATH, MIN_CALLBACK_INTERVAL, BOT_IMAGE_URL,
    CB_PREFIX_NAV_DIR, CB_PREFIX_NAV_FILE, CB_PREFIX_NAV_PAGE, CB_PREFIX_NAV_PARENT,
    CB_PREFIX_NAV_ROOT, CB_PREFIX_SRCH_BACK, CB_PREFIX_SRCH_DIR,
    CB_PREFIX_SRCH_FILE, CB_PREFIX_NOOP, CB_PREFIX_ACCEPT_USER, CB_PREFIX_REJECT_USER,
    CB_PREFIX_DISMISS_ADMIN_MSG,
    UD_KEY_VIEW_ITEMS, UD_KEY_SEARCH_RESULTS, UD_KEY_CURRENT_PATH, UD_KEY_CURRENT_PAGE,
    UD_KEY_LAST_CB_TIME, UD_KEY_SEARCH_BASE_PATH, UD_KEY_CURRENT_MESSAGE_ID, ADMIN_USER_ID
)
import localization as loc
from utils.auth_utils import is_authorized, add_authorized_user # <<<--- مصدر is_authorized الصحيح
from utils.helpers import (
    # is_authorized removed from here
    get_safe_path, set_safe_path, get_item_from_context, escape_html,
    create_callback_data, send_or_edit_photo_message, handle_unauthorized_access
)
from .common_handlers import display_folder_content

logger = logging.getLogger(__name__)

# ... (باقي الكود بتاع الملف ده كما هو من المرة السابقة، ما عدا تعديل الـ import فوق) ...
# والتعديل جوه main_callback_handler لاستخدام is_authorized مباشرة:

async def main_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.data:
        logger.warning("CallbackQuery received without data attribute.")
        return
    
    user_who_clicked = query.from_user
    
    is_admin_specific_cb = query.data.startswith(CB_PREFIX_ACCEPT_USER) or \
                           query.data.startswith(CB_PREFIX_REJECT_USER) or \
                           query.data.startswith(CB_PREFIX_DISMISS_ADMIN_MSG)

    # Use the directly imported 'is_authorized' from auth_utils
    user_is_authorized_for_bot = await is_authorized(update, context)

    if not user_is_authorized_for_bot:
        # Allow admin to press admin-specific buttons even if not in dynamic list (should be caught by user_is_authorized_for_bot if ADMIN_USER_ID matches)
        # This check is more about a non-admin, non-authorized user trying admin buttons.
        # The primary authorization handles "is this user allowed to use the bot AT ALL".
        # The secondary check here is "is THIS specific admin action allowed for THIS user" (which is stricter for admin buttons).
        if is_admin_specific_cb and user_who_clicked.id != ADMIN_USER_ID:
             await query.answer("Tʜɪs ᴀᴄᴛɪᴏɴ ɪs ғᴏʀ Aᴅᴍɪɴs ᴏɴʟʏ.", show_alert=True)
             return
        elif not is_admin_specific_cb: # Any other button by a non-authorized user
             await handle_unauthorized_access(update, context)
             try: await query.answer(loc.ACCESS_DENIED, show_alert=True)
             except BadRequest: pass
             return
    
    # ... (باقي دالة main_callback_handler)
# --- File Sending Logic --- (كاملة كما في الردود السابقة)
async def send_file_safe(context: ContextTypes.DEFAULT_TYPE, chat_id: int, file_path: Path):
    try:
        if not file_path.is_file():
            logger.error(f"Attempt to send non-file or non-existent path: {file_path}")
            await context.bot.send_message(
                chat_id=chat_id, text=loc.ERROR_SEND_NOT_A_VALID_FILE, parse_mode=constants.ParseMode.HTML
            )
            return
    except OSError as e:
        logger.error(f"OS error checking file {file_path}: {e}")
        await context.bot.send_message(chat_id=chat_id, text=loc.ERROR_OS_CHECK_BEFORE_SEND, parse_mode=constants.ParseMode.HTML)
        return

    file_name = file_path.name
    escaped_file_name_html = escape_html(file_name)
    status_message_obj = None

    try:
        status_message_text = f"{loc.SENDING_FILE} <code>{escaped_file_name_html}</code>\n{loc.PLEASE_WAIT}"
        status_message_obj = await context.bot.send_message(
            chat_id=chat_id, text=status_message_text,
            parse_mode=constants.ParseMode.HTML, disable_notification=True
        )
        await context.bot.send_chat_action(chat_id=chat_id, action=constants.ChatAction.UPLOAD_DOCUMENT)
        logger.info(f"Sending file {file_path} to chat {chat_id}")

        with open(file_path, 'rb') as file_to_send:
            await context.bot.send_document(
                chat_id=chat_id, document=file_to_send, filename=file_name,
                read_timeout=180, write_timeout=180, connect_timeout=60, pool_timeout=180,
            )
        logger.info(f"Successfully sent file {file_path} to chat {chat_id}")

    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        await context.bot.send_message(chat_id=chat_id, text=loc.ERROR_SEND_NOT_FOUND, parse_mode=constants.ParseMode.HTML)
    except PermissionError:
        logger.error(f"Permission denied: {file_path}")
        await context.bot.send_message(
            chat_id=chat_id, text=f"{loc.ERROR_SEND_PERMISSION}\n<code>{escape_html(str(file_path))}</code>",
            parse_mode=constants.ParseMode.HTML
        )
    except (TimedOut, NetworkError) as e:
        logger.error(f"Network/Timeout sending file: {e}")
        await context.bot.send_message(chat_id=chat_id, text=loc.ERROR_SEND_NETWORK, parse_mode=constants.ParseMode.HTML)
    except BadRequest as e:
        error_message_lower = str(e).lower()
        if "file is too big" in error_message_lower or "request entity too large" in e.message.lower():
            logger.error(f"File too large: {file_path}")
            await context.bot.send_message(chat_id=chat_id, text=loc.ERROR_SEND_TOO_LARGE, parse_mode=constants.ParseMode.HTML)
        else:
            logger.error(f"BadRequest sending file: {e}")
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"{loc.ERROR_SEND_TG_BADREQUEST}<code>{escaped_file_name_html}</code>\n<code>{escape_html(e.message)}</code>",
                parse_mode=constants.ParseMode.HTML
            )
    except Forbidden as e_forbidden:
         logger.error(f"Forbidden error sending file to {chat_id}: {e_forbidden}. Bot blocked or no permission?")
    except Exception as e:
        logger.exception(f"Unexpected error sending file {file_path}: {e}")
        try:
            await context.bot.send_message(
                chat_id=chat_id, text=loc.ERROR_SEND_UNEXPECTED.format(filename=escaped_file_name_html),
                parse_mode=constants.ParseMode.HTML
            )
        except Exception: pass
    finally:
        if status_message_obj:
            try:
                await context.bot.delete_message(chat_id=chat_id, message_id=status_message_obj.message_id)
            except Exception as del_e:
                logger.warning(f"Could not delete file sending status message: {del_e}")

# --- Callback Handler Helpers --- (كاملة كما في الردود السابقة)
async def handle_item_click(update: Update, context: ContextTypes.DEFAULT_TYPE, prefix: str, index_str: str):
    query = update.callback_query
    chat_id = update.effective_chat.id

    try:
        item_index = int(index_str)
    except ValueError:
        logger.error(f"Invalid item index: {prefix}{index_str}")
        await query.answer(loc.INVALID_INDEX_ERROR, show_alert=True)
        return

    item = get_item_from_context(context, UD_KEY_VIEW_ITEMS, item_index)
    if not item:
        logger.warning(f"Item not found at index {item_index} for CB {prefix}{index_str}")
        await query.answer(loc.STALE_DATA_ERROR, show_alert=True)
        return

    target_path_str = item.get("path")
    if not target_path_str:
        logger.error(f"Item {item_index} has no path attribute.")
        await query.answer(loc.ERROR_ITEM_PATH_MISSING, show_alert=True)
        return
    
    try:
        target_path = Path(target_path_str).resolve()
        if not (target_path == START_DIRECTORY_PATH or \
                str(target_path).startswith(str(START_DIRECTORY_PATH) + os.sep)):
            logger.error(f"SECURITY: Item path '{target_path_str}' (resolves to '{target_path}') is outside allowed root.")
            await query.answer(loc.ERROR_PERMISSION_DENIED.splitlines()[0], show_alert=True)
            return
        
        if item.get("is_symlink") and not target_path.exists():
            logger.warning(f"Symlink target does not exist: {target_path_str}")
            await query.answer("🔗 Eʀʀᴏʀ: Lɪɴᴋᴇᴅ ɪᴛᴇᴍ ɴᴏᴛ ғᴏᴜɴᴅ.", show_alert=True)
            return

    except Exception as path_err:
        logger.error(f"Error resolving path for item {item_index} ('{target_path_str}'): {path_err}")
        await query.answer(loc.ERROR_ITEM_PATH_MISSING, show_alert=True)
        return

    item_name = item.get('name', 'Unknown')
    escaped_item_name = escape_html(item_name)

    if prefix == CB_PREFIX_NAV_DIR:
        if not item.get('is_dir', False):
            logger.warning(f"Not a directory: {target_path_str} (Item marked as is_dir: {item.get('is_dir')})")
            await query.answer(loc.ERROR_NOT_A_FOLDER, show_alert=True)
            return
        await query.answer(loc.BUTTON_OPENING_FOLDER.format(name=escaped_item_name))
        await display_folder_content(update, context, target_path, page=0, edit_message=True)
    elif prefix == CB_PREFIX_NAV_FILE:
        if not item.get('is_file', False):
            logger.warning(f"Not a file: {target_path_str} (Item marked as is_file: {item.get('is_file')})")
            await query.answer(loc.ERROR_NOT_A_FILE, show_alert=True)
            return
        await query.answer(loc.BUTTON_PREPARING_FILE.format(name=escaped_item_name))
        await send_file_safe(context, chat_id, target_path)

async def handle_pagination(update: Update, context: ContextTypes.DEFAULT_TYPE, page_str: str):
    query = update.callback_query
    try:
        page = int(page_str)
        assert page >= 0
    except (ValueError, AssertionError):
        logger.error(f"Invalid page number: {page_str}")
        await query.answer(loc.INVALID_INDEX_ERROR, show_alert=True)
        return

    await query.answer(loc.BUTTON_LOADING_PAGE.format(page=page + 1))
    current_path = get_safe_path(context)
    await display_folder_content(update, context, current_path, page=page, edit_message=True)

async def handle_parent_nav(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    current_path = get_safe_path(context)

    if current_path != START_DIRECTORY_PATH:
        await query.answer(loc.BUTTON_GO_UP)
        await display_folder_content(update, context, current_path.parent, page=0, edit_message=True)
    else:
        await query.answer(loc.ALERT_ALREADY_ROOT, show_alert=True)

async def handle_root_nav(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer(loc.BUTTON_GO_ROOT)
    await display_folder_content(update, context, START_DIRECTORY_PATH, page=0, edit_message=True)

async def handle_search_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer(loc.BUTTON_SEARCH_RETURN_BROWSER)
    
    context.user_data.pop(UD_KEY_SEARCH_RESULTS, None)
    original_search_path_str = context.user_data.pop(UD_KEY_SEARCH_BASE_PATH, None)
    
    target_path_for_display = START_DIRECTORY_PATH
    if original_search_path_str:
        try:
            resolved_path = Path(original_search_path_str).resolve()
            if resolved_path == START_DIRECTORY_PATH or str(resolved_path).startswith(str(START_DIRECTORY_PATH) + os.sep):
                target_path_for_display = resolved_path
        except Exception:
            logger.warning(f"Could not resolve search base path '{original_search_path_str}', defaulting to root.")
    
    set_safe_path(context, target_path_for_display)
    await display_folder_content(update, context, target_path_for_display, page=0, edit_message=False)

async def handle_search_result_click(update: Update, context: ContextTypes.DEFAULT_TYPE, prefix: str, index_str: str):
    query = update.callback_query
    chat_id = update.effective_chat.id

    try:
        result_index = int(index_str)
    except ValueError:
        logger.error(f"Invalid search result index: {prefix}{index_str}")
        await query.answer(loc.SEARCH_INVALID_INDEX_ERROR, show_alert=True)
        return

    result_item = get_item_from_context(context, UD_KEY_SEARCH_RESULTS, result_index)
    if not result_item:
        logger.warning(f"Search result {result_index} not found for CB {prefix}{index_str}")
        await query.answer(loc.SEARCH_STALE_RESULTS_ERROR, show_alert=True)
        if query.message:
            try: await query.delete_message()
            except Exception: pass
        return

    target_path_str = result_item.get("path")
    if not target_path_str:
        logger.error(f"Search result {result_index} has no path.")
        await query.answer(loc.SEARCH_RESULT_PATH_MISSING_ERROR, show_alert=True)
        return

    try:
        target_path = Path(target_path_str)
        if not (target_path.resolve() == START_DIRECTORY_PATH or \
                str(target_path.resolve()).startswith(str(START_DIRECTORY_PATH) + os.sep)):
             logger.error(f"SECURITY: Search result path '{target_path_str}' is outside allowed root.")
             await query.answer(loc.ERROR_PERMISSION_DENIED.splitlines()[0], show_alert=True)
             return
        if result_item.get("is_symlink") and not target_path.exists():
            logger.warning(f"Search result symlink target does not exist: {target_path_str}")
            await query.answer("🔗 Eʀʀᴏʀ: Lɪɴᴋᴇᴅ ɪᴛᴇᴍ ɴᴏᴛ ғᴏᴜɴᴅ.", show_alert=True)
            return
            
    except Exception as path_err:
        logger.error(f"Error resolving path for search result {result_index} ('{target_path_str}'): {path_err}")
        await query.answer(loc.SEARCH_RESULT_PATH_MISSING_ERROR, show_alert=True)
        return

    item_name = result_item.get('name', 'Unknown')
    escaped_item_name = escape_html(item_name)

    if query.message:
        try:
            await query.delete_message()
            context.user_data.pop(UD_KEY_CURRENT_MESSAGE_ID, None)
        except Exception as del_e:
            logger.warning(f"Could not delete search results message {query.message.message_id}: {del_e}")
    
    context.user_data.pop(UD_KEY_SEARCH_RESULTS, None)
    context.user_data.pop(UD_KEY_SEARCH_BASE_PATH, None)

    if prefix == CB_PREFIX_SRCH_DIR:
        if not result_item.get('is_dir'):
            logger.warning(f"Search result not a directory: {target_path_str}")
            await query.answer(loc.SEARCH_RESULT_NOT_FOLDER, show_alert=True)
            return
        await query.answer(loc.SEARCH_OPENING_RESULT.format(name=escaped_item_name))
        await display_folder_content(update, context, target_path, page=0, edit_message=False)
    elif prefix == CB_PREFIX_SRCH_FILE:
        if not result_item.get('is_file'):
            logger.warning(f"Search result not a file: {target_path_str}")
            await query.answer(loc.SEARCH_RESULT_NOT_FILE, show_alert=True)
            return
        await query.answer(loc.SEARCH_PREPARING_RESULT.format(name=escaped_item_name))
        await send_file_safe(context, chat_id, target_path)

async def handle_admin_action(update: Update, context: ContextTypes.DEFAULT_TYPE, prefix: str, user_id_to_manage_str: str):
    query = update.callback_query
    admin_user_from_query = query.from_user

    if admin_user_from_query.id != ADMIN_USER_ID:
        logger.warning(f"Non-admin {admin_user_from_query.id} tried to use admin callback {prefix}{user_id_to_manage_str}")
        await query.answer("Tʜɪs ᴀᴄᴛɪᴏɴ ɪs ғᴏʀ Aᴅᴍɪɴs ᴏɴʟʏ.", show_alert=True)
        return

    try:
        user_id_to_manage = int(user_id_to_manage_str)
    except ValueError:
        logger.error(f"Invalid user_id in admin callback: {user_id_to_manage_str}")
        await query.answer("Eʀʀᴏʀ: Iɴᴠᴀʟɪᴅ ᴜsᴇʀ ID ɪɴ ᴄᴀʟʟʙᴀᴄᴋ.", show_alert=True)
        return

    if user_id_to_manage == ADMIN_USER_ID:
        await query.answer(loc.ADMIN_CANNOT_SELF_MODIFY, show_alert=True)
        return

    managed_user_mention_html = f"<a href='tg://user?id={user_id_to_manage}'>{user_id_to_manage}</a>"

    if prefix == CB_PREFIX_ACCEPT_USER:
        user_added = add_authorized_user(context, user_id_to_manage) # from auth_utils
        if user_added:
            await query.answer(f"Usᴇʀ {user_id_to_manage} ᴀᴄᴄᴇᴘᴛᴇᴅ.")
            edited_admin_text = loc.ADMIN_USER_ACCEPTED_NOTIFICATION.format(user_mention=managed_user_mention_html, user_id=user_id_to_manage)
            
            try:
                await context.bot.send_photo(
                    chat_id=user_id_to_manage,
                    photo=BOT_IMAGE_URL,
                    caption=loc.USER_NOW_AUTHORIZED.format(user_mention=managed_user_mention_html),
                    parse_mode=constants.ParseMode.HTML
                )
            except Exception as e_notify:
                logger.error(f"Failed to notify user {user_id_to_manage} of authorization: {e_notify}")
        else:
            if await is_authorized(Update(0, effective_user=type('obj', (), {'id': user_id_to_manage})()), context):
                await query.answer(f"Usᴇʀ {user_id_to_manage} ᴡᴀs ᴀʟʀᴇᴀᴅʏ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ.")
                edited_admin_text = loc.ADMIN_USER_ALREADY_ACCEPTED_NOTIFICATION.format(user_mention=managed_user_mention_html, user_id=user_id_to_manage)
            else:
                await query.answer(loc.ERROR_ADDING_USER, show_alert=True)
                edited_admin_text = loc.ERROR_ADDING_USER + f" (Usᴇʀ {user_id_to_manage})"
        
        dismiss_button = InlineKeyboardButton(loc.BUTTON_DISMISS_ADMIN_MSG, callback_data=create_callback_data(CB_PREFIX_DISMISS_ADMIN_MSG, user_id_to_manage))
        if query.message:
            try:
                await context.bot.edit_message_caption(
                    chat_id=query.message.chat_id, message_id=query.message.message_id,
                    caption=edited_admin_text, reply_markup=InlineKeyboardMarkup([[dismiss_button]]),
                    parse_mode=constants.ParseMode.HTML
                )
            except Exception as e_edit_admin: logger.error(f"Failed to edit admin msg on accept/already_auth: {e_edit_admin}")

    elif prefix == CB_PREFIX_REJECT_USER:
        await query.answer(f"Usᴇʀ {user_id_to_manage} ʀᴇᴊᴇᴄᴛᴇᴅ (ɴᴏ ᴄʜᴀɴɢᴇ ᴍᴀᴅᴇ).")
        edited_admin_text = loc.ADMIN_USER_REJECTED_NOTIFICATION.format(user_mention=managed_user_mention_html, user_id=user_id_to_manage)
        dismiss_button = InlineKeyboardButton(loc.BUTTON_DISMISS_ADMIN_MSG, callback_data=create_callback_data(CB_PREFIX_DISMISS_ADMIN_MSG, user_id_to_manage))
        if query.message:
            try:
                await context.bot.edit_message_caption(
                    chat_id=query.message.chat_id, message_id=query.message.message_id,
                    caption=edited_admin_text, reply_markup=InlineKeyboardMarkup([[dismiss_button]]),
                    parse_mode=constants.ParseMode.HTML
                )
            except Exception as e_edit_admin: logger.error(f"Failed to edit admin msg on reject: {e_edit_admin}")

    elif prefix == CB_PREFIX_DISMISS_ADMIN_MSG:
        await query.answer("Nᴏᴛɪғɪᴄᴀᴛɪᴏɴ ᴅɪsᴍɪssᴇᴅ.")
        if query.message:
            try:
                await query.delete_message()
            except Exception as e_del:
                logger.warning(f"Could not delete dismissed admin message: {e_del}")

# --- Main Callback Query Dispatcher ---
async def main_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.data:
        logger.warning("CallbackQuery received without data attribute.")
        return
    
    user_who_clicked = query.from_user
    
    is_admin_specific_cb = query.data.startswith(CB_PREFIX_ACCEPT_USER) or \
                           query.data.startswith(CB_PREFIX_REJECT_USER) or \
                           query.data.startswith(CB_PREFIX_DISMISS_ADMIN_MSG)

    user_is_authorized_for_bot = await is_authorized(update, context) # <<<--- Uses is_authorized from auth_utils

    if not user_is_authorized_for_bot:
        if is_admin_specific_cb and user_who_clicked.id != ADMIN_USER_ID:
             await query.answer("Tʜɪs ᴀᴄᴛɪᴏɴ ɪs ғᴏʀ Aᴅᴍɪɴs ᴏɴʟʏ.", show_alert=True)
             return
        elif not is_admin_specific_cb:
             await handle_unauthorized_access(update, context)
             try: await query.answer(loc.ACCESS_DENIED, show_alert=True)
             except BadRequest: pass
             return
    
    now = time.monotonic()
    last_cb_time = context.user_data.get(UD_KEY_LAST_CB_TIME, 0)
    if (now - last_cb_time) < MIN_CALLBACK_INTERVAL:
        logger.debug(f"Rapid callback click from {user_who_clicked.id} blocked: {query.data}")
        try:
            current_path_for_alert = get_safe_path(context)
            current_page_for_alert = context.user_data.get(UD_KEY_CURRENT_PAGE, 0)
            alert_text = loc.ALERT_CALLBACK_CONTEXT.format(
                name=escape_html(current_path_for_alert.name),
                page=current_page_for_alert + 1
            )
            await query.answer(alert_text, show_alert=True)
        except Exception:
            await query.answer("🔄 Pʀᴏᴄᴇssɪɴɢ...", show_alert=False)
        return
    context.user_data[UD_KEY_LAST_CB_TIME] = now

    callback_data = query.data
    logger.info(f"Callback received: User={user_who_clicked.id}, Data='{callback_data}'")

    answer_text_default = None
    answer_show_alert_default = False

    try:
        if callback_data == CB_PREFIX_NOOP:
            answer_text_default = None
        elif callback_data == CB_PREFIX_NAV_PARENT:
            await handle_parent_nav(update, context)
            return
        elif callback_data == CB_PREFIX_NAV_ROOT:
            await handle_root_nav(update, context)
            return
        elif callback_data == CB_PREFIX_SRCH_BACK:
            await handle_search_back(update, context)
            return
        
        elif ':' in callback_data:
            prefix, payload = callback_data.split(':', 1)
            prefix_with_colon = prefix + ":"

            if prefix_with_colon == CB_PREFIX_NAV_DIR or prefix_with_colon == CB_PREFIX_NAV_FILE:
                await handle_item_click(update, context, prefix_with_colon, payload)
                return 
            elif prefix_with_colon == CB_PREFIX_NAV_PAGE:
                await handle_pagination(update, context, payload)
                return
            elif prefix_with_colon == CB_PREFIX_SRCH_DIR or prefix_with_colon == CB_PREFIX_SRCH_FILE:
                await handle_search_result_click(update, context, prefix_with_colon, payload)
                return
            elif prefix_with_colon in [CB_PREFIX_ACCEPT_USER, CB_PREFIX_REJECT_USER, CB_PREFIX_DISMISS_ADMIN_MSG]:
                await handle_admin_action(update, context, prefix_with_colon, payload) # Authorization is checked inside
                return
            else:
                logger.warning(f"Unhandled CBQ prefix: {prefix_with_colon} from user {user_who_clicked.id}")
                answer_text_default = loc.ACTION_UNKNOWN
                answer_show_alert_default = True
        else:
            logger.warning(f"Malformed CBQ data: '{callback_data}' from user {user_who_clicked.id}")
            answer_text_default = loc.INVALID_FORMAT
            answer_show_alert_default = True

        if answer_text_default is not None or answer_show_alert_default:
            await query.answer(text=answer_text_default, show_alert=answer_show_alert_default)
        else:
            try: await query.answer()
            except BadRequest as e_ans:
                logger.debug(f"Silent query.answer failed (likely too old or already answered): {e_ans}")

    except Exception as e:
        logger.exception(f"Error processing CBQ '{callback_data}' from user {user_who_clicked.id}: {e}")
        try:
            await query.answer(loc.INTERNAL_ERROR, show_alert=True)
        except Exception as answer_e:
            logger.error(f"Failed to answer query after CBQ error: {answer_e}")

# Made by: Zaky1million 😊♥️
# For contact or project requests: https://t.me/Zaky1million
