"""
VotePath AI - Flask Backend
Election Process Guidance Assistant for India
"""

import os
import json
import logging
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), '..', 'templates'),
    static_folder=os.path.join(os.path.dirname(__file__), '..', 'static')
)
CORS(app)

# API Keys from environment
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")
GOOGLE_CALENDAR_API_KEY = os.getenv("GOOGLE_CALENDAR_API_KEY", "")

# ─────────────────────────────────────────────
# SERVE FRONTEND
# ─────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory(os.path.join(os.path.dirname(__file__), '..', 'frontend'), 'index.html')

@app.route("/<path:filename>")
def frontend_files(filename):
    return send_from_directory(os.path.join(os.path.dirname(__file__), '..', 'frontend'), filename)

# ─────────────────────────────────────────────
# FEATURE 1 — Voter ID Registration Guide
# ─────────────────────────────────────────────

@app.route("/api/voter-guide", methods=["GET"])
def voter_guide():
    guide = {
        "title": "Voter ID Registration Guide",
        "eligibility": {
            "age": "18 years or above",
            "citizenship": "Indian Citizen",
            "residence": "Must be ordinarily resident at the address"
        },
        "methods": [
            {
                "type": "Online Registration",
                "portal": "https://voters.eci.gov.in",
                "form": "Form 6",
                "steps": [
                    "Visit voters.eci.gov.in or the Voter Helpline App",
                    "Click 'Register as New Voter (Form 6)'",
                    "Fill in personal details, address, and upload documents",
                    "Submit form and note the reference number",
                    "BLO (Booth Level Officer) will verify your details",
                    "Your EPIC (Voter ID) will be issued within 30–45 days"
                ]
            },
            {
                "type": "Offline Registration",
                "form": "Form 6 (physical)",
                "steps": [
                    "Collect Form 6 from nearest Electoral Registration Office",
                    "Fill in all required details",
                    "Attach self-attested document copies",
                    "Submit to ERO / AERO or BLO in your area"
                ]
            }
        ],
        "documents_required": [
            "Aadhaar Card (identity + address proof)",
            "Passport-size photograph (2 copies)",
            "Age Proof: Birth Certificate / Class 10 Marksheet / Passport",
            "Address Proof: Aadhaar / Ration Card / Bank Passbook / Utility Bill"
        ],
        "timeline": "30–45 working days after verification",
        "tracking": "Track status at https://electoralsearch.eci.gov.in using your reference number",
        "correction_process": {
            "form": "Form 8",
            "portal": "https://voters.eci.gov.in",
            "note": "Use Form 8 for corrections in name, date of birth, address, or photo"
        },
        "transfer_process": {
            "form": "Form 6 (new constituency)",
            "note": "Apply fresh Form 6 at new place of residence; old entry will be deleted automatically"
        },
        "helpline": "1950 (Voter Helpline — toll free)"
    }
    return jsonify({"success": True, "data": guide})


# ─────────────────────────────────────────────
# FEATURE 2 — Eligibility Checker
# ─────────────────────────────────────────────

@app.route("/api/check-eligibility", methods=["POST"])
def check_eligibility():
    data = request.get_json()
    age = data.get("age", 0)
    citizen = data.get("citizen", False)
    has_id = data.get("has_id", False)

    try:
        age = int(age)
    except (TypeError, ValueError):
        return jsonify({"success": False, "error": "Invalid age input"}), 400

    if not citizen:
        return jsonify({
            "success": True,
            "eligible": False,
            "reason": "Only Indian citizens are eligible to vote.",
            "next_steps": ["Obtain Indian citizenship", "Apply for voter registration after citizenship"]
        })

    if age < 18:
        return jsonify({
            "success": True,
            "eligible": False,
            "reason": f"You are {age} years old. You must be at least 18 years old on the qualifying date (1st January of the revision year).",
            "next_steps": [
                "Wait until you turn 18",
                f"You can pre-register approximately {18 - age} year(s) before your 18th birthday in some states",
                "Check voters.eci.gov.in for advance registration options"
            ]
        })

    if has_id:
        return jsonify({
            "success": True,
            "eligible": True,
            "status": "already_registered",
            "message": "You are already registered! You can vote in your designated polling booth.",
            "next_steps": [
                "Verify your details at voters.eci.gov.in",
                "Find your polling booth using our Booth Finder",
                "Set an election day reminder using our Calendar feature"
            ]
        })

    return jsonify({
        "success": True,
        "eligible": True,
        "status": "needs_registration",
        "message": f"🎉 Great news! You are {age} years old and eligible to vote.",
        "next_steps": [
            "Apply online at voters.eci.gov.in using Form 6",
            "Keep your Aadhaar, photo, and age proof ready",
            "Track your application status after submission",
            "Application takes 30–45 days to process"
        ]
    })


# ─────────────────────────────────────────────
# FEATURE 3 — Document Checklist
# ─────────────────────────────────────────────

@app.route("/api/document-checklist", methods=["GET"])
def document_checklist():
    purpose = request.args.get("purpose", "new_registration")

    checklists = {
        "new_registration": {
            "title": "New Voter ID Registration — Document Checklist",
            "form": "Form 6",
            "documents": [
                {
                    "name": "Aadhaar Card",
                    "purpose": "Identity + Address Proof",
                    "mandatory": True,
                    "notes": "Self-attested photocopy"
                },
                {
                    "name": "Passport-size Photograph",
                    "purpose": "Voter ID photo",
                    "mandatory": True,
                    "notes": "2 recent colour photographs (white background)"
                },
                {
                    "name": "Age Proof",
                    "purpose": "Verify date of birth",
                    "mandatory": True,
                    "options": ["Birth Certificate", "Class 10 Marksheet", "Passport", "PAN Card"]
                },
                {
                    "name": "Address Proof",
                    "purpose": "Verify residential address",
                    "mandatory": True,
                    "options": ["Aadhaar Card", "Ration Card", "Electricity Bill", "Bank Passbook", "Telephone Bill"]
                }
            ]
        },
        "correction": {
            "title": "Voter ID Correction — Document Checklist",
            "form": "Form 8",
            "documents": [
                {
                    "name": "Existing Voter ID / EPIC",
                    "purpose": "Current voter ID for reference",
                    "mandatory": True
                },
                {
                    "name": "Proof of Correct Information",
                    "purpose": "Document showing the correct details",
                    "mandatory": True,
                    "options": ["Aadhaar Card", "Passport", "Birth Certificate", "Class 10 Marksheet"]
                },
                {
                    "name": "New Photograph (if photo correction)",
                    "purpose": "Updated passport-size photo",
                    "mandatory": False
                }
            ]
        },
        "transfer": {
            "title": "Constituency Transfer — Document Checklist",
            "form": "Form 6 (new area)",
            "documents": [
                {
                    "name": "Existing Voter ID / EPIC",
                    "purpose": "Proof of previous registration",
                    "mandatory": True
                },
                {
                    "name": "New Address Proof",
                    "purpose": "Prove residence in new constituency",
                    "mandatory": True,
                    "options": ["Aadhaar Card (updated address)", "Rental Agreement", "Utility Bill", "Bank Statement"]
                },
                {
                    "name": "Passport-size Photograph",
                    "purpose": "New voter ID card",
                    "mandatory": True,
                    "notes": "2 recent colour photographs"
                }
            ]
        }
    }

    checklist = checklists.get(purpose, checklists["new_registration"])
    return jsonify({"success": True, "data": checklist})


# ─────────────────────────────────────────────
# FEATURE 4 — Polling Booth Finder
# ─────────────────────────────────────────────

@app.route("/api/find-booth", methods=["POST"])
def find_booth():
    data = request.get_json()
    city = data.get("city", "")
    pincode = data.get("pincode", "")
    area = data.get("area", "")

    if not any([city, pincode, area]):
        return jsonify({"success": False, "error": "Please provide city, pincode, or area"}), 400

    query = f"polling booth electoral office {area} {city} {pincode} India"

    # Return search query and Maps embed data
    maps_search_url = f"https://www.google.com/maps/search/?api=1&query={requests.utils.quote(query)}"

    result = {
        "search_query": query,
        "maps_url": maps_search_url,
        "maps_embed_query": query,
        "official_lookup": {
            "url": "https://electoralsearch.eci.gov.in",
            "description": "Find your exact polling booth at the official Election Commission portal"
        },
        "tip": "The most accurate way to find your polling booth is through the Election Commission portal or Voter Helpline App.",
        "helpline": "1950"
    }

    return jsonify({"success": True, "data": result, "maps_api_key": GOOGLE_MAPS_API_KEY})


# ─────────────────────────────────────────────
# FEATURE 5 — Election Reminder System
# ─────────────────────────────────────────────

@app.route("/api/create-reminder", methods=["POST"])
def create_reminder():
    data = request.get_json()
    reminder_type = data.get("type", "election_day")
    event_date = data.get("date", "")
    user_email = data.get("email", "")

    reminders = {
        "registration_deadline": {
            "title": "📋 Voter Registration Deadline",
            "description": "Last date to register as a new voter. Visit voters.eci.gov.in or submit Form 6 at your ERO office.",
            "color": "#FF6B35"
        },
        "correction_deadline": {
            "title": "✏️ Voter ID Correction Deadline",
            "description": "Last date to submit corrections to your voter ID. Use Form 8 at voters.eci.gov.in.",
            "color": "#4ECDC4"
        },
        "election_day": {
            "title": "🗳️ Election Day — Your Vote Matters!",
            "description": "Today is Election Day! Carry your Voter ID or Aadhaar to the polling booth. Polling hours: 7 AM – 6 PM.",
            "color": "#FF8C00"
        }
    }

    reminder = reminders.get(reminder_type, reminders["election_day"])

    # Generate Google Calendar link
    if event_date:
        date_formatted = event_date.replace("-", "")
        gcal_url = (
            f"https://calendar.google.com/calendar/render?action=TEMPLATE"
            f"&text={requests.utils.quote(reminder['title'])}"
            f"&dates={date_formatted}/{date_formatted}"
            f"&details={requests.utils.quote(reminder['description'])}"
        )
    else:
        gcal_url = "https://calendar.google.com"

    return jsonify({
        "success": True,
        "data": {
            "reminder": reminder,
            "calendar_link": gcal_url,
            "message": "Click the link to add this reminder to your Google Calendar"
        }
    })


# ─────────────────────────────────────────────
# FEATURE 6 — Smart Election Q&A via Gemini
# ─────────────────────────────────────────────

@app.route("/api/ask", methods=["POST"])
def ask_assistant():
    data = request.get_json()
    question = data.get("question", "").strip()

    if not question:
        return jsonify({"success": False, "error": "Please enter a question"}), 400

    if not GEMINI_API_KEY:
        # Fallback intelligent responses
        return jsonify({
            "success": True,
            "answer": get_fallback_answer(question),
            "source": "knowledge_base"
        })

    system_prompt = """You are VotePath AI, an expert election guidance assistant for India. You help users with:
- Voter ID registration, correction, and transfer processes
- Electoral eligibility questions
- Document requirements for voting
- How to find polling booths
- Election day procedures
- EVM and VVPAT information
- NOTA option details
- Absentee/postal voting
- Election Commission of India rules and regulations

Always be helpful, clear, and provide step-by-step guidance. Cite official portals like voters.eci.gov.in when relevant.
Include important links, form numbers, and helpline numbers (1950) when appropriate.
Keep responses concise but complete. Format with clear steps when giving procedures.
Respond only about Indian elections and voting processes. If asked anything unrelated, politely redirect."""

    try:
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}",
            headers={"Content-Type": "application/json"},
            json={
                "contents": [{"parts": [{"text": f"{system_prompt}\n\nUser Question: {question}"}]}],
                "generationConfig": {
                    "temperature": 0.3,
                    "maxOutputTokens": 800,
                    "topP": 0.8
                }
            },
            timeout=15
        )

        if response.status_code == 200:
            result = response.json()
            answer = result["candidates"][0]["content"]["parts"][0]["text"]
            return jsonify({"success": True, "answer": answer, "source": "gemini"})
        else:
            logger.error(f"Gemini API error: {response.status_code} — {response.text}")
            return jsonify({
                "success": True,
                "answer": get_fallback_answer(question),
                "source": "knowledge_base"
            })

    except Exception as e:
        logger.error(f"Gemini request failed: {e}")
        return jsonify({
            "success": True,
            "answer": get_fallback_answer(question),
            "source": "knowledge_base"
        })


def get_fallback_answer(question: str) -> str:
    """Rule-based fallback for common election queries."""
    q = question.lower()

    if any(k in q for k in ["wrong address", "incorrect address", "address change", "correct address"]):
        return (
            "**Correcting Wrong Address on Voter ID**\n\n"
            "1. Visit **voters.eci.gov.in** and log in\n"
            "2. Select **'Form 8 — Correction of entries in Electoral Roll'**\n"
            "3. Enter your EPIC number and select 'Address Correction'\n"
            "4. Upload your new address proof (Aadhaar / Utility Bill)\n"
            "5. Submit and note the reference number\n"
            "6. BLO will verify and update within **30–45 days**\n\n"
            "📞 Helpline: **1950**"
        )
    elif any(k in q for k in ["lost voter id", "lost epic", "lost card"]):
        return (
            "**Lost Your Voter ID? Here's What to Do:**\n\n"
            "1. File an **FIR at the nearest police station** (recommended)\n"
            "2. Visit **voters.eci.gov.in** → Select 'Form 002' for duplicate EPIC\n"
            "3. Alternatively, apply at your **ERO (Electoral Registration Officer) office**\n"
            "4. Carry: FIR copy, Aadhaar, one passport-size photo\n"
            "5. Your duplicate card will be issued within **15–30 days**\n\n"
            "💡 **Tip:** You can vote using Aadhaar or other approved ID if your new card hasn't arrived. "
            "ECI accepts 12 alternative photo IDs on election day.\n\n"
            "📞 Helpline: **1950**"
        )
    elif any(k in q for k in ["transfer", "new city", "moved", "new constituency", "relocated"]):
        return (
            "**Transferring Your Voter ID to a New Constituency**\n\n"
            "1. Visit **voters.eci.gov.in** or download the **Voter Helpline App**\n"
            "2. Apply using **Form 6** at your NEW place of residence\n"
            "3. Your old entry will be **automatically deleted** from the previous roll\n"
            "4. Required documents:\n"
            "   - Current Voter ID / EPIC\n"
            "   - New address proof (Aadhaar with new address / Rental Agreement)\n"
            "   - 2 passport-size photographs\n"
            "5. Processing time: **30–45 days**\n\n"
            "📞 Helpline: **1950**"
        )
    elif any(k in q for k in ["status", "track", "application"]):
        return (
            "**Tracking Your Voter ID Application Status**\n\n"
            "1. Visit **https://electoralsearch.eci.gov.in**\n"
            "2. Enter your **reference number** received after form submission\n"
            "3. Alternatively, search by name, date of birth, and state\n"
            "4. You can also call **1950** (toll-free Voter Helpline)\n"
            "5. Download the **Voter Helpline App** for real-time updates\n\n"
            "⏱️ Standard processing time: **30–45 working days**"
        )
    elif any(k in q for k in ["register", "new voter", "first time", "18", "form 6"]):
        return (
            "**First-Time Voter Registration Guide**\n\n"
            "**Eligibility:** Indian citizen, 18+ years old\n\n"
            "**Online Process (Recommended):**\n"
            "1. Visit **https://voters.eci.gov.in**\n"
            "2. Click **'New Registration — Form 6'**\n"
            "3. Fill personal details and upload:\n"
            "   - Aadhaar Card\n"
            "   - Age Proof (Class 10 certificate / Passport)\n"
            "   - 2 passport-size photos\n"
            "4. Submit → Save your reference number\n"
            "5. BLO visits for verification\n"
            "6. EPIC issued in **30–45 days**\n\n"
            "📞 Helpline: **1950**"
        )
    elif any(k in q for k in ["booth", "polling", "where to vote", "voting centre"]):
        return (
            "**Finding Your Polling Booth**\n\n"
            "1. Visit **https://electoralsearch.eci.gov.in**\n"
            "2. Search by your name or EPIC number\n"
            "3. Your **polling booth address** appears in your voter details\n"
            "4. Download **Voter Helpline App** → Tap 'My Booth'\n"
            "5. Call **1950** for booth information\n\n"
            "📍 Use our **Booth Finder** feature above to locate nearby electoral offices on the map!"
        )
    elif any(k in q for k in ["nota", "none of the above"]):
        return (
            "**NOTA — None Of The Above**\n\n"
            "NOTA is a valid option on Indian EVMs since 2013 (Supreme Court order).\n\n"
            "• NOTA appears as the **last option** on the EVM ballot\n"
            "• Press the button next to the NOTA symbol\n"
            "• VVPAT will confirm your NOTA vote\n"
            "• If NOTA gets the most votes, the **runner-up candidate wins** and a re-election may be ordered\n\n"
            "Your vote always counts — even NOTA is a valid democratic expression! 🗳️"
        )
    else:
        return (
            "**Hello! I'm VotePath AI 🗳️**\n\n"
            "I can help you with:\n"
            "• **Voter ID Registration** — How to apply for your first voter ID\n"
            "• **Eligibility Check** — Am I eligible to vote?\n"
            "• **Document Checklist** — What papers do I need?\n"
            "• **Address/Name Correction** — Fix errors on your voter ID\n"
            "• **Lost Voter ID** — How to get a duplicate\n"
            "• **Constituency Transfer** — Moved to a new city?\n"
            "• **Find Polling Booth** — Where do I vote?\n"
            "• **Application Status** — Track your voter ID\n\n"
            "Please ask your specific question and I'll guide you step by step!\n\n"
            "📞 Voter Helpline: **1950** (toll-free)"
        )


# ─────────────────────────────────────────────
# HEALTH CHECK
# ─────────────────────────────────────────────

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "service": "VotePath AI",
        "version": "1.0.0",
        "apis": {
            "gemini": bool(GEMINI_API_KEY),
            "maps": bool(GOOGLE_MAPS_API_KEY),
            "calendar": bool(GOOGLE_CALENDAR_API_KEY)
        }
    })


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_ENV", "production") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug)
