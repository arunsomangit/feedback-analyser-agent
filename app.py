"""
Customer Feedback Analyser Agent - Web UI
------------------------------------------
A simple web interface for the feedback analyser agent.
Run with: python app.py
Then open: http://localhost:8080
"""

import anthropic
import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs
import sys

# ── Agent logic (same two-pass approach as agent.py) ──────────────────────────

def analyse_individual_items(client, feedback_items):
    feedback_text = "\n".join([f"{i+1}. {item}" for i, item in enumerate(feedback_items)])
    prompt = f"""You are a senior product analyst. Analyse the following customer feedback items.

For EACH item, return a JSON object with:
- "item_number": the item number (integer)
- "text": the original feedback text
- "theme": one of [UX/Navigation, Performance/Speed, Feature Request, Bug/Error, Pricing, Positive/Praise, Support/Documentation, Other]
- "sentiment": one of [Positive, Neutral, Negative]
- "key_point": a 5-10 word summary of the core issue or praise
- "priority_signal": one of [High, Medium, Low]

Return ONLY a valid JSON array of objects, no other text, no markdown.

FEEDBACK ITEMS:
{feedback_text}"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )
    try:
        return json.loads(message.content[0].text.strip())
    except:
        return []


def synthesise_insights(client, analyses, raw_feedback):
    if analyses:
        input_data = f"STRUCTURED ANALYSES:\n{json.dumps(analyses, indent=2)}"
    else:
        input_data = "RAW FEEDBACK:\n" + "\n".join([f"{i+1}. {item}" for i, item in enumerate(raw_feedback)])

    prompt = f"""You are a senior Product Manager synthesising customer feedback into an executive-ready insight report.

Based on the following feedback analyses, produce a structured JSON report with these exact keys:

{{
  "themes": [{{"name": "theme name", "count": number}}],
  "sentiment": {{"positive": number, "neutral": number, "negative": number}},
  "pain_points": ["pain point 1", "pain point 2", ...],
  "feature_requests": ["request 1", "request 2", ...],
  "positive_highlights": ["highlight 1", "highlight 2", ...],
  "recommendations": [
    {{"priority": "HIGH", "action": "what to do", "rationale": "why, with evidence"}},
    ...
  ]
}}

Be specific and evidence-based. Return ONLY valid JSON, no markdown, no explanation.

{input_data}"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}]
    )
    try:
        text = message.content[0].text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text.strip())
    except Exception as e:
        return {"error": str(e), "raw": message.content[0].text}


def run_analysis(feedback_text):
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return {"error": "ANTHROPIC_API_KEY environment variable not set."}

    client = anthropic.Anthropic(api_key=api_key)
    lines = [l.strip() for l in feedback_text.strip().split("\n") if l.strip()]
    items = []
    for line in lines:
        if line and line[0].isdigit() and len(line) > 2:
            parts = line.split(".", 1) if "." in line[:3] else line.split(")", 1)
            line = parts[1].strip() if len(parts) == 2 else line
        if line:
            items.append(line)

    if not items:
        return {"error": "No feedback items found. Please enter at least one line of feedback."}

    analyses = analyse_individual_items(client, items)
    report = synthesise_insights(client, analyses, items)
    report["item_count"] = len(items)
    report["item_analyses"] = analyses
    return report


# ── HTML template ──────────────────────────────────────────────────────────────

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Customer Feedback Analyser Agent</title>
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  :root {
    --blue: #1a56db; --blue-light: #e8f0fe; --blue-mid: #3b82f6;
    --green: #047857; --green-light: #d1fae5;
    --red: #b91c1c; --red-light: #fee2e2;
    --amber: #92400e; --amber-light: #fef3c7;
    --gray: #374151; --gray-light: #f9fafb; --gray-mid: #e5e7eb;
    --border: #e5e7eb; --text: #111827; --muted: #6b7280;
    --radius: 10px; --shadow: 0 1px 3px rgba(0,0,0,0.08);
  }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f3f4f6; color: var(--text); min-height: 100vh; }

  header { background: #fff; border-bottom: 1px solid var(--border); padding: 0 2rem; display: flex; align-items: center; gap: 1rem; height: 60px; }
  .logo { width: 32px; height: 32px; background: var(--blue); border-radius: 8px; display: flex; align-items: center; justify-content: center; }
  .logo svg { width: 18px; height: 18px; fill: none; stroke: #fff; stroke-width: 2; stroke-linecap: round; }
  header h1 { font-size: 16px; font-weight: 600; color: var(--text); }
  header p { font-size: 13px; color: var(--muted); margin-left: auto; }

  .main { max-width: 1100px; margin: 0 auto; padding: 2rem 1.5rem; }

  .input-card { background: #fff; border: 1px solid var(--border); border-radius: var(--radius); padding: 1.5rem; box-shadow: var(--shadow); margin-bottom: 1.5rem; }
  .input-card label { display: block; font-size: 14px; font-weight: 500; margin-bottom: 6px; }
  .input-card small { font-size: 12px; color: var(--muted); display: block; margin-bottom: 10px; }
  textarea { width: 100%; border: 1px solid var(--border); border-radius: 8px; padding: 12px; font-size: 14px; font-family: inherit; resize: vertical; min-height: 180px; outline: none; color: var(--text); background: var(--gray-light); transition: border 0.15s; }
  textarea:focus { border-color: var(--blue-mid); background: #fff; }
  .btn-row { display: flex; gap: 10px; margin-top: 12px; align-items: center; }
  .btn { padding: 9px 20px; border-radius: 8px; font-size: 14px; font-weight: 500; cursor: pointer; border: none; transition: opacity 0.15s, transform 0.1s; }
  .btn:active { transform: scale(0.98); }
  .btn-primary { background: var(--blue); color: #fff; }
  .btn-primary:hover { opacity: 0.9; }
  .btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
  .btn-secondary { background: var(--gray-light); color: var(--gray); border: 1px solid var(--border); }
  .btn-secondary:hover { background: var(--gray-mid); }
  .item-count { font-size: 13px; color: var(--muted); margin-left: auto; }

  .spinner { display: none; width: 18px; height: 18px; border: 2px solid #dbeafe; border-top-color: var(--blue); border-radius: 50%; animation: spin 0.7s linear infinite; }
  @keyframes spin { to { transform: rotate(360deg); } }
  .loading-msg { font-size: 13px; color: var(--muted); display: none; }

  #results { display: none; }
  .results-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem; }
  .results-header h2 { font-size: 17px; font-weight: 600; }
  .badge { font-size: 12px; padding: 3px 10px; border-radius: 20px; font-weight: 500; }
  .badge-blue { background: var(--blue-light); color: var(--blue); }

  .grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-bottom: 1rem; }
  .grid-2 { display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; margin-bottom: 1rem; }
  @media (max-width: 700px) { .grid-3, .grid-2 { grid-template-columns: 1fr; } }

  .card { background: #fff; border: 1px solid var(--border); border-radius: var(--radius); padding: 1.25rem; box-shadow: var(--shadow); }
  .card-title { font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; color: var(--muted); margin-bottom: 1rem; }

  .stat { text-align: center; }
  .stat-num { font-size: 32px; font-weight: 700; color: var(--blue); line-height: 1; }
  .stat-label { font-size: 12px; color: var(--muted); margin-top: 4px; }

  .sentiment-bar { display: flex; height: 10px; border-radius: 5px; overflow: hidden; margin-bottom: 10px; }
  .sentiment-bar .pos { background: #10b981; }
  .sentiment-bar .neu { background: #f59e0b; }
  .sentiment-bar .neg { background: #ef4444; }
  .sentiment-legend { display: flex; gap: 12px; }
  .legend-item { display: flex; align-items: center; gap: 5px; font-size: 12px; color: var(--muted); }
  .dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
  .dot-green { background: #10b981; }
  .dot-amber { background: #f59e0b; }
  .dot-red { background: #ef4444; }

  .theme-row { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
  .theme-name { font-size: 13px; color: var(--text); min-width: 140px; }
  .theme-track { flex: 1; background: var(--gray-mid); border-radius: 4px; height: 6px; overflow: hidden; }
  .theme-fill { height: 100%; background: var(--blue-mid); border-radius: 4px; }
  .theme-count { font-size: 12px; color: var(--muted); min-width: 24px; text-align: right; }

  .list-items { list-style: none; }
  .list-items li { font-size: 13px; color: var(--text); padding: 7px 0; border-bottom: 1px solid var(--gray-mid); display: flex; gap: 8px; align-items: flex-start; }
  .list-items li:last-child { border-bottom: none; }
  .list-num { font-size: 11px; font-weight: 600; color: var(--blue); background: var(--blue-light); border-radius: 4px; padding: 1px 6px; flex-shrink: 0; margin-top: 1px; }

  .rec-item { padding: 10px 12px; border-radius: 8px; margin-bottom: 8px; border-left: 3px solid; }
  .rec-high { background: #fff7ed; border-color: #ea580c; }
  .rec-medium { background: #fefce8; border-color: #ca8a04; }
  .rec-low { background: var(--gray-light); border-color: #9ca3af; }
  .rec-priority { font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px; }
  .rec-high .rec-priority { color: #ea580c; }
  .rec-medium .rec-priority { color: #ca8a04; }
  .rec-low .rec-priority { color: #6b7280; }
  .rec-action { font-size: 13px; font-weight: 500; color: var(--text); margin-bottom: 3px; }
  .rec-rationale { font-size: 12px; color: var(--muted); }

  .items-table { width: 100%; border-collapse: collapse; font-size: 13px; }
  .items-table th { text-align: left; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--muted); padding: 8px 10px; background: var(--gray-light); border-bottom: 1px solid var(--border); }
  .items-table td { padding: 8px 10px; border-bottom: 1px solid var(--gray-mid); vertical-align: top; }
  .items-table tr:last-child td { border-bottom: none; }
  .pill { display: inline-block; font-size: 11px; padding: 2px 8px; border-radius: 12px; font-weight: 500; }
  .pill-pos { background: var(--green-light); color: var(--green); }
  .pill-neg { background: var(--red-light); color: var(--red); }
  .pill-neu { background: var(--amber-light); color: var(--amber); }
  .pill-high { background: #fde8d8; color: #c2410c; }
  .pill-medium { background: #fef9c3; color: #854d0e; }
  .pill-low { background: var(--gray-light); color: #6b7280; }

  .error-box { background: var(--red-light); border: 1px solid #fca5a5; border-radius: var(--radius); padding: 1rem 1.25rem; color: var(--red); font-size: 14px; margin-bottom: 1rem; }

  .tab-row { display: flex; gap: 0; border-bottom: 1px solid var(--border); margin-bottom: 1rem; }
  .tab { padding: 8px 16px; font-size: 13px; font-weight: 500; color: var(--muted); cursor: pointer; border-bottom: 2px solid transparent; margin-bottom: -1px; background: none; border-top: none; border-left: none; border-right: none; }
  .tab.active { color: var(--blue); border-bottom-color: var(--blue); }
  .tab-content { display: none; }
  .tab-content.active { display: block; }
</style>
</head>
<body>

<header>
  <div class="logo">
    <svg viewBox="0 0 24 24"><path d="M9 19l-7-7 7-7"/><path d="M15 5l7 7-7 7"/></svg>
  </div>
  <h1>Customer Feedback Analyser Agent</h1>
  <p>Powered by Anthropic Claude</p>
</header>

<div class="main">
  <div class="input-card">
    <label for="feedback">Paste customer feedback below</label>
    <small>One feedback item per line. Numbers at the start (e.g. "1.") are automatically removed.</small>
    <textarea id="feedback" placeholder="1. The onboarding process is really confusing. I spent 20 minutes trying to figure out how to add my first team member.&#10;2. Love the dashboard design, very clean and intuitive.&#10;3. Would love a mobile app. I'm constantly on the go..."></textarea>
    <div class="btn-row">
      <button class="btn btn-primary" id="analyseBtn" onclick="runAnalysis()">Analyse Feedback</button>
      <button class="btn btn-secondary" onclick="loadSample()">Load sample data</button>
      <div class="spinner" id="spinner"></div>
      <span class="loading-msg" id="loadingMsg">Analysing — this takes 20–40 seconds...</span>
      <span class="item-count" id="itemCount"></span>
    </div>
  </div>

  <div id="errorBox" class="error-box" style="display:none;"></div>
  <div id="results"></div>
</div>

<script>
const SAMPLE = `1. The onboarding process is really confusing. I spent 20 minutes trying to figure out how to add my first team member.
2. Love the dashboard design, very clean and intuitive.
3. The system crashes every time I try to export a report with more than 500 rows.
4. Would love a mobile app. I'm constantly on the go and checking things on my phone is painful.
5. Pricing feels steep for small teams. Would be great to have a startup plan.
6. The bulk import feature saved us hours. Exactly what we needed.
7. Notifications are too frequent and I can't find where to customise them.
8. Integration with Slack would be a game changer for our team.
9. Dashboard takes forever to load when we have a large dataset. Sometimes over 30 seconds.
10. The customer support team is fantastic — responded within an hour.
11. Can't figure out how to set custom roles and permissions. The documentation doesn't help.
12. Would love to be able to schedule automated reports to be emailed weekly.
13. The search functionality is too basic. Can't filter by date range or status.
14. Really impressed with how fast new features are being released.
15. We keep getting logged out unexpectedly. Very frustrating during long sessions.
16. The API documentation is excellent — made integration straightforward.
17. Need better data visualisation options in the reporting module.
18. Onboarding flow needs a proper guided tour. New users are lost without it.
19. Performance has really improved lately — good work team.
20. Would be great to have a dark mode option.
21. The export function only supports CSV. Need PDF and Excel options.
22. Love the new filtering options added last month.
23. Session timeout is too aggressive — I lose my work frequently.
24. Custom branding options would help us present this to our clients.
25. The mobile experience is very poor. Buttons are too small and layout breaks.`;

function loadSample() {
  document.getElementById('feedback').value = SAMPLE;
  updateCount();
}

function updateCount() {
  const lines = document.getElementById('feedback').value.split('\n').filter(l => l.trim());
  document.getElementById('itemCount').textContent = lines.length + ' items';
}

document.getElementById('feedback').addEventListener('input', updateCount);

async function runAnalysis() {
  const text = document.getElementById('feedback').value.trim();
  if (!text) { showError('Please enter some feedback to analyse.'); return; }

  document.getElementById('analyseBtn').disabled = true;
  document.getElementById('spinner').style.display = 'block';
  document.getElementById('loadingMsg').style.display = 'block';
  document.getElementById('results').style.display = 'none';
  document.getElementById('errorBox').style.display = 'none';

  try {
    const resp = await fetch('/analyse', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: 'feedback=' + encodeURIComponent(text)
    });
    const data = await resp.json();
    if (data.error) { showError(data.error); return; }
    renderResults(data);
  } catch(e) {
    showError('Request failed: ' + e.message);
  } finally {
    document.getElementById('analyseBtn').disabled = false;
    document.getElementById('spinner').style.display = 'none';
    document.getElementById('loadingMsg').style.display = 'none';
  }
}

function showError(msg) {
  const box = document.getElementById('errorBox');
  box.textContent = msg;
  box.style.display = 'block';
  document.getElementById('analyseBtn').disabled = false;
  document.getElementById('spinner').style.display = 'none';
  document.getElementById('loadingMsg').style.display = 'none';
}

function sentClass(s) {
  if (!s) return '';
  const v = s.toLowerCase();
  if (v === 'positive') return 'pill-pos';
  if (v === 'negative') return 'pill-neg';
  return 'pill-neu';
}

function prioClass(p) {
  if (!p) return '';
  const v = p.toLowerCase();
  if (v === 'high') return 'pill-high';
  if (v === 'medium') return 'pill-medium';
  return 'pill-low';
}

function recClass(p) {
  if (!p) return 'rec-low';
  const v = p.toLowerCase();
  if (v === 'high') return 'rec-high';
  if (v === 'medium') return 'rec-medium';
  return 'rec-low';
}

function renderResults(data) {
  const sent = data.sentiment || {};
  const total = (sent.positive||0) + (sent.neutral||0) + (sent.negative||0) || 1;
  const posP = Math.round((sent.positive||0)/total*100);
  const neuP = Math.round((sent.neutral||0)/total*100);
  const negP = 100 - posP - neuP;

  const themes = (data.themes||[]);
  const maxTheme = Math.max(...themes.map(t => t.count||0), 1);

  const pains = (data.pain_points||[]);
  const feats = (data.feature_requests||[]);
  const highs = (data.positive_highlights||[]);
  const recs  = (data.recommendations||[]);
  const items = (data.item_analyses||[]);

  const html = `
  <div class="results-header">
    <h2>Analysis Report</h2>
    <span class="badge badge-blue">${data.item_count||0} items analysed</span>
  </div>

  <div class="grid-3">
    <div class="card stat">
      <div class="card-title">Total Feedback</div>
      <div class="stat-num">${data.item_count||0}</div>
      <div class="stat-label">items processed</div>
    </div>
    <div class="card stat">
      <div class="card-title">Negative Sentiment</div>
      <div class="stat-num" style="color:#ef4444">${negP}%</div>
      <div class="stat-label">need attention</div>
    </div>
    <div class="card stat">
      <div class="card-title">Feature Requests</div>
      <div class="stat-num" style="color:#8b5cf6">${feats.length}</div>
      <div class="stat-label">identified</div>
    </div>
  </div>

  <div class="grid-2">
    <div class="card">
      <div class="card-title">Sentiment breakdown</div>
      <div class="sentiment-bar">
        <div class="pos" style="width:${posP}%"></div>
        <div class="neu" style="width:${neuP}%"></div>
        <div class="neg" style="width:${negP}%"></div>
      </div>
      <div class="sentiment-legend">
        <div class="legend-item"><div class="dot dot-green"></div>Positive ${posP}%</div>
        <div class="legend-item"><div class="dot dot-amber"></div>Neutral ${neuP}%</div>
        <div class="legend-item"><div class="dot dot-red"></div>Negative ${negP}%</div>
      </div>
    </div>
    <div class="card">
      <div class="card-title">Themes by frequency</div>
      ${themes.map(t => `
        <div class="theme-row">
          <div class="theme-name">${t.name||''}</div>
          <div class="theme-track"><div class="theme-fill" style="width:${Math.round((t.count||0)/maxTheme*100)}%"></div></div>
          <div class="theme-count">${t.count||0}</div>
        </div>`).join('')}
    </div>
  </div>

  <div class="grid-2">
    <div class="card">
      <div class="card-title">Top pain points</div>
      <ul class="list-items">
        ${pains.map((p,i) => `<li><span class="list-num">${i+1}</span>${p}</li>`).join('')}
      </ul>
    </div>
    <div class="card">
      <div class="card-title">Top feature requests</div>
      <ul class="list-items">
        ${feats.map((f,i) => `<li><span class="list-num">${i+1}</span>${f}</li>`).join('')}
      </ul>
    </div>
  </div>

  <div class="card" style="margin-bottom:1rem">
    <div class="card-title">PM recommendations</div>
    ${recs.map(r => `
      <div class="rec-item ${recClass(r.priority)}">
        <div class="rec-priority">${r.priority||'NOTE'}</div>
        <div class="rec-action">${r.action||''}</div>
        <div class="rec-rationale">${r.rationale||''}</div>
      </div>`).join('')}
  </div>

  ${highs.length ? `
  <div class="card" style="margin-bottom:1rem">
    <div class="card-title">Positive highlights</div>
    <ul class="list-items">
      ${highs.map((h,i) => `<li><span class="list-num">${i+1}</span>${h}</li>`).join('')}
    </ul>
  </div>` : ''}

  ${items.length ? `
  <div class="card">
    <div class="card-title">Item-level analysis</div>
    <div class="tab-row">
      <button class="tab active" onclick="switchTab('all')">All</button>
      <button class="tab" onclick="switchTab('negative')">Negative</button>
      <button class="tab" onclick="switchTab('positive')">Positive</button>
      <button class="tab" onclick="switchTab('high')">High priority</button>
    </div>
    <div id="tab-all" class="tab-content active">
      <table class="items-table">
        <thead><tr><th>#</th><th>Feedback</th><th>Theme</th><th>Sentiment</th><th>Priority</th></tr></thead>
        <tbody>
          ${items.map(it => `
          <tr>
            <td>${it.item_number||''}</td>
            <td>${it.key_point||it.text||''}</td>
            <td>${it.theme||''}</td>
            <td><span class="pill ${sentClass(it.sentiment)}">${it.sentiment||''}</span></td>
            <td><span class="pill ${prioClass(it.priority_signal)}">${it.priority_signal||''}</span></td>
          </tr>`).join('')}
        </tbody>
      </table>
    </div>
    <div id="tab-negative" class="tab-content">
      <table class="items-table">
        <thead><tr><th>#</th><th>Feedback</th><th>Theme</th><th>Priority</th></tr></thead>
        <tbody>
          ${items.filter(it => (it.sentiment||'').toLowerCase()==='negative').map(it => `
          <tr>
            <td>${it.item_number||''}</td>
            <td>${it.key_point||it.text||''}</td>
            <td>${it.theme||''}</td>
            <td><span class="pill ${prioClass(it.priority_signal)}">${it.priority_signal||''}</span></td>
          </tr>`).join('')}
        </tbody>
      </table>
    </div>
    <div id="tab-positive" class="tab-content">
      <table class="items-table">
        <thead><tr><th>#</th><th>Feedback</th><th>Theme</th></tr></thead>
        <tbody>
          ${items.filter(it => (it.sentiment||'').toLowerCase()==='positive').map(it => `
          <tr>
            <td>${it.item_number||''}</td>
            <td>${it.key_point||it.text||''}</td>
            <td>${it.theme||''}</td>
          </tr>`).join('')}
        </tbody>
      </table>
    </div>
    <div id="tab-high" class="tab-content">
      <table class="items-table">
        <thead><tr><th>#</th><th>Feedback</th><th>Theme</th><th>Sentiment</th></tr></thead>
        <tbody>
          ${items.filter(it => (it.priority_signal||'').toLowerCase()==='high').map(it => `
          <tr>
            <td>${it.item_number||''}</td>
            <td>${it.key_point||it.text||''}</td>
            <td>${it.theme||''}</td>
            <td><span class="pill ${sentClass(it.sentiment)}">${it.sentiment||''}</span></td>
          </tr>`).join('')}
        </tbody>
      </table>
    </div>
  </div>` : ''}`;

  const results = document.getElementById('results');
  results.innerHTML = html;
  results.style.display = 'block';
  results.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function switchTab(name) {
  document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.getElementById('tab-' + name).classList.add('active');
  event.target.classList.add('active');
}
</script>
</body>
</html>"""


# ── HTTP request handler ───────────────────────────────────────────────────────

class Handler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        pass  # suppress default logging

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(HTML.encode("utf-8"))

    def do_POST(self):
        if self.path == "/analyse":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8")
            params = parse_qs(body)
            feedback_text = params.get("feedback", [""])[0]

            result = run_analysis(feedback_text)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(result).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()


# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"\n  Customer Feedback Analyser Agent — Web UI")
    print(f"  ─────────────────────────────────────────")
    print(f"  Open in browser: http://localhost:{port}")
    print(f"  Press Ctrl+C to stop\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Server stopped.")
        sys.exit(0)
