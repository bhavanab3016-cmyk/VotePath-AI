/* ══════════════════════════════════════════════════════
   VotePath AI — Frontend Logic
══════════════════════════════════════════════════════ */

const API_BASE = window.location.origin;
let selectedReminderType = "election_day";

// ─────────────────────────────────────────────
// SECTION NAVIGATION
// ─────────────────────────────────────────────

function openSection(id) {
  document.querySelectorAll(".panel").forEach(p => p.classList.remove("active"));
  const panel = document.getElementById(id);
  if (!panel) return;
  document.getElementById("sections-container").style.display = "block";
  document.querySelector(".hero").style.display = "none";
  document.querySelector(".journey").style.display = "none";
  document.querySelector(".features").style.display = "none";
  document.querySelector(".quick-links").style.display = "none";
  panel.classList.add("active");
  window.scrollTo({ top: 0, behavior: "smooth" });

  // Auto-load content
  if (id === "guide") loadGuide();
  if (id === "documents") loadChecklist("new_registration", document.querySelector(".tab-btn"));
}

function closeSection() {
  document.querySelectorAll(".panel").forEach(p => p.classList.remove("active"));
  document.getElementById("sections-container").style.display = "none";
  document.querySelector(".hero").style.display = "";
  document.querySelector(".journey").style.display = "";
  document.querySelector(".features").style.display = "";
  document.querySelector(".quick-links").style.display = "";
  window.scrollTo({ top: 0, behavior: "smooth" });
}

// ─────────────────────────────────────────────
// HAMBURGER MENU
// ─────────────────────────────────────────────

document.getElementById("hamburger").addEventListener("click", function () {
  const links = document.querySelector(".nav-links");
  const open = links.style.display === "flex";
  links.style.display = open ? "" : "flex";
  links.style.flexDirection = "column";
  links.style.position = "absolute";
  links.style.top = "64px";
  links.style.left = "0"; links.style.right = "0";
  links.style.background = "#fff";
  links.style.padding = "1rem 1.5rem";
  links.style.borderBottom = "1px solid #E4E8F0";
  links.style.zIndex = "99";
  this.setAttribute("aria-expanded", !open);
  if (open) { links.removeAttribute("style"); }
});

// ─────────────────────────────────────────────
// CHAT ASSISTANT
// ─────────────────────────────────────────────

function handleChatKey(e) {
  if (e.key === "Enter") sendMessage();
}

async function sendMessage() {
  const input = document.getElementById("chatInput");
  const question = input.value.trim();
  if (!question) return;
  input.value = "";
  appendMessage(question, "user");
  const typingId = appendTyping();
  try {
    const res = await fetch(`${API_BASE}/api/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question })
    });
    const data = await res.json();
    removeTyping(typingId);
    if (data.success) {
      appendMessage(formatAnswer(data.answer), "bot", true);
    } else {
      appendMessage("Sorry, I couldn't process your question. Please try again.", "bot");
    }
  } catch {
    removeTyping(typingId);
    appendMessage("Connection error. Please check your internet and try again.", "bot");
  }
}

function sendQuickPrompt(text) {
  document.getElementById("chatInput").value = text;
  sendMessage();
}

function appendMessage(content, role, isHtml = false) {
  const win = document.getElementById("chatWindow");
  const div = document.createElement("div");
  div.className = `chat-msg chat-msg--${role}`;
  const avatar = document.createElement("div");
  avatar.className = "msg-avatar";
  avatar.setAttribute("aria-hidden", "true");
  avatar.textContent = role === "bot" ? "🗳️" : "👤";
  const bubble = document.createElement("div");
  bubble.className = "msg-bubble";
  if (isHtml) {
    bubble.innerHTML = content;
  } else {
    bubble.textContent = content;
  }
  div.appendChild(avatar);
  div.appendChild(bubble);
  win.appendChild(div);
  win.scrollTop = win.scrollHeight;
}

function appendTyping() {
  const win = document.getElementById("chatWindow");
  const id = "typing-" + Date.now();
  const div = document.createElement("div");
  div.className = "chat-msg chat-msg--bot";
  div.id = id;
  div.innerHTML = `
    <div class="msg-avatar" aria-hidden="true">🗳️</div>
    <div class="msg-bubble">
      <div class="typing-indicator" aria-label="Assistant is typing">
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
      </div>
    </div>`;
  win.appendChild(div);
  win.scrollTop = win.scrollHeight;
  return id;
}

function removeTyping(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}

function formatAnswer(text) {
  return text
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.*?)\*/g, "<em>$1</em>")
    .replace(/^#{1,3}\s(.+)$/gm, "<strong>$1</strong>")
    .replace(/^[\-•]\s(.+)$/gm, "<li>$1</li>")
    .replace(/(<li>.*<\/li>)/s, "<ul>$1</ul>")
    .replace(/\n\n/g, "</p><p>")
    .replace(/\n/g, "<br/>")
    .replace(/^(.+)$/, "<p>$1</p>");
}

// ─────────────────────────────────────────────
// ELIGIBILITY CHECKER
// ─────────────────────────────────────────────

async function checkEligibility() {
  const age = document.getElementById("ageInput").value;
  const citizen = document.querySelector('input[name="citizen"]:checked')?.value === "yes";
  const hasId = document.querySelector('input[name="hasId"]:checked')?.value === "yes";
  const resultEl = document.getElementById("eligibilityResult");

  if (!age) {
    showResult(resultEl, "warning", "Please enter your age to continue.", []);
    return;
  }

  resultEl.style.display = "block";
  resultEl.innerHTML = `<div class="loading-state"><div class="spinner"></div><p>Checking eligibility...</p></div>`;

  try {
    const res = await fetch(`${API_BASE}/api/check-eligibility`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ age: parseInt(age), citizen, has_id: hasId })
    });
    const data = await res.json();
    if (!data.success) throw new Error(data.error);
    const d = data.data || data;
    const type = d.eligible ? "success" : "warning";
    const icon = d.eligible ? "✅" : "⚠️";
    const title = d.eligible
      ? (d.status === "already_registered" ? "You're Already Registered!" : "You're Eligible to Vote!")
      : "Not Yet Eligible";
    showResult(resultEl, type, `<h3>${icon} ${title}</h3><p>${d.message || d.reason}</p>`, d.next_steps || []);
  } catch (e) {
    showResult(resultEl, "warning", "Error checking eligibility. Please try again.", []);
  }
}

function showResult(el, type, htmlContent, steps) {
  el.style.display = "block";
  el.className = `result-card result-card--${type === "success" ? "success" : "warning"}`;
  let stepsHtml = "";
  if (steps && steps.length) {
    stepsHtml = `<div class="next-steps"><h4>Next Steps:</h4>` +
      steps.map((s, i) => `<div class="next-step-item"><span class="step-num">${i + 1}</span><span>${s}</span></div>`).join("") +
      `</div>`;
  }
  el.innerHTML = htmlContent + stepsHtml;
}

// ─────────────────────────────────────────────
// DOCUMENT CHECKLIST
// ─────────────────────────────────────────────

async function loadChecklist(purpose, btn) {
  // Update tabs
  document.querySelectorAll(".tab-btn").forEach(b => {
    b.classList.remove("tab-btn--active");
    b.setAttribute("aria-selected", "false");
  });
  if (btn) {
    btn.classList.add("tab-btn--active");
    btn.setAttribute("aria-selected", "true");
  }

  const el = document.getElementById("checklistResult");
  el.innerHTML = `<div class="loading-state"><div class="spinner"></div><p>Loading checklist...</p></div>`;

  try {
    const res = await fetch(`${API_BASE}/api/document-checklist?purpose=${purpose}`);
    const data = await res.json();
    if (!data.success) throw new Error();
    const d = data.data;
    let html = `
      <div style="margin-bottom:1rem;">
        <h3 style="font-family:var(--font-display);font-size:1.1rem;color:var(--navy);margin-bottom:0.25rem;">${d.title}</h3>
        <p style="font-size:0.82rem;color:var(--slate);">Form: <strong>${d.form}</strong></p>
      </div>`;
    d.documents.forEach(doc => {
      html += `
        <div class="doc-card">
          <div class="doc-card-header">
            <span class="doc-name">${doc.name}</span>
            <span class="doc-badge ${doc.mandatory ? "doc-badge--required" : "doc-badge--optional"}">${doc.mandatory ? "Required" : "Optional"}</span>
          </div>
          <p class="doc-purpose">${doc.purpose}</p>
          ${doc.options ? `<p class="doc-options">Accepted: ${doc.options.map(o => `<span>${o}</span>`).join("")}</p>` : ""}
          ${doc.notes ? `<p style="font-size:0.8rem;color:var(--slate);margin-top:0.3rem;">📌 ${doc.notes}</p>` : ""}
        </div>`;
    });
    html += `
      <div class="info-callout" style="margin-top:0.5rem;">
        <span>💡</span>
        <div>Carry self-attested photocopies of all documents. Keep originals handy for BLO verification.
        Apply online at <a href="https://voters.eci.gov.in" target="_blank" rel="noopener">voters.eci.gov.in</a></div>
      </div>`;
    el.innerHTML = html;
  } catch {
    el.innerHTML = `<p style="color:var(--red);padding:1rem;">Failed to load checklist. Please try again.</p>`;
  }
}

// ─────────────────────────────────────────────
// BOOTH FINDER
// ─────────────────────────────────────────────

async function findBooth() {
  const city = document.getElementById("boothCity").value.trim();
  const pincode = document.getElementById("boothPincode").value.trim();
  const area = document.getElementById("boothArea").value.trim();
  const resultEl = document.getElementById("boothResult");
  const mapEl = document.getElementById("mapContainer");

  if (!city && !pincode && !area) {
    resultEl.innerHTML = `<div class="result-card result-card--warning"><p>Please enter your city, pincode, or area to search.</p></div>`;
    return;
  }

  resultEl.innerHTML = `<div class="loading-state"><div class="spinner"></div><p>Searching for polling booths...</p></div>`;
  mapEl.style.display = "none";

  try {
    const res = await fetch(`${API_BASE}/api/find-booth`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ city, pincode, area })
    });
    const data = await res.json();
    if (!data.success) throw new Error(data.error);
    const d = data.data;
    const mapsKey = data.maps_api_key;

    resultEl.innerHTML = `
      <div class="booth-result-card">
        <h3 style="font-family:var(--font-display);font-size:1.1rem;color:var(--navy);margin-bottom:0.75rem;">📍 Polling Booth Search Results</h3>
        <p style="font-size:0.875rem;color:var(--ink);margin-bottom:0.5rem;">${d.tip}</p>
        <p style="font-size:0.8rem;color:var(--slate);margin-bottom:1.25rem;">Voter Helpline: <strong style="color:var(--saffron);">${d.helpline}</strong></p>
        <div class="booth-links">
          <a href="${d.maps_url}" target="_blank" rel="noopener noreferrer" class="booth-link-btn booth-link-btn--primary">
            🗺️ Open in Google Maps
          </a>
          <a href="${d.official_lookup.url}" target="_blank" rel="noopener noreferrer" class="booth-link-btn booth-link-btn--secondary">
            🏛️ Official ECI Portal
          </a>
        </div>
      </div>`;

    // Embed map
    if (mapsKey) {
      const q = encodeURIComponent(d.maps_embed_query);
      mapEl.innerHTML = `<iframe
        loading="lazy"
        allowfullscreen
        referrerpolicy="no-referrer-when-downgrade"
        src="https://www.google.com/maps/embed/v1/search?key=${mapsKey}&q=${q}&zoom=14"
        title="Polling booth map"
      ></iframe>`;
      mapEl.style.display = "block";
    } else {
      // Fallback: static map link
      mapEl.innerHTML = `
        <div style="background:var(--mist);border:1px solid var(--border);border-radius:var(--radius);padding:2rem;text-align:center;color:var(--slate);font-size:0.875rem;">
          <p>🗺️ Map preview requires a Google Maps API key.</p>
          <p style="margin-top:0.5rem;">Use the "Open in Google Maps" button above to view nearby booths.</p>
        </div>`;
      mapEl.style.display = "block";
    }
  } catch (e) {
    resultEl.innerHTML = `<div class="result-card result-card--warning"><p>${e.message || "Error finding booth. Please try again."}</p></div>`;
  }
}

// ─────────────────────────────────────────────
// REMINDERS
// ─────────────────────────────────────────────

document.querySelectorAll(".reminder-type-card").forEach(card => {
  card.addEventListener("click", function () {
    document.querySelectorAll(".reminder-type-card").forEach(c => c.classList.remove("selected"));
    this.classList.add("selected");
    selectedReminderType = this.dataset.type;
  });
});

// Select first by default
const firstCard = document.querySelector(".reminder-type-card");
if (firstCard) { firstCard.classList.add("selected"); selectedReminderType = firstCard.dataset.type; }

async function createReminder() {
  const date = document.getElementById("reminderDate").value;
  const resultEl = document.getElementById("reminderResult");

  if (!date) {
    resultEl.innerHTML = `<div class="result-card result-card--warning" style="margin-top:1rem;"><p>Please select a date for your reminder.</p></div>`;
    return;
  }

  resultEl.innerHTML = `<div class="loading-state" style="padding:1.5rem;"><div class="spinner"></div><p>Creating reminder...</p></div>`;

  try {
    const res = await fetch(`${API_BASE}/api/create-reminder`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ type: selectedReminderType, date })
    });
    const data = await res.json();
    if (!data.success) throw new Error();
    const d = data.data;
    resultEl.innerHTML = `
      <div class="result-card result-card--success" style="margin-top:1rem;">
        <h3>📅 Reminder Ready!</h3>
        <p style="margin-bottom:1rem;">${d.reminder.title}</p>
        <p style="font-size:0.85rem;color:var(--slate);margin-bottom:1.25rem;">${d.reminder.description}</p>
        <a href="${d.calendar_link}" target="_blank" rel="noopener noreferrer" class="booth-link-btn booth-link-btn--primary" style="display:inline-flex;text-decoration:none;">
          📅 Add to Google Calendar
        </a>
        <p style="font-size:0.78rem;color:var(--slate);margin-top:0.75rem;">${d.message}</p>
      </div>`;
  } catch {
    resultEl.innerHTML = `<div class="result-card result-card--warning" style="margin-top:1rem;"><p>Failed to create reminder. Please try again.</p></div>`;
  }
}

// ─────────────────────────────────────────────
// VOTER GUIDE
// ─────────────────────────────────────────────

async function loadGuide() {
  const el = document.getElementById("guideContent");
  try {
    const res = await fetch(`${API_BASE}/api/voter-guide`);
    const data = await res.json();
    if (!data.success) throw new Error();
    const d = data.data;

    el.innerHTML = `
      <div class="guide-section">
        <h3>✅ Eligibility Requirements</h3>
        ${Object.entries(d.eligibility).map(([k, v]) => `
          <div class="guide-step">
            <div class="guide-step-num">✓</div>
            <div class="guide-step-content"><strong>${capitalize(k)}:</strong> ${v}</div>
          </div>`).join("")}
      </div>

      ${d.methods.map(method => `
        <div class="guide-section">
          <h3>${method.type === "Online Registration" ? "🌐" : "🏢"} ${method.type}</h3>
          ${method.portal ? `<p style="font-size:0.82rem;color:var(--saffron);margin-bottom:0.75rem;">Portal: <a href="${method.portal}" target="_blank" rel="noopener" style="text-decoration:underline;">${method.portal}</a> · Form: ${method.form}</p>` : `<p style="font-size:0.82rem;color:var(--slate);margin-bottom:0.75rem;">Form: ${method.form}</p>`}
          ${method.steps.map((step, i) => `
            <div class="guide-step">
              <div class="guide-step-num">${i + 1}</div>
              <div class="guide-step-content">${step}</div>
            </div>`).join("")}
        </div>`).join("")}

      <div class="guide-section">
        <h3>📄 Required Documents</h3>
        ${d.documents_required.map(doc => `
          <div class="guide-step">
            <div class="guide-step-num">📎</div>
            <div class="guide-step-content">${doc}</div>
          </div>`).join("")}
      </div>

      <div class="guide-section">
        <h3>⏱️ Timeline & Tracking</h3>
        <div class="guide-step">
          <div class="guide-step-num">⏰</div>
          <div class="guide-step-content"><strong>Processing Time:</strong> ${d.timeline}</div>
        </div>
        <div class="guide-step">
          <div class="guide-step-num">🔍</div>
          <div class="guide-step-content"><strong>Track Status:</strong> <a href="${d.tracking.split(' at ')[1]}" target="_blank" rel="noopener" style="color:var(--saffron);text-decoration:underline;">${d.tracking}</a></div>
        </div>
      </div>

      <div class="guide-section">
        <h3>✏️ Correction Process</h3>
        <div class="guide-step">
          <div class="guide-step-num">📝</div>
          <div class="guide-step-content"><strong>${d.correction_process.form}</strong> — ${d.correction_process.note}. Portal: <a href="${d.correction_process.portal}" target="_blank" rel="noopener" style="color:var(--saffron);text-decoration:underline;">${d.correction_process.portal}</a></div>
        </div>
      </div>

      <div class="guide-section">
        <h3>🔄 Constituency Transfer</h3>
        <div class="guide-step">
          <div class="guide-step-num">📝</div>
          <div class="guide-step-content"><strong>${d.transfer_process.form}</strong> — ${d.transfer_process.note}</div>
        </div>
      </div>

      <div class="info-callout">
        <span>📞</span>
        <div><strong>Voter Helpline:</strong> Call <strong style="color:var(--saffron);">${d.helpline}</strong> (toll-free) for any election-related queries. Available in multiple languages.</div>
      </div>`;
  } catch {
    el.innerHTML = `<div class="result-card result-card--warning"><p>Failed to load guide. Please check your connection and try again.</p></div>`;
  }
}

function capitalize(str) {
  return str.charAt(0).toUpperCase() + str.slice(1).replace(/_/g, " ");
}

// ─────────────────────────────────────────────
// NAV SCROLL SHADOW
// ─────────────────────────────────────────────

window.addEventListener("scroll", () => {
  const nav = document.querySelector(".nav");
  nav.style.boxShadow = window.scrollY > 10 ? "0 2px 20px rgba(10,22,40,0.1)" : "";
}, { passive: true });
