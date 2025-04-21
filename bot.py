#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Telegram Bot for Remote File Management (Visually Styled - Zaky1million)

Main entry point for the bot application. Initializes the application,
sets up logging, registers handlers, sets command list and starts polling.
Includes Rich library integration for enhanced console output. Uses HTML ParseMode for Telegram.
(Functional structure based on original bot (7).py)
"""

import logging
import sys
import os
import asyncio
import time # Needed for sleep in animations
from pathlib import Path # Added for path handling

from telegram import Update, constants, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
    ConversationHandler,
    BaseHandler
)

# Import Rich components
from rich.logging import RichHandler
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import box
from rich.align import Align
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.style import Style
from rich.table import Table
from rich.padding import Padding # Added
from rich.rule import Rule # Added

# Import configuration, handlers, and constants (Keep original structure)
import config
import localization as loc
# --- KEEP ORIGINAL HANDLER IMPORTS ---
from handlers.command_handlers import start_command, help_command
from handlers.callback_handlers import main_callback_handler
# Import cancel_search_command from its original location (conversation_handlers)
from handlers.conversation_handlers import receive_search_term, cancel_search_command
from handlers.error_handlers import error_handler
# --- END ORIGINAL HANDLER IMPORTS ---

from config import (
    TOKEN, AUTHORIZED_USER_ID, START_DIRECTORY_PATH, LOG_FILE_NAME,
    ASKING_SEARCH_TERM, CB_PREFIX_SRCH_START
)

# --- Rich Console Initialization (Adopted Style) ---
console = Console(highlight=False)

# --- Constants for Visuals (Adopted Style) ---
HEADER_COLOR = "#00BFFF"
ACCENT_COLOR = "#FF69B4"
INFO_COLOR = "#00BFFF"
WARN_COLOR = "bold yellow"
ERROR_COLOR = "bold red"
SUCCESS_COLOR = "bold green"
DIM_COLOR = "dim white"
CONTACT_GRADIENT = ["#00FFFF", "#33CCFF", "#6699FF", "#9966FF", "#CC33FF", "#FF00FF", "#FF33CC", "#FF6699", "#FF9966"]
ZAKY_COLORS = ["#FF00FF", "#FF33FF", "#FF66FF", "#FF99FF"]

# --- Logging Setup using Rich (Adopted Style) ---
log_format_file = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
log_format_console = "%(message)s"
log_datefmt = "%Y-%m-%d %H:%M:%S"

logging.basicConfig(
    level=logging.INFO,
    format=log_format_file,
    datefmt=log_datefmt,
    handlers=[
        logging.FileHandler(config.LOG_FILE_NAME, encoding='utf-8'),
        RichHandler( # Adopted RichHandler setup
            console=console, rich_tracebacks=True, tracebacks_show_locals=False,
            markup=True, show_time=True, show_level=True, show_path=False,
            log_time_format="[%X]",
            keywords=["START", "SUCCESS", "FAILURE", "WARN", "INFO", "ERROR", "SECURITY", "INIT", "CONFIG", "HANDLER", "POLLING", "SHUTDOWN"]
        )
    ]
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram.vendor.ptb_urllib3.urllib3").setLevel(logging.WARNING)
logging.getLogger("apscheduler").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# --- Security Warning (Adopted Style) ---
def check_security_risks():
    if hasattr(os, 'geteuid'):
        is_root = os.geteuid() == 0
        try:
            start_path = Path(START_DIRECTORY_PATH).resolve()
            is_root_dir = start_path == Path("/").resolve()
        except Exception as e:
            logger.error(f"SECURITY: Error resolving START_DIRECTORY_PATH '{START_DIRECTORY_PATH}': {e}")
            is_root_dir = False

        if is_root_dir and is_root:
            logger.warning(f"[bold red]!!! SECURITY RISK !!![/] Bot configured for '/' and running as root!")
        elif is_root_dir:
            logger.warning(f"[bold yellow]! SECURITY RISK ![/] Bot configured for '/'. Ensure permissions are restricted.")
        elif is_root:
            logger.warning(f"[yellow]! Potential Risk ![/] Bot is running as root. Consider using a non-privileged user.")

# --- Visual Component Functions (Adopted Style) ---

def create_zaky_logo_text() -> Text:
    """Creates the ZAKY ASCII logo with static colors (Adopted Style)."""
    logo_lines = [
        ("███████╗", 0), (" █████╗ ", 1), ("██╗  ██╗", 2), ("██╗   ██╗", 3),
        ("╚══███╔╝", 0), ("██╔══██╗", 1), ("██║ ██╔╝", 2), ("╚██╗ ██╔╝", 3),
        ("  ███╔╝ ", 0), ("███████║", 1), ("█████╔╝ ", 2), (" ╚████╔╝ ", 3),
        (" ███╔╝  ", 0), ("██╔══██║", 1), ("██╔═██╗ ", 2), ("  ╚██╔╝  ", 3),
        ("███████╗", 0), ("██║  ██║", 1), ("██║  ██╗", 2), ("   ██║   ", 3),
        ("╚══════╝", 0), ("╚═╝  ╚═╝", 1), ("╚═╝  ╚═╝", 2), ("   ╚═╝   ", 3),
    ]
    num_colors = len(ZAKY_COLORS)
    logo_text = Text()
    current_line = 0
    for i, (text, color_index) in enumerate(logo_lines):
        line_num = i // 4
        if line_num > current_line: logo_text.append("\n"); current_line = line_num
        style = f"bold {ZAKY_COLORS[color_index % num_colors]}"
        logo_text.append(text, style=style)
    return logo_text

def create_million_text() -> Text:
    """Creates the '1 MILLION 👑' text with static gradient colors (Adopted Style)."""
    name = "1 MILLION 👑"
    text = Text(); num_colors = len(CONTACT_GRADIENT)
    for i, char in enumerate(name):
        if char == ' ': text.append(" "); continue
        style = f"bold {CONTACT_GRADIENT[i % num_colors]}"
        text.append(char, style=style)
    return text

def create_contact_link() -> Text:
    """Creates the contact link with static gradient colors (Adopted Style)."""
    link_text = "https://t.me/Zaky1million"; link_url = link_text
    text = Text.assemble(("For contact or project requests: ", DIM_COLOR))
    num_colors = len(CONTACT_GRADIENT)
    for i, char in enumerate(link_text):
        style = f"bold {CONTACT_GRADIENT[i % num_colors]} link {link_url}"
        text.append(char, style=style)
    return text

def create_config_table() -> Table:
    """Creates the configuration information table (Adopted Style)."""
    table = Table(box=box.ROUNDED, border_style=INFO_COLOR, show_header=False,
                  title="[bold]Bot Configuration[/]", title_style=f"bold {INFO_COLOR}",
                  padding=(0, 2), width=80) # Fixed width for consistency
    table.add_column("Property", style=SUCCESS_COLOR, justify="right", width=25)
    table.add_column("Value", style=f"bold {INFO_COLOR}", justify="left", no_wrap=False)
    start_dir_str = str(START_DIRECTORY_PATH); log_file_str = str(LOG_FILE_NAME)
    table.add_row("🔑 Authorized User ID", f"[cyan]{AUTHORIZED_USER_ID}[/]")
    table.add_row("📁 Root Directory", f"[italic cyan]{start_dir_str}[/]")
    table.add_row("📜 Log File", f"[italic cyan]{log_file_str}[/]")
    table.add_row("💬 Parse Mode", f"[cyan]HTML[/]") # Kept from original bot(7) structure
    return table

def create_inspiration_panel() -> Panel:
    """Creates the inspirational message panel (Adopted Style)."""
    inspirational_msg = Text.assemble(
        ("Every great project starts with a single line of code.\n", "bold green"),
        ("Believe in your skills and never stop learning.\n", "bold yellow"),
        ("You're not just coding – you're creating magic.\n", "bold magenta"),
        ("Your future self will thank you for the effort you put in today.", "bold cyan")
    )
    return Panel(Align.center(inspirational_msg, vertical="middle"),
                 title="[bold]✨ Words of Inspiration ✨[/]", title_align="center",
                 border_style=ACCENT_COLOR, box=box.DOUBLE_EDGE,
                 padding=(1, 2), width=80) # Fixed width

def display_progress_animation(text: str, total: float, sleep_time: float, color: str, transient: bool = True) -> None:
    """Displays a progress bar animation using Rich Progress (Adopted Style)."""
    total = max(1, int(total)); sleep_per_step = sleep_time / total if total > 0 else 0.01
    progress = Progress(SpinnerColumn(spinner_name="dots", style=f"bold {color}"),
                        TextColumn(f"[bold {color}]{text}[/]"),
                        BarColumn(bar_width=None, style=color, complete_style=SUCCESS_COLOR),
                        TimeElapsedColumn(), console=console, transient=transient, expand=True)
    try:
        with progress:
            task = progress.add_task(f"[{color}]Processing...", total=total)
            for i in range(total + 1):
                progress.update(task, completed=i); time.sleep(sleep_per_step)
            time.sleep(0.1 if transient else 0)
    except Exception as e:
        logger.error(f"Error displaying progress animation '{text}': {e}")
        console.print(f"[bold {color}]{text}... (Animation Error)[/]")

def display_static_startup_info():
    """Displays the startup information sequentially and statically (Adopted Style)."""
    console.print(Rule(f"[bold {HEADER_COLOR}]Telegram File Manager Bot[/]", style=HEADER_COLOR, align="center"))
    # Use the new logo function
    console.print(Padding(Align.center(create_zaky_logo_text()), (1, 0)))
    # Use the new million text function
    console.print(Padding(Align.center(create_million_text()), (0, 0, 1, 0)))
    console.print(Rule(style=HEADER_COLOR, align="center"))
    console.print(Padding(Align.center(create_config_table()), (1, 0)))
    console.print(Padding(Align.center(create_inspiration_panel()), (1, 0)))
    console.print(Padding(Align.center(create_contact_link()), (1, 0, 1, 0)))
    console.print(Rule(style=HEADER_COLOR, align="center"))

# --- Bot Command Setup (Keep original) ---
async def post_init(application: Application) -> None:
    """Set bot commands after initialization."""
    await application.bot.set_my_commands([
        BotCommand("start", "Start / Reset the bot"),
        BotCommand("help", "Show help message"),
        BotCommand("cancel", "Cancel current operation (like search)")
    ])
    logger.info("Bot command list set.")


# --- Main Function (Apply visual flow, keep original logic) ---
def main() -> None:
    """Starts the bot."""
    console.clear() # Start with clean console
    logger.info("--- INIT: Bot Initialization Sequence Started ---")

    # 1. Initial Boot Animation (Adopted Style)
    display_progress_animation("Booting system", total=100, sleep_time=1.5, color="cyan")

    # 2. Display Static Info (Adopted Style)
    display_static_startup_info()

    logger.info("INIT: Static startup display complete.")
    check_security_risks() # Log warnings after display

    logger.info("INIT: Initializing Telegram Bot Application...")

    # --- Define Conversation Handler (KEEP ORIGINAL STRUCTURE) ---
    # cancel_search_command is correctly imported from conversation_handlers now
    search_fallbacks = [
        CommandHandler('cancel', cancel_search_command, filters=filters.ChatType.PRIVATE),
        MessageHandler(
            filters.COMMAND & filters.ChatType.PRIVATE,
            lambda update, context: update.message.reply_text(
                loc.SEARCH_INVALID_COMMAND, parse_mode=constants.ParseMode.HTML
            )
        ),
        MessageHandler(
            ~filters.TEXT & filters.ChatType.PRIVATE,
             lambda update, context: update.message.reply_text(
                loc.SEARCH_INVALID_INPUT, parse_mode=constants.ParseMode.HTML
            )
        ),
    ]
    search_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(main_callback_handler, pattern=f"^{CB_PREFIX_SRCH_START}$")],
        states={
            ASKING_SEARCH_TERM: [
                MessageHandler(filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE, receive_search_term)
            ],
        },
        fallbacks=search_fallbacks,
        per_message=False,
        per_user=True,
        per_chat=True,
        allow_reentry=True
    )
    # --- END ORIGINAL CONVERSATION HANDLER ---

    # --- Application Setup (KEEP ORIGINAL STRUCTURE) ---
    try:
        application = Application.builder().token(TOKEN).post_init(post_init).build()
        logger.info("INIT: Application built successfully.")
    except Exception as e:
        logger.exception("FATAL: Failed to build Telegram Application.")
        console.print(Panel(f"[{ERROR_COLOR}]Error building Application: {e}[/]", title="[bold red]Fatal Error[/]", border_style="red"))
        sys.exit(1)

    # --- Handler Registration (KEEP ORIGINAL STRUCTURE) ---
    logger.info("HANDLER: Registering handlers...")
    try:
        private_auth_filter = filters.ChatType.PRIVATE & filters.User(user_id=AUTHORIZED_USER_ID)
        application.add_handler(CommandHandler("start", start_command, filters=private_auth_filter))
        application.add_handler(CommandHandler("help", help_command, filters=private_auth_filter))
        application.add_handler(search_conv_handler) # Add conversation handler
        application.add_handler(CallbackQueryHandler(main_callback_handler)) # Main button handler
        application.add_error_handler(error_handler) # Error handler
        logger.info("HANDLER: Handler registration SUCCESS.")
    except Exception as e:
        logger.exception("FATAL: Failed to register handlers.")
        console.print(Panel(f"[{ERROR_COLOR}]Error registering handlers: {e}[/]", title="[bold red]Fatal Error[/]", border_style="red"))
        sys.exit(1)

    # --- Signal Handling (Removed - Use PTB default) ---

    console.print(f"[{SUCCESS_COLOR}]✓ Initialization complete. Starting bot polling...[/]", style=SUCCESS_COLOR)
    console.print(Align.center(f"[{DIM_COLOR}]Press Ctrl+C to stop.[/{DIM_COLOR}]"))
    time.sleep(0.5) # Short pause

    # --- Start Bot (Use PTB default signal handling) ---
    logger.info("POLLING: Starting bot polling...")

    try:
        # Let PTB handle signals by NOT passing stop_signals=[]
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        logger.info("POLLING: run_polling loop finished gracefully.")

    except KeyboardInterrupt:
        logger.info("SHUTDOWN: KeyboardInterrupt detected. Stopping bot...")
    except Exception as e:
        logger.exception("FATAL: An unexpected error occurred during polling.")
        console.print(Panel(f"[{ERROR_COLOR}]Unexpected error during polling: {e}[/]", title="[bold red]Runtime Error[/]", border_style="red"))
    finally:
        # Display final message using adopted style
        logger.info("SHUTDOWN: Bot process finishing.")
        exc_info = sys.exc_info()
        final_message_style = ERROR_COLOR if exc_info[1] and not isinstance(exc_info[1], KeyboardInterrupt) else SUCCESS_COLOR
        console.print(f"\n[{final_message_style}]Bot stopped.[/{final_message_style}]")


if __name__ == '__main__':
    main()


# --- Credits and Motivation (Keep original) ---
# Made by: Zaky1million 😊♥️
# For contact or project requests: https://t.me/Zaky1million
# Please keep this credit as a sign of respect and support.
# Keep going, developer!
# Every great project starts with a single line of code.
# Believe in your skills and never stop learning.
# You're not just coding – you're creating magic.
# Your future self will thank you for the effort you put in today.
