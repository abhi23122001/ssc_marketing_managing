#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module 12 - Content Calendar & Content Generation (SHAH AI) - generator.

Pure, template-driven drafting helpers. No network calls, no accounts, no
payment. Drafts are written to outputs/ with an approval-required header.

Supported output shapes (driven by a calendar row):
    blog      -> service/website blog brief
    reel      -> Instagram/Facebook reel script
    linkedin  -> LinkedIn B2B post
    gbp-post  -> Google Business Profile post draft
    outreach  -> bilingual (English + Hinglish) outreach draft

Run directly:
    python3 scripts/ContentGenerator.py generate-all --calendar data/m12-content-calendar.csv --out outputs/12
    python3 scripts/ContentGenerator.py generate-one --id 1 --outdir outputs/12 --platform reel
"""
import argparse
import re
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve()
REPO_ROOT = None
for candidate in [HERE] + list(HERE.parents):
    if (Path(candidate) / "modules").is_dir():
        REPO_ROOT = Path(candidate)
        break
if REPO_ROOT is None:
    REPO_ROOT = Path.cwd().resolve()

TEMPLATES_DIR = REPO_ROOT / "shared" / "templates"
OUTPUTS_DIR = REPO_ROOT / "outputs"
DEFAULT_OUT_DIR = OUTPUTS_DIR / "12"

DRAFT_HEADER = """---
status: DRAFT
source: modules/12-content-calendar-content-generation/scripts/ContentGenerator.py
approval_required: yes
module: 12-content-calendar-content-generation
---

"""


def _slug(topic):
    slug = re.sub(r"[^a-z0-9]+", "-", topic.lower()).strip("-")
    return slug or "topic"


def _platform_sections(platform, language, topic):
    """Return a dict of HTML-ish markdown to attach for a platform/language."""
    plat = (platform or "").lower()
    lang = (language or "").lower()
    sections = {}

    if "reel" in plat or "instagram" in plat or "facebook" in plat:
        sections["hook"] = ("Hook (under 8-10 words) - e.g. 'Why your foundation may be wrong.' "
                            if lang in {"en", "eng", "english"} else
                            "Hook (8-10 words) - कृपया रोचक प 향수 (hook) लिखें।")
        sections["visual"] = "- Shot 1: ..." 
        sections["caption"] = "Caption (moderate length) - explain the value of survey data: planning, measurement, documentation, decision support, site coordination."
        sections["cta"] = "Single low-pressure CTA: request a discussion / share project requirements / request a quotation. Do not invent contact details."
        sections["hashtag"] = "#survey #geospatial #mparchitect #singrauli #waidhan #mp (relevant only; no keyword stuffing)"
    if "linkedin" in plat:
        sections["hook"] = "Hook (3-5 lines, professional) - value of survey data for EPC/contractor planning and site coordination."
        sections["message"] = "Main message in 3-5 bullet points covering planning, measurement, documentation, decision support."
        sections["cta"] = "Low-pressure CTA: request a discussion / share project requirements."
        sections["hashtag"] = "#survey #construction #mining #power #solar #mp #b2b (relevant only)"
    if "gbp" in plat:
        sections["headline"] = "Headline - factual service/location focus."
        sections["message"] = "2-3 sentence value statement about survey data for planning, measurement, documentation and site coordination."
        sections["cta"] = "Call to action: request a discussion / share project requirements. No fabricated offers, hours or locations."
    if "outreach" in plat or "email" in plat or "mail" in plat:
        sections["subject"] = "Subject (no fabricated authority)."
        sections["opening"] = "Opening - reference the shared public material, no invented names."
        sections["body"] = "Body - offer a discussion, ask for a reply, no pressure."
        sections["closing"] = "Closing - request a discussion / share project requirements. No fabricated email addresses or phone numbers."
    return sections


def _lang_suffix(language):
    lang = (language or "en").lower()
    if "hi" in lang or "hin" in lang:
        return ".hi"
    return ".en"


def generate_blog_brief(row, out_dir: Path):
    topic = (row.get("topic") or "").strip()
    owner = (row.get("owner") or "").strip() or "SSC owner"
    platform = (row.get("platform") or "").strip()
    language = (row.get("language") or "en").strip()
    subject = out_dir / ("12-blog-{}{}".format(_slug(topic), _lang_suffix(language)))
    lines = []
    lines.append("# SHAH AI - Draft: {} (Blog)".format(topic))
    lines.append("")
    lines.append(DRAFT_HEADER)
    lines.append("> This is a **draft draft**. It is a template and does not contain confirmed facts.")
    lines.append("> Add owner-confirmed facts and a source URL before review.")
    lines.append("")
    lines.append("## 1. Objective")
    lines.append("")
    lines.append("Publish a service/education page: why a particular survey matters for {} planning, measurement, documentation and site coordination.".format(topic))
    lines.append("")
    lines.append("## 2. Target audience")
    lines.append("")
    lines.append("EPC contractors, construction teams, mining and power-site engineers in Singrauli / Waidhan / Madhya Pradesh (only where factually relevant).")
    lines.append("")
    lines.append("## 3. Key messages")
    lines.append("")
    lines.append("- Planning and measurement reduce site rework.")
    lines.append("- Documentation supports decision support and coordination.")
    lines.append("- Survey data is the basis for tenders, layout and quality checks.")
    lines.append("")
    lines.append("## 4. Draft")
    lines.append("")
    lines.append("#### English draft")
    lines.append("")
    lines.append("Write the full blog copy here. Keep it factual, short, and free of unverified claims.")
    lines.append("")
    lines.append("#### Hinglish draft (optional)")
    lines.append("")
    lines.append("एक छोटा सा हिंग्लिश अनुवाद - स्पष्ट, पेशेवर, बिना दावों के।")
    lines.append("")
    lines.append("## 5. Visual / asset")
    lines.append("")
    lines.append("- Owned/approved photos of survey equipment and field work.")
    lines.append("- AI-generated illustrative image MAY be used - clearly labelled 'AI-generated illustrative media'.")
    lines.append("")
    lines.append("## 6. CTA")
    lines.append("")
    lines.append("Request a discussion / share project requirements. No invented contact details.")
    lines.append("")
    lines.append("## 7. Proof required")
    lines.append("")
    lines.append("- Owner-confirmed facts only.")
    lines.append("- Source URL for any external claim (with date).")
    lines.append("- Technical claims: qualified SSC review.")
    lines.append("")
    lines.append("## 8. Approval")
    lines.append("")
    lines.append("- Owner name: {}".format(owner))
    lines.append("- Approval record: " + (row.get("approval_record") or "not yet"))
    lines.append("")
    lines.append("---")
    lines.append("status: DRAFT")
    lines.append("source: modules/12-content-calendar-content-generation/scripts/ContentGenerator.py")
    lines.append("approval_required: yes")
    lines.append("module: 12-content-calendar-content-generation")
    lines.append("---")
    lines.append("")
    out_dir.mkdir(parents=True, exist_ok=True)
    subject.write_text("\n".join(lines), encoding="utf-8")
    print("Wrote: {}".format(subject))


def generate_reel_script(row, out_dir: Path):
    topic = (row.get("topic") or "").strip()
    owner = (row.get("owner") or "").strip() or "SSC owner"
    language = (row.get("language") or "en").strip()
    subject = out_dir / ("12-reel-{}-{}{}".format(_slug(topic), "en" if "hi" not in language.lower() else "hi", _lang_suffix(language)))
    lines = []
    lines.append("# SHAH AI - Draft: {} (Reel Script)".format(topic))
    lines.append("")
    lines.append(DRAFT_HEADER)
    lines.append("> Draft only - no confirmed facts.")
    lines.append("")
    lines.append("## 1. Objective")
    lines.append("")
    lines.append("Explain one idea about survey data in under 60 seconds for EPC/contractor and homeowner audiences.")
    lines.append("")
    lines.append("## 2. Hook (/title)")
    lines.append("")
    lines.append("Write a strong 8-10 word hook (English) or natural Hinglish hook.")
    lines.append("")
    lines.append("## 3. Main message")
    lines.append("")
    lines.append("- Planning, measurement and documentation before any build.")
    lines.append("- Survey data supports tender, layout, and quality checks.")
    lines.append("- No unverified accuracy or speed claims.")
    lines.append("")
    lines.append("## 4. Shot list / visual")
    lines.append("")
    lines.append("- Shot 1: field survey setup with owned/approved footage.")
    lines.append("- Shot 2: map or topo sheet generated from field points (illustrative).")
    lines.append("- Shot 3: simple on-screen text: 'Survey data -> better planning, measurement, coordination'.")
    lines.append("")
    lines.append("## 5. Caption")
    lines.append("")
    lines.append("One polished caption. Add a single CTA.")
    lines.append("")
    lines.append("## 6. CTA")
    lines.append("")
    lines.append("Request a discussion / share project requirements. No invented contact details.")
    lines.append("")
    lines.append("## 7. Approval")
    lines.append("")
    lines.append("- Owner: {}".format(owner))
    lines.append("- Approval record: " + (row.get("approval_record") or "not yet"))
    lines.append("")
    lines.append("---")
    lines.append("status: DRAFT")
    lines.append("source: modules/12-content-calendar-content-generation/scripts/ContentGenerator.py")
    lines.append("approval_required: yes")
    lines.append("module: 12-content-calendar-content-generation")
    lines.append("---")
    lines.append("")
    out_dir.mkdir(parents=True, exist_ok=True)
    subject.write_text("\n".join(lines), encoding="utf-8")
    print("Wrote: {}".format(subject))


def generate_linkedin_post(row, out_dir: Path):
    topic = (row.get("topic") or "").strip()
    owner = (row.get("owner") or "").strip() or "SSC owner"
    language = (row.get("language") or "en").strip()
    subject = out_dir / ("12-linkedin-{}-{}{}".format(_slug(topic), "en" if "hi" not in language.lower() else "hi", _lang_suffix(language)))
    lines = []
    lines.append("# SHAH AI - Draft: {} (LinkedIn)".format(topic))
    lines.append("")
    lines.append(DRAFT_HEADER)
    lines.append("> Draft only.")
    lines.append("")
    lines.append("## 1. Hook")
    lines.append("")
    lines.append("Write a professional 3-5 line hook on survey data for EPC, construction, mining, power and solar teams.")
    lines.append("")
    lines.append("## 2. Main message")
    lines.append("")
    lines.append("- Planning and measurement before site work.")
    lines.append("- Documentation and decision support.")
    lines.append("- No fabricated case outcomes or testimonials.")
    lines.append("")
    lines.append("## 3. Supporting points")
    lines.append("")
    lines.append("- Field, processing and delivery are all data-driven.")
    lines.append("- Consultancies use survey data to reduce cost and delay.")
    lines.append("")
    lines.append("## 4. CTA")
    lines.append("")
    lines.append("Request a discussion / share project requirements.")
    lines.append("")
    lines.append("## 5. Hashtags")
    lines.append("")
    lines.append("Relevant tags only; no keyword stuffing.")
    lines.append("")
    lines.append("## 6. Approval")
    lines.append("")
    lines.append("- Owner: {}".format(owner))
    lines.append("- Approval record: " + (row.get("approval_record") or "not yet"))
    lines.append("")
    lines.append("---")
    lines.append("status: DRAFT")
    lines.append("source: modules/12-content-calendar-content-generation/scripts/ContentGenerator.py")
    lines.append("approval_required: yes")
    lines.append("module: 12-content-calendar-content-generation")
    lines.append("---")
    lines.append("")
    out_dir.mkdir(parents=True, exist_ok=True)
    subject.write_text("\n".join(lines), encoding="utf-8")
    print("Wrote: {}".format(subject))


def generate_gbp_post(row, out_dir: Path):
    topic = (row.get("topic") or "").strip()
    owner = (row.get("owner") or "").strip() or "SSC owner"
    language = (row.get("language") or "en").strip()
    subject = out_dir / ("12-gbp-{}-{}{}".format(_slug(topic), "en" if "hi" not in language.lower() else "hi", _lang_suffix(language)))
    lines = []
    lines.append("# SHAH AI - Draft: {} (GBP Post)".format(topic))
    lines.append("")
    lines.append(DRAFT_HEADER)
    lines.append("> Draft only. GBP profiles are not modified here.")
    lines.append("")
    lines.append("## 1. Headline")
    lines.append("")
    lines.append("Factual, local, professional. Example: 'Survey data for Singrauli and Waidhan site teams.'")
    lines.append("")
    lines.append("## 2. Message / value point")
    lines.append("")
    lines.append("3-4 sentences on how survey data supports planning, measurement, documentation and site coordination.")
    lines.append("")
    lines.append("## 3. Visual / media direction")
    lines.append("")
    lines.append("- Owned/approved photos or footage; AI visuals labelled illustrative.")
    lines.append("")
    lines.append("## 4. CTA")
    lines.append("")
    lines.append("Request a discussion / share project requirements. No fabricated offers or hours.")
    lines.append("")
    lines.append("## 5. Approval")
    lines.append("")
    lines.append("- Owner: {}".format(owner))
    lines.append("- Approval record: " + (row.get("approval_record") or "not yet"))
    lines.append("")
    lines.append("---")
    lines.append("status: DRAFT")
    lines.append("source: modules/12-content-calendar-content-generation/scripts/ContentGenerator.py")
    lines.append("approval_required: yes")
    lines.append("module: 12-content-calendar-content-generation")
    lines.append("---")
    lines.append("")
    out_dir.mkdir(parents=True, exist_ok=True)
    subject.write_text("\n".join(lines), encoding="utf-8")
    print("Wrote: {}".format(subject))


def generate_outreach_draft(row, out_dir: Path):
    topic = (row.get("topic") or "").strip()
    owner = (row.get("owner") or "").strip() or "SSC owner"
    language = (row.get("language") or "en").strip()
    suffix = "" if "hi" not in language.lower() else "hi"
    subject = out_dir / ("12-outreach-{}-{}.md".format(_slug(topic), suffix))
    lines = []
    lines.append("# SHAH AI - Draft: {} (Outreach)".format(topic))
    lines.append("")
    lines.append(DRAFT_HEADER)
    lines.append("> Hinglish + English bilingual draft. Draft only - no sending.")
    lines.append("")
    lines.append("## 1. Subject")
    lines.append("")
    lines.append("Write a professional subject (no fabricated authority).")
    lines.append("")
    lines.append("## 2. Opening")
    lines.append("")
    lines.append("Reference the shared public material. Do not invent a named contact.")
    lines.append("")
    lines.append("## 3. Body")
    lines.append("")
    lines.append("We support EPC, construction, mining, power and solar teams with survey data for planning, measurement, documentation and site coordination.")
    lines.append("- Ask for a discussion.")
    lines.append("- Keep it low-pressure.")
    lines.append("")
    lines.append("## 4. Closing")
    lines.append("")
    lines.append("Request a discussion / share project requirements. Do not invent phone numbers or email addresses.")
    lines.append("")
    lines.append("## 5. Approvals")
    lines.append("")
    lines.append("- Owner: {}".format(owner))
    lines.append("- Approval record: " + (row.get("approval_record") or "not yet"))
    lines.append("")
    lines.append("---")
    lines.append("status: DRAFT")
    lines.append("source: modules/12-content-calendar-content-generation/scripts/ContentGenerator.py")
    lines.append("approval_required: yes")
    lines.append("module: 12-content-calendar-content-generation")
    lines.append("---")
    lines.append("")
    out_dir.mkdir(parents=True, exist_ok=True)
    subject.write_text("\n".join(lines), encoding="utf-8")
    print("Wrote: {}".format(subject))


def generate_for_row(row, out_dir: Path):
    platform = (row.get("platform") or "").strip().lower()
    if "blog" in platform or "blog" in (row.get("content_pillar") or "").lower():
        generate_blog_brief(row, out_dir)
    elif "reel" in platform or "instagram" in platform or "facebook" in platform:
        generate_reel_script(row, out_dir)
    elif "linkedin" in platform:
        generate_linkedin_post(row, out_dir)
    elif "gbp" in platform or "google" in platform:
        generate_gbp_post(row, out_dir)
    elif "outreach" in platform or "email" in platform or "mail" in platform:
        generate_outreach_draft(row, out_dir)
    else:
        generate_reel_script(row, out_dir)
        generate_linkedin_post(row, out_dir)


def generate_all(args):
    calendar_path = Path(args.calendar) if args.calendar else (REPO_ROOT / "data" / "m12-content-calendar.csv")
    out_dir = Path(args.outdir) if args.outdir else (OUTPUTS_DIR / "12")
    if not calendar_path.exists():
        print("Calendar not found: {}".format(calendar_path))
        return 1
    rows = []
    with calendar_path.open("r", newline="", encoding="utf-8") as fh:
        for line in fh:
            if line.lstrip().startswith("#"):
                continue
        fh.seek(0)
        reader = __import__("csv").DictReader(fh)
        if reader.fieldnames is None:
            print("No rows in calendar: {}".format(calendar_path))
            return 1
        rows = list(reader)
    generated = 0
    for row in rows:
        if (row.get("status") or "").strip().upper() not in {"DRAFT", "PENDING"}:
            continue
        generate_for_row(row, out_dir)
        generated += 1
        slug = _slug((row.get("topic") or "topic").strip().lower().replace(" ", "-"))
        row["draft_output"] = str(out_dir / "12-draft-{}.md".format(slug))
    print("Generated draft files for {} DRAFT/PENDING row(s) -> {}".format(generated, out_dir))
    return 0


def generate_one(args):
    calendar_path = Path(args.calendar) if args.calendar else (REPO_ROOT / "data" / "m12-content-calendar.csv")
    if not calendar_path.exists():
        print("Calendar not found: {}".format(calendar_path))
        return 1
    rows = []
    with calendar_path.open("r", newline="", encoding="utf-8") as fh:
        for line in fh:
            if line.lstrip().startswith("#"):
                continue
        fh.seek(0)
        reader = __import__("csv").DictReader(fh)
        rows = list(reader)
    targets = [r for r in rows if str(r.get("id", "")).strip() == str(args.id)] if args.id is not None else rows
    if not targets:
        print("No row with id {}.".format(args.id))
        return 1
    out_dir = args.outdir or (OUTPUTS_DIR / "12")
    for t in targets:
        generate_for_row(t, out_dir)
        t["draft_output"] = str(out_dir)
    return 0


# --- main ------------------------------------------------------------------
def build_parser():
    p = argparse.ArgumentParser(prog="ContentGenerator.py", description="SHAH AI Module 12 Content Generator")
    sub = p.add_subparsers(dest="command", required=True)

    sp = sub.add_parser("generate-all", help="Generate drafts for all DRAFT/PENDING rows")
    sp.add_argument("--calendar", type=Path, default=None)
    sp.add_argument("--outdir", type=Path, default=DEFAULT_OUT_DIR)
    sp.set_defaults(func=generate_all)

    sp = sub.add_parser("generate-one", help="Generate drafts for one row")
    sp.add_argument("--calendar", type=Path, default=None)
    sp.add_argument("--id", type=int, default=None)
    sp.add_argument("--outdir", type=Path, default=DEFAULT_OUT_DIR)
    sp.set_defaults(func=generate_one)

    return p


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
