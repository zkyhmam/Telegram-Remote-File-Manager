# -*- coding: utf-8 -*-
"""
Utility functions for managing authorized users.
"""
import json
import logging
from pathlib import Path
from typing import Set, Optional

from telegram import Update
from telegram.ext import ContextTypes

from config import ADMIN_USER_ID, AUTHORIZED_USERS_FILE

logger = logging.getLogger(__name__)

def load_authorized_users(context: ContextTypes.DEFAULT_TYPE) -> Set[int]:
    """Loads authorized user IDs from the JSON file into bot_data."""
    if 'authorized_ids' in context.bot_data:
        return context.bot_data['authorized_ids']

    auth_file = Path(AUTHORIZED_USERS_FILE)
    user_ids: Set[int] = set()
    if auth_file.exists():
        try:
            with open(auth_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list): # Legacy format
                    user_ids = set(filter(lambda x: isinstance(x, int), data))
                elif isinstance(data, dict) and "authorized_ids" in data: # New format
                     user_ids = set(filter(lambda x: isinstance(x, int), data.get("authorized_ids", [])))
                else: # Also new format, simple list
                     user_ids = set(filter(lambda x: isinstance(x, int), data))


            logger.info(f"Loaded {len(user_ids)} additional authorized user IDs from {AUTHORIZED_USERS_FILE}.")
        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from {AUTHORIZED_USERS_FILE}. File might be corrupted.")
            # Create new if corrupted
            with open(auth_file, 'w', encoding='utf-8') as f:
                json.dump({"authorized_ids": []}, f, indent=2)
            logger.info(f"Created a new empty {AUTHORIZED_USERS_FILE}.")
        except Exception as e:
            logger.error(f"Failed to load {AUTHORIZED_USERS_FILE}: {e}")
    else:
        logger.warning(f"{AUTHORIZED_USERS_FILE} not found. Creating a new one.")
        try:
            with open(auth_file, 'w', encoding='utf-8') as f:
                json.dump({"authorized_ids": []}, f, indent=2)
            logger.info(f"Created a new empty {AUTHORIZED_USERS_FILE}.")
        except Exception as e:
            logger.error(f"Could not create {AUTHORIZED_USERS_FILE}: {e}")

    context.bot_data['authorized_ids'] = user_ids
    return user_ids

def save_authorized_users(context: ContextTypes.DEFAULT_TYPE):
    """Saves the current set of authorized user IDs from bot_data to the JSON file."""
    user_ids: Set[int] = context.bot_data.get('authorized_ids', set())
    auth_file = Path(AUTHORIZED_USERS_FILE)
    try:
        with open(auth_file, 'w', encoding='utf-8') as f:
            json.dump({"authorized_ids": sorted(list(user_ids))}, f, indent=2)
        logger.info(f"Saved {len(user_ids)} additional authorized user IDs to {AUTHORIZED_USERS_FILE}.")
    except Exception as e:
        logger.error(f"Failed to save {AUTHORIZED_USERS_FILE}: {e}")

def add_authorized_user(context: ContextTypes.DEFAULT_TYPE, user_id: int) -> bool:
    """Adds a user ID to the authorized list and saves."""
    if not isinstance(user_id, int):
        logger.warning(f"Attempted to add non-integer user_id: {user_id}")
        return False
    user_ids = load_authorized_users(context) # Ensure it's loaded
    if user_id not in user_ids:
        user_ids.add(user_id)
        context.bot_data['authorized_ids'] = user_ids
        save_authorized_users(context)
        logger.info(f"User ID {user_id} added to authorized list.")
        return True
    logger.info(f"User ID {user_id} is already authorized.")
    return False # Already authorized

async def is_authorized(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Checks if the user sending the update is the admin or in the dynamic authorized list."""
    if not update.effective_user:
        return False
    user_id = update.effective_user.id

    if user_id == ADMIN_USER_ID:
        return True

    additional_authorized_ids = load_authorized_users(context)
    return user_id in additional_authorized_ids

# Made by: Zaky1million 😊♥️
# For contact or project requests: https://t.me/Zaky1million
