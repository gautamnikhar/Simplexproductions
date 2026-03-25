import streamlit as st
import sys
import os
import pandas as pd
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database.db import (
    init_db, insert_lead, get_all_leads, get_unconnected_leads,
    delete_lead, save_note_template, get_note_templates,
    delete_note_template, save_linkedin_config, get_linkedin_config,
    log_connection, get_connection_logs, get_week_sent_count, get_today_sent_count,
)
from scraper.linkedin_scraper import search_linkedin_founders, _extract_domain_from_company
from mailer.linkedin_connector import (
    create_client_with_cookies, send_connection_request,
    render_note, test_linkedin_cookies,
)

# --- Page Config ---
st.set_page_config(
    page_title="Simplex Outreach",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Init DB ---
init_db()

# --- Custom CSS ---
st.markdown("""
<style>
    .stApp { background-color: #0e1117; }
    .block-container { padding-top: 2rem; }
    h1 { color: #0077B5; }
    .metric-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #333;
        text-align: center;
    }
    .metric-card h2 { color: #0077B5; margin: 0; font-size: 2rem; }
    .metric-card p { color: #888; margin: 0; }
    .char-counter { font-size: 0.85rem; color: #888; }
    .char-counter.warn { color: #ff6b6b; }
</style>
""", unsafe_allow_html=True)

# --- Sidebar Navigation ---
st.sidebar.title("⚡ Simplex Outreach")
st.sidebar.markdown("*LinkedIn Connection Tool*")
st.sidebar.markdown("---")
page = st.sidebar.radio(
    "Navigate",
    ["🏠 Dashboard", "🔍 Find Leads", "✉️ Connection Notes", "🚀 Send Connections", "⚙️ LinkedIn Settings"],
    label_visibility="collapsed",
)


# ============================================================
# DASHBOARD PAGE
# ============================================================
if page == "🏠 Dashboard":
    st.title("Simplex Outreach Dashboard")
    st.markdown("Your LinkedIn lead generation & outreach command center.")

    leads = get_all_leads()
    unconnected = get_unconnected_leads()
    logs = get_connection_logs()
    sent_this_week = get_week_sent_count()
    sent_today = get_today_sent_count()
    config = get_linkedin_config()

    # Metrics row
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="metric-card"><h2>{len(leads)}</h2><p>Total Leads</p></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card"><h2>{len(unconnected)}</h2><p>Not Connected</p></div>""", unsafe_allow_html=True)
    with c3:
        total_sent = len([l for l in logs if l["status"] == "sent"])
        st.markdown(f"""<div class="metric-card"><h2>{total_sent}</h2><p>Total Requests Sent</p></div>""", unsafe_allow_html=True)
    with c4:
        limit = config["weekly_limit"] if config else 80
        st.markdown(f"""<div class="metric-card"><h2>{sent_this_week}/{limit}</h2><p>This Week</p></div>""", unsafe_allow_html=True)

    st.markdown("---")

    # Recent leads
    st.subheader("Recent Leads")
    if leads:
        df = pd.DataFrame(leads[:20])
        display_cols = [c for c in ["full_name", "title", "company", "location", "linkedin_url"] if c in df.columns]
        st.dataframe(df[display_cols], use_container_width=True, hide_index=True)
    else:
        st.info("No leads yet. Go to **Find Leads** to start searching.")

    # Recent connection activity
    st.subheader("Recent Connection Activity")
    if logs:
        df_logs = pd.DataFrame(logs[:10])
        display_cols = [c for c in ["full_name", "status", "note_sent", "sent_at", "error"] if c in df_logs.columns]
        st.dataframe(df_logs[display_cols], use_container_width=True, hide_index=True)
    else:
        st.info("No connection requests sent yet.")


# ============================================================
# FIND LEADS PAGE
# ============================================================
elif page == "🔍 Find Leads":
    st.title("Find Leads on LinkedIn")
    st.markdown("Search for founders, CEOs, decision-makers on LinkedIn via DuckDuckGo.")

    col1, col2 = st.columns([3, 1])
    with col1:
        query = st.text_input(
            "Search Query",
            placeholder='e.g. "founder" "fintech" "Dubai"',
            help="Use quotes for exact match. Combine role + industry + location.",
        )
    with col2:
        num_results = st.number_input("Max Results", min_value=5, max_value=100, value=20, step=5)

    # Example queries
    with st.expander("💡 Example Queries"):
        st.markdown("""
        | Query | What it finds |
        |-------|--------------|
        | `"founder" "SaaS" "Singapore"` | SaaS founders in Singapore |
        | `"CEO" "real estate" "Dubai"` | Real estate CEOs in Dubai |
        | `"founder" "agency" "London"` | Agency founders in London |
        | `"co-founder" "AI" "San Francisco"` | AI co-founders in SF |
        | `"managing director" "consulting" "Germany"` | MDs at consulting firms in Germany |
        """)

    if st.button("🔍 Search", type="primary", use_container_width=True):
        if not query:
            st.warning("Please enter a search query.")
        else:
            status = st.empty()
            progress = st.progress(0)

            def update_progress(msg):
                status.text(msg)

            with st.spinner("Searching DuckDuckGo for LinkedIn profiles..."):
                found_leads = search_linkedin_founders(query, num_results=num_results, progress_callback=update_progress)

            progress.progress(100)

            if found_leads:
                # Auto-save to database immediately
                saved = 0
                for lead in found_leads:
                    if insert_lead(lead):
                        saved += 1

                st.success(f"Found {len(found_leads)} leads — saved {saved} new leads to database!")

                # Show results
                df = pd.DataFrame(found_leads)
                st.dataframe(
                    df[["full_name", "title", "company", "location", "linkedin_url"]],
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.warning("No results found. Try a different query or check your internet connection.")

    # Show existing leads with management
    st.markdown("---")
    st.subheader("Saved Leads")

    leads = get_all_leads()
    if leads:
        df = pd.DataFrame(leads)
        display_cols = [c for c in ["id", "full_name", "title", "company", "location", "linkedin_url", "search_query"] if c in df.columns]
        st.dataframe(df[display_cols], use_container_width=True, hide_index=True)

        col1, col2 = st.columns(2)
        with col1:
            csv = df.to_csv(index=False)
            st.download_button("📥 Export Leads as CSV", csv, "simplex_leads.csv", "text/csv")
        with col2:
            if st.button("🗑️ Delete All Leads", type="secondary"):
                for lead in leads:
                    delete_lead(lead["id"])
                st.success("All leads deleted.")
                st.rerun()
    else:
        st.info("No saved leads.")


# ============================================================
# CONNECTION NOTES PAGE
# ============================================================
elif page == "✉️ Connection Notes":
    st.title("Connection Note Templates")
    st.markdown("Create personalized connection notes. **Max 300 characters** (LinkedIn limit).")

    with st.expander("📖 Available Placeholders", expanded=False):
        st.markdown("""
        | Placeholder | Description | Example |
        |-------------|-------------|---------|
        | `{first_name}` | Lead's first name | John |
        | `{last_name}` | Lead's last name | Doe |
        | `{full_name}` | Full name | John Doe |
        | `{company}` | Company name | Acme Corp |
        | `{title}` | Job title | Founder & CEO |
        | `{location}` | Location | Dubai |
        """)

    with st.expander("💡 Example Notes That Work", expanded=False):
        st.markdown("""
        **Direct & Value-Driven:**
        ```
        Hi {first_name}, saw you're building {company} — impressive work. We're Simplex Productions, we help founders like you with branding & digital presence. Would love to connect and share some ideas!
        ```

        **Casual & Curious:**
        ```
        Hey {first_name}! Came across your profile and loved what {company} is doing. We work with ambitious founders on creative & branding — thought it'd be great to connect!
        ```

        **Short & Sweet:**
        ```
        Hi {first_name}, love what you're building at {company}. We help founders stand out with world-class branding. Would love to connect!
        ```
        """)

    # Create new template
    st.subheader("Create Note Template")
    with st.form("note_form"):
        name = st.text_input("Template Name", placeholder="e.g. Founder Pitch v1")
        note = st.text_area(
            "Connection Note (max 300 characters)",
            height=120,
            max_chars=300,
            placeholder="Hi {first_name}, saw you're building {company} — impressive work. We're Simplex Productions, we help founders like you with branding & digital presence. Would love to connect!",
        )

        if note:
            char_count = len(note)
            color = "warn" if char_count > 280 else ""
            st.markdown(f'<span class="char-counter {color}">{char_count}/300 characters</span>', unsafe_allow_html=True)

            # Preview with sample data
            st.markdown("**Preview:**")
            preview = render_note(note, {
                "first_name": "John",
                "last_name": "Doe",
                "full_name": "John Doe",
                "company": "Acme Corp",
                "title": "Founder & CEO",
                "location": "Dubai",
            })
            st.info(preview)
            preview_len = len(preview)
            if preview_len > 300:
                st.warning(f"After filling placeholders, this note is {preview_len} chars. It will be trimmed to 300.")

        submitted = st.form_submit_button("💾 Save Template", type="primary")
        if submitted:
            if name and note:
                save_note_template(name, note)
                st.success(f"Template '{name}' saved!")
                st.rerun()
            else:
                st.warning("Please fill all fields.")

    # Existing templates
    st.markdown("---")
    st.subheader("Saved Templates")
    templates = get_note_templates()
    if templates:
        for t in templates:
            with st.expander(f"📄 {t['name']} ({len(t['note'])}/300 chars)"):
                st.text(t["note"])
                if st.button(f"🗑️ Delete", key=f"del_tmpl_{t['id']}"):
                    delete_note_template(t["id"])
                    st.rerun()
    else:
        st.info("No templates yet. Create one above.")


# ============================================================
# SEND CONNECTIONS PAGE
# ============================================================
elif page == "🚀 Send Connections":
    st.title("Send Connection Requests")
    st.markdown("Connect with leads on LinkedIn with a personalized note.")

    config = get_linkedin_config()
    if not config:
        st.error("⚠️ LinkedIn not configured! Go to **LinkedIn Settings** first.")
        st.stop()

    sent_this_week = get_week_sent_count()
    sent_today = get_today_sent_count()
    remaining = config["weekly_limit"] - sent_this_week

    # Status bar
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Sent Today", sent_today)
    with col2:
        st.metric("Sent This Week", f"{sent_this_week} / {config['weekly_limit']}")
    with col3:
        st.metric("Remaining This Week", remaining)

    if remaining <= 0:
        st.error("🛑 Weekly limit reached! Wait until next week to send more connection requests.")
        st.stop()

    # Select template
    templates = get_note_templates()
    if not templates:
        st.warning("No connection note templates found. Create one in **Connection Notes** first.")
        st.stop()

    template_options = {t["name"]: t for t in templates}
    selected_template_name = st.selectbox("Select Note Template", options=list(template_options.keys()))
    template = template_options[selected_template_name]

    # Select leads
    leads = get_unconnected_leads()
    if not leads:
        st.warning("No unconnected leads found. Find more leads or check if all have been connected.")
        st.stop()

    st.markdown(f"**{len(leads)} leads** available to connect with.")

    # Send options
    col1, col2 = st.columns(2)
    with col1:
        max_send = st.number_input("How many to connect with", min_value=1,
                                    max_value=min(remaining, len(leads), 25),
                                    value=min(5, remaining, len(leads)),
                                    help="LinkedIn is safest at 15-25 per day max.")
    with col2:
        delay = st.number_input("Delay between requests (seconds)", min_value=10,
                                max_value=120, value=config["delay_seconds"],
                                help="Keep this 15+ seconds to look human.")

    # Preview
    with st.expander("👀 Preview (first lead)"):
        sample = leads[0]
        st.markdown(f"**To:** {sample['full_name']}")
        st.markdown(f"**Profile:** {sample['linkedin_url']}")
        st.markdown(f"**Company:** {sample.get('company', 'N/A')}")
        st.markdown("**Note:**")
        preview_note = render_note(template["note"], sample)
        st.info(preview_note)
        st.caption(f"{len(preview_note)}/300 characters")

    # Send button
    st.markdown("---")
    st.warning(f"⚠️ This will send **{max_send} connection requests** from your LinkedIn account. "
               f"Each request will have a ~{delay}s delay between them.")

    if st.button(f"🚀 Send {max_send} Connection Requests", type="primary", use_container_width=True):
        progress = st.progress(0)
        status_text = st.empty()
        leads_to_send = leads[:max_send]

        # Login to LinkedIn using cookies
        status_text.text("Connecting to LinkedIn...")
        login = create_client_with_cookies(config["li_at"], config["jsessionid"])

        if not login["success"]:
            st.error(f"❌ LinkedIn login failed: {login['error']}")
            st.stop()

        status_text.text("Connected! Starting connection requests...")
        client = login["client"]

        success_count = 0
        fail_count = 0

        for i, lead in enumerate(leads_to_send):
            status_text.text(f"Connecting with {lead['full_name']} ({i+1}/{max_send})...")
            progress.progress((i) / max_send)

            note = render_note(template["note"], lead)
            result = send_connection_request(client, lead["linkedin_url"], note)

            if result["success"]:
                success_count += 1
                log_connection(lead["id"], template["id"], note, "sent")
            else:
                fail_count += 1
                log_connection(lead["id"], template["id"], note, "failed", result["error"])

                # Stop if we hit a limit
                if "limit" in result.get("error", "").lower():
                    st.error("🛑 LinkedIn rate limit hit! Stopping to protect your account.")
                    break

            # Rate limiting
            if i < len(leads_to_send) - 1:
                for sec in range(delay):
                    status_text.text(f"Waiting {delay - sec}s before next request...")
                    time.sleep(1)

        progress.progress(100)
        status_text.text("Done!")
        st.success(f"✅ Sent: **{success_count}** | Failed: **{fail_count}** | Total: **{success_count + fail_count}**")

        if fail_count > 0:
            st.info("Check the connection log below for error details.")

    # Connection log
    st.markdown("---")
    st.subheader("Connection Log")
    logs = get_connection_logs()
    if logs:
        df_logs = pd.DataFrame(logs)
        display_cols = [c for c in ["full_name", "status", "note_sent", "sent_at", "error"] if c in df_logs.columns]
        st.dataframe(df_logs[display_cols], use_container_width=True, hide_index=True)
    else:
        st.info("No connection requests sent yet.")


# ============================================================
# LINKEDIN SETTINGS PAGE
# ============================================================
elif page == "⚙️ LinkedIn Settings":
    st.title("LinkedIn Configuration")
    st.markdown("Connect your LinkedIn account using browser cookies (no CAPTCHA issues).")

    existing = get_linkedin_config()

    st.warning("""
    **Important safety tips:**
    - Keep weekly limit under **80-100** to avoid restrictions
    - Keep delay at **15+ seconds** between requests
    - Don't run this 24/7 — use it during normal working hours
    - Cookies expire periodically — you'll need to refresh them if they stop working
    """)

    with st.expander("📖 How to Get Your LinkedIn Cookies (takes 30 seconds)", expanded=not existing):
        st.markdown("""
        ### Step-by-step:

        1. Open **LinkedIn** in Chrome/Edge and make sure you're **logged in**
        2. Press **F12** (or right-click → Inspect) to open Developer Tools
        3. Click the **Application** tab at the top
        4. In the left sidebar, expand **Cookies** → click **https://www.linkedin.com**
        5. Find and copy these two cookies:

        | Cookie Name | What it looks like |
        |-------------|-------------------|
        | **li_at** | A long string like `AQEDASg...` |
        | **JSESSIONID** | A string in quotes like `"ajax:123..."` |

        6. Paste them below and hit Save!

        > **Tip:** These cookies last a few weeks. If the tool stops working, just grab fresh ones.
        """)

    with st.form("linkedin_form"):
        li_at = st.text_input("li_at Cookie",
                               value=existing["li_at"] if existing else "",
                               type="password",
                               help="The 'li_at' cookie from your LinkedIn session.")
        jsessionid = st.text_input("JSESSIONID Cookie",
                                    value=existing["jsessionid"] if existing else "",
                                    type="password",
                                    help="The 'JSESSIONID' cookie from your LinkedIn session.")

        col1, col2 = st.columns(2)
        with col1:
            weekly_limit = st.number_input("Weekly Connection Limit",
                                            value=existing["weekly_limit"] if existing else 80,
                                            min_value=10, max_value=150,
                                            help="LinkedIn allows ~100/week. Stay under to be safe.")
        with col2:
            delay_seconds = st.number_input("Delay Between Requests (sec)",
                                             value=existing["delay_seconds"] if existing else 15,
                                             min_value=10, max_value=120,
                                             help="Seconds to wait between each connection request.")

        submitted = st.form_submit_button("💾 Save Configuration", type="primary")
        if submitted:
            if li_at and jsessionid:
                save_linkedin_config({
                    "li_at": li_at,
                    "jsessionid": jsessionid,
                    "weekly_limit": weekly_limit,
                    "delay_seconds": delay_seconds,
                })
                st.success("LinkedIn configuration saved!")
                st.rerun()
            else:
                st.warning("Please enter both cookies.")

    # Test connection
    if existing:
        st.markdown("---")
        if st.button("🔌 Test LinkedIn Connection"):
            with st.spinner("Verifying LinkedIn cookies..."):
                result = test_linkedin_cookies(existing["li_at"], existing["jsessionid"])
            if result["success"]:
                st.success("✅ Cookies are valid! LinkedIn is ready to go.")
            else:
                st.error(f"❌ Connection failed: {result['error']}")


# --- Footer ---
st.sidebar.markdown("---")
st.sidebar.markdown("Built for **Simplex Productions**")
st.sidebar.markdown("v2.0 — LinkedIn Edition")
