import streamlit as st
import os
from google.cloud import bigquery
from langchain_openai import ChatOpenAI

# 🔹 Set your OpenAI API key
os.environ["OPENAI_API_KEY"] = "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"

st.set_page_config(page_title="QueryGenie - AI BigQuery Assistant", layout="wide")
st.title("🔍 QueryGenie - AI-Powered BigQuery Assistant")

# Store session state for connection details & conversation history
if "bigquery_config" not in st.session_state:
    st.session_state.bigquery_config = None
if "query_history" not in st.session_state:
    st.session_state.query_history = []
if "chat_context" not in st.session_state:
    st.session_state.chat_context = ""

# Step 1: User Inputs GCP Credentials
with st.form("gcp_credentials_form"):
    st.subheader("🔐 Enter Your Google Cloud Credentials")
    project_id = st.text_input("Google Cloud Project ID", help="Find it in your GCP Console")
    dataset_id = st.text_input("BigQuery Dataset ID", help="Enter your dataset name")
    table_name = st.text_input("BigQuery Table Name", help="Enter the table name you want to query")
    service_account_json = st.file_uploader("Upload Google Cloud Service Account JSON", type=["json"])
    submit_button = st.form_submit_button("🔗 Connect to BigQuery")
    
    if submit_button:
        if not project_id or not dataset_id or not table_name or not service_account_json:
            st.error("⚠️ Please fill in all required fields.")
        else:
            service_account_path = "service-account-temp.json"
            with open(service_account_path, "wb") as f:
                f.write(service_account_json.read())
            st.session_state.bigquery_config = {
                "project_id": project_id,
                "dataset_id": dataset_id,
                "table_name": table_name,
                "service_account_path": service_account_path
            }
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = service_account_path
            st.success("✅ Connected Successfully! You can now enter your queries below.")


# Step 2: Connect to BigQuery and Show Table Preview & Schema
if st.session_state.bigquery_config:
    config = st.session_state.bigquery_config
    client = bigquery.Client.from_service_account_json(config["service_account_path"])
    full_table_name = f"`{config['project_id']}.{config['dataset_id']}.{config['table_name']}`"

    st.subheader("📊 Table Information")
    show_preview = st.checkbox("Show Table Preview")
    show_schema = st.checkbox("Show Table Schema")
    
    if show_preview:
        st.subheader("🔍 Table Preview")
        preview_query = f"SELECT * FROM {full_table_name} LIMIT 5"
        preview_results = client.query(preview_query).result()
        preview_data = [dict(row) for row in preview_results]
        st.dataframe(preview_data)
    
    if show_schema:
        st.subheader("📋 Table Schema")
        table = client.get_table(full_table_name)
        schema_data = [{"Column Name": field.name, "Type": field.field_type} for field in table.schema]
        st.dataframe(schema_data)


# Step 2: Connect to BigQuery and Enable AI Querying
if st.session_state.bigquery_config:
    config = st.session_state.bigquery_config
    client = bigquery.Client.from_service_account_json(config["service_account_path"])
    llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")

    # Step 3: User Query Input
    st.subheader("💬 Ask Your Query in Natural Language")
    query_prompt = st.text_input("Enter your question (e.g., 'What is the total sales for shipped orders?')")

    if st.button("🚀 Run Query"):
        if not query_prompt:
            st.error("⚠️ Please enter a query!")
        else:
            try:
                full_table_name = f"`{config['project_id']}.{config['dataset_id']}.{config['table_name']}`"
                sql_prompt = f"""
Generate a valid SQL query for BigQuery using the table exactly as provided: {full_table_name}.
Do not modify or repeat the table reference. Use it exactly as shown.
User Query: {query_prompt}
SQL Query:
"""
                sql_query = llm.predict(sql_prompt).strip()
                if not sql_query.lower().startswith("select"):
                    st.error("❌ AI-generated query is invalid. Please try refining your input.")
                else:
                    st.info(f"📝 Generated SQL Query:\n```sql\n{sql_query}\n```")
                    query_job = client.query(sql_query)
                    results = query_job.result()
                    data = [dict(row) for row in results]
                    st.success("✅ Query executed successfully!")
                    # st.write(data)    -----  changes made here
                    st.dataframe(data)
                    
                    # Store query context
                    st.session_state.query_history.append((query_prompt, sql_query, data))
                    st.session_state.chat_context = f"Previous Query: {query_prompt}\nSQL Query:\n{sql_query}\nResults: {data[:2]}..."
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
    
     # Step 5: Row-Based CRUD Operations (NEW FEATURE 🚀)
    st.subheader("📝 Perform Row-Based CRUD Operations")
    crud_prompt = st.text_input("Describe the operation (e.g., 'Insert order 101 for Alice with $500')")

    if st.button("🔄 Execute CRUD Operation"):
        if not crud_prompt:
            st.error("⚠️ Please enter a CRUD operation prompt!")
        else:
            try:
                full_table_name = f"`{config['project_id']}.{config['dataset_id']}.{config['table_name']}`"
                crud_sql_prompt = f"""
Generate a valid SQL query for BigQuery to perform a CRUD operation using the table: {full_table_name}.
User Request: {crud_prompt}
SQL Query:
"""
                crud_sql_query = llm.predict(crud_sql_prompt).strip()
                
                if not crud_sql_query.lower().startswith(("insert", "update", "delete")):
                    st.error("❌ AI-generated query is invalid for CRUD operations. Please try again.")
                else:
                    st.info(f"📝 Generated SQL Query:\n```sql\n{crud_sql_query}\n```")
                    client.query(crud_sql_query)
                    st.success("✅ CRUD operation executed successfully!")
                    
                    # Log the operation
                    st.session_state.query_history.append((crud_prompt, crud_sql_query, "Executed Successfully"))
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
