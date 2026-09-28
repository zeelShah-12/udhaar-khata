import uuid
from datetime import date, datetime

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from PIL import Image

from storage import load_entries, save_entries
from vision import extract_entries

load_dotenv()

st.set_page_config(
    page_title="Udhaar Khata",
    page_icon="₹",
    layout="wide",
    initial_sidebar_state="expanded",
)

AVATAR_PALETTE = [
    "#2a78d6", "#eb6834", "#1baf7a", "#eda100",
    "#e87ba4", "#008300", "#4a3aa7", "#e34948",
]

CUSTOM_CSS = """
<style>
    #MainMenu, footer, header {visibility: hidden;}

    .stApp { background: #0a0a0a; }

    .block-container {
        padding-top: 1.75rem;
        padding-bottom: 3rem;
        max-width: 1300px;
    }

    /* halftone dot texture, echoing the inspo's dithered hero backdrop */
    .hero {
        position: relative;
        overflow: hidden;
        background:
            radial-gradient(circle, rgba(255,255,255,0.35) 1px, transparent 1.2px) 0 0/14px 14px,
            #0f0f0f;
        border: 1px solid rgba(255,255,255,0.18);
        border-radius: 16px;
        padding: 1.75rem 2.25rem;
        margin-bottom: 1.5rem;
        color: #f2f2f2;
    }
    .hero::after {
        content: "";
        position: absolute;
        inset: 0;
        z-index: 0;
        background: radial-gradient(ellipse 90% 100% at 50% 120%, transparent 40%, #0a0a0a 78%);
        pointer-events: none;
    }
    .hero h1 { margin: 0 0 0.3rem 0; font-size: 1.9rem; color: #f2f2f2; position: relative; z-index: 1; }
    .hero p { margin: 0; opacity: 0.7; font-size: 0.98rem; position: relative; z-index: 1; max-width: 640px; }

    .eyebrow {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        border: 1px solid rgba(255,255,255,0.25);
        border-radius: 100px;
        padding: 0.2rem 0.7rem;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        color: #cfcfcf;
        margin-bottom: 0.7rem;
        position: relative;
        z-index: 1;
    }

    .stat-chip {
        display: inline-block;
        background: transparent;
        border: 1px solid rgba(255,255,255,0.3);
        border-radius: 999px;
        padding: 0.3rem 0.9rem;
        margin-right: 0.5rem;
        margin-top: 0.6rem;
        font-size: 0.85rem;
        font-weight: 600;
        position: relative;
        z-index: 1;
        color: #f2f2f2;
    }

    /* Contact list */
    .contact-list-title {
        font-weight: 700;
        font-size: 1.05rem;
        margin-bottom: 0.4rem;
        color: #f2f2f2;
    }
    div[data-testid="stButton"] > button {
        text-align: left;
        justify-content: flex-start;
        border-radius: 10px;
        font-weight: 500;
        border: 1px solid rgba(255,255,255,0.16);
        background: #111;
        color: #e8e8e8;
        padding: 0.6rem 0.8rem;
    }
    div[data-testid="stButton"] > button:hover {
        border-color: rgba(255,255,255,0.45);
        color: #fff;
    }
    .stButton > button[kind="primary"] {
        border-radius: 10px;
        font-weight: 600;
        background: #f2f2f2;
        color: #0a0a0a;
        border: 1px solid #f2f2f2;
    }
    .stButton > button[kind="primary"]:hover {
        background: #fff;
        color: #0a0a0a;
    }

    /* Ledger detail */
    .customer-header {
        display: flex;
        align-items: center;
        gap: 0.8rem;
        margin-bottom: 0.4rem;
    }
    .avatar {
        width: 46px; height: 46px; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        color: #0a0a0a; font-weight: 700; font-size: 1.1rem;
        flex-shrink: 0;
        border: 1px solid rgba(255,255,255,0.4);
    }
    .balance-owed { color: #ef4444; font-weight: 700; font-size: 1.6rem; }
    .balance-settled { color: #22c55e; font-weight: 700; font-size: 1.6rem; }

    .bubble-row { display: flex; margin-bottom: 0.5rem; }
    .bubble-row.given { justify-content: flex-start; }
    .bubble-row.received { justify-content: flex-end; }
    .bubble {
        max-width: 72%;
        padding: 0.55rem 0.85rem;
        border-radius: 12px;
        font-size: 0.88rem;
        line-height: 1.4;
        border: 1px solid;
        background: #111;
    }
    .bubble.given {
        color: #fca5a5;
        border-color: rgba(239,68,68,0.4);
        border-top-left-radius: 2px;
    }
    .bubble.received {
        color: #86efac;
        border-color: rgba(34,197,94,0.4);
        border-top-right-radius: 2px;
    }
    .bubble .amt { font-weight: 700; }
    .bubble .meta { font-size: 0.72rem; opacity: 0.7; margin-top: 0.15rem; }

    .empty-state {
        border: 1px dashed rgba(255,255,255,0.25);
        border-radius: 14px;
        padding: 3rem 1.5rem;
        text-align: center;
        opacity: 0.6;
        color: #e8e8e8;
    }

    section[data-testid="stFileUploaderDropzone"] {
        border-radius: 12px;
        border: 1px dashed rgba(255,255,255,0.3) !important;
        background: #111;
    }

    section[data-testid="stSidebar"] {
        background: #0a0a0a;
        border-right: 1px solid rgba(255,255,255,0.14);
    }

    div[data-baseweb="tab-list"] { gap: 4px; }
    button[data-baseweb="tab"] { color: #a8a8a8; }
    button[data-baseweb="tab"][aria-selected="true"] { color: #f2f2f2; }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ---------------------------------------------------------------- state ----

if "entries" not in st.session_state:
    st.session_state.entries = load_entries()
if "selected_customer" not in st.session_state:
    st.session_state.selected_customer = None
if "pending_entries" not in st.session_state:
    st.session_state.pending_entries = None
if "search" not in st.session_state:
    st.session_state.search = ""


def customer_key(name: str) -> str:
    return name.strip().lower()


def avatar_color(name: str) -> str:
    return AVATAR_PALETTE[hash(customer_key(name)) % len(AVATAR_PALETTE)]


def initials(name: str) -> str:
    parts = [p for p in name.strip().split() if p]
    if not parts:
        return "?"
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][0] + parts[-1][0]).upper()


def build_customer_summary(entries: list[dict]) -> pd.DataFrame:
    if not entries:
        return pd.DataFrame(columns=["key", "name", "balance", "count"])
    df = pd.DataFrame(entries)
    df["signed"] = df.apply(
        lambda r: r["amount"] if r["type"] == "given" else -r["amount"], axis=1
    )
    df["key"] = df["customer_name"].apply(customer_key)
    grouped = (
        df.groupby("key")
        .agg(
            name=("customer_name", "last"),
            balance=("signed", "sum"),
            count=("signed", "count"),
        )
        .reset_index()
        .sort_values("balance", ascending=False)
    )
    return grouped


# ---------------------------------------------------------------- hero -----

total_outstanding = 0.0
customer_count = 0
if st.session_state.entries:
    summary_all = build_customer_summary(st.session_state.entries)
    total_outstanding = summary_all[summary_all["balance"] > 0]["balance"].sum()
    customer_count = len(summary_all)

st.markdown(
    f"""
    <div class="hero">
        <span class="eyebrow">◆ DIGITAL LEDGER</span>
        <h1>Udhaar Khata — Digital Credit Book</h1>
        <p>Snap a photo of your udhaar notebook page — AI reads every name and amount, so you
        never lose track of who owes what.</p>
        <span class="stat-chip">Outstanding: ₹{total_outstanding:,.0f}</span>
        <span class="stat-chip">Customers: {customer_count}</span>
        <span class="stat-chip">Entries: {len(st.session_state.entries)}</span>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("### Settings")
    shop_name = st.text_input("Your shop name", value="", placeholder="e.g. Sharma Kirana Store")

    st.markdown("---")
    st.markdown(
        "**Who this is for**\n\n"
        "Kirana stores, medical shops, and small wholesalers who track customer credit "
        "(udhaar) in a paper notebook and want it digitized — with a ready-to-send "
        "WhatsApp reminder for each customer."
    )
    st.markdown("---")
    if st.session_state.entries and st.button("Clear entire ledger", use_container_width=True):
        st.session_state.entries = []
        st.session_state.selected_customer = None
        save_entries([])
        st.rerun()

# ------------------------------------------------------------ scan panel ---

with st.expander("Scan a notebook page", expanded=not st.session_state.entries):
    uploaded_file = st.file_uploader(
        "Photo of udhaar notebook page", type=["jpg", "jpeg", "png", "webp"]
    )

    if uploaded_file:
        col_img, col_action = st.columns([1, 1])
        with col_img:
            image = Image.open(uploaded_file).convert("RGB")
            st.image(image, use_container_width=True)
        with col_action:
            if st.button("Extract entries", type="primary", use_container_width=True):
                with st.spinner("Reading handwriting..."):
                    try:
                        result = extract_entries(image)
                        st.session_state.pending_entries = result.get("entries", [])
                    except Exception as exc:
                        st.error(f"Extraction failed: {exc}")

    if st.session_state.pending_entries is not None:
        st.markdown("**Review before adding to ledger** — fix anything the AI misread:")
        pending_df = pd.DataFrame(st.session_state.pending_entries)
        if pending_df.empty:
            st.info("No entries were detected in this photo.")
        else:
            pending_df["date"] = pending_df.get("date").apply(
                lambda v: date.fromisoformat(v) if v else None
            )
            edited = st.data_editor(
                pending_df,
                use_container_width=True,
                hide_index=True,
                num_rows="dynamic",
                column_config={
                    "customer_name": st.column_config.TextColumn("Customer", width="medium"),
                    "amount": st.column_config.NumberColumn("Amount", format="₹%.2f"),
                    "type": st.column_config.SelectboxColumn(
                        "Type", options=["given", "received"]
                    ),
                    "date": st.column_config.DateColumn("Date", format="YYYY-MM-DD"),
                    "notes": st.column_config.TextColumn("Notes", width="large"),
                },
                key="pending_editor",
            )

            c1, c2 = st.columns(2)
            if c1.button("Add to ledger", type="primary", use_container_width=True):
                new_entries = []
                for row in edited.to_dict("records"):
                    if not row.get("customer_name") or not row.get("amount"):
                        continue
                    new_entries.append(
                        {
                            "id": str(uuid.uuid4()),
                            "customer_name": str(row["customer_name"]).strip(),
                            "amount": float(row["amount"]),
                            "type": row.get("type") or "given",
                            "date": row["date"].isoformat() if row.get("date") else None,
                            "notes": row.get("notes") or "",
                            "source": uploaded_file.name if uploaded_file else "manual",
                            "created_at": datetime.now().isoformat(),
                        }
                    )
                st.session_state.entries.extend(new_entries)
                save_entries(st.session_state.entries)
                st.session_state.pending_entries = None
                st.success(f"Added {len(new_entries)} entries to the ledger.")
                st.rerun()
            if c2.button("Discard", use_container_width=True):
                st.session_state.pending_entries = None
                st.rerun()

st.markdown("---")

# --------------------------------------------------------------- layout ----

left, right = st.columns([1, 1.6], gap="large")

with left:
    st.markdown('<div class="contact-list-title">Customers</div>', unsafe_allow_html=True)

    if not st.session_state.entries:
        st.markdown(
            '<div class="empty-state">No customers yet.<br>Scan a notebook page above '
            "to get started.</div>",
            unsafe_allow_html=True,
        )
    else:
        search = st.text_input(
            "Search", placeholder="Search customers...", label_visibility="collapsed"
        )
        summary = build_customer_summary(st.session_state.entries)
        if search:
            summary = summary[summary["name"].str.contains(search, case=False, na=False)]

        for _, row in summary.iterrows():
            owes = row["balance"] > 0.01
            tag = "DUE" if owes else ("OK" if abs(row["balance"]) < 0.01 else "CR")
            balance_text = (
                f"₹{row['balance']:,.0f} due" if owes else
                ("settled" if abs(row["balance"]) < 0.01 else f"₹{abs(row['balance']):,.0f} credit")
            )
            label = f"[{tag}]  {row['name']} — {balance_text}"
            if st.button(label, key=f"cust_{row['key']}", use_container_width=True):
                st.session_state.selected_customer = row["key"]

with right:
    selected_key = st.session_state.selected_customer

    if not st.session_state.entries:
        st.markdown(
            '<div class="empty-state">Your ledger is empty.<br>'
            "Scan a notebook page to add your first customers.</div>",
            unsafe_allow_html=True,
        )
    elif not selected_key:
        st.markdown(
            '<div class="empty-state">Select a customer from the list to view '
            "their ledger.</div>",
            unsafe_allow_html=True,
        )
    else:
        summary = build_customer_summary(st.session_state.entries)
        match = summary[summary["key"] == selected_key]
        if match.empty:
            st.session_state.selected_customer = None
            st.rerun()
        else:
            row = match.iloc[0]
            name = row["name"]
            balance = row["balance"]
            color = avatar_color(name)

            st.markdown(
                f"""
                <div class="customer-header">
                    <div class="avatar" style="background:#161616; border-color:{color}; color:{color};">{initials(name)}</div>
                    <div>
                        <div style="font-size:1.2rem; font-weight:700; color:#f2f2f2;">{name}</div>
                        <div class="{'balance-owed' if balance > 0.01 else 'balance-settled'}">
                            {'Owes ₹' + format(balance, ',.0f') if balance > 0.01 else 'All settled'}
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            tab_ledger, tab_add, tab_reminder = st.tabs(
                ["Ledger", "Add entry", "WhatsApp reminder"]
            )

            customer_entries = [
                e for e in st.session_state.entries
                if customer_key(e["customer_name"]) == selected_key
            ]
            customer_entries.sort(key=lambda e: e.get("date") or e.get("created_at") or "")

            with tab_ledger:
                if not customer_entries:
                    st.info("No entries yet.")
                for e in customer_entries:
                    sign = "+" if e["type"] == "given" else "−"
                    date_label = e.get("date") or "no date"
                    notes = f" · {e['notes']}" if e.get("notes") else ""
                    st.markdown(
                        f"""
                        <div class="bubble-row {e['type']}">
                            <div class="bubble {e['type']}">
                                <span class="amt">{sign}₹{e['amount']:,.0f}</span>{notes}
                                <div class="meta">{date_label}</div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            with tab_add:
                with st.form(f"add_entry_{selected_key}", clear_on_submit=True):
                    c1, c2 = st.columns(2)
                    amount = c1.number_input("Amount (₹)", min_value=0.0, step=10.0)
                    entry_type = c2.selectbox("Type", ["given", "received"])
                    entry_date = st.date_input("Date", value=date.today())
                    notes = st.text_input("Notes (optional)")
                    if st.form_submit_button("Add entry", type="primary", use_container_width=True):
                        if amount > 0:
                            st.session_state.entries.append(
                                {
                                    "id": str(uuid.uuid4()),
                                    "customer_name": name,
                                    "amount": float(amount),
                                    "type": entry_type,
                                    "date": entry_date.isoformat(),
                                    "notes": notes,
                                    "source": "manual",
                                    "created_at": datetime.now().isoformat(),
                                }
                            )
                            save_entries(st.session_state.entries)
                            st.success("Entry added.")
                            st.rerun()

            with tab_reminder:
                if balance > 0.01:
                    shop_line = f" at {shop_name}" if shop_name else ""
                    message = (
                        f"Namaste {name} ji,\n\n"
                        f"Yeh ek reminder hai ki aapka udhaar balance{shop_line} "
                        f"₹{balance:,.0f} hai. Jab suvidha ho, kripya payment kar dijiye.\n\n"
                        f"Dhanyavaad!"
                    )
                    st.caption("Copy this message and send it on WhatsApp — nothing is sent automatically.")
                    st.code(message, language=None)
                else:
                    st.success("This customer has no outstanding balance — no reminder needed.")
