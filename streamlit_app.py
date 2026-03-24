"""
Free web UI for GitHub portfolio scan — calls POST /scan/voiceflow (same as Voiceflow).

Run from project root:
  pip install -e ".[demo]"
  streamlit run streamlit_app.py
"""

from __future__ import annotations

import json

import httpx
import streamlit as st

DEFAULT_API_BASE = "https://github-cleaner-api.onrender.com"


def _scan_url(base: str) -> str:
    return f"{base.rstrip('/')}/scan/voiceflow"


def main() -> None:
    st.set_page_config(
        page_title="GitHub Cleaner — Scan",
        page_icon="📊",
        layout="wide",
    )
    st.title("GitHub portfolio scan")
    st.caption(
        "Uses your deployed API’s **POST /scan/voiceflow** — no Voiceflow credits. "
        "First request after idle (Render free tier) can take 1–2 minutes."
    )

    with st.sidebar:
        api_base = st.text_input(
            "API base URL",
            value=DEFAULT_API_BASE,
            help="No trailing path — e.g. https://github-cleaner-api.onrender.com",
        )
        timeout_s = st.slider("Request timeout (seconds)", 30, 180, 120, 5)

    col1, col2, col3 = st.columns(3)
    with col1:
        username = st.text_input("GitHub username", placeholder="octocat", key="gh_user")
    with col2:
        review_mode = st.selectbox("Review mode", ("portfolio", "cleanup"))
    with col3:
        scan_scope = st.selectbox("Scan scope", ("public", "all"))

    run = st.button("Run scan", type="primary")

    if not run:
        return

    u = (username or "").strip()
    if not u:
        st.warning("Enter a GitHub username.")
        return

    url = _scan_url(api_base)
    payload = {
        "github_username": u,
        "review_mode": review_mode,
        "scan_scope": scan_scope,
    }

    try:
        with st.spinner("Scanning… (wait if the server was sleeping)"):
            resp = httpx.post(url, json=payload, timeout=timeout_s)
    except httpx.TimeoutException:
        st.error(
            "Request timed out. Try a longer timeout in the sidebar, "
            "or wait a minute and retry (Render cold start)."
        )
        return
    except httpx.RequestError as e:
        st.error(f"Network error: {e}")
        return

    if resp.status_code == 200:
        data = resp.json()
        _render_success(data)
        with st.expander("Raw JSON"):
            st.code(json.dumps(data, indent=2), language="json")
        return

    # Error responses from FastAPI
    try:
        err = resp.json()
        detail = err.get("detail", resp.text)
        if isinstance(detail, list):
            detail = json.dumps(detail, indent=2)
    except Exception:
        detail = resp.text or str(resp.status_code)

    if resp.status_code == 404:
        st.error(f"**User not found** (404)\n\n{detail}")
    elif resp.status_code == 400:
        st.error(f"**Bad request** (400)\n\n{detail}")
    elif resp.status_code == 422:
        st.error(f"**Invalid input** (422)\n\n{detail}")
    else:
        st.error(f"**Error {resp.status_code}**\n\n{detail}")


def _render_success(data: dict) -> None:
    st.success("Scan complete")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total repos", data.get("total_repos", 0))
    m2.metric("Showcase-ready", data.get("showcase_ready", 0))
    m3.metric("Need cleanup", data.get("needs_cleanup", 0))
    m4.metric("Archive candidates", data.get("archive_candidates", 0))

    st.subheader("Most common issues")
    for i in range(1, 4):
        key = f"top_issue_{i}"
        text = (data.get(key) or "").strip()
        if text:
            st.markdown(f"{i}. {text}")

    st.subheader("Showcase highlights (highest scores)")
    for k in ("showcase_repo_1", "showcase_repo_2"):
        v = (data.get(k) or "").strip()
        if v:
            st.markdown(f"- `{v}`")

    st.subheader("Repos to prioritize")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Cleanup**")
        for k in ("cleanup_repo_1", "cleanup_repo_2"):
            v = (data.get(k) or "").strip()
            if v:
                st.markdown(f"- `{v}`")
    with c2:
        st.markdown("**Archive**")
        for k in ("archive_repo_1", "archive_repo_2"):
            v = (data.get(k) or "").strip()
            if v:
                st.markdown(f"- `{v}`")

    step = (data.get("recommended_next_step") or "").strip()
    if step:
        st.subheader("Recommended next step")
        st.info(step)


if __name__ == "__main__":
    main()
