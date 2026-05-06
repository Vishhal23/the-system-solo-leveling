# ⚔️ THE SYSTEM — Solo Leveling Productivity Tracker

> *"You have been chosen as a Player."*

A gamified productivity tracker inspired by **Solo Leveling**, powered by **Google Gemini AI**. Log your daily tasks through Telegram, and The System will evaluate, rank, and reward you with XP and stat points — just like a real Hunter.

---

## 🎮 Features

| Feature | Description |
|---|---|
| 🤖 **Telegram Bot** | Log tasks via Telegram. The System responds instantly. |
| 🧠 **Gemini AI Assessment** | Tasks are ranked (E → S) by AI based on difficulty & type. |
| 📊 **Streamlit Dashboard** | Dark-themed UI with radar charts, XP bars, and quest logs. |
| ⏰ **Auto Daily Quests** | Midnight scheduler assigns core training (push-ups, squats, running). |
| 💀 **Penalty System** | Miss your deadline? The System deducts XP. No mercy. |
| 👑 **Job Class Progression** | Hit 50 in a stat to unlock a hidden class (Assassin, Mage, Fighter...). |

---

## 🏗️ Architecture

```
the_system/
├── agents/          # Gemini AI task assessment
├── bot/             # Telegram bot handlers
├── config/          # Settings & environment config
├── core/            # Leveling, progression, scheduler
├── db/              # SQLite database & models
├── ui/              # Streamlit dashboard & CLI
├── Dockerfile       # Container image
├── render.yaml      # Render deployment blueprint
└── requirements.txt
```

---

## 🚀 Quick Start (Local)

```bash
# 1. Clone
git clone https://github.com/YOUR_USERNAME/the-system-solo-leveling.git
cd the-system-solo-leveling

# 2. Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment
cp .env.example .env
# Edit .env with your API keys

# 5. Run the Telegram Bot
python run_bot.py

# 6. Run the Dashboard (separate terminal)
streamlit run ui/dashboard.py
```

---

## 🔑 Environment Variables

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key
TELEGRAM_TOKEN=your_telegram_bot_token
TELEGRAM_ALLOWED_USER_ID=your_telegram_user_id
```

---

## 📡 Deployment (Render)

This project includes a `render.yaml` Blueprint for one-click deployment:

1. Push this repo to GitHub
2. Go to [Render Dashboard](https://dashboard.render.com)
3. Click **New → Blueprint** and connect this repo
4. Set your environment variables
5. Deploy!

Two services will be created:
- **the-system-bot** (Background Worker) — Telegram bot
- **the-system-dashboard** (Web Service) — Streamlit UI

---

## ⚔️ Job Classes

| Stat | Class | Threshold |
|---|---|---|
| Strength | Fighter | 50 pts |
| Agility | Assassin | 50 pts |
| Intelligence | Mage | 50 pts |
| Endurance | Tank | 50 pts |
| Charisma | Commander | 50 pts |

---

## 📜 License

This project is for personal use. Built with ❤️ and the desire to **arise**.

> *"I alone level up."*
