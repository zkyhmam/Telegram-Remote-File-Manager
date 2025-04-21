# 📂 Telegram Remote File Manager 📂

<img src="https://i.imgur.com/dBaSKWF.gif" height="90" width="100%">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Black+Ops+One&size=60&duration=3000&pause=1000&color=00FFFF&background=000000&center=true&vCenter=true&width=900&height=120&lines=TELEGRAM+REMOTE;FILE+MANAGER;BY+ZAKY+1M" alt="Remote File Manager" /></a>

<img src="https://i.imgur.com/dBaSKWF.gif" height="90" width="100%">

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.8+"/>
  <img src="https://img.shields.io/badge/Telegram-Bot-blue.svg?style=for-the-badge&logo=telegram&logoColor=white" alt="Telegram Bot"/>
  <img src="https://img.shields.io/badge/Security-Focused-red.svg?style=for-the-badge&logo=shield&logoColor=white" alt="Security Focused"/>
</p>

---

<p align="center">
  <a href="https://github.com/zkyhmam/Remote-file-share-TG">
    <img src="https://i.postimg.cc/3Nywwzmk/Flux-Dev-Create-a-visually-appealing-and-slightly-futuristic-g-0.jpg" alt="Telegram Remote File Manager Visual" width="85%">
  </a>
</p>

### 🌟 Connect With Me
<p align="center">
  <a href="https://wa.me/201280779419"><img src="https://img.shields.io/badge/WhatsApp-25D366?style=for-the-badge&logo=whatsapp&logoColor=white" width="24%"></a>
  <a href="https://t.me/Zaky1million"><img src="https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white" width="23%"></a>
</p>

<img src="https://i.imgur.com/dBaSKWF.gif" height="90" width="100%">

## 📖 Overview

**Telegram Remote File Manager** is a powerful and secure bot that revolutionizes how you access your server files. Through a clean Telegram interface, you can browse, search, and download files/folders directly from any server where the bot is running.

Designed for personal use, it provides seamless access to your remote files without SSH or other complex tools, while maintaining strict security by restricting access exclusively to your authorized Telegram ID.

---

## ✨ Key Features

<table>
  <tr>
    <td width="50%">
      <h3>🔐 Secure Access</h3>
      <p>Only your configured <code>AUTHORIZED_USER_ID</code> can interact with the bot. All unauthorized attempts are immediately rejected with no exceptions.</p>
    </td>
    <td width="50%">
      <h3>🧭 Intuitive Navigation</h3>
      <p>Browse directories seamlessly with elegant inline buttons (<code>⬅️ Back</code>, <code>🏠 Root</code>, <code>◀️ Prev</code>, <code>Next ▶️</code>) for a fluid experience.</p>
    </td>
  </tr>
  <tr>
    <td width="50%">
      <h3>📄 File Downloading</h3>
      <p>Download any accessible file directly into your Telegram chat with a single click, maintaining original filenames and metadata.</p>
    </td>
    <td width="50%">
      <h3>🔍 Advanced Recursive Search</h3>
      <p>Find files and folders within the current directory and all subdirectories with powerful pattern matching, including wildcards.</p>
    </td>
  </tr>
  <tr>
    <td width="50%">
      <h3>🔗 Symlink Intelligence</h3>
      <p>Symbolic links are clearly marked (🔗) and handled securely. The bot resolves targets while ensuring they don't escape the allowed directory.</p>
    </td>
    <td width="50%">
      <h3>📊 Smart Pagination</h3>
      <p>Directories with numerous items are automatically paginated for smooth browsing, eliminating overwhelming file lists.</p>
    </td>
  </tr>
  <tr>
    <td width="50%">
      <h3>🌐 Multi-language Support</h3>
      <p>You can customize all bot messages and responses to any language you prefer by modifying the text strings.</p>
    </td>
    <td width="50%">
      <h3>🛡️ Directory Protection</h3>
      <p>The bot prevents navigation outside the configured root directory to maintain security boundaries.</p>
    </td>
  </tr>
</table>

<img src="https://i.imgur.com/dBaSKWF.gif" height="90" width="100%">

## 📋 Requirements

* **Python 3.8+**
* **Dependencies:**
  ```
  python-telegram-bot
  python-dotenv
  rich
  ```

---

## 🚀 Setup & Installation

| Step | Command or Action |
|------|------------------|
| **1. Clone Repository** | `git clone https://github.com/zkyhmam/Remote-file-share-TG.git` |
| **2. Navigate to Folder** | `cd Remote-file-share-TG` |
| **3. Install Requirements** | `pip install -r requirements.txt` |
| **4. Create Config File** | `cp .env.example .env` (Linux/Mac)<br>`copy .env.example .env` (Windows) |
| **5. Edit Configuration** | Set your bot token, user ID, and starting directory |
| **6. Launch the Bot** | `python bot.py` |

<img src="https://i.imgur.com/dBaSKWF.gif" height="90" width="100%">

## ⚙️ Configuration Details

| Parameter | Required | Description |
|-----------|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | ✅ | Your unique bot token from [BotFather](https://t.me/BotFather) |
| `AUTHORIZED_USER_ID` | ✅ | Your numerical Telegram ID (the only person who can use this bot) |
| `START_DIRECTORY` | ❌ | The root directory for browsing (defaults to home directory if unset) |

---

## 🕹️ Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Begin browsing your server files |
| `/help` | Display usage instructions and command list |
| `/cancel` | Abort current operation (especially during search) |

<img src="https://i.imgur.com/dBaSKWF.gif" height="90" width="100%">

## 🔒 Security Architecture

The bot implements multiple security layers to protect your files:

* **Exclusive Access Control:** Hardcoded to only respond to your specific Telegram ID
* **Directory Containment:** Prevents navigation outside the configured root directory
* **Symlink Safety:** All symbolic links are verified to ensure they don't bypass security boundaries
* **Permission Inheritance:** Operates with the permissions of the executing user

<img src="https://i.imgur.com/dBaSKWF.gif" height="90" width="100%">

## 💡 Usage Guide

Once your bot is running, interact with it on Telegram:

### Basic Navigation

1. **Start Browsing:** Send `/start` to see the contents of your root directory
2. **Open Folders:** Tap on any folder name (📁) to view its contents
3. **Download Files:** Tap on any file to immediately download it
4. **Navigate Up:** Use `⬅️ Back` to move up one directory level
5. **Return Home:** Use `🏠 Root` to jump back to your starting directory
6. **Move Between Pages:** Use `◀️ Prev` and `Next ▶️` for directories with many items

### Search Functionality

1. Tap `🔍 Search Here` in any folder
2. The bot will prompt you for your search term
3. Enter your query (supports wildcards like `*.pdf` or `report*`)
4. Browse search results and interact with them normally
5. Use `↩️ Back to Browser` to return to normal browsing

<img src="https://i.imgur.com/dBaSKWF.gif" height="90" width="100%">

## 👥 Contributors

<p align="center">
  <a href="https://t.me/Zaky1million">
    <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=700&size=24&duration=2000&pause=1000&color=00BFFF&center=true&vCenter=true&width=435&lines=Developed+by+Zaky1million;With+Passion+and+Precision;For+Power+Users+Worldwide" alt="Creator" />
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

<img src="https://i.imgur.com/dBaSKWF.gif" height="90" width="100%">

## 🌟 Support This Project

<p align="center">
  <a href="https://github.com/zkyhmam/Remote-file-share-TG"><img src="https://img.shields.io/badge/⭐_Star_this_Project-30363d?style=for-the-badge&logo=github&logoColor=white" alt="Star this Project"></a>
</p>

<p align="center">
  <a href="https://github.com/zkyhmam/Remote-file-share-TG/fork"><img src="https://img.shields.io/badge/🍴_Fork_this_Project-30363d?style=for-the-badge&logo=github&logoColor=white" alt="Fork this Project"></a>
</p>

<img src="https://i.imgur.com/dBaSKWF.gif" height="90" width="100%">

## 📜 License

This project is released under the MIT License - see the LICENSE file for details.

<p align="center">
  <a href="https://t.me/Zaky1million">
    <img src="https://readme-typing-svg.demolab.com?font=Black+Ops+One&size=40&pause=1000&color=00FFFF&center=true&vCenter=true&width=500&height=80&lines=Created+by+Zaky+1M" alt="Zaky 1M Signature" />
  </a>
</p>
