"""Streamlit UI for DocQA — Lucide SVG icons, no emoji."""

import os
import time

import requests
import streamlit as st

API_URL = os.environ.get("API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="DocQA",
    page_icon="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'><text y='20' font-size='20'>📋</text></svg>",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Lucide SVG icons ───────────────────────────────────────────────────────────
_PATHS: dict[str, str] = {
    "file-text":    '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/>',
    "upload-cloud": '<polyline points="16 16 12 12 8 16"/><line x1="12" y1="12" x2="12" y2="21"/><path d="M20.39 18.39A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.3"/>',
    "database":     '<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/>',
    "cpu":          '<rect x="4" y="4" width="16" height="16" rx="2" ry="2"/><rect x="9" y="9" width="6" height="6"/><line x1="9" y1="1" x2="9" y2="4"/><line x1="15" y1="1" x2="15" y2="4"/><line x1="9" y1="20" x2="9" y2="23"/><line x1="15" y1="20" x2="15" y2="23"/><line x1="20" y1="9" x2="23" y2="9"/><line x1="20" y1="14" x2="23" y2="14"/><line x1="1" y1="9" x2="4" y2="9"/><line x1="1" y1="14" x2="4" y2="14"/>',
    "check-circle": '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>',
    "x-circle":     '<circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/>',
    "alert-circle": '<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>',
    "quote":        '<path d="M3 21c3 0 7-1 7-8V5c0-1.25-.756-2.017-2-2H4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2 1 0 1 0 1 1v1c0 1-1 2-2 2s-1 .008-1 1.031V20c0 1 0 1 1 1z"/><path d="M15 21c3 0 7-1 7-8V5c0-1.25-.757-2.017-2-2h-4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2h.75c0 2.25.25 4-2.75 4v3c0 1 0 1 1 1z"/>',
    "trash-2":      '<polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/><line x1="10" y1="11" x2="10" y2="17"/><line x1="14" y1="11" x2="14" y2="17"/>',
    "search-x":     '<path d="m13.5 8.5-5 5"/><path d="m8.5 8.5 5 5"/><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
    "library":      '<path d="m16 6 4 14"/><path d="M12 6v14"/><path d="M8 8v12"/><path d="M4 4v16"/>',
    "zap":          '<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>',
    "layers":       '<polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/>',
}


def lucide(name: str, size: int = 15, color: str = "currentColor", cls: str = "") -> str:
    inner = _PATHS.get(name, "")
    style = "display:inline-block;vertical-align:middle;flex-shrink:0"
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" '
        f'stroke-linecap="round" stroke-linejoin="round" '
        f'class="{cls}" style="{style}">{inner}</svg>'
    )


# ── Global styles ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
  /* Reset and base */
  .stApp { background: #f8fafc; }
  #MainMenu, footer, header { visibility: hidden; }
  [data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 1px solid #e2e8f0;
  }

  /* Sidebar section label */
  .sb-label {
    font-size: 0.7rem; font-weight: 700; letter-spacing: 0.08em;
    text-transform: uppercase; color: #94a3b8; margin: 14px 0 6px;
  }

  /* Status row */
  .status-row {
    display: flex; align-items: center; gap: 8px;
    padding: 4px 0; font-size: 0.82rem; color: #475569;
  }
  .dot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }
  .dot-green { background: #22c55e; box-shadow: 0 0 0 2px #dcfce7; }
  .dot-red   { background: #ef4444; box-shadow: 0 0 0 2px #fee2e2; }

  /* Document card in sidebar */
  .doc-card {
    display: flex; align-items: flex-start; gap: 10px;
    background: #f8fafc; border: 1px solid #e2e8f0;
    border-radius: 6px; padding: 9px 12px; margin: 5px 0;
  }
  .doc-icon { margin-top: 1px; flex-shrink: 0; }
  .doc-name { font-size: 0.82rem; font-weight: 600; color: #1e293b; line-height: 1.3; }
  .doc-meta { font-size: 0.73rem; color: #94a3b8; margin-top: 2px; }

  /* Welcome step cards */
  .step-card {
    background: #fff; border: 1px solid #e2e8f0; border-radius: 8px;
    padding: 20px; height: 100%;
  }
  .step-num {
    display: inline-flex; align-items: center; justify-content: center;
    width: 28px; height: 28px; border-radius: 6px;
    background: #ede9fe; color: #6366f1;
    font-size: 0.78rem; font-weight: 700; margin-bottom: 12px;
  }
  .step-title { font-size: 0.92rem; font-weight: 600; color: #1e293b; margin-bottom: 5px; }
  .step-body  { font-size: 0.8rem; color: #64748b; line-height: 1.55; }

  /* Citation block */
  .citation {
    background: #fafafa; border: 1px solid #e2e8f0;
    border-left: 3px solid #6366f1; border-radius: 4px;
    padding: 10px 14px; margin: 8px 0;
  }
  .citation-header {
    display: flex; align-items: center; gap: 6px;
    font-size: 0.71rem; font-weight: 700; color: #6366f1;
    text-transform: uppercase; letter-spacing: 0.07em;
    margin-bottom: 5px;
  }
  .citation-text { font-size: 0.82rem; color: #64748b; font-style: italic; }

  /* Inline alert row */
  .info-row {
    display: flex; align-items: center; gap: 8px;
    background: #f0f9ff; border: 1px solid #bae6fd; border-radius: 6px;
    padding: 8px 12px; font-size: 0.82rem; color: #0369a1; margin-top: 6px;
  }
  .warn-row {
    display: flex; align-items: center; gap: 8px;
    background: #fffbeb; border: 1px solid #fde68a; border-radius: 6px;
    padding: 8px 12px; font-size: 0.82rem; color: #92400e; margin-top: 6px;
  }

  hr { border: none; border-top: 1px solid #e2e8f0; margin: 12px 0; }
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploaded_docs" not in st.session_state:
    st.session_state.uploaded_docs = []


# ── API helpers ────────────────────────────────────────────────────────────────
def check_health():
    try:
        r = requests.get(f"{API_URL}/health", timeout=4)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None


def upload_pdf(file_bytes: bytes, filename: str):
    try:
        r = requests.post(
            f"{API_URL}/ingest",
            files={"file": (filename, file_bytes, "application/pdf")},
            timeout=180,
        )
        if r.status_code == 200:
            return r.json(), None
        try:
            detail = r.json().get("detail", "Upload failed")
        except Exception:
            detail = f"HTTP {r.status_code}"
        return None, detail
    except requests.exceptions.ConnectionError:
        return None, "Cannot reach the backend service."
    except Exception as exc:
        return None, str(exc)


def ask_question(question: str):
    try:
        r = requests.post(f"{API_URL}/query", json={"question": question}, timeout=120)
        if r.status_code == 200:
            return r.json(), None
        try:
            detail = r.json().get("detail", "Query failed")
        except Exception:
            detail = f"HTTP {r.status_code} — {r.text[:200]}"
        return None, detail
    except requests.exceptions.ConnectionError:
        return None, "Cannot reach the backend service."
    except requests.exceptions.Timeout:
        return None, "Request timed out. The model may still be warming up — try again."
    except Exception as exc:
        return None, str(exc)


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:8px;padding:4px 0 8px">'
        f'{lucide("layers", 18, "#6366f1")}'
        f'<span style="font-size:1rem;font-weight:700;color:#1e293b">DocQA</span>'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.caption("Document question answering with citations")
    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Status ──────────────────────────────────────────────────────────────
    st.markdown('<div class="sb-label">Services</div>', unsafe_allow_html=True)
    health = check_health()
    if health:
        qdrant_ok = health.get("qdrant") == "ok"
        llm       = health.get("llm_provider", "unknown").capitalize()
        st.markdown(
            f'<div class="status-row"><div class="dot dot-green"></div>'
            f'{lucide("zap", 13, "#22c55e")} &nbsp;API</div>'
            f'<div class="status-row">'
            f'<div class="dot {"dot-green" if qdrant_ok else "dot-red"}"></div>'
            f'{lucide("database", 13, "#64748b")} &nbsp;Vector database</div>'
            f'<div class="status-row"><div class="dot dot-green"></div>'
            f'{lucide("cpu", 13, "#64748b")} &nbsp;{llm}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="status-row"><div class="dot dot-red"></div>'
            'Service offline</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="warn-row">{lucide("alert-circle", 14, "#92400e")}'
            f'&nbsp; Run <code>docker compose up</code> then refresh.</div>',
            unsafe_allow_html=True,
        )

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Upload ──────────────────────────────────────────────────────────────
    st.markdown('<div class="sb-label">Documents</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("PDF", type=["pdf"], label_visibility="collapsed")

    if uploaded_file:
        size_kb = len(uploaded_file.getvalue()) // 1024
        st.markdown(
            f'<div style="font-size:0.78rem;color:#64748b;margin:4px 0 8px">'
            f'{uploaded_file.name} &nbsp;·&nbsp; {size_kb} KB</div>',
            unsafe_allow_html=True,
        )
        if st.button("Index document", type="primary", use_container_width=True):
            bar = st.progress(0, text="Reading…")
            time.sleep(0.15)
            bar.progress(30, text="Extracting text…")
            result, error = upload_pdf(uploaded_file.getvalue(), uploaded_file.name)
            bar.progress(90, text="Indexing…")
            time.sleep(0.15)
            bar.empty()

            if error:
                st.markdown(
                    f'<div class="warn-row">{lucide("alert-circle", 14, "#92400e")}'
                    f'&nbsp;{error}</div>',
                    unsafe_allow_html=True,
                )
            else:
                chunks = result.get("chunks_indexed", 0)
                st.markdown(
                    f'<div class="info-row">{lucide("check-circle", 14, "#0369a1")}'
                    f'&nbsp;Indexed <strong>{chunks} sections</strong></div>',
                    unsafe_allow_html=True,
                )
                if not any(d["name"] == uploaded_file.name for d in st.session_state.uploaded_docs):
                    st.session_state.uploaded_docs.append({
                        "name": uploaded_file.name,
                        "chunks": chunks,
                    })

    # ── Indexed list ────────────────────────────────────────────────────────
    if st.session_state.uploaded_docs:
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown('<div class="sb-label">Indexed</div>', unsafe_allow_html=True)
        for doc in st.session_state.uploaded_docs:
            st.markdown(
                f'<div class="doc-card">'
                f'<div class="doc-icon">{lucide("file-text", 14, "#6366f1")}</div>'
                f'<div><div class="doc-name">{doc["name"]}</div>'
                f'<div class="doc-meta">{doc["chunks"]} sections</div></div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    if st.session_state.messages:
        st.markdown("<hr>", unsafe_allow_html=True)
        if st.button("Clear conversation", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(
        f'<div style="display:flex;gap:6px;align-items:flex-start;font-size:0.75rem;color:#94a3b8">'
        f'{lucide("alert-circle", 12, "#cbd5e1")}'
        f'<span>Answers are grounded in uploaded documents only.</span></div>',
        unsafe_allow_html=True,
    )


# ── Main ───────────────────────────────────────────────────────────────────────
st.markdown("## Document Q&A")

if not st.session_state.uploaded_docs and not st.session_state.messages:
    c1, c2, c3 = st.columns(3)
    for col, num, icon_name, title, body in [
        (c1, "01", "upload-cloud", "Upload a document",
         "Select any PDF from the sidebar. Text is extracted and split into searchable sections automatically."),
        (c2, "02", "layers",       "Ask in plain English",
         "No keywords or search syntax. Ask like you would ask a colleague."),
        (c3, "03", "quote",        "Read with sources",
         "Every answer shows the exact document, page, and section it came from."),
    ]:
        with col:
            st.markdown(
                f'<div class="step-card">'
                f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:12px">'
                f'<span class="step-num">{num}</span>'
                f'{lucide(icon_name, 16, "#6366f1")}'
                f'</div>'
                f'<div class="step-title">{title}</div>'
                f'<div class="step-body">{body}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        f'<div class="info-row">{lucide("alert-circle", 14, "#0369a1")}'
        f'&nbsp; <strong>First query may take 30–60 s</strong> while the AI model warms up. '
        f'Subsequent queries are faster.</div>',
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)

# ── Chat history ──────────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg["role"] == "assistant" and msg.get("citations"):
            with st.expander(f"Sources — {len(msg['citations'])} section(s) referenced"):
                for i, cit in enumerate(msg["citations"], 1):
                    st.markdown(
                        f'<div class="citation">'
                        f'<div class="citation-header">'
                        f'{lucide("quote", 11, "#6366f1")}'
                        f'&nbsp;Source {i} &nbsp;·&nbsp; {cit["source"]} &nbsp;·&nbsp; Page {cit["page"]}'
                        f'</div>'
                        f'<div class="citation-text">&ldquo;{cit["text_snippet"]}&rdquo;</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
            r, n = msg.get("retrieved_count", 0), msg.get("reranked_count", 0)
            if r:
                st.caption(f"Searched {r} sections · ranked top {n}")


# ── Input ─────────────────────────────────────────────────────────────────────
prompt = st.chat_input(
    "Ask a question about your documents…"
    if st.session_state.uploaded_docs
    else "Upload a document first, then ask your question here…"
)

if prompt:
    with st.chat_message("user"):
        st.write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Searching and generating answer…"):
            result, error = ask_question(prompt)

        if error:
            st.markdown(
                f'<div class="warn-row">{lucide("alert-circle", 14, "#92400e")}'
                f'&nbsp;{error}</div>',
                unsafe_allow_html=True,
            )
            st.session_state.messages.append(
                {"role": "assistant", "content": error, "citations": []}
            )
        else:
            answer    = result.get("answer", "")
            citations = result.get("citations", [])
            retrieved = result.get("retrieved_count", 0)
            reranked  = result.get("reranked_count", 0)
            is_refusal = "don't have that in the provided documents" in answer.lower()

            st.write(answer)

            if is_refusal:
                st.markdown(
                    f'<div class="info-row">{lucide("search-x", 14, "#0369a1")}'
                    f'&nbsp;No matching content found in the indexed documents.</div>',
                    unsafe_allow_html=True,
                )
            elif citations:
                with st.expander(f"Sources — {len(citations)} section(s) referenced"):
                    for i, cit in enumerate(citations, 1):
                        st.markdown(
                            f'<div class="citation">'
                            f'<div class="citation-header">'
                            f'{lucide("quote", 11, "#6366f1")}'
                            f'&nbsp;Source {i} &nbsp;·&nbsp; {cit["source"]} &nbsp;·&nbsp; Page {cit["page"]}'
                            f'</div>'
                            f'<div class="citation-text">&ldquo;{cit["text_snippet"]}&rdquo;</div>'
                            f'</div>',
                            unsafe_allow_html=True,
                        )
                if retrieved:
                    st.caption(f"Searched {retrieved} sections · ranked top {reranked}")

            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "citations": citations,
                "retrieved_count": retrieved,
                "reranked_count": reranked,
            })
