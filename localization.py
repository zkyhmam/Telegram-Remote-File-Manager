# -*- coding: utf-8 -*-
"""
Stores all user-facing strings for the bot, using HTML formatting.
"""
import html

def escape_html(text: str) -> str:
    """Escapes essential HTML characters <, >, &."""
    return html.escape(str(text), quote=False) # quote=False doesn't escape "

# --- General ---
ACCESS_DENIED = "⛔ <b>Aᴄᴄᴇss Dᴇɴɪᴇᴅ.</b>"
INTERNAL_ERROR = "❌ Aɴ ɪɴᴛᴇʀɴᴀʟ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ. Pʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ."
INTERNAL_ERROR_LOGGED = "⚠️ Sᴏʀʀʏ, ᴀɴ ᴜɴᴇxᴘᴇᴄᴛᴇᴅ ɪɴᴛᴇʀɴᴀʟ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ. Tʜᴇ ᴅᴇᴛᴀɪʟs ʜᴀᴠᴇ ʙᴇᴇɴ ʟᴏɢɢᴇᴅ."
ACTION_UNKNOWN = "🤔 Uɴᴋɴᴏᴡɴ ᴀᴄᴛɪᴏɴ."
INVALID_FORMAT = "🤔 Iɴᴠᴀʟɪᴅ ᴅᴀᴛᴀ ғᴏʀᴍᴀᴛ."
STALE_DATA_ERROR = "⚠️ <b>Eʀʀᴏʀ:</b> Dᴀᴛᴀ ᴍɪɢʜᴛ ʙᴇ ᴏᴜᴛᴅᴀᴛᴇᴅ. Pʟᴇᴀsᴇ ᴛʀʏ ʀᴇғʀᴇsʜɪɴɢ ᴛʜᴇ ᴠɪᴇᴡ."
INVALID_INDEX_ERROR = "❌ <b>Eʀʀᴏʀ:</b> Iɴᴠᴀʟɪᴅ ɪɴᴅᴇx."

# --- Start & Help ---
WELCOME_MESSAGE = "❧ Wᴇʟᴄᴏᴍᴇ {user_mention}! Tʜɪs ʙᴏᴛ ʜᴇʟᴘs ʏᴏᴜ ᴍᴀɴᴀɢᴇ ғɪʟᴇs ʀᴇᴍᴏᴛᴇʟʏ." # User mention is already HTML safe
STARTING_FOLDER = "🌱 <b>Sᴛᴀʀᴛɪɴɢ Fᴏʟᴅᴇʀ:</b>"
# Using HTML tags in HELP_TEXT
HELP_TEXT = """
🤖 <b>Bᴏᴛ Hᴇʟᴘ</b>

<code>/start</code> - Sᴛᴀʀᴛ ᴏʀ ʀᴇsᴇᴛ ᴛʜᴇ ʙᴏᴛ ᴛᴏ ᴛʜᴇ ᴍᴀɪɴ ᴅɪʀᴇᴄᴛᴏʀʏ.
<code>/help</code> - Sʜᴏᴡ ᴛʜɪs ʜᴇʟᴘ ᴍᴇssᴀɢᴇ.

🧭 <b>Nᴀᴠɪɢᴀᴛɪᴏɴ:</b>
 - U̷s̷ᴇ̷ ᴛ̷ʜ̷ᴇ̷ ʙ̷ᴜ̷ᴛ̷ᴛ̷ᴏ̷ɴ̷s̷ ᴛ̷ᴏ̷ ɴ̷ᴀ̷ᴠ̷ɪ̷ɢ̷ᴀ̷ᴛ̷ᴇ̷ ᴛ̷ʜ̷ʀ̷ᴏ̷ᴜ̷ɢ̷ʜ̷ ғ̷ᴏ̷ʟ̷ᴅ̷ᴇ̷ʀ̷s̷ ᴀ̷ɴ̷ᴅ̷ ᴘ̷ᴀ̷ɢ̷ᴇ̷s̷.
 - <code>⬅️ Bᴀᴄᴋ</code>: Gᴏ ᴛᴏ ᴛʜᴇ ᴘᴀʀᴇɴᴛ ғᴏʟᴅᴇʀ.
 - <code>🏠 Rᴏᴏᴛ</code>: Gᴏ ᴛᴏ ᴛʜᴇ ɪɴɪᴛɪᴀʟ sᴛᴀʀᴛ ᴅɪʀᴇᴄᴛᴏʀʏ.
 - <code>◀️ Pʀᴇᴠ</code> / <code>Nᴇxᴛ ▶️</code>: Sᴡɪᴛᴄʜ ʙᴇᴛᴡᴇᴇɴ ʟɪsᴛ ᴘᴀɢᴇs.
 - <code>📄 X / Y</code>: Sʜᴏᴡs ᴄᴜʀʀᴇɴᴛ ᴘᴀɢᴇ ᴀɴᴅ ᴛᴏᴛᴀʟ ᴘᴀɢᴇs.

📁 <b>Fɪʟᴇs & Fᴏʟᴅᴇʀs:</b>
 - Cʟɪᴄᴋ ᴀ ғᴏʟᴅᴇʀ ɴᴀᴍᴇ (<code>📁</code> ᴏʀ <code>🔗</code> ғᴏʀ ʟɪɴᴋᴇᴅ ғᴏʟᴅᴇʀ) ᴛᴏ ᴏᴘᴇɴ ɪᴛ.
 - Cʟɪᴄᴋ ᴀ ғɪʟᴇ ɴᴀᴍᴇ (ᴡɪᴛʜ ɪᴛs ɪᴄᴏɴ ᴏʀ <code>🔗</code> ғᴏʀ ʟɪɴᴋᴇᴅ ғɪʟᴇ) ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ ɪᴛ.

🔍 <b>Sᴇᴀʀᴄʜ:</b>
 - Pʀᴇss <code>🔍 Sᴇᴀʀᴄʜ Hᴇʀᴇ</code> ᴛᴏ sᴇᴀʀᴄʜ ɪɴsɪᴅᴇ ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ғᴏʟᴅᴇʀ ᴀɴᴅ sᴜʙғᴏʟᴅᴇʀs.
 - Sᴇᴀʀᴄʜ sᴜᴘᴘᴏʀᴛs <code>*</code> ᴀs ᴀ ᴡɪʟᴅᴄᴀʀᴅ (e.g., <code>*.txt</code>).
 - Cᴀsᴇ-ɪɴsᴇɴsɪᴛɪᴠᴇ.

✨ <b>Nᴏᴛᴇs:</b>
 - Rᴀᴘɪᴅʟʏ ᴄʟɪᴄᴋɪɴɢ ʙᴜᴛᴛᴏɴs ᴍᴀʏ sʜᴏᴡ ᴀ ᴘᴏᴘᴜᴘ ᴡɪᴛʜ ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ʟᴏᴄᴀᴛɪᴏɴ.
"""

# --- Filesystem & Browsing ---
CURRENT_PATH = "📍 <b>Cᴜʀʀᴇɴᴛ Pᴀᴛʜ:</b>"
PAGE_NUMBER = "📄 Pᴀɢᴇ {current} ᴏғ {total}"
FOLDER_EMPTY = "<i>📂 Fᴏʟᴅᴇʀ ɪs Eᴍᴘᴛʏ</i>"
ERROR_NOT_FOUND = "❌ <b>Eʀʀᴏʀ:</b> Pᴀᴛʜ ɴᴏᴛ ғᴏᴜɴᴅ:"
ERROR_PERMISSION_DENIED = "🚫 <b>Eʀʀᴏʀ:</b> Pᴇʀᴍɪssɪᴏɴ ᴅᴇɴɪᴇᴅ ғᴏʀ:"
ERROR_NOT_A_FOLDER = "⚠️ Tʜɪs ɪs ɴᴏᴛ ᴀ ғᴏʟᴅᴇʀ."
ERROR_NOT_A_FILE = "⚠️ Tʜɪs ɪs ɴᴏᴛ ᴀ ғɪʟᴇ."
ERROR_ITEM_PATH_MISSING = "❌ <b>Eʀʀᴏʀ:</b> Iᴛᴇᴍ ᴘᴀᴛʜ ᴍɪssɪɴɢ."
ERROR_UNEXPECTED_LISTING = "❌ Aɴ ᴜɴᴇxᴘᴇᴄᴛᴇᴅ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ ᴡʜɪʟᴇ ʟɪsᴛɪɴɢ ᴄᴏɴᴛᴇɴᴛs."
ERROR_DISPLAY_UPDATE = "⚠️ Eʀʀᴏʀ ᴜᴘᴅᴀᴛɪɴɢ ᴛʜᴇ ᴠɪᴇᴡ."
ERROR_FATAL_DISPLAY = "❌ <b>Fᴀᴛᴀʟ ᴇʀʀᴏʀ</b> ᴅᴜʀɪɴɢ ғᴏʟᴅᴇʀ ᴅɪsᴘʟᴀʏ."
ERROR_BOT_PERMISSION = "⛔ Tʜᴇ ʙᴏᴛ ᴅᴏᴇsɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪssɪᴏɴ ʜᴇʀᴇ."
BUTTON_LOADING_PAGE = "📄 Lᴏᴀᴅɪɴɢ ᴘᴀɢᴇ {page}..."
BUTTON_GO_UP = "⬆️ Gᴏɪɴɢ ᴜᴘ..."
BUTTON_GO_ROOT = "🏠 Gᴏɪɴɢ ᴛᴏ ʀᴏᴏᴛ..."
BUTTON_OPENING_FOLDER = "📂 Oᴘᴇɴɪɴɢ: {name}"
BUTTON_PREPARING_FILE = "⏳ Pʀᴇᴘᴀʀɪɴɢ: {name}"
ALERT_ALREADY_ROOT = "🏠 Yᴏᴜ ᴀʀᴇ ᴀʟʀᴇᴀᴅʏ ɪɴ ᴛʜᴇ ʀᴏᴏᴛ ᴅɪʀᴇᴄᴛᴏʀʏ."
ALERT_CALLBACK_CONTEXT = "📍 {name}\n📄 Pᴀɢᴇ {page}"
BUTTON_BACK = "⬅️ Bᴀᴄᴋ"
BUTTON_ROOT = "🏠 Rᴏᴏᴛ"
BUTTON_SEARCH_HERE = "🔍 Sᴇᴀʀᴄʜ Hᴇʀᴇ"
BUTTON_PREV_PAGE = "◀️ Pʀᴇᴠ"
BUTTON_NEXT_PAGE = "Nᴇxᴛ ▶️"
BUTTON_PAGE_INDICATOR = "📄 {current} / {total}"

# --- File Sending ---
SENDING_FILE = "⬆️ Sᴇɴᴅɪɴɢ ғɪʟᴇ:"
PLEASE_WAIT = "<i>Pʟᴇᴀsᴇ ᴡᴀɪᴛ...</i>"
ERROR_SEND_NOT_FOUND = "❌ <b>Eʀʀᴏʀ:</b> Fɪʟᴇ ɴᴏᴛ ғᴏᴜɴᴅ (ᴍᴀʏʙᴇ ɪᴛ ᴡᴀs ᴅᴇʟᴇᴛᴇᴅ?)."
ERROR_SEND_PERMISSION = "🚫 <b>Eʀʀᴏʀ:</b> Pᴇʀᴍɪssɪᴏɴ ᴅᴇɴɪᴇᴅ ᴛᴏ ʀᴇᴀᴅ ғɪʟᴇ:"
ERROR_SEND_NETWORK = "⏳ Nᴇᴛᴡᴏʀᴋ ᴇʀʀᴏʀ ᴏʀ ᴛɪᴍᴇᴏᴜᴛ ᴡʜɪʟᴇ sᴇɴᴅɪɴɢ ғɪʟᴇ. Yᴏᴜ ᴍᴀʏ ɴᴇᴇᴅ ᴛᴏ ᴛʀʏ ᴀɢᴀɪɴ."
ERROR_SEND_TOO_LARGE = "🐘 <b>Eʀʀᴏʀ:</b> Fɪʟᴇ ɪs ᴛᴏᴏ ʟᴀʀɢᴇ ᴛᴏ sᴇɴᴅ ᴠɪᴀ ᴛʜᴇ ʙᴏᴛ (ᴛʏᴘɪᴄᴀʟʟʏ 50MB ʟɪᴍɪᴛ)."
ERROR_SEND_TG_INTERNAL = "❓ Tᴇʟᴇɢʀᴀᴍ ᴇʀʀᴏʀ ᴡʜɪʟᴇ ʜᴀɴᴅʟɪɴɢ ᴛʜᴇ ғɪʟᴇ. Tʜɪs ᴍɪɢʜᴛ ʙᴇ ᴛᴇᴍᴘᴏʀᴀʀʏ."
ERROR_SEND_TG_BADREQUEST = "⚠️ Tᴇʟᴇɢʀᴀᴍ ᴇʀʀᴏʀ ᴡʜɪʟᴇ sᴇɴᴅɪɴɢ ғɪʟᴇ:"
ERROR_SEND_UNEXPECTED = "❌ Uɴᴇxᴘᴇᴄᴛᴇᴅ ᴇʀʀᴏʀ ᴡʜɪʟᴇ sᴇɴᴅɪɴɢ ғɪʟᴇ {filename}."
ERROR_OS_CHECK_BEFORE_SEND = "🚫 OS ᴇʀʀᴏʀ ᴄʜᴇᴄᴋɪɴɢ ғɪʟᴇ ʙᴇғᴏʀᴇ sᴇɴᴅ."
ERROR_SEND_NOT_A_VALID_FILE = "❌ <b>Eʀʀᴏʀ:</b> Tʜᴇ sᴘᴇᴄɪғɪᴇᴅ ᴘᴀᴛʜ ɪs ɴᴏᴛ ᴀ ᴠᴀʟɪᴅ ғɪʟᴇ ᴏʀ ɴᴏ ʟᴏɴɢᴇʀ ᴇxɪsᴛs."


# --- Search ---
SEARCH_STARTING = "🔍 Sᴛᴀʀᴛɪɴɢ sᴇᴀʀᴄʜ..."
SEARCH_PROMPT = "🔍 <b>Eɴᴛᴇʀ ᴛʜᴇ sᴇᴀʀᴄʜ ᴛᴇʀᴍ</b> ғᴏʀ ғɪʟᴇs/ғᴏʟᴅᴇʀs ᴡɪᴛʜɪɴ:"
SEARCH_PROMPT_HINT = "<i>(U̷s̷ᴇ̷ * ᴀ̷s̷ ᴀ̷ ᴡ̷ɪʟ̷ᴅ̷ᴄ̷ᴀ̷ʀ̷ᴅ̷,̷ ᴄ̷ᴀ̷s̷ᴇ̷-ɪ̷ɴ̷s̷ᴇ̷ɴ̷s̷ɪ̷ᴛ̷ɪ̷ᴠ̷ᴇ̷)</i>" # Simpler hint, use italics
SEARCH_PROMPT_CANCEL = "Tʏᴘᴇ <code>/cancel</code> ᴛᴏ ᴄᴀɴᴄᴇʟ."
SEARCH_INPUT_PLACEHOLDER = "Sᴇᴀʀᴄʜ ᴛᴇʀᴍ..."
SEARCH_ERROR_STARTING = "❌ Eʀʀᴏʀ sᴛᴀʀᴛɪɴɢ ᴛʜᴇ sᴇᴀʀᴄʜ ᴘʀᴏᴄᴇss."
SEARCH_ERROR_SEND_PROMPT = "⛔ Tʜᴇ ʙᴏᴛ ᴅᴏᴇsɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪssɪᴏɴ ᴛᴏ sᴇɴᴅ ᴀ ᴍᴇssᴀɢᴇ ʜᴇʀᴇ."
SEARCH_PERFORMING = "⏳ Sᴇᴀʀᴄʜɪɴɢ ғᴏʀ <code>{term}</code> ɪɴ <code>{path}</code>..." # Use escape_html on term/path when formatting
SEARCH_ERROR_PERMISSION = "🚫 Pᴇʀᴍɪssɪᴏɴ ᴅᴇɴɪᴇᴅ ᴅᴜʀɪɴɢ sᴇᴀʀᴄʜ ɪɴɪᴛɪᴀᴛɪᴏɴ."
SEARCH_ERROR_GENERAL = "❌ Aɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ ᴅᴜʀɪɴɢ ᴛʜᴇ sᴇᴀʀᴄʜ: {error}" # Use escape_html on error when formatting
SEARCH_NO_RESULTS = "🤷 Nᴏ ʀᴇsᴜʟᴛs ғᴏᴜɴᴅ ғᴏʀ <code>{term}</code> ɪɴ <code>{path}</code>." # Use escape_html on term/path
SEARCH_FOUND_RESULTS = "🔍 Fᴏᴜɴᴅ <b>{count}</b> ʀᴇsᴜʟᴛ(s) ғᴏʀ <code>{term}</code>:" # Use escape_html on count/term
SEARCH_FOUND_LIMITED_RESULTS = "🔍 Fᴏᴜɴᴅ <b>{count_display}</b> ʀᴇsᴜʟᴛ(s) (sʜᴏᴡɪɴɢ ғɪʀsᴛ {limit}) ғᴏʀ <code>{term}</code>:" # Use escape_html
SEARCH_BUTTON_ERROR = "<i>(Eʀʀᴏʀ ᴄʀᴇᴀᴛɪɴɢ ʀᴇsᴜʟᴛ ʙᴜᴛᴛᴏɴs)</i>"
SEARCH_SEND_RESULT_ERROR = "❌ Eʀʀᴏʀ ᴅɪsᴘʟᴀʏɪɴɢ sᴇᴀʀᴄʜ ʀᴇsᴜʟᴛs."
SEARCH_INVALID_INDEX_ERROR = "❌ <b>Eʀʀᴏʀ:</b> Iɴᴠᴀʟɪᴅ sᴇᴀʀᴄʜ ʀᴇsᴜʟᴛ ɪɴᴅᴇx."
SEARCH_STALE_RESULTS_ERROR = "⚠️ <b>Eʀʀᴏʀ:</b> Sᴇᴀʀᴄʜ ʀᴇsᴜʟᴛ ᴅᴀᴛᴀ ɪs ᴏᴜᴛᴅᴀᴛᴇᴅ. Pʟᴇᴀsᴇ sᴇᴀʀᴄʜ ᴀɢᴀɪɴ."
SEARCH_RESULT_PATH_MISSING_ERROR = "❌ <b>Eʀʀᴏʀ:</b> Rᴇsᴜʟᴛ ᴘᴀᴛʜ ɪs ᴍɪssɪɴɢ."
SEARCH_RESULT_NOT_FOLDER = "⚠️ Tʜɪs ʀᴇsᴜʟᴛ ɪs ɴᴏᴛ ᴀ ғᴏʟᴅᴇʀ."
SEARCH_RESULT_NOT_FILE = "⚠️ Tʜɪs ʀᴇsᴜʟᴛ ɪs ɴᴏᴛ ᴀ ғɪʟᴇ."
SEARCH_OPENING_RESULT = "📂 Oᴘᴇɴɪɴɢ sᴇᴀʀᴄʜ ʀᴇsᴜʟᴛ: {name}"
SEARCH_PREPARING_RESULT = "⏳ Pʀᴇᴘᴀʀɪɴɢ sᴇᴀʀᴄʜ ʀᴇsᴜʟᴛ: {name}"
SEARCH_CANCELLED = "🚫 Sᴇᴀʀᴄʜ ᴄᴀɴᴄᴇʟʟᴇᴅ. Rᴇᴛᴜʀɴɪɴɢ ᴛᴏ ʙʀᴏᴡsᴇʀ..."
SEARCH_INVALID_COMMAND = "⚠️ Iɴᴠᴀʟɪᴅ ᴄᴏᴍᴍᴀɴᴅ ᴅᴜʀɪɴɢ sᴇᴀʀᴄʜ. U̷s̷ᴇ̷ <code>/cancel</code> ᴛ̷ᴏ̷ ᴇ̷x̷ɪ̷ᴛ̷."
SEARCH_INVALID_INPUT = "⚠️ Pʟᴇᴀsᴇ ᴇɴᴛᴇʀ ᴛʜᴇ sᴇᴀʀᴄʜ ᴛᴇʀᴍ ᴀs ᴛᴇxᴛ ᴏʀ ᴜsᴇ <code>/cancel</code>."
BUTTON_SEARCH_BACK_TO_BROWSER = "↩️ Bᴀᴄᴋ ᴛᴏ Bʀᴏᴡsᴇʀ"
BUTTON_SEARCH_RETURN_BROWSER = "↩️ Rᴇᴛᴜʀɴɪɴɢ ᴛᴏ ʙʀᴏᴡsᴇʀ..."
ALERT_SEARCH_CANNOT_FIND_ORIGINAL_PATH = "⚠️ <b>Eʀʀᴏʀ:</b> Cᴀɴɴᴏᴛ ᴅᴇᴛᴇʀᴍɪɴᴇ ᴏʀɪɢɪɴᴀʟ ғᴏʟᴅᴇʀ. Rᴇᴛᴜʀɴɪɴɢ ᴛᴏ ʀᴏᴏᴛ."


# Made by: Zaky1million 😊♥️
# For contact or project requests: https://t.me/Zaky1million
# Please keep this credit as a sign of respect and support.
# Keep going, developer!
# Every great project starts with a single line of code.
# Believe in your skills and never stop learning.
# You're not just coding – you're creating magic.
# Your future self will thank you for the effort you put in today.


