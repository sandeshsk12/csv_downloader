import pandas as pd
import streamlit as st
import requests
from datetime import datetime, timezone
import re

# ---------- Helpers ----------

@st.cache_data
def convert_df_to_csv(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")

def fetch_dune_data(api_key: str, query_id: int) -> dict:
    url = f"https://api.dune.com/api/v1/query/{query_id}/results"
    headers = {"X-DUNE-API-KEY": api_key}
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    return r.json()

def safe_filename(name: str, default: str) -> str:
    name = name.strip()
    name = re.sub(r"\s+", " ", name)
    name = re.sub(r'[\\/:"*?<>|]+', "_", name)
    return name or default

# ---------- App setup ----------

st.set_page_config(layout="centered", page_title="Dune CSV Downloader")
st.title("Dune CSV Downloader 📊")

if "user_api_key" not in st.session_state:
    st.session_state.user_api_key = ""
if "query_id" not in st.session_state:
    st.session_state.query_id = 2833363
# This key holds the current downloadable payload
if "download_payload" not in st.session_state:
    st.session_state.download_payload = None  # dict with csv_bytes, filename, df_preview, meta

# ---------- Inputs ----------

st.session_state.user_api_key = st.text_input(
    "Enter your Dune API Key",
    placeholder="Enter your key here...",
    value=st.session_state.user_api_key,
    type="password",
)

st.session_state.query_id = st.number_input(
    "Enter the Dune Query ID",
    min_value=1,
    step=1,
    format="%d",
    value=st.session_state.query_id,
    help="The ID of the query you want to fetch results from.",
)

# If any inputs change, we can optionally invalidate the prior download
# (Uncomment if you want to strictly tie downloads to the exact inputs)
# st.session_state.download_payload = None

# ---------- Fetch Results ----------

fetch = st.button("🚀 Get Query Results", use_container_width=True)

if fetch:
    if not st.session_state.user_api_key:
        st.warning("Please enter your Dune API key to proceed.", icon="🔑")
    else:
        with st.spinner(f'Fetching results for Query ID: {st.session_state.query_id}...'):
            try:
                resp = fetch_dune_data(st.session_state.user_api_key, st.session_state.query_id)
                if "result" in resp and "rows" in resp["result"]:
                    rows = resp["result"]["rows"]
                    df = pd.DataFrame(rows)
                    csv_bytes = convert_df_to_csv(df)

                    utc_ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
                    default_name = f"dune_query_{st.session_state.query_id}_{utc_ts}.csv"

                    # Save everything needed to rehydrate the download button on ANY rerun
                    st.session_state.download_payload = {
                        "csv_bytes": csv_bytes,
                        "default_filename": default_name,
                        "df_preview": df.head(200),  # small preview for UI; keep big dfs light
                        "meta": {
                            "rows": len(df),
                            "generated_at": utc_ts,
                            "query_id": st.session_state.query_id,
                        },
                    }

                    st.success(f"Successfully retrieved {len(df)} rows!", icon="✅")
                else:
                    st.error("API response not in expected format.", icon="👎")
                    st.json(resp)
                    st.session_state.download_payload = None
            except requests.exceptions.HTTPError as e:
                st.error(f"HTTP error: {e.response.status_code} {e.response.reason}", icon="🚨")
                st.error("Check API key and Query ID.", icon="🧐")
                st.session_state.download_payload = None
            except requests.exceptions.RequestException as e:
                st.error(f"Network error: {e}", icon="🌐")
                st.session_state.download_payload = None
            except Exception as e:
                st.error(f"Unexpected error: {e}", icon="💥")
                st.session_state.download_payload = None

# ---------- Download Section (session file manager) ----------

payload = st.session_state.download_payload
if payload is not None:
    st.markdown("---")
    st.subheader("Preview & Download")

    # Lightweight preview to keep reruns snappy
    st.caption(
        f"Rows: {payload['meta']['rows']} • Query ID: {payload['meta']['query_id']} • Generated (UTC): {payload['meta']['generated_at']}"
    )
    st.dataframe(payload["df_preview"])

    # Let user customize filename on every rerun; regenerate the download button each time
    raw_name = st.text_input(
        "Enter file name (without .csv)",
        value=payload["default_filename"].rsplit(".csv", 1)[0],
        help="Avoid special characters; we'll sanitize it.",
    )
    final_name = safe_filename(raw_name, payload["default_filename"].rsplit(".csv", 1)[0]) + ".csv"

    st.download_button(
        label="📥 Download Results as CSV",
        data=payload["csv_bytes"],        # <-- persisted bytes
        file_name=final_name,             # <-- regenerated each rerun
        mime="text/csv",
        use_container_width=True,
        key="download-csv",               # key can stay constant
    )

    st.caption(
        "Tip: Click the button directly. The link is recreated on each rerun to avoid stale `/~/media` URLs."
    )

    # Optional: a clear/reset action
    if st.button("🧹 Clear Results", use_container_width=True):
        st.session_state.download_payload = None
        st.experimental_rerun()
