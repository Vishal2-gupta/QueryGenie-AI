import streamlit as st
import os
from azure.cosmos import CosmosClient, exceptions
from langchain_openai import ChatOpenAI
import pandas as pd

# 🔹 Set your OpenAI API key
os.environ["OPENAI_API_KEY"] = "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"

st.set_page_config(page_title="QueryGenie - Azure Cosmos DB Assistant", layout="wide")
st.title("🔍 QueryGenie - AI-Powered Cosmos DB Assistant")

# Store session state for connection details & conversation history
if "cosmos_config" not in st.session_state:
    st.session_state.cosmos_config = None
if "query_history" not in st.session_state:
    st.session_state.query_history = []
if "chat_context" not in st.session_state:
    st.session_state.chat_context = ""

# Step 1: User Inputs Azure Cosmos DB Credentials
with st.form("cosmos_credentials_form"):
    st.subheader("🔐 Enter Your Azure Cosmos DB Credentials")
    endpoint = st.text_input("Cosmos DB Endpoint URI", help="Find it in your Azure portal")
    primary_key = st.text_input("Primary Key", type="password", help="Find it in your Azure portal")
    database_name = st.text_input("Database Name", help="Enter your Cosmos DB database name")
    container_name = st.text_input("Container Name", help="Enter the container name")
    submit_button = st.form_submit_button("🔗 Connect to Cosmos DB")
    
    if submit_button:
        if not endpoint or not primary_key or not database_name or not container_name:
            st.error("⚠️ Please fill in all required fields.")
        else:
            try:
                client = CosmosClient(endpoint, primary_key)
                database = client.get_database_client(database_name)
                container = database.get_container_client(container_name)
                st.session_state.cosmos_config = {
                    "endpoint": endpoint,
                    "primary_key": primary_key,
                    "database_name": database_name,
                    "container_name": container_name
                }
                st.success("✅ Connected Successfully! You can now enter your queries below.")
            except exceptions.CosmosHttpResponseError as e:
                st.error(f"❌ Connection Failed: {str(e)}")

schema_details = {}

# Step 2: Table Preview Functionality
if st.session_state.cosmos_config:
    config = st.session_state.cosmos_config
    client = CosmosClient(config["endpoint"], config["primary_key"])
    database = client.get_database_client(config["database_name"])
    container = database.get_container_client(config["container_name"])
    
    st.subheader("📊 Preview Table Data & Schema")
    show_table = st.checkbox("🔍 Show Table Data")
    show_schema = st.checkbox("📑 Show Table Schema")
    
    if show_table:
        try:
            query = f"SELECT * FROM c"
            data = list(container.query_items(query=query, enable_cross_partition_query=True))
            if data:
                import pandas as pd
                df = pd.DataFrame(data)
                st.dataframe(df)
            else:
                st.info("ℹ️ No data available in this container.")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
    
    if show_schema:
        try:
            query = f"SELECT * FROM c OFFSET 0 LIMIT 1"
            data = list(container.query_items(query=query, enable_cross_partition_query=True))
            if data:
                sample_record = data[0]
                schema_details = {key: type(value).__name__ for key, value in sample_record.items()}
                schema_df = pd.DataFrame(list(schema_details.items()), columns=["Column Name", "Data Type"])
                st.dataframe(schema_df)
            else:
                st.info("ℹ️ No data available to infer schema.")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# Step 2: Connect to Cosmos DB and Enable AI Querying
if st.session_state.cosmos_config:
    config = st.session_state.cosmos_config
    client = CosmosClient(config["endpoint"], config["primary_key"])
    database = client.get_database_client(config["database_name"])
    container = database.get_container_client(config["container_name"])
    llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")

    # Step 3: User Query Input
    st.subheader("💬 Ask Your Query in Natural Language")
    query_prompt = st.text_input("Enter your question (e.g., 'Get all orders where amount > 100')")

    if st.button("🚀 Run Query"):
        if not query_prompt:
            st.error("⚠️ Please enter a query!")
        else:
            try:
                sql_prompt = f"""
Generate a valid NoSQL query for Azure Cosmos DB using the SQL API.
- Use the provided schema to correctly reference attribute names, automatically correcting any mismatches between user input and the schema.
- Do NOT use 'AS' for aliasing, as it is not supported in Cosmos DB SQL API.
- Ensure the query includes a VALUE clause before aggregate functions where necessary.
- Format the query correctly for execution in Cosmos DB.
- If the user requests a non-existent field, intelligently map it to the closest relevant field from the schema using semantic similarity.
- Maintain proper query structure, ensuring that aggregate functions (e.g., COUNT, SUM, AVG) use VALUE for correct execution.

Schema Details (Reference):  
{schema_details}

User Query:  
{query_prompt}

Generated NoSQL Query:
"""
                sql_query = llm.predict(sql_prompt).strip()
                if not sql_query.lower().startswith("select"):
                    st.error("❌ AI-generated query is invalid. Please try refining your input.")
                else:
                    st.info(f"📝 Generated NoSQL Query:\n```sql\n{sql_query}\n```")
                    
                    # Execute query
                    query_result = container.query_items(query=sql_query, enable_cross_partition_query=True)
                    data = list(query_result)
                    
                    st.success("✅ Query executed successfully!")
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
Provide an updated NoSQL query or explanation.
"""
                follow_up_response = llm.predict(bot_prompt).strip()
                st.info(f"🤖 AI Response:\n{follow_up_response}")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# Step 3: CRUD Operations
if st.session_state.cosmos_config:
    config = st.session_state.cosmos_config
    client = CosmosClient(config["endpoint"], config["primary_key"])
    database = client.get_database_client(config["database_name"])
    container = database.get_container_client(config["container_name"])
    
    st.subheader("🛠️ Perform CRUD Operations")
    operation = st.selectbox("Select Operation", ["SELECT", "INSERT", "DELETE","UPDATE"])
    user_query = st.text_area("Enter your Query")
    
    if st.button("🚀 Execute Query"):
        if not user_query:
            st.error("⚠️ Please enter a query!")
        else:
            try:
                sql_prompt = f"""
                Generate a valid NoSQL query for Cosmos DB using the SQL API.
                User Query: {user_query}
                """
                sql_query = llm.predict(sql_prompt).strip()
                st.info(f"📝 AI-Generated Query:\n```sql\n{sql_query}\n```")
                
                if operation == "SELECT":
                    results = list(container.query_items(query=sql_query, enable_cross_partition_query=True))
                    st.success("✅ Query executed successfully!")
                    st.dataframe(results)
                
                elif operation == "INSERT":
                    insert_data_prompt = f"""
                    Extract JSON data from this SQL query:
                    {sql_query}
                    """
                    json_data = llm.predict(insert_data_prompt).strip()
                    container.create_item(body=eval(json_data))
                    st.success("✅ Data inserted successfully!")
                elif operation == "DELETE":
                    container.query_items(query=sql_query, enable_cross_partition_query=True)
                    st.success("✅ Data deleted successfully!")   
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")



