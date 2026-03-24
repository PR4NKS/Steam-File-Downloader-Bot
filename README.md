<div align="center">

# 🎮 Steam File Downloader Bot

<img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
<img src="https://img.shields.io/badge/discord.py-2.x-5865F2?style=for-the-badge&logo=discord&logoColor=white"/>
<img src="https://img.shields.io/badge/aiohttp-async-009688?style=for-the-badge&logo=aiohttp&logoColor=white"/>
<img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge"/>

**A Discord bot that fetches downloadable game files from multiple Steam API sources using smart priority-based fallback.**

</div>

---

## 📌 Overview

**Steam File Downloader Bot** is designed to fetch downloadable game files from multiple sources using a simple App ID input. It automatically cycles through configured APIs and retrieves the file from the first available source.

The bot enhances user experience with:

- 🎨 Rich Discord embeds
- 🖼️ Game logo previews
- 📊 API health monitoring
- 📁 Organized command structure

---

## ✨ Features

### 🔍 Smart Multi-API Fetching
- Searches across multiple endpoints simultaneously
- Uses a priority-based fallback system
- Ensures maximum uptime and success rate

### 📥 File Download System
- Download files using `/download <appid>`
- Automatically names files based on game title
- Supports binary file streaming

### 🖼️ Game Logo Integration
- Fetches official Steam header images
- Displays game logo inside Discord embed

### 📊 API Status Monitoring
- `/api_status` command checks all configured endpoints
- Displays `🟢 Online` / `🔴 Offline` state per API
- Detects unexpected or malformed responses

### 🎮 Game Database
- Predefined `AppID → Game Title` mapping
- Easily extendable via config or dictionary

### ⚡ Async & Optimized
- Built with `aiohttp` for high performance
- Non-blocking HTTP requests
- Efficient session reuse across commands

---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| Python 3.10+ | Core language |
| discord.py 2.x | Discord bot framework |
| aiohttp | Async HTTP client |
| asyncio | Async runtime |

---

## 📂 Project Structure

```
📁 steam-downloader-bot/
│
├── bot.py                # Main bot file
├── config.json           # (Optional) API config
├── requirements.txt      # Python dependencies
└── README.md             # Documentation
```

---

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/PR4NKS/steam-downloader-bot.git
cd steam-downloader-bot
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Add Your Bot Token

Open `bot.py` and replace the placeholder:

```python
TOKEN = "YOUR_DISCORD_BOT_TOKEN"
```

> 💡 **Tip:** Use environment variables or a `.env` file for security. Never commit your token to version control.

---

## ▶️ Running the Bot

```bash
python bot.py
```

---

## 🤖 Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/download` | Download game files by App ID | `/download appid:730 show_logo:true` |
| `/list_games` | Display all available games in the database | `/list_games` |
| `/api_status` | Check health/status of all configured APIs | `/api_status` |
| `!help_bot` | Show the help menu | `!help_bot` |

### 🔹 `/download`

Fetches and delivers the game file for the specified Steam App ID.

```
/download appid:730 show_logo:true
```

- `appid` — The Steam App ID of the game (e.g., `730` for CS2)
- `show_logo` — Whether to display the game header image in the embed (`true`/`false`)

### 🔹 `/list_games`

Lists all games available in the predefined game database.

### 🔹 `/api_status`

Runs a health check on every configured API endpoint and reports their status.

### 🔹 `!help_bot`

Sends a formatted help embed showing all available commands.

---

## ⚙️ Configuration

### API Configuration Example

```python
API_CONFIG = {
    "endpoints": [
        {
            "name": "API-1",
            "url": "http://example.com/{appid}",
            "success_code": 200,
            "unavailable_code": 404,
            "enabled": True,
            "priority": 1
        },
        {
            "name": "API-2",
            "url": "http://backup-example.com/{appid}",
            "success_code": 200,
            "unavailable_code": 404,
            "enabled": True,
            "priority": 2
        }
    ]
}
```

### Key Configuration Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Display name for the API endpoint |
| `url` | `str` | URL template — use `{appid}` as a placeholder |
| `success_code` | `int` | HTTP status code indicating a successful file fetch |
| `unavailable_code` | `int` | HTTP status code indicating the file is missing |
| `enabled` | `bool` | Toggle this endpoint on/off |
| `priority` | `int` | Lower number = higher priority (tried first) |

> ⚠️ **Note:** Endpoints are tried in ascending priority order. If API-1 fails or is unavailable, the bot automatically falls back to API-2, and so on.

---

## 📋 requirements.txt

```
discord.py>=2.0.0
aiohttp>=3.8.0
```

---

## 🔒 Security Notice

- Never hardcode your bot token in source code
- Use `.env` files with `python-dotenv` for token management
- Add `.env` to your `.gitignore`

```bash
# .gitignore
.env
__pycache__/
*.pyc
```

---

## 🤝 Contributing

Contributions are welcome! Feel free to open issues or pull requests for:

- New API endpoint integrations
- Additional game database entries
- Bug fixes and performance improvements
- UI/embed enhancements

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

Made with ❤️ and Python

</div>
