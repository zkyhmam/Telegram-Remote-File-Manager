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
AUTHORIZED_USER_ID_STR = os.getenv("AUTHORIZED_USER_ID")

if not TOKEN:
    logger.critical("Eʀʀᴏʀ: TELEGRAM_BOT_TOKEN ɴᴏᴛ ғᴏᴜɴᴅ ɪɴ .env ғɪʟᴇ ᴏʀ ᴇɴᴠɪʀᴏɴᴍᴇɴᴛ ᴠᴀʀɪᴀʙʟᴇs.")
    sys.exit(1)

if not AUTHORIZED_USER_ID_STR:
    logger.critical("Eʀʀᴏʀ: AUTHORIZED_USER_ID ɴᴏᴛ ғᴏᴜɴᴅ ɪɴ .env ғɪʟᴇ ᴏʀ ᴇɴᴠɪʀᴏɴᴍᴇɴᴛ ᴠᴀʀɪᴀʙʟᴇs.")
    sys.exit(1)

try:
    AUTHORIZED_USER_ID = int(AUTHORIZED_USER_ID_STR)
except ValueError:
    logger.critical(f"Eʀʀᴏʀ: Iɴᴠᴀʟɪᴅ AUTHORIZED_USER_ID '{AUTHORIZED_USER_ID_STR}'. Mᴜsᴛ ʙᴇ ᴀɴ ɪɴᴛᴇɢᴇʀ.")
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
MIN_CALLBACK_INTERVAL = 0.8
LOG_FILE_NAME = "bot_activity.log"

# --- Callback Data Prefixes ---
CB_PREFIX_NAV_DIR = "d:"
CB_PREFIX_NAV_FILE = "f:"
CB_PREFIX_NAV_PAGE = "p:"
CB_PREFIX_NAV_PARENT = "up"
CB_PREFIX_NAV_ROOT = "rt"
CB_PREFIX_SRCH_START = "s_go"
CB_PREFIX_SRCH_BACK = "s_bk"
CB_PREFIX_SRCH_DIR = "sd:"
CB_PREFIX_SRCH_FILE = "sf:"
CB_PREFIX_SRCH_CANCEL = "s_cl" # <-- New prefix for search cancel button
CB_PREFIX_NOOP = "noop"

# --- Conversation States for Search ---
ASKING_SEARCH_TERM = 0

# --- User Data Keys ---
UD_KEY_CURRENT_PATH = "current_path"
UD_KEY_CURRENT_PAGE = "current_page"
UD_KEY_VIEW_ITEMS = "view_items"
UD_KEY_SEARCH_RESULTS = "search_results"
UD_KEY_SEARCH_BASE_PATH = "search_base_path"
# UD_KEY_SEARCH_PROMPT_MSG_ID = "search_prompt_msg_id" # Will store ID of message *with* cancel button
UD_KEY_SEARCH_PROMPT_MSG_ID = "search_prompt_cancel_msg_id" # <-- Renamed for clarity
UD_KEY_SEARCH_FORCE_REPLY_MSG_ID = "search_force_reply_msg_id" # <-- New key for ForceReply message ID
UD_KEY_LAST_CB_TIME = "last_cb_time"

# Made by: Zaky1million 😊♥️
# For contact or project requests: https://t.me/Zaky1million
# Please keep this credit as a sign of respect and support.
# Keep going, developer!
# Every great project starts with a single line of code.
# Believe in your skills and never stop learning.
# You're not just coding – you're creating magic.
# Your future self will thank you for the effort you put in today.
