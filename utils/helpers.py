# -*- coding: utf-8 -*-
"""
Utility functions for authorization, path handling, text formatting, etc.
"""

import os
import logging
import html # Import html module for escaping
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional

from telegram import Update
from telegram.ext import ContextTypes
# telegram.helpers.escape_markdown is no longer needed here

# Import config variables and localization strings
from config import (
    AUTHORIZED_USER_ID, START_DIRECTORY_PATH, MAX_FILENAME_DISPLAY_LENGTH,
    MAX_CALLBACK_DATA_LENGTH, UD_KEY_CURRENT_PATH
)
import localization as loc # localization now uses HTML internally

logger = logging.getLogger(__name__)

# --- Authorization ---

def is_authorized(update: Update) -> bool:
    """Checks if the user sending the update is the authorized user."""
    return update.effective_user and update.effective_user.id == AUTHORIZED_USER_ID

# --- Text Formatting ---

def escape_html(text: Any) -> str:
    """Escapes essential HTML characters < > & in text."""
    return html.escape(str(text), quote=False)

def truncate_filename(filename: str, max_len: int = MAX_FILENAME_DISPLAY_LENGTH) -> str:
    """Truncates filename display if it exceeds max_len."""
    if len(filename) > max_len:
        # Ensure max_len is reasonable before slicing
        if max_len < 4: return "…" # Avoid tiny slices
        return filename[:max_len-1] + "…" # Use ellipsis character
    return filename

def get_file_emoji(filename: str) -> str:
    """Returns an emoji based on the file extension."""
    ext = filename.lower().split('.')[-1] if '.' in filename else ''
    # Expanded map (consider making this configurable or moving to localization if needed)
    emoji_map = {
        # Text & Docs
        'txt': '📝', 'log': '📜', 'md': '📄', 'rtf': '📄', # Changed MD emoji
        'pdf': '📕', 'doc': '📄', 'docx': '📄', 'odt': '📄', 'xls': '📊', 'xlsx': '📊', 'ppt': '🖥️', 'pptx': '🖥️',
        # Images
        'jpg': '🖼️', 'jpeg': '🖼️', 'png': '🖼️', 'gif': '🖼️', 'bmp': '🖼️', 'svg': '🎨', 'webp': '🖼️', 'tiff': '🖼️', 'ico': '🖼️',
        # Audio/Video
        'mp4': '🎥', 'avi': '🎬', 'mkv': '🎬', 'mov': '🎬', 'wmv': '🎬', 'flv': '🎬',
        'mp3': '🎵', 'wav': '🎵', 'ogg': '🎵', 'flac': '🎵', 'aac': '🎵', 'm4a': '🎵',
        # Archives
        'zip': '📦', 'rar': '📦', '7z': '📦', 'tar': '📦', 'gz': '📦', 'bz2': '📦', 'xz': '📦',
        # Code & Config
        'py': '🐍', 'js': '📜', 'html': '🌐', 'css': '🎨', 'json': '⚙️', 'xml': '⚙️', 'yaml': '⚙️', 'yml': '⚙️',
        'sh': '💻', 'bash': '💻', 'bat': '💻', 'ps1': '💻', 'java': '☕', 'c': '#️⃣', 'cpp': '#️⃣', 'h': '#️⃣', 'rb': '💎',
        'php': '🐘', 'go': '🐹', 'rs': '🦀', 'swift': '🐦', 'kt': '📱', 'sql': '🗄️', 'env': '🔑',
        # System & Executables
        'exe': '⚙️', 'msi': '⚙️', 'deb': '📦', 'rpm': '📦', 'apk': '📱', 'iso': '💿', 'img': '💾', 'dmg': '⚙️',
        # Other
        'csv': '📈', 'db': '🗄️', 'sqlite': '🗄️', 'ttf': '🔡', 'otf': '🔡', 'woff': '🔡', 'woff2': '🔡',
        'conf': '⚙️', 'ini': '⚙️', 'cfg': '⚙️',
    }
    return emoji_map.get(ext, '📎') # Default: paperclip

# --- Path Handling ---

def get_safe_path(context: ContextTypes.DEFAULT_TYPE, key: str = UD_KEY_CURRENT_PATH) -> Path:
    """
    Gets a path from user_data, resolving and ensuring it's within START_DIRECTORY bounds.
    Defaults to START_DIRECTORY_PATH if the key is missing or the path is invalid/unsafe.
    """
    path_str = context.user_data.get(key, str(START_DIRECTORY_PATH))
    try:
        resolved_path = Path(path_str).resolve()
        # Final check to prevent escaping START_DIRECTORY (belt and braces)
        if resolved_path == START_DIRECTORY_PATH or str(resolved_path).startswith(str(START_DIRECTORY_PATH) + os.sep):
            return resolved_path
        else:
            logger.warning(f"Pᴀᴛʜ '{resolved_path}' ʀᴇᴛʀɪᴇᴠᴇᴅ ғʀᴏᴍ ᴄᴏɴᴛᴇxᴛ ᴋᴇʏ '{key}' ɪs ᴏᴜᴛsɪᴅᴇ START_DIRECTORY '{START_DIRECTORY_PATH}'. Rᴇsᴇᴛᴛɪɴɢ.")
            context.user_data[key] = str(START_DIRECTORY_PATH)
            return START_DIRECTORY_PATH
    except Exception as e:
        logger.error(f"Eʀʀᴏʀ ʀᴇsᴏʟᴠɪɴɢ ᴘᴀᴛʜ '{path_str}' ғʀᴏᴍ ᴄᴏɴᴛᴇxᴛ ᴋᴇʏ '{key}': {e}. Dᴇғᴀᴜʟᴛɪɴɢ ᴛᴏ START_DIRECTORY.")
        context.user_data[key] = str(START_DIRECTORY_PATH)
        return START_DIRECTORY_PATH

def set_safe_path(context: ContextTypes.DEFAULT_TYPE, path: str | Path, key: str = UD_KEY_CURRENT_PATH) -> Path:
    """
    Sets a path in user_data, ensuring it's resolved, absolute,
    and within the bounds of START_DIRECTORY. Returns the resolved, validated Path.
    Resets to START_DIRECTORY_PATH if the provided path is unsafe or invalid.
    """
    try:
        target_path = Path(path).resolve()

        # Security Check: Ensure the target path is START_DIRECTORY or a subdirectory of it.
        is_safe = (
            target_path == START_DIRECTORY_PATH or
            str(target_path).startswith(str(START_DIRECTORY_PATH) + os.sep)
        )

        if is_safe:
            logger.debug(f"Setting safe path for key '{key}': '{str(target_path)}'")
            context.user_data[key] = str(target_path)
            return target_path
        else:
            logger.warning(
                f"Aᴛᴛᴇᴍᴘᴛ ᴛᴏ sᴇᴛ ᴘᴀᴛʜ '{target_path}' ᴏᴜᴛsɪᴅᴇ START_DIRECTORY '{START_DIRECTORY_PATH}'. Rᴇsᴇᴛᴛɪɴɢ ᴛᴏ START_DIRECTORY."
            )
            context.user_data[key] = str(START_DIRECTORY_PATH)
            return START_DIRECTORY_PATH

    except Exception as e:
        logger.error(f"Eʀʀᴏʀ ʀᴇsᴏʟᴠɪɴɢ ᴏʀ sᴇᴛᴛɪɴɢ ᴘᴀᴛʜ '{path}': {e}. Rᴇsᴇᴛᴛɪɴɢ ᴛᴏ START_DIRECTORY.")
        context.user_data[key] = str(START_DIRECTORY_PATH)
        return START_DIRECTORY_PATH

# --- Callback Data ---

def create_callback_data(prefix: str, payload: Any) -> Optional[str]:
    """Creates callback data string. Returns None if too long."""
    data = f"{prefix}{payload}"
    if len(data.encode('utf-8')) > MAX_CALLBACK_DATA_LENGTH:
        logger.error(f"Cᴀʟʟʙᴀᴄᴋ ᴅᴀᴛᴀ ᴇxᴄᴇᴇᴅs Tᴇʟᴇɢʀᴀᴍ ʟɪᴍɪᴛ ({MAX_CALLBACK_DATA_LENGTH} ʙʏᴛᴇs): '{data}'")
        return None
    return data

# --- Context Data Handling ---

def store_list_in_context(context: ContextTypes.DEFAULT_TYPE, key: str, items: List[Dict[str, Any]]):
    """Stores a list of items (e.g., view items, search results) in user_data."""
    context.user_data[key] = items
    logger.debug(f"Stored {len(items)} items in context key '{key}'")

def get_item_from_context(context: ContextTypes.DEFAULT_TYPE, key: str, index: int) -> Optional[Dict[str, Any]]:
    """Retrieves an item from a stored list in user_data using its index."""
    items = context.user_data.get(key)
    if isinstance(items, list):
        if 0 <= index < len(items):
            return items[index]
        else:
             logger.warning(f"Index {index} out of bounds for context key '{key}' (list length: {len(items)}).")
    else:
        logger.warning(f"Failed to retrieve item list or invalid data type for context key '{key}'. Stored data type: {type(items)}")
    return None


# Made by: Zaky1million 😊♥️
# For contact or project requests: https://t.me/Zaky1million
# Please keep this credit as a sign of respect and support.
# Keep going, developer!
# Every great project starts with a single line of code.
# Believe in your skills and never stop learning.
# You're not just coding – you're creating magic.
# Your future self will thank you for the effort you put in today.

