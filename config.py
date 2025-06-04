# -*- coding: utf-8 -*-
"""
Loads configuration from environment variables and defines constants.
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# --- Load Configuration from .env ---
load_dotenv()
logger = logging.getLogger(__name__)

# --- Core Bot Configuration ---
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_USER_ID_STR = os.getenv("ADMIN_USER_ID")
BOT_IMAGE_URL = os.getenv("BOT_IMAGE_URL", "https://i.postimg.cc/SRKg918j/filesharing-plesk-t.jpg")


if not TOKEN:
    logger.critical("Eʀʀᴏʀ: TELEGRAM_BOT_TOKEN ɴᴏᴛ ғᴏᴜɴᴅ ɪɴ .env ғɪʟᴇ ᴏʀ ᴇɴᴠɪʀᴏɴᴍᴇɴᴛ ᴠᴀʀɪᴀʙʟᴇs.")
    sys.exit(1)

if not ADMIN_USER_ID_STR:
    logger.critical("Eʀʀᴏʀ: AUTHORIZED_USER_ID (Admin ID) ɴᴏᴛ ғᴏᴜɴᴅ ɪɴ .env ғɪʟᴇ ᴏʀ ᴇɴᴠɪʀᴏɴᴍᴇɴᴛ ᴠᴀʀɪᴀʙʟᴇs.")
    sys.exit(1)

try:
    ADMIN_USER_ID = int(ADMIN_USER_ID_STR)
except ValueError:
    logger.critical(f"Eʀʀᴏʀ: Iɴᴠᴀʟɪᴅ AUTHORIZED_USER_ID '{ADMIN_USER_ID_STR}'. Mᴜsᴛ ʙᴇ ᴀɴ ɪɴᴛᴇɢᴇʀ.")
    sys.exit(1)

# --- Filesystem Configuration ---
_start_dir_env = os.getenv("START_DIRECTORY")
if _start_dir_env:
    _start_path_candidate = Path(_start_dir_env)
    try:
        if _start_path_candidate.is_dir():
            START_DIRECTORY = str(_start_path_candidate.resolve())
            logger.info(f"Using START_DIRECTORY from environment: {START_DIRECTORY}")
        else:
            START_DIRECTORY = str(Path.home().resolve())
            logger.warning(f"Wᴀʀɴɪɴɢ: START_DIRECTORY '{_start_dir_env}' ɴᴏᴛ ғᴏᴜɴᴅ ᴏʀ ɴᴏᴛ ᴀ ᴅɪʀᴇᴄᴛᴏʀʏ. Dᴇғᴀᴜʟᴛɪɴɢ ᴛᴏ ʜᴏᴍᴇ: {START_DIRECTORY}")
    except Exception as e:
         START_DIRECTORY = str(Path.home().resolve())
         logger.error(f"Eʀʀᴏʀ ᴄʜᴇᴄᴋɪɴɢ START_DIRECTORY '{_start_dir_env}': {e}. Dᴇғᴀᴜʟᴛɪɴɢ ᴛᴏ ʜᴏᴍᴇ: {START_DIRECTORY}")
else:
    START_DIRECTORY = str(Path.home().resolve())
    logger.info(f"START_DIRECTORY not set in environment. Defaulting to home: {START_DIRECTORY}")

START_DIRECTORY_PATH = Path(START_DIRECTORY).resolve()

# --- Constants ---
MAX_BUTTONS_PER_ROW = 3
MAX_FILENAME_DISPLAY_LENGTH = 28
ITEMS_PER_PAGE = 24
MAX_CALLBACK_DATA_LENGTH = 64
SEARCH_RESULTS_LIMIT = 100
MIN_CALLBACK_INTERVAL = 0.8 # Seconds
LOG_FILE_NAME = "bot_activity.log"
AUTHORIZED_USERS_FILE = "authorized_users.json"


# --- Callback Data Prefixes ---
CB_PREFIX_NAV_DIR = "d:"
CB_PREFIX_NAV_FILE = "f:"
CB_PREFIX_NAV_PAGE = "p:"
CB_PREFIX_NAV_PARENT = "up"
CB_PREFIX_NAV_ROOT = "rt"
# CB_PREFIX_SRCH_START = "s_go" # No longer needed, search is automatic
CB_PREFIX_SRCH_BACK = "s_bk"
CB_PREFIX_SRCH_DIR = "sd:"
CB_PREFIX_SRCH_FILE = "sf:"
# CB_PREFIX_SRCH_CANCEL = "s_cl" # Cancel is a command /cancel
CB_PREFIX_NOOP = "noop"
CB_PREFIX_ACCEPT_USER = "au:"
CB_PREFIX_REJECT_USER = "ru:"
CB_PREFIX_DISMISS_ADMIN_MSG = "adm_d:"


# --- Conversation States for Search (No longer used as search is not a conversation) ---
# ASKING_SEARCH_TERM = 0 # Removed

# --- User Data Keys ---
UD_KEY_CURRENT_PATH = "current_path"
UD_KEY_CURRENT_PAGE = "current_page"
UD_KEY_VIEW_ITEMS = "view_items" # Items currently displayed in folder view
UD_KEY_SEARCH_RESULTS = "search_results" # Results from the last automatic text search
UD_KEY_SEARCH_BASE_PATH = "search_base_path" # Path from which the last search was initiated
UD_KEY_LAST_CB_TIME = "last_cb_time"
UD_KEY_CURRENT_MESSAGE_ID = "current_message_id" # To edit messages with photo

# Made by: Zaky1million 😊♥️
# For contact or project requests: https://t.me/Zaky1million
# Please keep this credit as a sign of respect and support.
# Keep going, developer!
# Every great project starts with a single line of code.
# Believe in your skills and never stop learning.
# You're not just coding – you're creating magic.
# Your future self will thank you for the effort you put in today.
