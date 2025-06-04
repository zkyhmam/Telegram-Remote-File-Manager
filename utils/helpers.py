# -*- coding: utf-8 -*-
"""
Utility functions for path handling, text formatting, photo messages, etc.
"""

import os
import logging
import html # Python's html module
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional

from telegram import Update, InlineKeyboardMarkup, InputMediaPhoto, constants, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.error import BadRequest

from config import (
    START_DIRECTORY_PATH, MAX_FILENAME_DISPLAY_LENGTH,
    MAX_CALLBACK_DATA_LENGTH, UD_KEY_CURRENT_PATH, BOT_IMAGE_URL,
    UD_KEY_CURRENT_MESSAGE_ID, ADMIN_USER_ID,
    CB_PREFIX_ACCEPT_USER, CB_PREFIX_REJECT_USER, CB_PREFIX_DISMISS_ADMIN_MSG
)
import localization as loc
# No more 'is_authorized' import from auth_utils here, it will be imported directly where needed.

logger = logging.getLogger(__name__)


# --- Text Formatting ---
def escape_html(text: Any) -> str:
    return html.escape(str(text), quote=False)

def truncate_filename(filename: str, max_len: int = MAX_FILENAME_DISPLAY_LENGTH) -> str:
    if len(filename) > max_len:
        if max_len < 4: return "…"
        return filename[:max_len-1] + "…"
    return filename

def get_file_emoji(filename: str) -> str:
    ext = filename.lower().split('.')[-1] if '.' in filename else ''
    emoji_map = {
        'txt': '📝', 'log': '📜', 'md': '📄', 'rtf': '📄',
        'pdf': '📕', 'doc': '📄', 'docx': '📄', 'odt': '📄', 'xls': '📊', 'xlsx': '📊', 'ppt': '🖥️', 'pptx': '🖥️',
        'jpg': '🖼️', 'jpeg': '🖼️', 'png': '🖼️', 'gif': '🖼️', 'bmp': '🖼️', 'svg': '🎨', 'webp': '🖼️', 'tiff': '🖼️', 'ico': '🖼️',
        'mp4': '🎥', 'avi': '🎬', 'mkv': '🎬', 'mov': '🎬', 'wmv': '🎬', 'flv': '🎬',
        'mp3': '🎵', 'wav': '🎵', 'ogg': '🎵', 'flac': '🎵', 'aac': '🎵', 'm4a': '🎵',
        'zip': '📦', 'rar': '📦', '7z': '📦', 'tar': '📦', 'gz': '📦', 'bz2': '📦', 'xz': '📦',
        'py': '🐍', 'js': '📜', 'html': '🌐', 'css': '🎨', 'json': '⚙️', 'xml': '⚙️', 'yaml': '⚙️', 'yml': '⚙️',
        'sh': '💻', 'bash': '💻', 'bat': '💻', 'ps1': '💻', 'java': '☕', 'c': '#️⃣', 'cpp': '#️⃣', 'h': '#️⃣', 'rb': '💎',
        'php': '🐘', 'go': '🐹', 'rs': '🦀', 'swift': '🐦', 'kt': '📱', 'sql': '🗄️', 'env': '🔑',
        'exe': '⚙️', 'msi': '⚙️', 'deb': '📦', 'rpm': '📦', 'apk': '📱', 'iso': '💿', 'img': '💾', 'dmg': '⚙️',
        'csv': '📈', 'db': '🗄️', 'sqlite': '🗄️', 'ttf': '🔡', 'otf': '🔡', 'woff': '🔡', 'woff2': '🔡',
        'conf': '⚙️', 'ini': '⚙️', 'cfg': '⚙️',
    }
    return emoji_map.get(ext, '📎')

# --- Path Handling ---
def get_safe_path(context: ContextTypes.DEFAULT_TYPE, key: str = UD_KEY_CURRENT_PATH) -> Path:
    path_str = context.user_data.get(key, str(START_DIRECTORY_PATH))
    try:
        resolved_path = Path(path_str).resolve()
        if resolved_path == START_DIRECTORY_PATH or str(resolved_path).startswith(str(START_DIRECTORY_PATH) + os.sep):
            return resolved_path
        else:
            logger.warning(f"Pᴀᴛʜ '{resolved_path}' ʀᴇᴛʀɪᴇᴠᴇᴅ ғʀᴏᴍ ᴄᴏɴᴛᴇxᴛ ᴋᴇʏ '{key}' ɪs ᴏᴜᴛsɪᴅᴇ START_DIRECTORY. Rᴇsᴇᴛᴛɪɴɢ.")
            context.user_data[key] = str(START_DIRECTORY_PATH)
            return START_DIRECTORY_PATH
    except Exception as e:
        logger.error(f"Eʀʀᴏʀ ʀᴇsᴏʟᴠɪɴɢ ᴘᴀᴛʜ '{path_str}' ғʀᴏᴍ ᴄᴏɴᴛᴇxᴛ ᴋᴇʏ '{key}': {e}. Dᴇғᴀᴜʟᴛɪɴɢ.")
        context.user_data[key] = str(START_DIRECTORY_PATH)
        return START_DIRECTORY_PATH

def set_safe_path(context: ContextTypes.DEFAULT_TYPE, path: str | Path, key: str = UD_KEY_CURRENT_PATH) -> Path:
    try:
        target_path = Path(path).resolve()
        is_safe_path = (
            target_path == START_DIRECTORY_PATH or
            str(target_path).startswith(str(START_DIRECTORY_PATH) + os.sep)
        )
        if is_safe_path:
            context.user_data[key] = str(target_path)
            return target_path
        else:
            logger.warning(f"Aᴛᴛᴇᴍᴘᴛ ᴛᴏ sᴇᴛ ᴘᴀᴛʜ '{target_path}' ᴏᴜᴛsɪᴅᴇ START_DIRECTORY. Rᴇsᴇᴛᴛɪɴɢ.")
            context.user_data[key] = str(START_DIRECTORY_PATH)
            return START_DIRECTORY_PATH
    except Exception as e:
        logger.error(f"Eʀʀᴏʀ ʀᴇsᴏʟᴠɪɴɢ ᴏʀ sᴇᴛᴛɪɴɢ ᴘᴀᴛʜ '{path}': {e}. Rᴇsᴇᴛᴛɪɴɢ.")
        context.user_data[key] = str(START_DIRECTORY_PATH)
        return START_DIRECTORY_PATH

# --- Callback Data ---
def create_callback_data(prefix: str, payload: Any) -> Optional[str]:
    data = f"{prefix}{str(payload)}"
    if len(data.encode('utf-8')) > MAX_CALLBACK_DATA_LENGTH:
        logger.error(f"Cᴀʟʟʙᴀᴄᴋ ᴅᴀᴛᴀ ᴇxᴄᴇᴇᴅs Tᴇʟᴇɢʀᴀᴍ ʟɪᴍɪᴛ: '{data}'")
        return None
    return data

# --- Context Data Handling ---
def store_list_in_context(context: ContextTypes.DEFAULT_TYPE, key: str, items: List[Dict[str, Any]]):
    context.user_data[key] = items

def get_item_from_context(context: ContextTypes.DEFAULT_TYPE, key: str, index: int) -> Optional[Dict[str, Any]]:
    items = context.user_data.get(key)
    if isinstance(items, list):
        if 0 <= index < len(items):
            return items[index]
        else:
             logger.warning(f"Index {index} out of bounds for context key '{key}' (len: {len(items)}).")
    else:
        logger.warning(f"Invalid data type for context key '{key}'. Type: {type(items)}")
    return None

# --- Photo Message Helper ---
async def send_or_edit_photo_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    caption: str,
    reply_markup: Optional[InlineKeyboardMarkup],
    edit_existing: bool = True
) -> Optional[int]:
    photo_url_to_use = BOT_IMAGE_URL
    message_id_to_edit = context.user_data.get(UD_KEY_CURRENT_MESSAGE_ID) if edit_existing else None
    new_message_id = None

    if message_id_to_edit and update.callback_query: # Only edit if triggered by a callback (button press)
        try:
            media = InputMediaPhoto(media=photo_url_to_use, caption=caption, parse_mode=constants.ParseMode.HTML)
            await context.bot.edit_message_media(
                chat_id=chat_id,
                message_id=message_id_to_edit,
                media=media,
                reply_markup=reply_markup
            )
            logger.debug(f"Photo message {message_id_to_edit} edited.")
            new_message_id = message_id_to_edit
        except BadRequest as e:
            if "Message is not modified" in str(e):
                logger.debug(f"Photo message {message_id_to_edit} not modified.")
                new_message_id = message_id_to_edit
            elif "message to edit not found" in str(e).lower():
                logger.warning(f"Photo message {message_id_to_edit} to edit not found. Will send new.")
                message_id_to_edit = None # Force send new
            else:
                logger.warning(f"BadRequest editing photo message {message_id_to_edit}: {e}. Will send new.")
                message_id_to_edit = None # Force send new
        except Exception as e: # Other errors during edit
            logger.error(f"Error editing photo message {message_id_to_edit}: {e}. Will send new.")
            message_id_to_edit = None # Force send new
    else: # Not editing or not a callback context
        message_id_to_edit = None

    if not new_message_id: # Send new message if edit failed or was not attempted
        # If we intended to edit but couldn't (message_id_to_edit was initially set but became None)
        # and we are in a callback context, try to delete the old message.
        old_msg_id_for_del = context.user_data.get(UD_KEY_CURRENT_MESSAGE_ID)
        if update.callback_query and message_id_to_edit is None and old_msg_id_for_del :
             try:
                 await context.bot.delete_message(chat_id=chat_id, message_id=old_msg_id_for_del)
                 logger.debug(f"Deleted old message {old_msg_id_for_del} because edit failed and sending new photo message.")
             except Exception as del_e:
                 logger.warning(f"Could not delete old message {old_msg_id_for_del} after edit failed: {del_e}")
        
        try:
            sent_message = await context.bot.send_photo(
                chat_id=chat_id,
                photo=photo_url_to_use,
                caption=caption,
                reply_markup=reply_markup,
                parse_mode=constants.ParseMode.HTML
            )
            new_message_id = sent_message.message_id
            logger.debug(f"New photo message {new_message_id} sent.")
        except Exception as e:
            logger.error(f"Failed to send new photo message: {e}")
            try:
                await context.bot.send_message(chat_id, loc.ERROR_SENDING_PHOTO_FALLBACK, parse_mode=constants.ParseMode.HTML)
            except Exception as fallback_e:
                logger.error(f"Failed to send text fallback error message: {fallback_e}")
            return None

    if new_message_id: # Store the ID of the successfully sent/edited message
        context.user_data[UD_KEY_CURRENT_MESSAGE_ID] = new_message_id
    return new_message_id

async def handle_unauthorized_access(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    user_info = f"User ID: {user.id}"
    if user.username:
        user_info += f", Username: @{user.username}"
    user_mention = user.mention_html()
    
    attempted_message_text = ""
    if update.message and update.message.text:
        attempted_message_text = update.message.text
    elif update.message and update.message.caption:
        attempted_message_text = update.message.caption
    elif update.callback_query and update.callback_query.data:
        attempted_message_text = f"Callback: {update.callback_query.data}"

    logger.warning(
        f"UNAUTHORIZED ACCESS ATTEMPT by {user_info}. Message: '{escape_html(attempted_message_text)}'"
    )

    try:
        await send_or_edit_photo_message(
            update, context, chat_id,
            caption=loc.ACCESS_DENIED_PHOTO,
            reply_markup=None,
            edit_existing=False # Always send new message to unauthorized user
        )
    except Exception as e:
        logger.error(f"Failed to send access denied message to user {user.id}: {e}")

    if ADMIN_USER_ID: # From config
        admin_message_caption = loc.ADMIN_UNAUTHORIZED_ATTEMPT.format(
            user_mention=user_mention,
            user_id=user.id,
            username=f"@{user.username}" if user.username else "N/A",
            message_text=escape_html(attempted_message_text) if attempted_message_text else "N/A"
        )
        
        accept_cb_data = create_callback_data(CB_PREFIX_ACCEPT_USER, user.id) # Prefixes from config
        reject_cb_data = create_callback_data(CB_PREFIX_REJECT_USER, user.id)
        
        admin_buttons_row = []
        if accept_cb_data:
            admin_buttons_row.append(InlineKeyboardButton(loc.BUTTON_ACCEPT_USER, callback_data=accept_cb_data))
        if reject_cb_data:
            admin_buttons_row.append(InlineKeyboardButton(loc.BUTTON_REJECT_USER, callback_data=reject_cb_data))
        
        admin_reply_markup_val = InlineKeyboardMarkup([admin_buttons_row]) if admin_buttons_row else None

        try:
            await context.bot.send_photo( # Send as new message to admin
                chat_id=ADMIN_USER_ID,
                photo=BOT_IMAGE_URL,
                caption=admin_message_caption,
                reply_markup=admin_reply_markup_val,
                parse_mode=constants.ParseMode.HTML
            )
        except Exception as e:
            logger.error(f"Failed to send unauthorized attempt notification to Admin {ADMIN_USER_ID}: {e}")

# Made by: Zaky1million 😊♥️
# For contact or project requests: https://t.me/Zaky1million
