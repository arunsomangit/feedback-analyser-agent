![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![Claude API](https://img.shields.io/badge/Anthropic-Claude%20API-orange.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

# Customer Feedback Analyser Agent

An agentic AI tool that transforms raw customer feedback into structured, PM-ready product insights — using the Anthropic Claude API.

Available in two modes:
- **Web UI** (`app.py`) — browser-based dashboard with visual results
- **CLI** (`agent.py`) — command-line tool that outputs a text report

---

## What it does

1. Accepts a batch of customer feedback (text file or pasted into the web UI)
2. Categorises each item by theme (UX, Performance, Feature Request, Bug, Pricing, etc.)
3. Analyses sentiment (Positive, Neutral, Negative)
4. Identifies the top pain points and feature requests
5. Produces a structured PM-ready insight summary with prioritised recommendations

---

## Web UI (recommended)

Run the web app and open it in your browser for a visual dashboard.

```bash
# Install dependencies
pip install anthropic

# Set your API key
export ANTHROPIC_API_KEY=your_api_key_here

# Start the web server
python app.py

# Open in browser
http://localhost:8080
```

### What the dashboard shows

- **Sentiment breakdown** — visual bar showing positive / neutral / negative split
- **Theme frequency** — horizontal bar chart of identified themes by mention count
- **Top pain points** — ranked list of the most critical issues
- **Top feature requests** — ranked list of most requested capabilities
- **PM recommendations** — prioritised actions (HIGH / MEDIUM / LOW) with evidence-based rationale
- **Item-level analysis** — filterable table of every feedback item with theme, sentiment, and priority signal

---

## CLI (command line)

Run the agent from the terminal and save the report to a text file.

```bash
# Install dependencies
pip install anthropic

# Set your API key
export ANTHROPIC_API_KEY=your_api_key_here

# Run with sample data
python agent.py --input sample_feedback.txt

# Run with your own feedback file
python agent.py --input your_feedback.txt

# Specify output file
python agent.py --input your_feedback.txt --output my_report.txt
```

---

## Example output (CLI)

```
=== FEEDBACK ANALYSIS REPORT ===

THEMES IDENTIFIED:
  - UX/Navigation: 8 mentions
  - Performance/Speed: 6 mentions
  - Feature Requests: 5 mentions
  - Bugs/Errors: 4 mentions
  - Pricing: 2 mentions

SENTIMENT BREAKDOWN:
  - Negative: 52%
  - Positive: 31%
  - Neutral: 17%

TOP PAIN POINTS:
  1. Onboarding flow is confusing — users struggle to complete setup
  2. Dashboard loads slowly, especially with large datasets
  3. No bulk export functionality

TOP FEATURE REQUESTS:
  1. Mobile app or responsive mobile view
  2. Integration with Slack for notifications
  3. Custom reporting templates

PM RECOMMENDATIONS (prioritised by frequency + sentiment):
  HIGH PRIORITY: Simplify onboarding flow — highest frequency, strongest negative sentiment
  HIGH PRIORITY: Performance optimisation for dashboard load time
  MEDIUM PRIORITY: Bulk export feature
  CONSIDER: Mobile responsiveness (feature request volume growing)
```

---

## Project structure

```
feedback-analyser-agent/
├── app.py                  # Web UI — browser-based dashboard
├── agent.py                # CLI — command-line text report
├── sample_feedback.txt     # 25 sample feedback items for testing
├── requirements.txt        # Python dependencies
└── README.md
```

---

## Architecture — two-pass agentic approach

The agent uses a deliberate two-pass design that mirrors how a senior PM actually processes feedback:

**Pass 1 — Item Analysis**
Each feedback item is individually analysed by Claude. For every item, the agent returns:
- Theme classification
- Sentiment score (Positive / Neutral / Negative)
- Key point summary (5–10 words)
- Priority signal (High / Medium / Low)

**Pass 2 — Synthesis**
The structured item-level outputs are fed back into Claude for pattern recognition and synthesis. The agent produces:
- Theme frequency breakdown
- Sentiment aggregate
- Top pain points ranked by frequency and severity
- Top feature requests ranked by demand
- PM recommendations with evidence-based rationale

This two-pass approach produces more reliable, structured output than a single-prompt summarisation — and it means the agent can explain *why* it made each recommendation, not just what the recommendation is.

---

## Design decisions

| Decision | Rationale |
|---|---|
| Two-pass architecture | Mirrors real PM thinking — item-level first, pattern recognition second |
| Structured JSON output (Pass 2) | Enables the web UI to render visual components from agent output |
| No external web framework | `http.server` is built into Python — zero additional dependencies |
| Graceful error handling | Agent degrades cleanly on ambiguous or low-quality input |
| Prompt specificity | Vague prompts produce vague outputs — every prompt specifies exact output schema |

---

## Setup — get your API key

1. Create a free account at [console.anthropic.com](https://console.anthropic.com)
2. Generate an API key
3. Set it as an environment variable:

```bash
# macOS / Linux
export ANTHROPIC_API_KEY=your_key_here

# Windows (Command Prompt)
set ANTHROPIC_API_KEY=your_key_here

# Windows (PowerShell)
$env:ANTHROPIC_API_KEY="your_key_here"
```

---

## Requirements

- Python 3.9+
- `anthropic` Python SDK (`pip install anthropic`)
- Anthropic API key

---

## Author

**Arun Soman** — Senior Product Manager / Lead Product Owner

[LinkedIn](https://www.linkedin.com/in/arunsoman-biography/) | [Portfolio](https://arunsomangit.github.io/arunsoman/) | [GitHub](https://github.com/arunsomangit)

---

*Built to demonstrate practical Agentic AI application in a product management context.*
