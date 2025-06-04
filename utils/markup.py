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

from config import (
    START_DIRECTORY_PATH, MAX_BUTTONS_PER_ROW, ITEMS_PER_PAGE,
    CB_PREFIX_NAV_DIR, CB_PREFIX_NAV_FILE, CB_PREFIX_NAV_PAGE, CB_PREFIX_NAV_PARENT,
    CB_PREFIX_NAV_ROOT, CB_PREFIX_NOOP,
    UD_KEY_VIEW_ITEMS, UD_KEY_CURRENT_PAGE
)
import localization as loc
from .helpers import (
    truncate_filename, get_file_emoji, create_callback_data, store_list_in_context,
    escape_html
)

logger = logging.getLogger(__name__)

def create_navigation_buttons(
    current_path: Path, current_page: int, total_pages: int
) -> List[List[InlineKeyboardButton]]:
    """Creates Back, Root, and pagination buttons. Search button removed."""
    buttons: List[List[InlineKeyboardButton]] = []
    is_at_start_dir = current_path == START_DIRECTORY_PATH

    nav_row = []
    if not is_at_start_dir:
        parent_path = current_path.parent
        is_parent_safe = str(parent_path).startswith(str(START_DIRECTORY_PATH)) or parent_path == START_DIRECTORY_PATH
        if is_parent_safe:
            cb_parent = create_callback_data(CB_PREFIX_NAV_PARENT, "")
            if cb_parent: nav_row.append(InlineKeyboardButton(loc.BUTTON_BACK, callback_data=cb_parent))

    if not is_at_start_dir:
        cb_root = create_callback_data(CB_PREFIX_NAV_ROOT, "")
        if cb_root: nav_row.append(InlineKeyboardButton(loc.BUTTON_ROOT, callback_data=cb_root))
    
    # Add a noop button if nav_row is too small for layout, or to ensure it's not empty
    # if len(nav_row) == 1 and MAX_BUTTONS_PER_ROW > 1 : # Example condition
    #     nav_row.append(InlineKeyboardButton(" ", callback_data=CB_PREFIX_NOOP))


    if nav_row: # Only add row if there are buttons
        # Fill up nav_row to MAX_BUTTONS_PER_ROW with invisible buttons if it helps layout
        # For now, keep it simple. Let Telegram handle flexible button widths.
        buttons.append(nav_row)


    if total_pages > 1:
        pagination_row = []
        if current_page > 0:
            cb_prev = create_callback_data(CB_PREFIX_NAV_PAGE, current_page - 1)
            if cb_prev: pagination_row.append(InlineKeyboardButton(loc.BUTTON_PREV_PAGE, callback_data=cb_prev))
        else: # Placeholder for alignment
             pagination_row.append(InlineKeyboardButton(" ", callback_data=CB_PREFIX_NOOP))

        page_indicator_text = loc.BUTTON_PAGE_INDICATOR.format(current=current_page + 1, total=total_pages)
        pagination_row.append(InlineKeyboardButton(page_indicator_text, callback_data=CB_PREFIX_NOOP))

        if current_page < total_pages - 1:
            cb_next = create_callback_data(CB_PREFIX_NAV_PAGE, current_page + 1)
            if cb_next: pagination_row.append(InlineKeyboardButton(loc.BUTTON_NEXT_PAGE, callback_data=cb_next))
        else: # Placeholder for alignment
             pagination_row.append(InlineKeyboardButton(" ", callback_data=CB_PREFIX_NOOP))
        
        if len(pagination_row) > 1: # Ensure not just a single page indicator
            buttons.append(pagination_row)
            
    return buttons

def generate_file_list_markup(
    context: ContextTypes.DEFAULT_TYPE, path: Path, page: int = 0
) -> Tuple[Optional[InlineKeyboardMarkup], str]:
    """
    Generates the InlineKeyboardMarkup and message text (caption) for directory contents.
    Stores items for current view in context.user_data[UD_KEY_VIEW_ITEMS].
    Returns (markup, caption_text).
    """
    buttons: List[List[InlineKeyboardButton]] = []
    error_message: Optional[str] = None
    total_pages = 1
    items_for_this_page: List[Dict[str, Any]] = []
    validated_page = 0

    try:
        if not (path == START_DIRECTORY_PATH or str(path).startswith(str(START_DIRECTORY_PATH) + os.sep)):
            raise PermissionError(f"Attempt to list directory outside START_DIRECTORY: {path}")

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
                            target_path_resolved = Path(entry.path).resolve() # Don't use strict=True for symlinks that might be broken but still listable
                            if target_path_resolved == START_DIRECTORY_PATH or str(target_path_resolved).startswith(str(START_DIRECTORY_PATH) + os.sep):
                                if target_path_resolved.exists():
                                     effective_is_dir = target_path_resolved.is_dir()
                                     effective_is_file = target_path_resolved.is_file()
                                target_path_str = str(target_path_resolved) # Use resolved path for symlink actions if valid
                            # If symlink points outside, it's handled by path validation later. Here, just record it.
                        except OSError as sym_e: # Catches FileNotFoundError if broken symlink during resolve
                            logger.debug(f"Symlink '{entry.path}' seems broken or inaccessible: {sym_e}. Will be marked.")
                            # effective_is_dir/file remain False. Button will be non-actionable or show warning.
                        except Exception as sym_e_gen:
                             logger.warning(f"Unexpected error resolving symlink {entry.path}: {sym_e_gen}")

                    else: # Not a symlink
                        effective_is_dir = is_dir
                        effective_is_file = is_file
                    
                    # For symlinks, entry.path is the link path, target_path_str is what it resolves to (or link path if broken/invalid)
                    all_items.append({
                        "name": entry.name,
                        "path": target_path_str, # This is the path that will be acted upon
                        "is_dir": effective_is_dir,
                        "is_file": effective_is_file,
                        "is_symlink": is_symlink,
                        "original_link_path": entry.path if is_symlink else None # Store original link path for info
                    })
                except OSError as e:
                    logger.warning(f"OS error accessing metadata for {entry.path}: {e}. Skipping.")
                except Exception as e:
                    logger.warning(f"Unexpected error processing entry {entry.name} in {path}: {e}. Skipping.")
        
        all_items.sort(key=lambda x: (not x["is_dir"], x["name"].lower()))
        total_items = len(all_items)
        total_pages = math.ceil(total_items / ITEMS_PER_PAGE) if ITEMS_PER_PAGE > 0 else 1
        validated_page = max(0, min(page, total_pages - 1))

        start_index = validated_page * ITEMS_PER_PAGE
        end_index = start_index + ITEMS_PER_PAGE
        items_for_this_page = all_items[start_index:end_index]
        
        store_list_in_context(context, UD_KEY_VIEW_ITEMS, items_for_this_page)
        context.user_data[UD_KEY_CURRENT_PAGE] = validated_page

        row: List[InlineKeyboardButton] = []
        for index, item in enumerate(items_for_this_page):
            display_name = escape_html(truncate_filename(item['name']))
            callback_prefix = CB_PREFIX_NOOP
            emoji = "❓" # Default for unknown/inaccessible

            if item["is_dir"]:
                emoji = "🔗" if item["is_symlink"] else "📁"
                callback_prefix = CB_PREFIX_NAV_DIR
            elif item["is_file"]:
                emoji = "🔗" if item["is_symlink"] else get_file_emoji(item['name'])
                callback_prefix = CB_PREFIX_NAV_FILE
            elif item["is_symlink"]: # Symlink that isn't a valid dir or file (e.g. broken, points outside)
                emoji = "⚠️🔗" # Warning symlink
                callback_prefix = CB_PREFIX_NOOP # Make it non-actionable or show info on click
            
            button_text = f"{emoji} {display_name}"
            # Item index for callback refers to its position in items_for_this_page
            callback_action = create_callback_data(callback_prefix, index) 

            if callback_action:
                row.append(InlineKeyboardButton(button_text, callback_data=callback_action))
            else:
                logger.error(f"Callback data generation failed for item: {item.get('path', 'N/A')}")
                row.append(InlineKeyboardButton(f"⚠️ {display_name}", callback_data=CB_PREFIX_NOOP))
            
            if len(row) >= MAX_BUTTONS_PER_ROW:
                buttons.append(row)
                row = []
        if row: buttons.append(row)

    except FileNotFoundError:
        logger.warning(f"Directory not found: {path}")
        error_message = f"{loc.ERROR_NOT_FOUND}\n<code>{escape_html(str(path))}</code>"
        # Try to show nav buttons for parent if possible
        try:
             nav_buttons_on_error = create_navigation_buttons(path.parent if path != START_DIRECTORY_PATH else START_DIRECTORY_PATH, 0, 1)
             buttons.extend(nav_buttons_on_error)
        except Exception: pass
        return (InlineKeyboardMarkup(buttons) if buttons else None), error_message
    
    except PermissionError:
        logger.warning(f"Permission denied listing directory: {path}")
        error_message = f"{loc.ERROR_PERMISSION_DENIED}\n<code>{escape_html(str(path))}</code>"
        try:
             nav_buttons_on_error = create_navigation_buttons(path.parent if path != START_DIRECTORY_PATH else START_DIRECTORY_PATH, 0, 1)
             buttons.extend(nav_buttons_on_error)
        except Exception: pass
        return (InlineKeyboardMarkup(buttons) if buttons else None), error_message

    except Exception as e:
        logger.exception(f"Unexpected error listing directory {path}: {e}")
        error_message = loc.ERROR_UNEXPECTED_LISTING
        try:
            nav_buttons_on_error = create_navigation_buttons(path, validated_page, total_pages) # current path
            buttons.extend(nav_buttons_on_error)
        except Exception: pass
        return (InlineKeyboardMarkup(buttons) if buttons else None), error_message

    # --- Add navigation buttons to the main item buttons ---
    nav_buttons = create_navigation_buttons(path, validated_page, total_pages)
    buttons.extend(nav_buttons)

    if not items_for_this_page and validated_page == 0 and not error_message:
        empty_button_row = [InlineKeyboardButton(loc.FOLDER_EMPTY, callback_data=CB_PREFIX_NOOP)]
        # Insert before nav buttons if nav buttons exist
        if nav_buttons:
            buttons.insert(len(buttons) - len(nav_buttons), empty_button_row)
        else:
            buttons.append(empty_button_row)

    keyboard = InlineKeyboardMarkup(buttons) if buttons else None
    
    # Construct the caption text
    escaped_path_str = escape_html(str(path))
    caption_text = f"{loc.CURRENT_PATH}\n<code>{escaped_path_str}</code>"
    if total_pages > 1:
        page_num_str = escape_html(loc.PAGE_NUMBER.format(current=validated_page + 1, total=total_pages))
        caption_text += f"\n{page_num_str}"

    if error_message: # Prepend error to path info or replace
        caption_text = f"{error_message}\n\n{caption_text}" if not loc.ERROR_NOT_FOUND in error_message and not loc.ERROR_PERMISSION_DENIED in error_message else error_message

    return keyboard, caption_text

# Made by: Zaky1million 😊♥️
# For contact or project requests: https://t.me/Zaky1million
