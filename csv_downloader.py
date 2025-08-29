import pandas as pd
import streamlit as st
import requests
from datetime import datetime, timezone

# --- Helper Functions ---

@st.cache_data
def convert_df_to_csv(df: pd.DataFrame) -> bytes:
    """Converts a DataFrame to a UTF-8 encoded CSV file."""
    return df.to_csv(index=False).encode('utf-8')

def fetch_dune_data(api_key: str, query_id: int) -> dict:
    """
    Fetches query results from the Dune API.
    Returns the JSON response as a dictionary.
    Raises an exception if the request fails.
    """
    url = f"https://api.dune.com/api/v1/query/{query_id}/results"
    headers = {"X-DUNE-API-KEY": api_key}
    
    response = requests.get(url, headers=headers)
    # Raise an HTTPError if the HTTP request returned an unsuccessful status code
    response.raise_for_status() 
    return response.json()

# --- Streamlit App UI ---

st.set_page_config(layout="centered", page_title="Dune CSV Downloader")
st.title('Dune CSV Downloader 📊')

# --- User Inputs ---
# Use session state to hold onto the API key and query ID
if 'user_api_key' not in st.session_state:
    st.session_state.user_api_key = ''
if 'query_id' not in st.session_state:
    st.session_state.query_id = 2833363 # A default public query ID

st.session_state.user_api_key = st.text_input(
    label='Enter your Dune API Key',
    placeholder='Enter your key here...',
    value=st.session_state.user_api_key,
    type='password',  # Hides the API key for security
    help="You can find your API key on your Dune Analytics user settings page."
)

st.session_state.query_id = st.number_input(
    label='Enter the Dune Query ID',
    min_value=1,
    step=1,
    format="%d",
    value=st.session_state.query_id,
    help="The ID of the query you want to fetch results from."
)

# --- Main Logic ---
if st.button('🚀 Get Query Results', use_container_width=True):
    # Validate inputs first
    if not st.session_state.user_api_key:
        st.warning('Please enter your Dune API key to proceed.', icon="🔑")
    elif not st.session_state.query_id:
        st.warning('Please enter a valid Query ID.', icon="🔢")
    else:
        with st.spinner(f'Fetching results for Query ID: {st.session_state.query_id}...'):
            try:
                # 1. Fetch data from API
                response_json = fetch_dune_data(st.session_state.user_api_key, st.session_state.query_id)
                
                # 2. Process the response
                if 'result' in response_json and 'rows' in response_json['result']:
                    data_rows = response_json['result']['rows']
                    # Check if there are any rows to process
                    if data_rows:
                        # 💡 FIX: Get the original column order from the first row's keys
                        original_column_order = list(data_rows[0].keys())
                        
                        # Create the DataFrame (columns will be sorted alphabetically here)
                        df = pd.DataFrame(data_rows)
                        
                        # 💡 FIX: Reorder the DataFrame to match the original order
                        df = df[original_column_order]
                    else:
                        # If no rows, create an empty DataFrame
                        df = pd.DataFrame()
                    
                    
                    # Store dataframe in session state to use for downloading
                    st.session_state.df_to_download = df 
                    
                    st.success(f"Successfully retrieved {len(df)} rows!", icon="✅")
                    st.dataframe(df)
                else:
                    st.error("The API response was not in the expected format. It might be an execution error on Dune's side.", icon="👎")
                    st.json(response_json) # Show the actual response for debugging
                    st.session_state.df_to_download = None


            except requests.exceptions.HTTPError as e:
                st.error(f"An HTTP error occurred: {e.response.status_code} {e.response.reason}", icon="🚨")
                st.error("Please check if your API Key is correct and the Query ID is valid.", icon="🧐")
                st.session_state.df_to_download = None
            except requests.exceptions.RequestException as e:
                st.error(f"A network error occurred: {e}", icon="🌐")
                st.session_state.df_to_download = None
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}", icon="💥")
                st.session_state.df_to_download = None

# --- Download Section ---
# Only show the download section if a dataframe is available in the session state
if 'df_to_download' in st.session_state and st.session_state.df_to_download is not None:
    st.markdown("---")
    
    # Generate a dynamic file name
    utc_timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    file_name=st.text_input(label='Enter file name')
    if not file_name:
        file_name = f"dune_query_{st.session_state.query_id}_{utc_timestamp}.csv"


    csv_data = convert_df_to_csv(st.session_state.df_to_download)

    st.download_button(
        label="📥 Download Results as CSV",
        data=csv_data,
        file_name=file_name,
        mime="text/csv",
        use_container_width=True,
        key='download-csv'
    )
