# 🗳️ VotePath AI

**Your AI-Powered Election Process Guidance Assistant for India**

> From "I need my voter ID" → to "I successfully voted." — VotePath AI guides every Indian citizen through the complete election process.

[![Made for PromptWars](https://img.shields.io/badge/PromptWars-Challenge%202-FF8C00?style=flat-square)](https://promptwars.dev)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-black?style=flat-square&logo=flask)](https://flask.palletsprojects.com)
[![Google Gemini](https://img.shields.io/badge/Gemini-AI-4285F4?style=flat-square&logo=google)](https://ai.google.dev)

---

## 📌 Problem Statement

India has 95+ crore eligible voters, yet millions — especially first-time voters, students, rural citizens, and the elderly — are confused by the voter registration process. Questions like:

- "How do I get my first voter ID?"
- "My address is wrong on my voter ID — what do I do?"
- "Where is my polling booth?"
- "I moved cities — how do I transfer my voter registration?"

...go unanswered, leading to voter disengagement and disenfranchisement.

**VotePath AI solves this** by providing an intelligent, personalized assistant that guides citizens through every step of India's election process in plain, simple language.

---

## 🎯 Chosen Vertical

**Civic Tech / Government Services / Election Accessibility**

---

## ✨ Features

| Feature | Description |
|---|---|
| 🤖 Smart AI Assistant | Gemini-powered Q&A for any election query |
| ✅ Eligibility Checker | Instant check with next-step guidance |
| 📋 Document Checklist | Tailored lists for registration, correction, transfer |
| 📍 Polling Booth Finder | Google Maps integration to locate booths |
| 📅 Election Reminders | Google Calendar deep links for key deadlines |
| 📖 Complete Voter Guide | Step-by-step guide from Form 6 to approval |

---

## 🔧 Google Services Used

### 1. Google Gemini API
- Powers the Smart Election Q&A Assistant
- Trained with election-specific system prompt
- Provides step-by-step guidance for 20+ query types
- Falls back to a rule-based knowledge base if API unavailable

### 2. Google Maps API
- Polling Booth Finder feature
- Embeds interactive map in the UI
- Generates "Open in Google Maps" search links for electoral offices

### 3. Google Calendar API
- Election Reminder System
- Creates deep-link calendar events for:
  - Voter registration deadline
  - Voter ID correction deadline
  - Election Day reminder
- One-click "Add to Google Calendar" integration

---

## 🏗️ Architecture & Approach

```
┌─────────────────────────────────┐
│         VotePath AI             │
├────────────────┬────────────────┤
│   Frontend     │    Backend     │
│  HTML/CSS/JS   │  Python/Flask  │
│                │                │
│  • Hero Page   │  • /api/ask    │
│  • Chat UI     │  • /api/guide  │
│  • Eligibility │  • /api/check- │
│  • Doc Check   │    eligibility │
│  • Maps Embed  │  • /api/docs   │
│  • Calendar    │  • /api/booth  │
│    Reminders   │  • /api/remind │
└────────────────┴────────────────┘
         │              │
    Google Maps    Gemini API
    Calendar API   (AI Q&A)
```

### How the Solution Works

1. **User visits VotePath AI** → sees a professional civic-tech landing page
2. **Selects a feature** (or asks the AI assistant directly)
3. **AI Assistant**: User types a question → Flask routes to Gemini API → Response formatted and displayed in chat UI
4. **Eligibility Checker**: User inputs age + citizenship → Rule engine determines status → Returns personalized next steps
5. **Document Checklist**: User selects purpose (new/correction/transfer) → Backend returns tailored document list
6. **Booth Finder**: User inputs location → Backend calls Google Maps → Embedded map + direct link returned
7. **Reminders**: User selects type + date → Backend generates Google Calendar deep link → One-click add

---

## 🧠 Assumptions Made

1. Users have basic internet access (mobile or desktop)
2. Primary audience: Indian citizens aged 18–35 and first-time voters
3. Official ECI data (voters.eci.gov.in) is the source of truth for forms and procedures
4. Google Gemini is the primary AI engine; a robust rule-based fallback handles offline/API-error scenarios
5. The app is informational — users must complete actual registration on official ECI portals
6. Map integration shows electoral offices; exact assigned booth requires ECI portal lookup

---

## 🚀 Setup Instructions

### Prerequisites
- Python 3.10+
- pip
- A Google Cloud account (for API keys)

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/VotePath-AI.git
cd VotePath-AI
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### 4. Configure API Keys
```bash
cp .env.example .env
```
Edit `.env` and add your keys:
```env
GEMINI_API_KEY=your_gemini_api_key_here
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
GOOGLE_CALENDAR_API_KEY=your_google_calendar_api_key_here
```

**Getting API Keys:**
- **Gemini**: https://aistudio.google.com/app/apikey (free tier available)
- **Google Maps**: https://console.cloud.google.com/apis/credentials (enable Maps Embed API)
- **Calendar**: Not required — app generates Calendar deep links without OAuth

---

## 💻 How to Run Locally

```bash
cd VotePath-AI
source venv/bin/activate
python backend/app.py
```

Open `http://localhost:5000` in your browser.

**Test the API:**
```bash
# Health check
curl http://localhost:5000/api/health

# Ask the assistant
curl -X POST http://localhost:5000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "How do I register for a voter ID?"}'

# Check eligibility
curl -X POST http://localhost:5000/api/check-eligibility \
  -H "Content-Type: application/json" \
  -d '{"age": 20, "citizen": true, "has_id": false}'
```

---

## 🌐 Deployment Instructions

### Deploy on Render (Recommended)

1. Push code to GitHub (one branch: `main`)
2. Go to [render.com](https://render.com) → New Web Service
3. Connect your GitHub repository
4. Render auto-detects `render.yaml`
5. Add environment variables in Render dashboard:
   - `GEMINI_API_KEY`
   - `GOOGLE_MAPS_API_KEY`
6. Click **Deploy**

### Deploy on Railway

```bash
# Install Railway CLI
npm install -g @railway/cli
railway login
railway init
railway up
```
Set environment variables in Railway dashboard.

### Deploy on Vercel (Static frontend only)

For full-stack deployment, use Render or Railway. For frontend-only demo:
```bash
vercel --prod frontend/
```

---

## 📁 Project Structure

```
VotePath-AI/
├── frontend/
│   ├── index.html          # Main SPA — all features
│   ├── style.css           # Premium design system
│   └── script.js           # All frontend logic
├── backend/
│   ├── app.py              # Flask application + all API routes
│   └── requirements.txt    # Python dependencies
├── screenshots/
│   ├── homepage.png
│   └── chatbot-demo.png
├── .env.example            # Environment variables template
├── .gitignore
├── Procfile                # For Railway/Heroku deployment
├── render.yaml             # Render deployment config
└── README.md
```

---

## 🔒 Security

- API keys stored in environment variables (never in code)
- CORS configured via Flask-CORS
- All external links use `rel="noopener noreferrer"`
- Input validation on all API endpoints
- No sensitive user data stored (stateless design)
- `.env` excluded from version control via `.gitignore`

---

## ♿ Accessibility

- Semantic HTML5 elements throughout (`nav`, `section`, `main`, `footer`)
- ARIA labels on all interactive elements
- `aria-live` regions for dynamic content (chat, results)
- Screen-reader-only helper class (`.sr-only`)
- `:focus-visible` outlines for keyboard navigation
- Color contrast ratios meet WCAG AA standards
- Mobile-responsive at all breakpoints (320px–1440px+)

---

## 🔮 Future Scope

1. **Multi-language Support** — Hindi, Tamil, Telugu, Bengali, Marathi (using Google Translate API)
2. **SMS Notifications** — Election day reminders via Twilio/MSG91
3. **WhatsApp Bot** — Integration with WhatsApp Business API for rural users
4. **Offline PWA** — Service worker for offline access in low-connectivity areas
5. **State-specific Guides** — Customized flows for each Indian state's election rules
6. **Real-time Election Data** — Integration with ECI's official data feed for live election schedules
7. **Voice Interface** — Web Speech API for elderly and visually impaired users
8. **Voter ID OCR** — Camera-based voter ID scanning to auto-detect errors
9. **Community Q&A** — Crowdsourced FAQs moderated by verified civic volunteers
10. **Analytics Dashboard** — Anonymous usage patterns to identify voter confusion hotspots

---

## 🛠️ Tech Stack Summary

| Layer | Technology |
|---|---|
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Backend | Python 3.10+, Flask 3.0 |
| AI | Google Gemini 1.5 Flash |
| Maps | Google Maps Embed API |
| Calendar | Google Calendar (deep links) |
| Deployment | Render / Railway |
| Auth | Environment variables |

---

## 📞 Official Election Resources

- **ECI Portal**: https://voters.eci.gov.in
- **Electoral Search**: https://electoralsearch.eci.gov.in
- **Voter Helpline**: 1950 (toll-free)
- **Voter Helpline App**: Available on Google Play & App Store

---

*Built with ❤️ for PromptWars Hackathon — Making Indian democracy more accessible, one voter at a time.*
