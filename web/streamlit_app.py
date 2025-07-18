import streamlit as st
import requests
import pandas as pd
import json
import sqlite3
from pathlib import Path
import sys
import numpy as np
import plotly.express as px

sys.path.append(str(Path(__file__).resolve().parent.parent))
from src.paths import DB_PATH

st.set_page_config(
    page_title="Text to SQL Project",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    /* ... [CSS unchanged for brevity; use your existing CSS here] ... */
</style>
""", unsafe_allow_html=True)

# === Database Upload Feature ===
DB_PARENT = Path(__file__).resolve().parent.parent / "data"
DB_PARENT.mkdir(exist_ok=True)

if "db_upload_count" not in st.session_state:
    st.session_state["db_upload_count"] = 0
if "current_db_path" not in st.session_state:
    st.session_state["current_db_path"] = None

st.markdown("""
<div class="main-header">
    <h2>📤 Upload Your SQL File</h2>
    <p>Upload a <b>.sql</b> file to create a SQLite database before running any queries.</p>
</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload your .sql file", type=["sql"], key="file_upload")

if uploaded_file:
    db_number = st.session_state["db_upload_count"] + 1
    db_folder = DB_PARENT / f"db{db_number}"
    if db_folder.exists():
        import shutil
        shutil.rmtree(db_folder)
    db_folder.mkdir(exist_ok=True)
    
    sql_path = db_folder / "uploaded.sql"
    db_path = db_folder / "uploaded.sqlite"
    
    with open(sql_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    try:
        conn = sqlite3.connect(str(db_path))
        with open(sql_path, "r", encoding="utf-8") as f:
            sql_script = f.read()
        conn.executescript(sql_script)
        conn.close()
        
        st.success("Database created successfully.")
        st.session_state["current_db_path"] = db_path
        st.session_state["db_upload_count"] = db_number
    except Exception as e:
        st.error(f"Failed to convert SQL file: {str(e)}")
        st.session_state["current_db_path"] = None

if st.session_state["current_db_path"]:
    DB_PATH = st.session_state["current_db_path"]

# === History Feature ===
if "nl_history" not in st.session_state:
    st.session_state["nl_history"] = []  # list of dict: {"question": ..., "sql": ...}
if "sql_history" not in st.session_state:
    st.session_state["sql_history"] = []  # list of dict: {"query": ...}

def add_nl_history(question, sql_query):
    st.session_state["nl_history"].append({"question": question, "sql": sql_query})

def add_sql_history(query):
    st.session_state["sql_history"].append({"query": query})

def remove_nl_history(index):
    if 0 <= index < len(st.session_state["nl_history"]):
        st.session_state["nl_history"].pop(index)

def remove_sql_history(index):
    if 0 <= index < len(st.session_state["sql_history"]):
        st.session_state["sql_history"].pop(index)

def clear_nl_history():
    st.session_state["nl_history"] = []

def clear_sql_history():
    st.session_state["sql_history"] = []

def visualize_ui(df, block_key=""):
    all_cols = df.columns.tolist()
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    
    st.markdown("#### 📊 Manual Visualization Controls")
    
    chart_type = st.selectbox(
        "Chart type",
        ["Bar", "Line", "Pie", "Scatter", "Histogram"],
        key=f"chart_type_{block_key}"
    )
    
    x_col = st.selectbox("X axis", all_cols, key=f"x_{block_key}")
    y_col = st.selectbox("Y axis (numeric)", numeric_cols, key=f"y_{block_key}")
    
    visualize_btn = st.button("Visualize!", key=f"visualize_btn_{block_key}")
    
    if visualize_btn:
        if chart_type == "Bar":
            fig = px.bar(df, x=x_col, y=y_col)
        elif chart_type == "Line":
            fig = px.line(df, x=x_col, y=y_col)
        elif chart_type == "Pie":
            fig = px.pie(df, names=x_col, values=y_col)
        elif chart_type == "Scatter":
            fig = px.scatter(df, x=x_col, y=y_col)
        elif chart_type == "Histogram":
            fig = px.histogram(df, x=y_col)
        
        st.plotly_chart(fig, use_container_width=True)

st.markdown("""
<div class="main-header">
    <h1>🔍 Text to SQL Project</h1>
    <p>AI-powered natural language to SQL query system for student transcript data</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["💬 Natural Language", "📝 Direct SQL", "🕑 History"])

with tab1:
    st.markdown("### 💬 Ask your question in natural language:")
    
    user_query = st.text_input(
        "Your Question",
        placeholder="e.g., Show me the number of students per year...",
        key="query_input",
        label_visibility="collapsed"
    )
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        submit_button_nl = st.button("🚀 Execute NL Query", use_container_width=True, key="nl_submit")
    
    if submit_button_nl and user_query:
        with st.spinner("🔄 Processing your query..."):
            try:
                response = requests.post(
                    "http://localhost:8000/query",
                    json={"query": user_query},
                    timeout=300
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if "error" in result:
                        st.markdown(f"""
                        <div class="error-box">
                            <h3>❌ Error</h3>
                            <p style="color: #ff6666;">{result['error']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        st.session_state['nl_result_df'] = None
                    else:
                        # Parse the result if it's a JSON string
                        if isinstance(result, str):
                            try:
                                result = json.loads(result)
                            except json.JSONDecodeError:
                                st.error("Failed to parse API response")
                                st.session_state['nl_result_df'] = None
                        
                        if isinstance(result, dict) and "success" in result and result["success"]:
                            st.markdown(f"""
                            <div class="query-box">
                                <h3>🔍 Generated SQL Query:</h3>
                                <code>{result['query']}</code>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            if result['data']:
                                df = pd.DataFrame(result['data'])
                                st.session_state['nl_result_df'] = df
                                add_nl_history(user_query, result['query'])
                            else:
                                st.info("🔍 Query executed successfully but returned no results.")
                                st.session_state['nl_result_df'] = None
                        else:
                            st.markdown(f"""
                            <div class="query-box">
                                <h3>📋 Raw Response:</h3>
                                <code>{json.dumps(result, indent=2)}</code>
                            </div>
                            """, unsafe_allow_html=True)
                            st.session_state['nl_result_df'] = None
                else:
                    st.error(f"❌ API Error: {response.status_code} - {response.text}")
                    st.session_state['nl_result_df'] = None
                    
            except requests.exceptions.RequestException as e:
                st.markdown(f"""
                <div class="error-box">
                    <h3>🌐 Connection Error</h3>
                    <p style="color: #ff6666;">Could not connect to the API. Please make sure your FastAPI server is running on http://localhost:8000</p>
                    <p style="color: #ff6666;"><small>Error details: {str(e)}</small></p>
                </div>
                """, unsafe_allow_html=True)
                st.session_state['nl_result_df'] = None
                
            except Exception as e:
                st.markdown(f"""
                <div class="error-box">
                    <h3>⚠️ Unexpected Error</h3>
                    <p style="color: #ff6666;">{str(e)}</p>
                </div>
                """, unsafe_allow_html=True)
                st.session_state['nl_result_df'] = None
    
    # Display results exactly like Direct SQL tab
    df_nl = st.session_state.get('nl_result_df', None)
    if df_nl is not None and not df_nl.empty:
        st.markdown('<div class="results-header">📊 Query Results</div>', unsafe_allow_html=True)
        st.dataframe(
            df_nl,
            use_container_width=True,
            hide_index=True,
            column_config={
                col: st.column_config.TextColumn(
                    col,
                    help=f"Data from column: {col}"
                ) for col in df_nl.columns
            }
        )
        
        csv = df_nl.to_csv(index=False)
        st.download_button(
            label="📥 Download Results as CSV",
            data=csv,
            file_name=f"query_results_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
        
        visualize_ui(df_nl, block_key="nl")
    elif df_nl is not None and df_nl.empty:
        st.info("🔍 Query executed successfully but returned no results.")

with tab2:
    st.markdown("### 📝 Write your SQL query directly:")
    
    user_sql_query = st.text_area(
        "Your SQL Query",
        placeholder="SELECT year, COUNT(*) as student_count FROM students GROUP BY year;",
        key="sql_input",
        height=120,
        label_visibility="collapsed"
    )
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        submit_button_sql = st.button("🚀 Execute SQL Query", use_container_width=True, key="sql_submit")
    
    if submit_button_sql and user_sql_query:
        db_path = DB_PATH
        if not db_path.exists():
            st.error("❌ Database file not found.")
            st.session_state['sql_result_df'] = None
        else:
            with st.spinner("🔄 Executing your SQL query..."):
                try:
                    with sqlite3.connect(str(db_path)) as conn:
                        cursor = conn.cursor()
                        cursor.execute(user_sql_query)
                        rows = cursor.fetchall()
                        columns = [desc[0] for desc in cursor.description] if cursor.description else []
                        
                        if rows and columns:
                            df = pd.DataFrame(rows, columns=columns)
                            st.session_state['sql_result_df'] = df
                            add_sql_history(user_sql_query)
                        elif columns:
                            st.session_state['sql_result_df'] = pd.DataFrame(columns=columns)
                            add_sql_history(user_sql_query)
                        else:
                            st.session_state['sql_result_df'] = None
                            add_sql_history(user_sql_query)
                            
                except Exception as e:
                    st.markdown(f"""
                    <div class="error-box">
                        <h3>❌ SQL Error</h3>
                        <p style="color: #ff6666;">{str(e)}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    st.session_state['sql_result_df'] = None
    
    df_sql = st.session_state.get('sql_result_df', None)
    if df_sql is not None and not df_sql.empty:
        st.markdown('<div class="results-header">📊 Query Results</div>', unsafe_allow_html=True)
        st.dataframe(
            df_sql,
            use_container_width=True,
            hide_index=True,
            column_config={
                col: st.column_config.TextColumn(
                    col,
                    help=f"Data from column: {col}"
                ) for col in df_sql.columns
            }
        )
        
        csv = df_sql.to_csv(index=False)
        st.download_button(
            label="📥 Download Results as CSV",
            data=csv,
            file_name=f"sql_results_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
        
        visualize_ui(df_sql, block_key="sql")
    elif df_sql is not None and df_sql.empty:
        st.info("🔍 Query executed successfully but returned no results.")

with tab3:
    st.markdown("### 🕑 Query History")
    
    st.markdown("#### 💬 Natural Language History")
    if st.session_state["nl_history"]:
        for idx, item in enumerate(st.session_state["nl_history"]):
            st.markdown(f"- **Q:** {item['question']} <br> <span style='color:gray'>SQL: <code>{item['sql']}</code></span>", unsafe_allow_html=True)
            col_hist1, col_hist2 = st.columns([0.1, 0.9])
            with col_hist1:
                if st.button(f"🗑️ Remove", key=f"remove_nl_tab_{idx}"):
                    remove_nl_history(idx)
                    st.experimental_rerun()
        
        if st.button("🗑️ Clear All NL History", key="clear_all_nl_tab"):
            clear_nl_history()
            st.experimental_rerun()
    else:
        st.info("No natural language history yet.")
    
    st.markdown("---")
    st.markdown("#### 📝 Direct SQL History")
    if st.session_state["sql_history"]:
        for idx, item in enumerate(st.session_state["sql_history"]):
            st.markdown(f"- <span style='color:gray'>SQL: <code>{item['query']}</code></span>", unsafe_allow_html=True)
            col_hist1, col_hist2 = st.columns([0.1, 0.9])
            with col_hist1:
                if st.button(f"🗑️ Remove", key=f"remove_sql_tab_{idx}"):
                    remove_sql_history(idx)
                    st.experimental_rerun()
        
        if st.button("🗑️ Clear All SQL History", key="clear_all_sql_tab"):
            clear_sql_history()
            st.experimental_rerun()
    else:
        st.info("No direct SQL history yet.")

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #FFD700; padding: 20px;">
    <p>🚀 Powered by FastAPI & Streamlit | 🤖 AI-Driven SQL Generation</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 📋 Instructions")
    st.markdown("""
    1. **Upload your .sql file** above to create a SQLite database.
    2. **Natural Language**: Enter your question and click 'Execute NL Query'.
    3. **Direct SQL**: Write your SQL and click 'Execute SQL Query'.
    4. **View the results** in the table.
    5. **Download results** as CSV if needed.
    6. **Visualize results**: Choose X and Y, then click 'Visualize'!
    7. **History**: View or remove previous queries in the History tab.
    """)

    st.markdown("### ⚙️ API Settings")
    st.info("Make sure your FastAPI server is running on http://localhost:8000") 