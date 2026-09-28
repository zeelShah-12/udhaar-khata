# Udhaar Khata — Digital Credit Book

Kirana stores, medical shops, and small wholesalers track customer credit ("udhaar") in a
paper notebook — easy to lose, impossible to search, and no way to remind customers except
by memory. **Udhaar Khata** digitizes it:

![Demo: scan a notebook page, review AI-read entries, customer timeline, WhatsApp reminder](demo.gif)

- Snap a photo of a notebook page — AI reads every name and amount, tells "credit given"
  apart from "payment received", and adds them to a persistent digital ledger.
- Review and correct the AI's reading before it's committed (handwriting OCR isn't perfect —
  this app assumes that and builds a review step in, rather than trusting it blindly).
- A **contact-list UI** (not a spreadsheet) — customers sorted by how much they owe, click
  into anyone to see their full transaction history as a chat-style timeline.
- Generates a ready-to-copy **WhatsApp reminder message** per customer — you paste and send
  it yourself; nothing is sent automatically.

**Who pays:** Kirana stores, medical shops, small wholesalers — ₹99–299/month.

## Stack

- **Streamlit** — but with a custom contact-list + chat-thread layout instead of the
  tables/tabs pattern, to match how a shop owner actually thinks about "who owes me money"
- **Groq** (`qwen/qwen3.8-27b`) — reads handwritten notebook pages, returns structured entries
- **A flat JSON ledger** (`data/udhaar.json`) — every entry persists across restarts

## Local setup

```bash
cd "11 project"
pip install -r requirements.txt
cp .env.example .env   # add your GROQ_API_KEY (free at console.groq.com)
streamlit run app.py
```

Runs on `http://localhost:8501`.

## Project structure

```
11 project/
├── app.py              Streamlit UI — scan panel, customer list, ledger timeline
├── vision.py            Groq Vision call + prompt/schema for notebook OCR
├── storage.py            Flat JSON persistence for the ledger
├── data/                 udhaar.json lives here (created on first scan)
├── sample_images/        (drop a demo notebook photo here for testing)
├── requirements.txt
└── .env.example
```

## Notes for the portfolio writeup

- Customers are grouped by a normalized (lowercased, trimmed) name key — no separate
  customer table. Simple, and good enough for a single shop owner's own notebook where
  they already know their customers by name.
- The scan → review → confirm flow exists specifically because handwriting recognition on
  messy notebook pages is unreliable; letting the AI write directly to the ledger without a
  human check would silently corrupt real people's balances.
- WhatsApp reminders are drafted as copyable text (`st.code`, which ships a built-in copy
  button) rather than sent via any API — sending a message on someone's behalf needs their
  explicit action each time, not an automated integration.
