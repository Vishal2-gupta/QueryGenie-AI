import streamlit as st
import openai
import sqlglot
from sqlglot import transpile
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage

# OpenAI API Key (Replace with your key or load from env)
OPENAI_API_KEY = "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"

# Initialize OpenAI Model
chat_model = ChatOpenAI(openai_api_key=OPENAI_API_KEY, model_name="gpt-4")

# Streamlit UI
st.set_page_config(page_title="SQL Query Translator", layout="wide")

st.title("🧠 QueryGenie - AI-Powered SQL Translator ")

# Sidebar for dialect selection
st.sidebar.header("🔄 SQL Dialects")
dialects = {
    "MySQL": "mysql",
    "PostgreSQL": "postgres",
    "T-SQL (SQL Server)": "tsql",
    "SQLite": "sqlite",
    "NoSQL (MongoDB)": "mongodb"
}
selected_dialects = st.sidebar.multiselect("Select target dialects:", list(dialects.keys()), default=["PostgreSQL"])

# User Input for SQL Query
st.subheader("💡 Paste Your SQL Query")
user_query = st.text_area("Enter SQL Query:", height=150)

if st.button("Translate Query"):
    if user_query.strip():
        translations = {}

        for db, dialect in dialects.items():
            if dialect == "mongodb":
                # Use OpenAI GPT-4 for MongoDB Translation
                mongo_prompt = f"Convert this SQL query to MongoDB query:\n\n{user_query}"
                response = chat_model([SystemMessage(content=mongo_prompt)])
                translations[db] = response.content
            else:
                try:
                    translated_query = transpile(user_query, read="mysql", write=dialect)[0]
                    translations[db] = translated_query
                except Exception as e:
                    translations[db] = f"⚠️ Translation Error: {str(e)}"

        # Display Translated Queries
        st.subheader("📝 Translated Queries")
        for db, translated_sql in translations.items():
            if db in selected_dialects:
                st.markdown(f"**{db} Query:**")
                st.code(translated_sql, language="sql" if db != "NoSQL (MongoDB)" else "json")
    else:
        st.warning("⚠️ Please enter an SQL query first.")

# Chatbot Section
st.subheader("🤖 SQL Assistant Bot")
chat_input = st.text_input("Ask anything about your SQL query:", "")

if st.button("Ask Bot"):
    if chat_input.strip():
        messages = [
            SystemMessage(content="You are an SQL expert. Explain the query and answer user questions."),
            HumanMessage(content=f"User Query: {user_query}\nUser Question: {chat_input}")
        ]
        response = chat_model(messages)
        st.markdown("### 🤖 AI Response:")
        st.write(response.content)
    else:
        st.warning("⚠️ Please enter a question for the bot.")
