"""
Customer Feedback Analyser Agent
---------------------------------
An agentic AI tool that transforms raw customer feedback into structured,
PM-ready product insights using the Anthropic Claude API.

Author: Arun Soman
"""

import anthropic
import argparse
import json
import sys
from pathlib import Path


def load_feedback(filepath: str) -> list[str]:
    """Load feedback items from a text file (one item per line)."""
    path = Path(filepath)
    if not path.exists():
        print(f"Error: File '{filepath}' not found.")
        sys.exit(1)

    with open(path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f.readlines()]
        # Remove empty lines and strip leading numbers/punctuation
        items = []
        for line in lines:
            if not line:
                continue
            # Strip leading numbers like "1. " or "1) "
            if line[0].isdigit():
                parts = line.split(".", 1) if "." in line[:3] else line.split(")", 1)
                if len(parts) == 2:
                    line = parts[1].strip()
            items.append(line)
        return items


def analyse_individual_items(client: anthropic.Anthropic, feedback_items: list[str]) -> list[dict]:
    """
    Pass 1: Analyse each feedback item individually.
    Categorise by theme and score sentiment.
    """
    print("\nPass 1: Analysing individual feedback items...")

    feedback_text = "\n".join([f"{i+1}. {item}" for i, item in enumerate(feedback_items)])

    prompt = f"""You are a senior product analyst. Analyse the following customer feedback items.

For EACH item, return a JSON object with:
- "item_number": the item number (integer)
- "text": the original feedback text
- "theme": one of [UX/Navigation, Performance/Speed, Feature Request, Bug/Error, Pricing, Positive/Praise, Support/Documentation, Other]
- "sentiment": one of [Positive, Neutral, Negative]
- "key_point": a 5-10 word summary of the core issue or praise
- "priority_signal": one of [High, Medium, Low] based on how impactful this seems for product decisions

Return ONLY a valid JSON array of objects, no other text, no markdown, no explanation.

FEEDBACK ITEMS:
{feedback_text}"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )

    response_text = message.content[0].text.strip()

    try:
        analyses = json.loads(response_text)
        print(f"  ✓ Analysed {len(analyses)} feedback items")
        return analyses
    except json.JSONDecodeError:
        print("  Warning: Could not parse individual analyses. Proceeding with raw text.")
        return []


def synthesise_insights(client: anthropic.Anthropic, analyses: list[dict], raw_feedback: list[str]) -> str:
    """
    Pass 2: Synthesise individual analyses into a structured PM-ready summary.
    This mirrors how a PM would step back and find patterns after reading all feedback.
    """
    print("Pass 2: Synthesising insights into PM-ready summary...")

    if analyses:
        analysis_text = json.dumps(analyses, indent=2)
        input_data = f"STRUCTURED ANALYSES:\n{analysis_text}"
    else:
        input_data = "RAW FEEDBACK:\n" + "\n".join([f"{i+1}. {item}" for i, item in enumerate(raw_feedback)])

    prompt = f"""You are a senior Product Manager synthesising customer feedback into an executive-ready insight report.

Based on the following feedback analyses, produce a structured PM report that includes:

1. THEMES IDENTIFIED — list each theme with count of mentions
2. SENTIMENT BREAKDOWN — percentage breakdown of Positive / Neutral / Negative
3. TOP PAIN POINTS — the 3-5 most critical issues customers are experiencing (ranked by frequency and severity)
4. TOP FEATURE REQUESTS — the 3-5 most requested capabilities (ranked by frequency)
5. POSITIVE HIGHLIGHTS — what customers are praising (keep brief)
6. PM RECOMMENDATIONS — 3-5 prioritised, actionable recommendations with clear rationale
   Format each as: [PRIORITY LEVEL]: [Recommendation] — [Why: brief evidence from the data]

Write this as a clear, professional report a Head of Product would act on immediately.
Use plain text formatting with clear section headers using ===.
Be specific and evidence-based — reference actual feedback patterns, not vague generalities.

{input_data}"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}]
    )

    return message.content[0].text.strip()


def save_report(report: str, output_path: str = "feedback_report.txt"):
    """Save the generated report to a file."""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"\n  ✓ Report saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Customer Feedback Analyser Agent — transforms raw feedback into PM-ready insights"
    )
    parser.add_argument(
        "--input",
        type=str,
        default="sample_feedback.txt",
        help="Path to feedback file (one item per line)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="feedback_report.txt",
        help="Path to save the generated report"
    )
    args = parser.parse_args()

    print("=" * 60)
    print("  Customer Feedback Analyser Agent")
    print("  Powered by Anthropic Claude")
    print("=" * 60)

    # Initialise Anthropic client
    client = anthropic.Anthropic()

    # Load feedback
    print(f"\nLoading feedback from: {args.input}")
    feedback_items = load_feedback(args.input)
    print(f"  ✓ Loaded {len(feedback_items)} feedback items")

    # Pass 1: Analyse individual items
    analyses = analyse_individual_items(client, feedback_items)

    # Pass 2: Synthesise into PM report
    report = synthesise_insights(client, analyses, feedback_items)

    # Display report
    print("\n" + "=" * 60)
    print(report)
    print("=" * 60)

    # Save report
    save_report(report, args.output)


if __name__ == "__main__":
    main()
