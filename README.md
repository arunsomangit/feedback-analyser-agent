# Customer Feedback Analyser Agent

An agentic AI tool that transforms raw customer feedback into structured, PM-ready product insights — using the Anthropic Claude API.

## What it does

1. Accepts a batch of customer feedback (text file or inline)
2. Categorises each item by theme (e.g. UX, Performance, Feature Request, Bug, Pricing)
3. Analyses sentiment (Positive, Neutral, Negative)
4. Identifies the top pain points and feature requests
5. Produces a structured PM-ready insight summary with prioritised recommendations

## Why it exists

Product Managers and Product Owners spend significant time manually triaging customer feedback. This agent automates the initial synthesis layer — surfacing patterns, themes, and priorities so the PM team can focus on decisions, not data processing.

## Tech stack

- Python 3.9+
- Anthropic Claude API (claude-sonnet-4-6)
- No external dependencies beyond `anthropic`

## Setup

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/feedback-analyser-agent.git
cd feedback-analyser-agent

# Install dependencies
pip install anthropic

# Set your API key
export ANTHROPIC_API_KEY=your_api_key_here

# Run with sample data
python agent.py --input sample_feedback.txt

# Run with your own feedback file
python agent.py --input your_feedback.txt
```

## Output example

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

## Architecture

The agent uses a two-pass approach:
1. **Pass 1 — Item Analysis**: Each feedback item is individually categorised and sentiment-scored
2. **Pass 2 — Synthesis**: The agent aggregates individual analyses into a structured PM summary with prioritised recommendations

This mirrors how a senior PM would manually triage feedback — line by line first, then pattern recognition.

## Interview / demo notes

This project was built to demonstrate practical Agentic AI application in a product management context. The key design decisions:

- **Two-pass architecture** mirrors real PM thinking (item-level → pattern-level)
- **Structured output** is designed to be immediately actionable, not just interesting
- **Prompt design** emphasises specificity — vague prompts produce vague outputs
- **Error handling** ensures the agent degrades gracefully on ambiguous or low-quality input

## Author

Arun Soman — Senior Product Manager / Lead Product Owner
[LinkedIn](https://www.linkedin.com/in/arunsoman-biography/) | [Website](https://arunsomangit.github.io/arunsoman/)
