# -*- coding: utf-8 -*-
"""
Functions for generating InlineKeyboardMarkup and message text for browsing (HTML).
"""

import os
import math
import logging
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

# Import config, localization, and helpers
from config import (
    START_DIRECTORY_PATH, MAX_BUTTONS_PER_ROW, ITEMS_PER_PAGE,
    CB_PREFIX_NAV_DIR, CB_PREFIX_NAV_FILE, CB_PREFIX_NAV_PAGE, CB_PREFIX_NAV_PARENT,
    CB_PREFIX_NAV_ROOT, CB_PREFIX_SRCH_START, CB_PREFIX_NOOP,
    UD_KEY_VIEW_ITEMS, UD_KEY_CURRENT_PAGE
)
import localization as loc
from .helpers import (
    truncate_filename, get_file_emoji, create_callback_data, store_list_in_context,
    escape_html # Use escape_html now
)

logger = logging.getLogger(__name__)

def create_navigation_buttons(
    current_path: Path, current_page: int, total_pages: int
) -> List[List[InlineKeyboardButton]]:
    """Creates Back, Root, Search, and pagination buttons."""
    buttons: List[List[InlineKeyboardButton]] = []
    is_at_start_dir = current_path == START_DIRECTORY_PATH

    nav_row = []
    # --- Parent Button ---
    if not is_at_start_dir:
        parent_path = current_path.parent
        is_parent_safe = str(parent_path).startswith(str(START_DIRECTORY_PATH)) or parent_path == START_DIRECTORY_PATH
        if is_parent_safe:
            cb = create_callback_data(CB_PREFIX_NAV_PARENT, "")
            if cb: nav_row.append(InlineKeyboardButton(loc.BUTTON_BACK, callback_data=cb))

    # --- Root Button ---
    if not is_at_start_dir:
        cb = create_callback_data(CB_PREFIX_NAV_ROOT, "")
        if cb: nav_row.append(InlineKeyboardButton(loc.BUTTON_ROOT, callback_data=cb))

    # --- Search Button ---
    cb = create_callback_data(CB_PREFIX_SRCH_START, "")
    if cb: nav_row.append(InlineKeyboardButton(loc.BUTTON_SEARCH_HERE, callback_data=cb))

    if nav_row:
        buttons.append(nav_row)

    # --- Pagination Buttons ---
    if total_pages > 1:
        pagination_row = []
        if current_page > 0:
            cb_prev = create_callback_data(CB_PREFIX_NAV_PAGE, current_page - 1)
            if cb_prev: pagination_row.append(InlineKeyboardButton(loc.BUTTON_PREV_PAGE, callback_data=cb_prev))
        else:
             pagination_row.append(InlineKeyboardButton(" ", callback_data=CB_PREFIX_NOOP))

        page_indicator_text = loc.BUTTON_PAGE_INDICATOR.format(current=current_page + 1, total=total_pages)
        pagination_row.append(InlineKeyboardButton(page_indicator_text, callback_data=CB_PREFIX_NOOP))

        if current_page < total_pages - 1:
            cb_next = create_callback_data(CB_PREFIX_NAV_PAGE, current_page + 1)
            if cb_next: pagination_row.append(InlineKeyboardButton(loc.BUTTON_NEXT_PAGE, callback_data=cb_next))
        else:
             pagination_row.append(InlineKeyboardButton(" ", callback_data=CB_PREFIX_NOOP))

        if len(pagination_row) > 1:
            buttons.append(pagination_row)

    return buttons

def generate_file_list_markup(
    context: ContextTypes.DEFAULT_TYPE, path: Path, page: int = 0
) -> Tuple[Optional[InlineKeyboardMarkup], str]:
    """
    Generates the InlineKeyboardMarkup and message text for directory contents (HTML).
    Stores the items for the current page view in context.user_data[UD_KEY_VIEW_ITEMS].
    Handles pagination and potential errors. Returns (markup, message_text).
    """
    buttons: List[List[InlineKeyboardButton]] = []
    error_message: Optional[str] = None
    total_pages = 1
    items_for_this_page: List[Dict[str, Any]] = []
    validated_page = 0
    logger.info(f"-> generate_file_list_markup: Path='{path}', Requested Page={page}")

    try:
        if not (path == START_DIRECTORY_PATH or str(path).startswith(str(START_DIRECTORY_PATH) + os.sep)):
            raise PermissionError(f"Aᴛᴛᴇᴍᴘᴛ ᴛᴏ ʟɪsᴛ ᴅɪʀᴇᴄᴛᴏʀʏ ᴏᴜᴛsɪᴅᴇ START_DIRECTORY: {path}")

        all_items: List[Dict[str, Any]] = []
        with os.scandir(path) as it:
            for entry in it:
                try:
                    is_dir = entry.is_dir(follow_symlinks=False)
                    is_symlink = entry.is_symlink()
                    is_file = entry.is_file(follow_symlinks=False)
                    effective_is_dir = False
                    effective_is_file = False
                    target_path_str = entry.path

                    if is_symlink:
                        try:
                            target_path = Path(entry.path).resolve()
                            if target_path == START_DIRECTORY_PATH or str(target_path).startswith(str(START_DIRECTORY_PATH) + os.sep):
                                if target_path.exists():
                                     effective_is_dir = target_path.is_dir()
                                     effective_is_file = target_path.is_file()
                                     target_path_str = str(target_path)
                                else:
                                     logger.debug(f"Sʏᴍʟɪɴᴋ ᴛᴀʀɢᴇᴛ ᴅᴏᴇs ɴᴏᴛ ᴇxɪsᴛ: {entry.path} -> {target_path}")
                            else:
                                logger.warning(f"Sʏᴍʟɪɴᴋ {entry.path} ᴘᴏɪɴᴛs ᴏᴜᴛsɪᴅᴇ START_DIRECTORY ᴛᴏ {target_path}. Tʀᴇᴀᴛɪɴɢ ᴀs ɪɴᴀᴄᴄᴇssɪʙʟᴇ.")
                        except OSError as sym_e:
                            logger.warning(f"OS ᴇʀʀᴏʀ ʀᴇsᴏʟᴠɪɴɢ/ᴄʜᴇᴄᴋɪɴɢ sʏᴍʟɪɴᴋ ᴛᴀʀɢᴇᴛ {entry.path}: {sym_e}. Tʀᴇᴀᴛɪɴɢ ᴀs ʙʀᴏᴋᴇɴ ʟɪɴᴋ.")
                        except Exception as sym_e_gen:
                            logger.warning(f"Uɴᴇxᴘᴇᴄᴛᴇᴅ ᴇʀʀᴏʀ ʀᴇsᴏʟᴠɪɴɢ/ᴄʜᴇᴄᴋɪɴɢ sʏᴍʟɪɴᴋ ᴛᴀʀɢᴇᴛ {entry.path}: {sym_e_gen}. Tʀᴇᴀᴛɪɴɢ ᴀs ʙʀᴏᴋᴇɴ ʟɪɴᴋ.")
                    else:
                        effective_is_dir = is_dir
                        effective_is_file = is_file

                    all_items.append({
                        "name": entry.name,
                        "path": target_path_str,
                        "is_dir": effective_is_dir,
                        "is_file": effective_is_file,
                        "is_symlink": is_symlink,
                    })
                except OSError as e:
                    logger.warning(f"OS ᴇʀʀᴏʀ ᴀᴄᴄᴇssɪɴɢ ᴍᴇᴛᴀᴅᴀᴛᴀ ғᴏʀ {entry.path}: {e}. Sᴋɪᴘᴘɪɴɢ ɪᴛᴇᴍ.")
                except Exception as e:
                    logger.warning(f"Uɴᴇxᴘᴇᴄᴛᴇᴅ ᴇʀʀᴏʀ ᴘʀᴏᴄᴇssɪɴɢ ᴇɴᴛʀʏ {entry.name} ɪɴ {path}: {e}. Sᴋɪᴘᴘɪɴɢ ɪᴛᴇᴍ.")

        all_items.sort(key=lambda x: (not x["is_dir"], x["name"].lower()))

        total_items = len(all_items)
        total_pages = math.ceil(total_items / ITEMS_PER_PAGE) if ITEMS_PER_PAGE > 0 else 1
        validated_page = max(0, min(page, total_pages - 1))
        logger.info(f"   Cᴀʟᴄᴜʟᴀᴛᴇᴅ: total_items={total_items}, total_pages={total_pages}, validated_page={validated_page}")

        start_index = validated_page * ITEMS_PER_PAGE
        end_index = start_index + ITEMS_PER_PAGE
        items_for_this_page = all_items[start_index:end_index]
        logger.info(f"   Sʟɪᴄɪɴɢ: start_index={start_index}, end_index={end_index}, items_on_this_page={len(items_for_this_page)}")

        store_list_in_context(context, UD_KEY_VIEW_ITEMS, items_for_this_page)
        context.user_data[UD_KEY_CURRENT_PAGE] = validated_page
        logger.info(f"   Sᴛᴏʀᴇᴅ: {UD_KEY_VIEW_ITEMS} (count: {len(items_for_this_page)}), {UD_KEY_CURRENT_PAGE}={validated_page}")

        row: List[InlineKeyboardButton] = []
        for index, item in enumerate(items_for_this_page):
            # Escape filename for display in button text
            display_name = escape_html(truncate_filename(item['name']))
            callback_prefix = CB_PREFIX_NOOP
            button_text = ""
            emoji = "❓"

            if item["is_dir"]:
                emoji = "📁"
                if item["is_symlink"]: emoji = "🔗"
                button_text = f"{emoji} {display_name}"
                callback_prefix = CB_PREFIX_NAV_DIR
            elif item["is_file"]:
                emoji = get_file_emoji(item['name']) # Emoji is safe
                if item["is_symlink"]: emoji = "🔗"
                button_text = f"{emoji} {display_name}"
                callback_prefix = CB_PREFIX_NAV_FILE
            elif item["is_symlink"]:
                emoji = "⚠️🔗"
                button_text = f"{emoji} {display_name}"
                callback_prefix = CB_PREFIX_NOOP
            else:
                 button_text = f"{emoji} {display_name}"
                 callback_prefix = CB_PREFIX_NOOP

            callback_action = create_callback_data(callback_prefix, index)

            if callback_action:
                row.append(InlineKeyboardButton(button_text, callback_data=callback_action))
            else:
                logger.error(f"Cᴀʟʟʙᴀᴄᴋ ᴅᴀᴛᴀ ɢᴇɴᴇʀᴀᴛɪᴏɴ ғᴀɪʟᴇᴅ ғᴏʀ ɪᴛᴇᴍ: {item.get('path', 'N/A')}, index: {index}")
                row.append(InlineKeyboardButton(f"⚠️ {display_name}", callback_data=CB_PREFIX_NOOP))

            if len(row) >= MAX_BUTTONS_PER_ROW:
                buttons.append(row)
                row = []
        if row: buttons.append(row)

    except FileNotFoundError:
        logger.warning(f"Dɪʀᴇᴄᴛᴏʀʏ ɴᴏᴛ ғᴏᴜɴᴅ ᴅᴜʀɪɴɢ ʟɪsᴛɪɴɢ: {path}")
        # Use escape_html for path display in error message
        error_message = f"{loc.ERROR_NOT_FOUND}\n<code>{escape_html(str(path))}</code>"
        try: buttons.extend(create_navigation_buttons(path.parent, 0, 1))
        except Exception as nav_err: logger.warning(f"Could not create nav buttons after FileNotFoundError: {nav_err}")
        return (InlineKeyboardMarkup(buttons) if buttons else None), error_message

    except PermissionError:
        logger.warning(f"Pᴇʀᴍɪssɪᴏɴ ᴅᴇɴɪᴇᴅ ʟɪsᴛɪɴɢ ᴅɪʀᴇᴄᴛᴏʀʏ: {path}")
        # Use escape_html for path display in error message
        error_message = f"{loc.ERROR_PERMISSION_DENIED}\n<code>{escape_html(str(path))}</code>"
        try: buttons.extend(create_navigation_buttons(path.parent, 0, 1))
        except Exception as nav_err: logger.warning(f"Could not create nav buttons after PermissionError: {nav_err}")
        return (InlineKeyboardMarkup(buttons) if buttons else None), error_message

    except Exception as e:
        logger.exception(f"Uɴᴇxᴘᴇᴄᴛᴇᴅ ᴇʀʀᴏʀ ʟɪsᴛɪɴɢ ᴅɪʀᴇᴄᴛᴏʀʏ {path}: {e}")
        error_message = loc.ERROR_UNEXPECTED_LISTING
        try: buttons.extend(create_navigation_buttons(path, validated_page, total_pages))
        except Exception as nav_err: logger.warning(f"Could not create nav buttons after general Exception: {nav_err}")
        return (InlineKeyboardMarkup(buttons) if buttons else None), error_message

    nav_buttons = create_navigation_buttons(path, validated_page, total_pages)
    buttons.extend(nav_buttons)

    if not items_for_this_page and validated_page == 0 and not error_message:
        empty_button_row = [InlineKeyboardButton(loc.FOLDER_EMPTY, callback_data=CB_PREFIX_NOOP)]
        if nav_buttons:
            buttons.insert(len(buttons) - len(nav_buttons), empty_button_row)
        else:
            buttons.append(empty_button_row)

    keyboard = InlineKeyboardMarkup(buttons) if buttons else None

    # Construct the message text using HTML
    # Escape the path string for display within <code> tags
    escaped_path_str = escape_html(str(path))
    message_text = f"{loc.CURRENT_PATH}\n<code>{escaped_path_str}</code>"
    if total_pages > 1:
        # Escape page numbers just in case, though they should be safe
        page_num_str = escape_html(loc.PAGE_NUMBER.format(current=validated_page + 1, total=total_pages))
        message_text += f"\n{page_num_str}"

    if error_message:
        message_text = error_message # Error messages are already formatted with HTML

    return keyboard, message_text


# Made by: Zaky1million 😊♥️
# For contact or project requests: https://t.me/Zaky1million
# Please keep this credit as a sign of respect and support.
# Keep going, developer!
# Every great project starts with a single line of code.
# Believe in your skills and never stop learning.
# You're not just coding – you're creating magic.
# Your future self will thank you for the effort you put in today.

