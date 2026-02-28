#!/usr/bin/env python3
"""Simple keyless news aggregator that sends a plain-text email digest.

Behavior:
- Reads `topics.yaml` for feed lists
- Uses `ingestors/rss_ingestor.fetch_feed` to get recent entries
- Builds a plain-text summary and attempts to send via local `sendmail`
- If `sendmail` is unavailable, writes an .eml file to `outbox/`

No external API keys required.
"""
import os
import sys
import argparse
import yaml
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
from email.message import EmailMessage
from ingestors.rss_ingestor import fetch_feed
import smtplib
import ssl


def load_topics(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def build_digest(topics, article_limit_per_topic=50):
    parts = []
    total = 0
    for t in topics:
        name = t.get("name", "Unnamed")
        lookback = t.get("lookback_hours", 48)
        cap = t.get("article_cap", article_limit_per_topic)
        parts.append(f"=== {name} ===")
        collected = 0
        for src in t.get("sources", []):
            try:
                entries = fetch_feed(src, since_hours=lookback)
            except Exception:
                entries = []

            for e in entries:
                if collected >= cap:
                    break
                title = e.get("title") or "(no title)"
                link = e.get("link") or ""
                pub = e.get("published") or ""
                desc = e.get("description", "").strip()
                if len(desc) > 300:
                    desc = desc[:297] + "..."

                parts.append(f"- {title}\n  {link}\n  {pub}\n  {desc}")
                collected += 1
                total += 1
        if collected == 0:
            parts.append("(no recent items)")
        parts.append("")

    header = f"News digest generated {datetime.utcnow().isoformat()} UTC\nTotal items: {total}\n"
    return header + "\n".join(parts)


def send_via_sendmail(from_addr, to_addr, subject, body) -> bool:
    sendmail_path = shutil.which("sendmail") or shutil.which("/usr/sbin/sendmail")
    if not sendmail_path:
        return False

    msg = EmailMessage()
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg["Subject"] = subject
    msg.set_content(body)

    try:
        p = subprocess.Popen([sendmail_path, "-t", "-oi"], stdin=subprocess.PIPE)
        p.communicate(msg.as_bytes())
        return p.returncode == 0
    except Exception:
        return False


def send_via_smtp(host, port, username, password, from_addr, to_addr, subject, body) -> bool:
    msg = EmailMessage()
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg["Subject"] = subject
    msg.set_content(body)

    try:
        port = int(port) if port else None
        # Try SSL on 465, otherwise STARTTLS
        if port == 465:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(host, port, context=context) as server:
                if username and password:
                    server.login(username, password)
                server.send_message(msg)
        else:
            # default port 587 for STARTTLS
            smtp_port = port or 587
            with smtplib.SMTP(host, smtp_port, timeout=30) as server:
                server.ehlo()
                try:
                    server.starttls(context=ssl.create_default_context())
                    server.ehlo()
                except Exception:
                    pass
                if username and password:
                    server.login(username, password)
                server.send_message(msg)
        return True
    except Exception:
        return False


def write_eml(outdir: Path, from_addr, to_addr, subject, body) -> Path:
    outdir.mkdir(parents=True, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    path = outdir / f"news_digest_{ts}.eml"
    msg = EmailMessage()
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg["Subject"] = subject
    msg.set_content(body)
    with path.open("wb") as f:
        f.write(msg.as_bytes())
    return path


def main():
    p = argparse.ArgumentParser(description="Simple keyless news aggregator and emailer")
    p.add_argument("--topics", default="topics.yaml", help="path to topics.yaml")
    p.add_argument("--to", default=os.getenv("NEWS_TO_EMAIL"), help="recipient email (or set NEWS_TO_EMAIL)")
    p.add_argument("--from", dest="from_addr", default=os.getenv("NEWS_FROM_EMAIL", "news@example.com"), help="from email address")
    p.add_argument("--outbox", default="outbox", help="directory to write .eml when sendmail absent")
    p.add_argument("--subject", default="Daily News Digest", help="email subject")
    args = p.parse_args()

    if not args.to:
        print("Recipient email required: pass --to or set NEWS_TO_EMAIL environment variable", file=sys.stderr)
        sys.exit(2)

    topics_path = Path(args.topics)
    if not topics_path.exists():
        print(f"Topics file not found: {topics_path}", file=sys.stderr)
        sys.exit(2)

    topics = load_topics(topics_path)
    body = build_digest(topics)

    # Try SMTP if configured via env or args
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = os.getenv("SMTP_PORT")
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")

    sent = False
    if smtp_host:
        sent = send_via_smtp(smtp_host, smtp_port, smtp_user, smtp_pass, args.from_addr, args.to, args.subject, body)
        if sent:
            print(f"Email sent to {args.to} via SMTP host {smtp_host}")

    if not sent:
        # Try local sendmail
        sent = send_via_sendmail(args.from_addr, args.to, args.subject, body)
        if sent:
            print(f"Email sent to {args.to} via sendmail")

    if not sent:
        outp = write_eml(Path(args.outbox), args.from_addr, args.to, args.subject, body)
        print(f"Sendmail/SMTP not available or failed. Wrote message to {outp}")


if __name__ == "__main__":
    main()
