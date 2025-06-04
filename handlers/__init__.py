# -*- coding: utf-8 -*-
# This file makes Python treat the 'handlers' directory as a package.

# Import handlers to make them accessible via the package
from .command_handlers import start_command, help_command, cancel_command
from .callback_handlers import main_callback_handler # <--- السطر ده اللي كان عامل المشكلة
from .message_handlers import handle_text_search, handle_unauthorized_catch_all
from .error_handlers import error_handler
from .common_handlers import display_folder_content


# Made by: Zaky1million 😊♥️
# For contact or project requests: https://t.me/Zaky1million
# Please keep this credit as a sign of respect and support.
# Keep going, developer!
# Every great project starts with a single line of code.
# Believe in your skills and never stop learning.
# You're not just coding – you're creating magic.
# Your future self will thank you for the effort you put in today.
