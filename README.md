
---

## 🚀 Setup & Installation

| Step | Command or Action |
|------|------------------|
| **1. Clone Repository** | `git clone https://github.com/zkyhmam/Remote-file-share-TG.git` |
| **2. Navigate to Folder** | `cd Remote-file-share-TG` |
| **3. Install Requirements** | `pip install -r requirements.txt` |
| **4. Create Config File** | `cp .env.example .env` (Linux/Mac)<br>`copy .env.example .env` (Windows) |
| **5. Edit Configuration** | Set your bot token (`TELEGRAM_BOT_TOKEN`), your primary admin Telegram ID (`AUTHORIZED_USER_ID`), and optionally `START_DIRECTORY`. |
| **6. Create Auth File** | Create an empty file named `authorized_users.json` in the `Remote-file-share-TG` directory. (e.g., `touch authorized_users.json` or create it with `{}` as content) |
| **7. Launch the Bot** | `python bot.py` |

---

## ⚙️ Configuration Details (`.env` file)

| Parameter | Required | Description |
|-----------|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | ✅ | Your unique bot token from [BotFather](https://t.me/BotFather). |
| `AUTHORIZED_USER_ID` | ✅ | Your numerical Telegram ID. This user is the primary Admin. |
| `START_DIRECTORY` | ❌ | The root directory for browsing (defaults to home directory if unset). Bot needs read access. |
| `BOT_IMAGE_URL` | ❌ | URL of the image to display with messages (defaults to `https://i.postimg.cc/SRKg918j/filesharing-plesk-t.jpg` if unset). |

The `authorized_users.json` file will store IDs of additional users authorized by the Admin.

## 🕹️ Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Begin browsing your server files from the root directory. |
| `/help` | Display usage instructions and command list. |
| `/cancel` | Clears current search results or refreshes the view to the current/root directory. |

---

## 🔒 Security Architecture

The bot implements multiple security layers:

* **Primary Admin & Dynamic Authorization:** Only the `AUTHORIZED_USER_ID` and users they approve can use the bot.
* **Admin Notifications:** Admin is alerted to unauthorized access attempts.
* **Directory Containment:** Prevents navigation outside the configured root directory.
* **Symlink Safety:** Symbolic links are verified to ensure they don't bypass security boundaries.
* **Permission Inheritance:** Operates with the permissions of the user executing the bot script.

---

## 💡 Usage Guide

Once your bot is running and you (Admin) are authorized:

### Basic Navigation

1.  **Start Browsing:** Send `/start` to see the contents of your root directory.
2.  **Open Folders:** Tap on any folder name (📁 or 🔗) to view its contents.
3.  **Download Files:** Tap on any file name (e.g., 📝, 🖼️, 🔗) to immediately download it.
4.  **Navigate Up:** Use `⬅️ Back` to move up one directory level.
5.  **Return Home:** Use `🏠 Root` to jump back to your starting directory.
6.  **Move Between Pages:** Use `◀️ Prev` and `Next ▶️` for directories with many items.

### Automatic Search Functionality

1.  Navigate to the directory where you want to search.
2.  Simply type your search term (e.g., `report*.docx`, `config.json`, `image.png`) and send it as a message.
3.  The bot will search recursively within the current directory.
4.  Browse search results and interact with them (download file, open folder).
5.  Use `/cancel` or `↩️ Back to Browser` (from search results) to return to normal browsing.

### User Authorization (Admin Only)
If an unauthorized user attempts to interact with the bot:
1. The Admin receives a message with the user's details and the message they sent.
2. Buttons "✅ Accept User" and "❌ Reject User" are provided.
3. Clicking "✅ Accept User" adds the user to the `authorized_users.json` file, granting them access. The user is notified.
4. Clicking "❌ Reject User" dismisses the notification.

---

## 👥 Contributors

<p align="center">
<a href="https://t.me/Zaky1million">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=700&size=24&duration=2000&pause=1000&color=00BFFF¢er=true&vCenter=true&width=435&lines=Developed+by+Zaky1million;With+Passion+and+Precision;For+Power+Users+Worldwide" alt="Creator" />
</a>
</p>

<p align="center">
For custom projects, feedback, or collaboration:<br>
<a href="https://t.me/Zaky1million"><img src="https://img.shields.io/badge/Telegram-Zaky1million-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white" alt="Telegram Contact"></a>
<a href="https://wa.me/201280779419"><img src="https://img.shields.io/badge/WhatsApp-Chat-25D366?style=for-the-badge&logo=whatsapp&logoColor=white" alt="WhatsApp Contact"></a>
</p>

<p align="center">
<strong>"Bringing your remote servers into your pocket, one file at a time."</strong>
</p>

---

## 🌟 Support This Project

<p align="center">
<a href="https://github.com/zkyhmam/Remote-file-share-TG"><img src="https://img.shields.io/badge/⭐_Star_this_Project-30363d?style=for-the-badge&logo=github&logoColor=white" alt="Star this Project"></a>
</p>

<p align="center">
<a href="https://github.com/zkyhmam/Remote-file-share-TG/fork"><img src="https://img.shields.io/badge/🍴_Fork_this_Project-30363d?style=for-the-badge&logo=github&logoColor=white" alt="Fork this Project"></a>
</p>

---

## By Me 😊♥️

<p align="center">
<a href="https://t.me/Zaky1million">
  <img src="https://readme-typing-svg.demolab.com?font=Black+Ops+One&size=40&pause=1000&color=00FFFF¢er=true&vCenter=true&width=500&height=80&lines=Created+by+Zaky+1M" alt="Zaky 1M Signature" />
</a>
</p>
