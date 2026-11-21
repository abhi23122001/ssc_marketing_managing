#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module 14 - Email Assistant (SHAH AI).

Draft-only, read-only email analysis for Shah Surveyors & Consultancy (SSC).

WHAT THIS MODULE DOES (always works):
  * Parses an email file or pasted text (stdlib-only; .eml and plain text).
  * CLASSIFIES each email into:
        NTPC, Clients, Contractors, Vendors, Finance, HR, Personal, Notifications
  * Produces a summary, priority, follow-up recommendations and a bilingual
    (English + Hinglish) reply draft.

WHAT THIS MODULE DOES NOT DO BY DEFAULT:
  * No email is sent. No Gmail state is changed. No account, API or paid
    service is installed.
  * A Gmail OAuth adapter is provided but DISABLED until the owner supplies
    credentials and places a token file OUTSIDE the repository. It never
    automatically sends email.

Run directly:
    python3 scripts/EmailAssistant.py analyze --file messages/inbox.eml
    python3 scripts/EmailAssistant.py classify --file messages/inbox.eml
    python3 scripts/EmailAssistant.py summary --file messages/inbox.eml
    python3 scripts/EmailAssistant.py priority --file messages/inbox.eml
    python3 scripts/EmailAssistant.py follow-up --file messages/inbox.eml
    python3 scripts/EmailAssistant.py bilingual --file messages/inbox.eml
    python3 scripts/EmailAssistant.py dry-run --file messages/inbox.eml
"""
import argparse
import csv
import re
import sys
from datetime import date
from email import policy
from email.parser import BytesParser
from pathlib import Path

HERE = Path(__file__).resolve()
REPO_ROOT = None
for candidate in [HERE] + list(HERE.parents):
    if (Path(candidate) / "modules").is_dir():
        REPO_ROOT = Path(candidate)
        break
if REPO_ROOT is None:
    REPO_ROOT = Path.cwd().resolve()

OUTPUTS_DIR = REPO_ROOT / "outputs"

CATEGORIES = [
    "NTPC", "Clients", "Contractors", "Vendors", "Finance", "HR", "Personal", "Notifications",
]

# Keyword heuristics (matched case-insensitively against subject + body + from).
CATEGORY_KEYWORDS = {
    "NTPC": [
        "ntpc", "ntp", "national thermal", "national thermal power",
        "ncl", "secl", "coal india", "coal india ltd", "coal india limited",
        "coth", "heri", "mow", "shakti", "coal ministry",
    ],
    "Clients": [
        "client", "customer", "c/l ", "contractor client", "client project",
        "client update", "client meeting", "client feedback",
    ],
    "Contractors": [
        "contractor", "contracting", "subcontract", "subcontractor",
        "contractor firm", "contractor company", "construction contractor",
        "drilling contractor", "excavation contractor",
    ],
    "Vendors": [
        "vendor", "supplier", "equipment vendor", "material vendor",
        "vendor firm", "vendor company", "supply chain", "procurement",
    ],
    "Finance": [
        "finance", "accounts", "invoice", "billing", "payment", "gst",
        "tax", "bank ", "rtgs", "neft", "itr", "audit", "arrears",
    ],
    "HR": [
        "hr", "human resources", "recruitment", "resume", "applicant",
        "employee", "hiring", "interview", "offer letter", "offer letter",
        "joining letter", "onboarding", "paid leave", "casual leave",
    ],
    "Personal": [
        "personal", "family", "friends", "friend", "personal project",
        "gift", "wedding", "birthday",
    ],
    "Notifications": [
        "notify", "notification", "reminder", "automatic", "system",
        "no-reply", "mailer", "weekly report", "daily report", "alert",
        "auto-generated", "out of office", "away",
    ],
}

URGENT_KEYWORDS = {
    "High": ["urgent", "asap", "immediately", "today", "deadline", "now",
             "projected", "critical", "escalat", "expedite", "mandatory",
             "fire", "call today"],
}

# Generic follow-up text per category (merged with priority).
FOLLOWUP_TEMPATE = {
    "NTPC": "Review scope/requirements and request a formal written summary and quote.",
    "Clients": "Acknowledge promptly and schedule a discussion to understand requirements.",
    "Contractors": "Send a formal quote/terms and update the lead record.",
    "Vendors": "Confirm delivery timeline, EOD details and next review date.",
    "Finance": "Review invoicing/payment; confirm reference values and due dates.",
    "HR": "Review resume/interview schedule and coordinate next round.",
    "Personal": "Follow up as needed; keep the record private.",
    "Notifications": "No action required unless flagged urgent.",
}


def _norm(text):
    return " ".join(str(text or "").split()).lower()


def _blob(subject, from_email, body):
    return " ".join([_norm(subject), _norm(from_email), _norm(body)])


def classify(subject, from_email, body):
    """Return the single best category for an email."""
    best = "Notifications"
    best_score = -1
    blob = _blob(subject, from_email, body)
    for cat, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in blob)
        if score > best_score:
            best_score = score
            best = cat
    # Presentational rule: urgent signals can override for some categories.
    if best == "Notifications":
        if any(k in blob for k in URGENT_KEYWORDS["High"]):
            return "HR" if any(k in blob for k in ["interview", "resume", "offer", "hr"]) else "Finance"
    return best


def summarize(subject, from_email, body, max_bullets=4):
    """Return a concise bullet list summarising the email body."""
    text = (body or "").strip()
    # Split into sentences on sentence-ending punctuation.
    sentences = re.split(r"(?<=[.!?])\s+", text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 25]
    picked = []
    for s in sentences[: max_bullets * 3]:
        if len(picked) >= max_bullets:
            break
        if s not in picked:
            picked.append(s)
    if not picked:
        picked = [text[:200] + ("..." if len(text) > 200 else "")]
    lines = []
    for s in picked:
        lines.append("- " + s[:200].replace("\n", " "))
    return lines


def priority(subject, from_email, body, category):
    """Derive an action priority: High / Medium / Low."""
    blob = _blob(subject, from_email, body)
    high_signals = [k for k in URGENT_KEYWORDS["High"] if k in blob]
    if high_signals:
        return "High"
    if category == "Notifications":
        return "Low"
    # Finance and personal remain medium/low.
    return "Medium"


def follow_up_recommendations(subject, from_email, body, category, priority):
    """Actionable follow-up text derived from existing fields (no contact made)."""
    recs = []
    if category == "Notifications":
        recs.append("No action required unless flagged urgent.")
    else:
        recs.append(FOLLOWUP_TEMPATE.get(category, "Review and respond."))
    if priority == "High":
        recs.append("Respond/act today.")
    if category == "NTPC" and priority != "High":
        recs.append("Follow up within 3 business days.")
    elif category in ("Contractors", "Vendors") and priority != "High":
        recs.append("Follow up within 7 days.")
    if not recs:
        recs.append("Review record; monitor for updates.")
    return recs


def _lang(language):
    return (language or "en").lower()


def _hinglish(canonical):
    pairs = {
        "review": "review karein",
        "respond": "jawab do",
        "follow up": "follow-up karein",
        "discussion": "baithak",
        "meeting": "meet",
        "application": "application",
        "enquiry": "enquiry",
        "custom": "custom",
        "project": "project",
        "please": "kripya",
        "kindly": "kripya",
        "thanks": "shukriya",
        "thank you": "shukriya",
        "hi": "namaste",
    }
    out = canonical
    for eng, hin in pairs.items():
        out = out.replace(" " + eng, " " + hin)
    return out


def bilingual_reply_draft(recipient, subject, body, category, summary_lines):
    """Return a bilingual (English + Hinglish) reply draft for owner review."""
    subject_line = subject or "Your email"
    recipient_line = recipient or "the sender"
    eng_lines = [
        "Subject: %s" % subject_line,
        "To: %s" % recipient_line,
        "Dear Ma'am / Sir,",
        "Thank you for your message. We have noted the following:",
    ]
    for s in summary_lines:
        eng_lines.append("  - " + s)
    eng_lines += [
        "Could you please confirm your requirements and timeline?",
        "We will respond within 1-2 business days.",
        "Thank you.",
        "Regards,",
        "Shah Surveyors & Consultancy (SSC)",
    ]
    hin_lines = [
        "Subject: %s" % subject_line,
        "To: %s" % recipient_line,
        "Namaste,",
        "Aapki message padh li. Humne niche diya hai:",
    ]
    for s in summary_lines:
        hin_lines.append("  - " + s)
    hin_lines += [
        "Kripya aapki requirements aur timeline confirm karein.",
        "Hum 1-2 business days ke andar reply karenge.",
        "Shukriya.",
        "Regards,",
        "Shah Surveyors & Consultancy (SSC)",
    ]
    return {
        "language": "en",
        "draft_en": "\n".join(eng_lines),
        "language_hi": "hi",
        "draft_hi": "\n".join(hin_lines),
    }


def analyze_email(subject, from_email, body, language="en"):
    """Run the full analysis pipeline and return a dict."""
    cat = classify(subject, from_email, body)
    pri = priority(subject, from_email, body, cat)
    recs = follow_up_recommendations(subject, from_email, body, cat, pri)
    summary = summarize(subject, from_email, body)
    return {
        "subject": subject,
        "from_email": from_email,
        "category": cat,
        "priority": pri,
        "summary": summary,
        "follow_up": recs,
        "bilingual": bilingual_reply_draft(from_email, subject, body, cat, summary),
    }


def dry_run(analysis):
    print("=" * 66)
    print("  SHAH AI - Email Assistant (Dry-run only)")
    print("  Date: {}".format(date.today().isoformat()))
    print("  Mode: read-only. No email is sent.")
    print("=" * 66)
    print("  Subject : {}".format(analysis["subject"]))
    print("  From    : {}".format(analysis["from_email"]))
    print("  Category: {}".format(analysis["category"]))
    print("  Priority: {}".format(analysis["priority"]))
    print("  Summary :")
    for s in analysis["summary"]:
        print("    {}".format(s))
    print("  Follow-up:")
    for r in analysis["follow_up"]:
        print("    - {}".format(r))
    print("  Reply draft (English):")
    print("    " + analysis["bilingual"]["draft_en"].replace("\n", "\n    "))
    print("  Reply draft (Hinglish):")
    print("    " + analysis["bilingual"]["draft_hi"].replace("\n", "\n    "))
    print("=" * 66)


# --- GmailSync (optional, disabled by default) ----------------------------------
class NotConfiguredError(Exception):
    pass


class GmailSync:
    """Read-only Gmail access. Must be configured with OAuth tokens that live
    OUTSIDE this repository. No sending is ever automatic."""

    def __init__(self, config_path=None):
        self.config_path = Path(config_path) if config_path else self._default_config()

    def _default_config(self):
        return (Path.home() / ".hermes" / "shah-ai" / "gmail" / "token.json")

    def is_configured(self):
        return self.config_path.exists()

    def read_only(self):
        if not self.is_configured():
            raise NotConfiguredError(
                "Gmail is not configured. Place a token.json OUTSIDE the repository at "
                "{}, or use the --file/--text mode (draft-only). "
                "See modules/14-email-assistant/README.md".format(self.config_path))
        # In a fully wired deployment the Gmail API client would fetch messages
        # here. This implementation refuses to auto-read external Gmail until the
        # owner completes OAuth setup and approves the read flow.
        return []

    def send_draft(self, draft):
        if not self.is_configured():
            raise NotConfiguredError(
                "Gmail is not configured; email send is blocked. Requires explicit "
                "owner approval and a configured token outside the repository.")
        raise NotImplementedError(
            "Email sending is never automatic. This method is a draft-only stub; "
            "publishing/sending requires an explicit approval record.")


# --- Parsing helpers -----------------------------------------------------------
def parse_email_file(path):
    """Return (subject, from_email, body) from a .eml or plain text file."""
    raw = path.read_bytes()
    if path.suffix.lower() == ".eml":
        msg = BytesParser(policy=policy.default).parsebytes(raw)
        subject = str(msg.get("Subject") or "")
        from_email = str(msg.get("From") or "")
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                ct = str(part.get_content_type())
                if "text/plain" in ct:
                    try:
                        body += part.get_content()
                    except Exception:
                        pass
        if not body:
            body = str(msg.get_content() or "")
    else:
        text = path.read_text(encoding="utf-8", errors="replace")
        subject = ""
        from_email = ""
        body = text
    return subject, from_email, body


# --- CLI -----------------------------------------------------------------------
def build_parser():
    p = argparse.ArgumentParser(prog="EmailAssistant.py", description="SHAH AI Module 14 Email Assistant (draft-only)")
    sub = p.add_subparsers(dest="command", required=True)

    def add_common(sub):
        sub.add_argument("--file", type=Path, help="Path to an email file (.eml or text)")
        sub.add_argument("--text", default=None, help="Paste email body text directly")

    sp = sub.add_parser("analyze", help="Run the full analysis pipeline")
    add_common(sp)
    sp.set_defaults(func=cmd_analyze)

    sp = sub.add_parser("classify", help="Classify an email")
    add_common(sp)
    sp.set_defaults(func=cmd_classify)

    sp = sub.add_parser("summary", help="Summarise an email")
    add_common(sp)
    sp.set_defaults(func=cmd_summary)

    sp = sub.add_parser("priority", help="Derive priority")
    add_common(sp)
    sp.set_defaults(func=cmd_priority)

    sp = sub.add_parser("follow-up", help="Follow-up recommendations")
    add_common(sp)
    sp.set_defaults(func=cmd_followup)

    sp = sub.add_parser("bilingual", help="Bilingual reply draft")
    add_common(sp)
    sp.set_defaults(func=cmd_bilingual)

    sp = sub.add_parser("dry-run", help="Dry-run summary (no state change)")
    add_common(sp)
    sp.set_defaults(func=cmd_dryrun)

    return p


def _load(args):
    if args.file:
        subject, from_email, body = parse_email_file(args.file)
    else:
        subject = args.text or ""
        from_email = args.text or ""
        body = args.text or ""
    return subject, from_email, body


def cmd_analyze(args):
    subject, from_email, body = _load(args)
    res = analyze_email(subject, from_email, body)
    for k in ("subject", "from_email", "category", "priority"):
        print("{}: {}".format(k, res[k]))
    print("Summary:")
    for s in res["summary"]:
        print("  - " + s)
    print("Follow-up:")
    for r in res["follow_up"]:
        print("  - " + r)
    return 0


def cmd_classify(args):
    subject, from_email, body = _load(args)
    print("Category: {}".format(classify(subject, from_email, body)))
    return 0


def cmd_summary(args):
    subject, from_email, body = _load(args)
    for s in summarize(subject, from_email, body):
        print(s)
    return 0


def cmd_priority(args):
    subject, from_email, body = _load(args)
    print("Priority: {}".format(priority(subject, from_email, body, "")))
    return 0


def cmd_followup(args):
    subject, from_email, body = _load(args)
    for r in follow_up_recommendations(subject, from_email, body, "", ""):
        print("- " + r)
    return 0


def cmd_bilingual(args):
    subject, from_email, body = _load(args)
    res = analyze_email(subject, from_email, body)
    print("English:")
    print(res["bilingual"]["draft_en"])
    print("\nHinglish:")
    print(res["bilingual"]["draft_hi"])
    return 0


def cmd_dryrun(args):
    subject, from_email, body = _load(args)
    res = analyze_email(subject, from_email, body)
    dry_run(res)
    return 0


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
