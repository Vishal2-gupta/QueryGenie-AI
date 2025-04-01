import streamlit as st
import os
import psycopg2
import pandas as pd
from langchain_openai import ChatOpenAI

# Set OpenAI API Key
os.environ["OPENAI_API_KEY"] = "your-openai-api-key"

st.set_page_config(page_title="QueryGenie - AI Redshift Assistant", layout="wide")
st.title("🚀 QueryGenie - AI-Powered AWS Redshift Assistant")

# Store session state for connection details & conversation history
if "redshift_config" not in st.session_state:
    st.session_state.redshift_config = None
if "query_history" not in st.session_state:
    st.session_state.query_history = []
if "chat_context" not in st.session_state:
    st.session_state.chat_context = ""

# Step 1: User Inputs AWS Redshift Credentials
with st.form("aws_credentials_form"):
    st.subheader("🔐 Enter Your AWS Redshift Credentials")
    host = st.text_input("Redshift Cluster Endpoint", help="Example: my-cluster.xxxxxxx.region.redshift.amazonaws.com")
    port = st.text_input("Port", value="5439", help="Default: 5439")
    database = st.text_input("Database Name", help="Enter your Redshift database name")
    user = st.text_input("Username")
    password = st.text_input("Password", type="password")
    submit_button = st.form_submit_button("🔗 Connect to Redshift")

    if submit_button:
        if not host or not port or not database or not user or not password:
            st.error("⚠️ Please fill in all required fields.")
        else:
            st.session_state.redshift_config = {
                "host": host,
                "port": port,
                "database": database,
                "user": user,
                "password": password
            }
            st.success("✅ Connected Successfully! You can now enter your queries below.")

# Step 2: Connect to Redshift and Enable AI Querying
if st.session_state.redshift_config:
    config = st.session_state.redshift_config
    conn = psycopg2.connect(
        host=config["host"],
        port=config["port"],
        dbname=config["database"],
        user=config["user"],
        password=config["password"]
    )
    cursor = conn.cursor()
    llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")

    # Step 3: User Query Input
    st.subheader("💬 Ask Your Query in Natural Language")
    query_prompt = st.text_input("Enter your question (e.g., 'Show total sales for 2023')")

    if st.button("🚀 Run Query"):
        if not query_prompt:
            st.error("⚠️ Please enter a query!")
        else:
            try:
                sql_prompt = f"""
Generate a valid SQL query for AWS Redshift.
Use standard SQL syntax.
User Query: {query_prompt}
SQL Query:
"""
                sql_query = llm.predict(sql_prompt).strip()

                if not sql_query.lower().startswith("select"):
                    st.error("❌ AI-generated query is invalid. Please try refining your input.")
                else:
                    st.info(f"📝 Generated SQL Query:\n```sql\n{sql_query}\n```")
                    cursor.execute(sql_query)
                    rows = cursor.fetchall()
                    colnames = [desc[0] for desc in cursor.description]
                    df = pd.DataFrame(rows, columns=colnames)
                    
                    st.success("✅ Query executed successfully!")
                    st.dataframe(df)

                    # Store query context
                    st.session_state.query_history.append((query_prompt, sql_query, df.head().to_dict()))
                    st.session_state.chat_context = f"Previous Query: {query_prompt}\nSQL Query:\n{sql_query}\nResults: {df.head().to_dict()}..."
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

    # Step 4: Follow-Up Bot Interaction
    st.subheader("🤖 Follow-up AI Assistant")
    follow_up_prompt = st.text_input("Ask a follow-up question about the results")

    if st.button("💬 Ask Follow-up"):
        if not follow_up_prompt:
            st.error("⚠️ Please enter a follow-up question!")
        else:
            try:
                bot_prompt = f"""
Based on the following previous query and results:
{st.session_state.chat_context}

User Follow-Up: {follow_up_prompt}
Provide an updated SQL query or explanation.
"""
                follow_up_response = llm.predict(bot_prompt).strip()
                st.info(f"🤖 AI Response:\n{follow_up_response}")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

    cursor.close()
    conn.close()
