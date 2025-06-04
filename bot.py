#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Telegram Bot for Remote File Management.
Main entry point for the bot application.
Initializes the application, sets up logging, registers handlers,
sets command list and starts polling.
Console output is limited to WARNINGS, ERRORS, and unauthorized access attempts.
"""

import logging
import sys
import os
from pathlib import Path

from telegram import Update, BotCommand, constants
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    PicklePersistence, # For bot_data persistence
    PersistenceInput #  <--- Import الجديد
)

# Import configuration, handlers, and constants
import config
# import localization as loc # Not directly used here, but good for consistency
from handlers import (
    start_command, help_command, cancel_command,
    main_callback_handler,
    handle_text_search, # handle_unauthorized_catch_all is now mostly part of other handlers
    error_handler
)
from utils.auth_utils import load_authorized_users # To load initially

# --- Logging Setup (Simplified) ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(config.LOG_FILE_NAME, encoding='utf-8'),
    ]
)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.WARNING)
console_formatter = logging.Formatter('%(levelname)s: %(name)s - %(message)s')
console_handler.setFormatter(console_formatter)
logging.getLogger().addHandler(console_handler)

logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram.vendor.ptb_urllib3.urllib3").setLevel(logging.WARNING)
logging.getLogger("apscheduler").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


# --- Security Warning Function (Simplified Console Output) ---
def check_security_risks():
    is_root_user = hasattr(os, 'geteuid') and os.geteuid() == 0
    try:
        start_path = Path(config.START_DIRECTORY_PATH).resolve()
        is_root_dir_configured = start_path == Path("/").resolve()
    except Exception as e:
        logger.error(f"Error resolving START_DIRECTORY_PATH '{config.START_DIRECTORY_PATH}': {e}")
        is_root_dir_configured = False

    if is_root_dir_configured and is_root_user:
        logger.warning("!!! SECURITY RISK !!! Bot configured for '/' AND running as root!")
    elif is_root_dir_configured:
        logger.warning("! SECURITY RISK ! Bot configured for '/'. Ensure permissions are strictly limited.")
    elif is_root_user:
        logger.warning("! Potential Risk ! Bot is running as root. Consider a non-privileged user.")

# --- Bot Command Setup ---
async def post_init(application: Application) -> None:
    """Set bot commands after initialization and load authorized users."""
    await application.bot.set_my_commands([
        BotCommand("start", "Sᴛᴀʀᴛ / Rᴇsᴇᴛ ᴛʜᴇ ʙᴏᴛ"),
        BotCommand("help", "Sʜᴏᴡ ʜᴇʟᴘ ᴍᴇssᴀɢᴇ"),
        BotCommand("cancel", "Cᴀɴᴄᴇʟ ᴏᴘ / Cʟᴇᴀʀ sᴇᴀʀᴄʜ")
    ])
    logger.info("Bot command list set.")
    
    # Load authorized users into bot_data for the first time if persistence didn't handle it
    # (PicklePersistence should load it automatically if file exists)
    if 'authorized_ids' not in application.bot_data:
        load_authorized_users(application) # Pass application which has .bot_data
        logger.info(f"Initial authorized users loaded via post_init. Admin ID: {config.ADMIN_USER_ID}")
    else:
        logger.info(f"Authorized users already present in bot_data (likely from persistence). Admin ID: {config.ADMIN_USER_ID}")


# --- Main Function ---
def main() -> None:
    """Starts the bot."""
    logger.info("--- Bot Initialization Sequence Started ---")
    check_security_risks()

    # Configure persistence for bot_data (like authorized users list)
    # The .json file is for human readability and manual backup/restore if needed.
    # PTB's PicklePersistence will use the .pickle file for its own operations.
    # We load from .json if .pickle doesn't exist or on first run logic.
    # Our `save_authorized_users` in `auth_utils` writes to the .json.
    # PTB's persistence writes to the .pickle. We need to keep them in sync or choose one.
    # For simplicity with PTB's built-in persistence, let's rely on PTB to manage the state
    # and our `load_authorized_users` can be a fallback if the pickle doesn't exist initially.

    # This configures what data PTB's persistence system will store.
    # We are primarily interested in bot_data for the dynamic authorized users list.
    persistence_config = PersistenceInput(bot_data=True, chat_data=False, user_data=False)
    
    # The filepath for PicklePersistence. PTB will create/manage this .pickle file.
    # Our manual `authorized_users.json` can serve as a human-readable backup or initial seed.
    # Let's use a distinct name for the pickle file managed by PTB.
    ptb_persistence_file = Path(config.AUTHORIZED_USERS_FILE).with_suffix('.pickle')

    persistence = PicklePersistence(
        filepath=ptb_persistence_file,
        store_data=persistence_config
    )
    logger.info(f"Using PicklePersistence with file: {ptb_persistence_file}")


    logger.info("Initializing Telegram Bot Application...")
    try:
        application = (
            Application.builder()
            .token(config.TOKEN)
            .post_init(post_init) # post_init now also ensures authorized_ids is in bot_data
            .persistence(persistence)
            .build()
        )
        logger.info("Application built successfully.")
    except Exception as e:
        logger.critical(f"FATAL: Failed to build Telegram Application: {e}", exc_info=True)
        sys.exit(1)

    logger.info("Registering handlers...")
    try:
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("cancel", cancel_command))
        application.add_handler(CallbackQueryHandler(main_callback_handler))
        application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE,
            handle_text_search
        ))
        application.add_error_handler(error_handler)
        logger.info("Handler registration SUCCESS.")
    except Exception as e:
        logger.critical(f"FATAL: Failed to register handlers: {e}", exc_info=True)
        sys.exit(1)

    logger.info("Initialization complete. Starting bot polling...")
    try:
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        logger.info("Bot polling finished gracefully.")
    except KeyboardInterrupt:
        logger.info("Shutdown: KeyboardInterrupt detected. Stopping bot...")
    except Exception as e:
        logger.critical(f"FATAL: An unexpected error occurred during polling: {e}", exc_info=True)
    finally:
        logger.info("Bot process finishing.")


if __name__ == '__main__':
    # Initial check/creation of the primary .json file for authorized users
    # This file can act as an initial seed if the .pickle file for PTB persistence doesn't exist.
    auth_json_file_path = Path(config.AUTHORIZED_USERS_FILE)
    if not auth_json_file_path.exists():
        try:
            with open(auth_json_file_path, 'w', encoding='utf-8') as f:
                import json
                # Store as a dictionary with a key, which is more robust for future additions
                json.dump({"authorized_ids": []}, f, indent=2)
            logging.info(f"Created empty {config.AUTHORIZED_USERS_FILE} for initial user data.")
        except Exception as e_create:
            logging.error(f"Could not create {config.AUTHORIZED_USERS_FILE}: {e_create}. Please create it manually with content: {{\"authorized_ids\": []}}")
            sys.exit(1)
    elif auth_json_file_path.stat().st_size == 0 : # If file exists but is empty
        try:
            with open(auth_json_file_path, 'w', encoding='utf-8') as f:
                import json
                json.dump({"authorized_ids": []}, f, indent=2)
            logging.info(f"Initialized empty {config.AUTHORIZED_USERS_FILE} with proper JSON structure.")
        except Exception as e_init_empty:
             logging.error(f"Could not initialize empty {config.AUTHORIZED_USERS_FILE}: {e_init_empty}")
             sys.exit(1)
    main()

# --- Credits and Motivation ---
# Made by: Zaky1million 😊♥️
# For contact or project requests: https://t.me/Zaky1million
# Please keep this credit as a sign of respect and support.
