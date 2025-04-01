import os
import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import requests
from langchain_openai import ChatOpenAI
from langchain_community.utilities.sql_database import SQLDatabase
from langgraph.graph import StateGraph
import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
from PIL import Image


# Ensure database path
db_path = "my_demo.db"
if not os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    conn.close()

st.set_page_config(page_title="QueryGenie - AI SQL Assistant", layout="wide")

# Header with a bot-like feel
st.markdown("<h1 style='text-align: center;'>🤖 QueryGenie - AI SQL Assistant</h1>", unsafe_allow_html=True)

# Sidebar logo and description
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/4712/4712027.png", width=100)
st.sidebar.markdown("### Your AI-powered SQL Assistant")
st.sidebar.markdown("Upload your dataset, provide an API URL, or ask SQL queries in natural language.")

# Upload File
uploaded_file = st.file_uploader("📂 Upload CSV, Excel, or JSON:", type=["csv", "xlsx", "json"])

# Input API URL
api_url = st.text_input("🌐 Enter API URL (optional):", "")

def generate_schema(df):
    """Generate a table schema from a dataframe."""
    schema = [(col, str(df[col].dtype)) for col in df.columns]
    return schema

def generate_er_diagram(table_name, schema, output_path="er_diagram.png"):
    """Generate and save ER diagram as a PNG."""
    G = nx.DiGraph()

    # Add table node
    G.add_node(table_name, color="#3498db", size=4500)  # Blue

    # Add column nodes and edges
    for column, dtype in schema:
        G.add_node(column, color="#2ecc71", size=4500)  # Green
        G.add_edge(table_name, column, label=dtype)

    # Plot ER Diagram
    plt.figure(figsize=(9, 6))  # Reduce figure size
    pos = nx.spring_layout(G, seed=42)

    # Extract node colors & sizes
    node_colors = [G.nodes[n]["color"] for n in G.nodes]
    node_sizes = [G.nodes[n]["size"] for n in G.nodes]

    # Draw nodes & edges
    nx.draw(G, pos, with_labels=True, node_color=node_colors, node_size=node_sizes, edge_color="gray", font_size=10, font_weight="bold")
    edge_labels = {(u, v): d["label"] for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=9, font_color="black")

    # Save as PNG
    plt.savefig(output_path, format="png", bbox_inches="tight", dpi=300)
    plt.close()

def display_er_diagram(image_path):
    """Resize and display ER diagram with proper size."""
    img = Image.open(image_path)
    img = img.resize((600, 400))  # Resize image to a medium size
    st.image(img, caption="📌 ER Diagram", use_container_width=False)  # Remove deprecated param


if uploaded_file is not None:
    # Process uploaded file as before
    try:
        # Load the dataset
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(".xlsx"):
            df = pd.read_excel(uploaded_file)
        elif uploaded_file.name.endswith(".json"):
            df = pd.read_json(uploaded_file)
        else:
            st.error("Unsupported file format.")
            st.stop()

        # Show uploaded data in a scrollable format
        st.write("📊 **Preview of Uploaded Data:**")
        st.dataframe(df, use_container_width=True)

        # Save dataset in SQLite
        table_name = uploaded_file.name.split('.')[0]
        conn = sqlite3.connect(db_path)
        df.to_sql(table_name, conn, index=False, if_exists="replace")
        conn.close()


                # ✅ Extract Schema
        schema = generate_schema(df)

        # ✅ Show Schema (Optional)
        if st.checkbox("📜 Show Table Schema"):
            schema_df = pd.DataFrame(schema, columns=["Column Name", "Data Type"])
            st.table(schema_df)

        # ✅ Generate & Show ER Diagram as PNG
        if st.checkbox("📊 Show ER Diagram"):
            er_diagram_path = "er_diagram.png"
            generate_er_diagram(table_name, schema, er_diagram_path)
            display_er_diagram(er_diagram_path)


    except Exception as e:
        st.error(f"Error processing file: {e}")

elif api_url:
    # Fetch data from the provided API URL
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()  # Assuming the API returns JSON data

        # Convert fetched data to a DataFrame
        df = pd.json_normalize(data)

        # Show fetched data in a scrollable format
        st.write("📊 **Preview of Fetched Data from API:**")
        st.dataframe(df, use_container_width=True)

        # Save dataset in SQLite
        table_name = "api_data"
        conn = sqlite3.connect(db_path)
        df.to_sql(table_name, conn, index=False, if_exists="replace")
        conn.close()

                # ✅ Extract Schema
        schema = generate_schema(df)

        # ✅ Show Schema (Optional)
        if st.checkbox("📜 Show Table Schema"):
            schema_df = pd.DataFrame(schema, columns=["Column Name", "Data Type"])
            st.table(schema_df)

        # ✅ Generate & Show ER Diagram as PNG
        if st.checkbox("📊 Show ER Diagram"):
            er_diagram_path = "er_diagram.png"
            generate_er_diagram(table_name, schema, er_diagram_path)
            display_er_diagram(er_diagram_path)


    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data from API: {e}")

# Connect LangChain to SQLite
db = SQLDatabase.from_uri(f"sqlite:///{db_path}")

# Initialize OpenAI model
llm = ChatOpenAI(temperature=0, api_key="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")

# Define multi-agent execution flow
def generate_sql(state):
    user_input = state["query"]
    sql_query = llm.predict(f"Convert this to an SQL query: {user_input} based on the table {state['table_name']}")
    return {"query": sql_query, "table_name": state["table_name"]}

def optimize_query(state):
    optimized_query = llm.predict(f"Optimize this SQL query: {state['query']}")
    return {"query": state["query"], "optimized_query": optimized_query, "table_name": state["table_name"]}

def secure_query(state):
    secure_sql = llm.predict(f"Check this query for security risks: {state['optimized_query']}")
    return {"query": state["query"], "optimized_query": state["optimized_query"], "secure_query": secure_sql, "table_name": state["table_name"]}

def execute_query(state):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        table_name = state.get("table_name", None)
        if not table_name:
            raise ValueError("No table name provided")

        query = state["query"].replace("<table_name>", table_name)
        cursor.execute(query)
        result = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]  # Get column names
        conn.close()
        return {"query": state["query"], "optimized_query": state["optimized_query"], "secure_query": state["secure_query"], "result": result, "columns": column_names, "table_name": table_name}
    except Exception as e:
        return {"query": state["query"], "optimized_query": state["optimized_query"], "secure_query": state["secure_query"], "result": f"Error: {e}", "columns": [], "table_name": table_name}

# Define Multi-Agent Workflow
workflow = StateGraph(dict)
workflow.add_node("Generate SQL", generate_sql)
workflow.add_node("Optimize SQL", optimize_query)
workflow.add_node("Secure Query", secure_query)
workflow.add_node("Execute Query", execute_query)

workflow.add_edge("Generate SQL", "Optimize SQL")
workflow.add_edge("Optimize SQL", "Secure Query")
workflow.add_edge("Secure Query", "Execute Query")

workflow.set_entry_point("Generate SQL")
langgraph_agent = workflow.compile()

# Chat message container
chat_container = st.container()

# User Query Input (Text)
if "user_query" not in st.session_state:
    st.session_state.user_query = ""

user_query = st.text_input("💬 Type your SQL question:", value=st.session_state.user_query)

if user_query:
    st.session_state.user_query = user_query  # Save query in session

    with st.spinner("🤖 Thinking..."):
        try:
            # Invoke LangGraph agent
            result_state = langgraph_agent.invoke({"query": user_query, "table_name": table_name})

            with chat_container:
                st.chat_message("user", avatar="👤").write(user_query)

                # Display results
                bot_response = f"**SQL Query:**\n```sql\n{result_state['query']}\n```\n"
                bot_response += f"**Optimized Query:**\n```sql\n{result_state['optimized_query']}\n```\n"
                bot_response += f"**Secured Query:**\n```sql\n{result_state['secure_query']}\n```\n"
                st.chat_message("assistant", avatar="🤖").write(bot_response)

                # Display Execution Results
                st.write("**Execution Result:**")
                result_data = result_state.get("result", [])
                column_names = result_state.get("columns", [])

                if isinstance(result_data, list) and len(result_data) > 0:
                    # Convert to DataFrame
                    df_result = pd.DataFrame(result_data, columns=column_names)
                    st.dataframe(df_result)

                    # Visualization Section
                    st.write("📊 **Visualize Your Data**")
                    chart_type = st.selectbox("Choose chart type:", ["Bar Chart", "Line Chart", "Pie Chart"])

                    if len(column_names) >= 2:  # Ensure we have at least 2 columns for visualization
                        x_axis = st.selectbox("Select X-axis:", column_names)
                        y_axis = st.selectbox("Select Y-axis:", column_names)

                        if chart_type == "Bar Chart":
                            fig = px.bar(df_result, x=x_axis, y=y_axis)
                            st.plotly_chart(fig)

                        elif chart_type == "Line Chart":
                            fig = px.line(df_result, x=x_axis, y=y_axis)
                            st.plotly_chart(fig)

                        elif chart_type == "Pie Chart":
                            fig = px.pie(df_result, names=x_axis, values=y_axis)
                            st.plotly_chart(fig)

                    # Follow-up question
                    bot_query = st.text_input("Ask me anything (related to data, SQL, or insights):")
                    if bot_query:
                        with st.spinner("AI is analyzing..."):
                            context = f"""
                            - SQL Query: {result_state['secure_query']}
                            - Optimized SQL: {result_state['optimized_query']}
                            - Executed Result: {result_state['result']}
                            - Data Preview: {df.to_dict()}
                            - User Question: {bot_query}
                            """
                            bot_response = llm.predict(f"Answer the user based on this context:\n{context}")
                            st.write("**Bot's Answer:**")
                            st.write(bot_response)

        except Exception as e:
            st.error(f"Error: {e}")