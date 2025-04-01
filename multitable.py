import os
import streamlit as st
import pandas as pd
import sqlite3
import pyperclip
from langchain_openai import ChatOpenAI
from langchain_community.utilities.sql_database import SQLDatabase
import networkx as nx
import matplotlib.pyplot as plt

# OpenAI API Key (Solution 4: Passed directly)
API_KEY = "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"  # Replace with your OpenAI API key

# Ensure database file exists
db_path = "my_demo.db"
if not os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    conn.close()

# Streamlit Page Configuration
st.set_page_config(page_title="QueryGenie - AI SQL Assistant", layout="wide")

# Header
st.markdown("<h1 style='text-align: center;'>🤖 QueryGenie - MultiTable AI SQL Assistant</h1>", unsafe_allow_html=True)

# Sidebar
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/4712/4712027.png", width=100)
st.sidebar.markdown("### Your AI-powered SQL Assistant")
st.sidebar.markdown("Upload your dataset and ask SQL queries in natural language.")

# Upload Multiple Files
uploaded_files = st.file_uploader("📂 Upload CSV, Excel, or JSON files:", type=["csv", "xlsx", "json"], accept_multiple_files=True)
dataframes = {}

if uploaded_files:
    conn = sqlite3.connect(db_path)
    for uploaded_file in uploaded_files:
        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith(".xlsx"):
                df = pd.read_excel(uploaded_file)
            elif uploaded_file.name.endswith(".json"):
                df = pd.read_json(uploaded_file)
            else:
                st.error(f"Unsupported file format: {uploaded_file.name}")
                continue

            table_name = uploaded_file.name.split('.')[0]
            df.to_sql(table_name, conn, index=False, if_exists="replace")
            dataframes[table_name] = df
        except Exception as e:
            st.error(f"Error processing file {uploaded_file.name}: {e}")
    conn.close()

    # Display all uploaded tables
    for table_name, df in dataframes.items():
        st.write(f"📊 **Preview of {table_name}:**")
        st.dataframe(df, use_container_width=True)

# Connect LangChain to SQLite
db = SQLDatabase.from_uri(f"sqlite:///{db_path}")
llm = ChatOpenAI(temperature=0, api_key=API_KEY)


# Function to extract schema information for uploaded tables
def extract_schema_from_uploads():
    schema_info = {}

    # Analyze each uploaded file
    for table_name, df in dataframes.items():
        columns = list(df.columns)
        
        # Identify primary keys (Assuming 'ID', 'id', or columns ending with '_id' are PKs)
        primary_keys = [col for col in columns if col.lower() == "id" or col.endswith("_id")]
        
        # Identify foreign keys (If a column exists in another table as a primary key)
        foreign_keys = []
        for col in columns:
            for other_table, other_df in dataframes.items():
                if table_name != other_table and col in other_df.columns and col in primary_keys:
                    foreign_keys.append((other_table, col, col))  # Correct format: (Referenced Table, FK Column, PK Column)

        # Identify indexes (Assuming numeric columns as indexed for performance)
        indexes = [col for col in columns if df[col].dtype in ['int64', 'float64']]

        schema_info[table_name] = {
            "columns": columns,
            "primary_keys": primary_keys,
            "foreign_keys": foreign_keys,  
            "indexes": indexes
        }

    return schema_info

# Store schema info globally
schema_details = extract_schema_from_uploads()

# Checkbox to show Schema Details
show_schema = st.checkbox("📌 Show Schema Details")

if show_schema:
    st.markdown("### 🏛️ Uploaded Dataset Schema Overview")

    for table, details in schema_details.items():
        st.markdown(f"#### 📋 Table: `{table}`")

        # Convert schema details to DataFrame for tabular display
        schema_df = pd.DataFrame({
            "Column Name": details["columns"],
            "Primary Key": ["✅" if col in details["primary_keys"] else "" for col in details["columns"]],
            "Foreign Key": ["✅" if any(fk[1] == col for fk in details["foreign_keys"]) else "" for col in details["columns"]],
            "Index": ["✅" if col in details["indexes"] else "" for col in details["columns"]]
        })
        
        # Display as a table
        st.table(schema_df)

# Checkbox to show ER Diagram
show_er = st.checkbox("📌 Show ER Diagram")

# Function to generate ER Diagram
def generate_er_diagram(schema):
    G = nx.DiGraph()

    # Adding nodes and edges
    for table, details in schema.items():
        G.add_node(table, shape="box", style="filled", fillcolor="lightblue")
        for fk in details["foreign_keys"]:
            if len(fk) == 3:  # Ensure correct tuple format
                ref_table, fk_column, pk_column = fk
                G.add_edge(table, ref_table, label=f"{fk_column} → {pk_column}")

    # Set a good figure size for UI
    plt.figure(figsize=(5, 3))  # Reduced size for better UI fit

    # Use better layout for clear visualization
    pos = nx.kamada_kawai_layout(G)  # More readable structure

    # Draw the graph with enhanced visuals
    nx.draw(
        G, pos, with_labels=True, node_color="lightblue", edge_color="gray", 
        node_size=2500, font_size=9, font_weight="bold", linewidths=1.5
    )

    # Add edge labels for relationships
    edge_labels = {(u, v): d["label"] for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)

    # Add a title for clarity
    plt.title("Entity-Relationship Diagram", fontsize=10, fontweight="bold")

    # Display in Streamlit
    st.pyplot(plt)


# Display ER Diagram if selected
if show_er:
    st.markdown("### 🏗️ Entity-Relationship Diagram")
    generate_er_diagram(schema_details)

# Detect table relationships dynamically
def detect_relationships():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    relationships = {}

    for table in tables:
        cursor.execute(f"PRAGMA foreign_key_list({table})")
        fk_info = cursor.fetchall()
        
        fk_relations = []
        for fk in fk_info:
            fk_relations.append((fk[2], fk[3], fk[4]))  # (Referencing Table, Column, Referenced Column)
        
        relationships[table] = fk_relations

    conn.close()
    return relationships

table_relationships = detect_relationships()

# User selects tables
tables = list(table_relationships.keys())
selected_tables = st.multiselect("Select tables for querying:", tables)

# Generate JOIN queries dynamically based on relationships
def generate_join_query(selected_tables):
    if len(selected_tables) < 2:
        return f"SELECT * FROM {selected_tables[0]}" if selected_tables else ""

    base_table = selected_tables[0]
    query = f"SELECT * FROM {base_table}"
    joins = []

    for table in selected_tables[1:]:
        for parent_table, parent_column, child_column in table_relationships.get(table, []):
            if parent_table in selected_tables:
                join_clause = f" JOIN {table} ON {base_table}.{parent_column} = {table}.{child_column}"
                joins.append(join_clause)

    query += " ".join(joins)
    return query

# Function to execute query dynamically based on schema
def execute_query_dynamically(query):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        df_result = pd.DataFrame(result, columns=column_names)
        conn.close()
        return df_result  # Return DataFrame directly
    except Exception as e:
        conn.close()
        return f"❌ Error executing query: {e}"

# Fetch table schema details
def get_table_schema():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    schema_info = {}

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]

    for table in tables:
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        schema_info[table] = [(col[1], col[2]) for col in columns]  # (Column Name, Data Type)

    conn.close()
    return schema_info

def generate_sql_from_natural_query(user_query, selected_tables):
    if not selected_tables:
        return "⚠️ Please select at least one table."

    schema_info = get_table_schema()
    base_query = generate_join_query(selected_tables)

    schema_details = "\n".join([f"{table}: {schema_info[table]}" for table in selected_tables])

    prompt = f"""
    You are an SQL expert. Generate an optimized SQLite query for the following user request: "{user_query}".
    Ensure correct JOINs and use only existing columns.

    Database Schema:
    {schema_details}
    
    Table Relationships:
    {table_relationships}
    
    Base Query: {base_query}

    - Validate the SQL syntax for SQLite.
    - Ensure all selected columns exist in the schema.
    - Generate queries that dynamically adapt based on table structures.
    - If a column or table is missing, suggest alternative queries.

    Provide only the final SQL query as the response.
    """

    response = llm.invoke(prompt)
    
    if isinstance(response, str):
        return response.strip()  
    elif hasattr(response, "content"):  
        return response.content.strip()
    else:
        return "Error: Unexpected response format"



# Function to display results dynamically
def display_query_results(query):
    result = execute_query_dynamically(query)
    
    if isinstance(result, pd.DataFrame) and not result.empty:
        st.write("📊 **Query Results:**")
        st.dataframe(result, use_container_width=True)
    else:
        st.write("❌ No data found or an error occurred.")

# User Query Input
user_query = st.text_input("💬 Type your SQL question:")
if user_query:
    query = generate_sql_from_natural_query(user_query, selected_tables)
        # Display query in a code box with copy option
    st.write("📝 **Generated SQL Query:**")
    query_code = f"```sql\n{query}\n```"
    st.code(query, language="sql")  # Display SQL query in a formatted code box

    # Add a button to copy the query
    if st.button("📋 Copy Query"):
        pyperclip.copy(query)  # Copy query to clipboard
        st.success("Query copied to clipboard!")

    display_query_results(query)

# Follow-up question
bot_query = st.text_input("🤖 Ask me anything (related to data, SQL, or insights):")
if bot_query:
    with st.spinner("AI is analyzing..."):
        context = f"""
        - Last Generated SQL Query: {query}
        - Database Tables: {selected_tables}
        - User Question: {bot_query}
        """
        bot_response = llm.predict(f"Given this context, analyze and answer the user query:\n{context}")
        st.write("**Bot's Answer:**")
        st.write(bot_response)

