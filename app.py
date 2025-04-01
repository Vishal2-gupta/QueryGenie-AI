import streamlit as st
import subprocess

# Set page configuration
st.set_page_config(page_title="QueryGenie - AI SQL Assistant", layout="wide")

# Custom CSS for styling
st.markdown("""
    <style>
        body {
       
            background-color: #f4f7fa;
            font-family: 'Arial', sans-serif;
        }
        .main-container {
            background: url('https://source.unsplash.com/1600x900/?technology,database') no-repeat center center;
            background-size: cover;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0px 10px 15px rgba(0, 0, 0, 0.1);
            margin-top: 30px;
        }
        h1 {
            color: #4CAF50;
            font-size: 40px;
            text-align: center;
            margin-bottom: 20px;
        }
        .agent-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0px 5px 10px rgba(0, 0, 0, 0.1);
            text-align: center;
            transition: transform 0.3s ease-in-out;
        }
        .agent-card:hover {
            transform: scale(1.05);
        }
        .icon {
            font-size: 50px;
            color: #4CAF50;
            margin-bottom: 10px;
        }
        .cta-button {
            background-color: #4CAF50;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            text-align: center;
            font-size: 18px;
            display: block;
            margin: 20px auto;
        }
        .cta-button:hover {
            background-color: #45a049;
        }
    </style>
""", unsafe_allow_html=True)

# Sidebar Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["About QueryGenie", "Run QueryGenie Agent"])

if page == "About QueryGenie":
    st.title("About QueryGenie - AI SQL Assistant")
    st.write("""
        QueryGenie is an AI-powered assistant that helps you convert natural language questions into SQL queries.
        With just a few steps, you can upload your dataset, ask questions, and get results in real-time.
        It's designed to make querying databases more accessible, intuitive, and efficient.
    """)

    st.header("How to Use QueryGenie?")
    st.markdown("""
1. **Upload your dataset** (CSV, Excel, JSON).  
2. **Ask your question in natural language**, such as:  
   - *"Show me the top 10 customers by revenue."*  
   - *"Find the total sales for the last quarter grouped by region."*  
   - *"List all transactions above $5000 from the last month."*  
3. **View the SQL query generated** by the AI.  
4. The assistant will also **optimize and check the query for security risks**.  
5. **Execute the query** and see results in the form of tables and visualizations.  
6. **Ask follow-up questions** to refine or drill down into your data, such as:  
   - *"Now group the results by product category."*  
   - *"Filter only high-value transactions above $10,000."*  
7. **MultiTable Support**: Effortlessly handle complex queries spanning multiple tables, ensuring seamless data integration and analysis.  
8. **BigQuery Integration**: Seamlessly connect with Google Cloud BigQuery datasets, allowing users to generate SQL queries and perform large-scale data analysis in real-time.  
9. **Azure Cosmos DB Agent**: Use AI to generate **NoSQL queries** for Cosmos DB, infer schemas dynamically, and refine queries interactively.  
10. **AWS Redshift Querying**: Connect to Redshift for efficient data warehousing and real-time analytics across massive datasets.  
11. **SQL Query Translator**: Convert SQL queries from one dialect to another (e.g., MySQL to PostgreSQL, Redshift to Snowflake) for seamless database interoperability.  
12. **Conversational Querying**: Interact dynamically with your data, ask iterative questions, and refine results in an intuitive manner.  
""")

    st.header("Features:")
    st.markdown("""
- **AI-driven SQL Query Generation**: Convert natural language into SQL queries.  
- **Query Optimization and Security Checks**: Ensure efficient and secure queries.  
- **MultiTable Support**: Handle complex queries across multiple tables.  
- **BigQuery Integration**: Connect with Google Cloud BigQuery for large-scale data processing.  
- **Azure Cosmos DB Agent**: AI-powered **NoSQL query generation**, **schema inference**, and **adaptive query refinement**.  
- **AWS Redshift Querying**: Execute and optimize queries in Redshift for scalable analytics.  
- **SQL Query Translator**: Convert SQL between **different database dialects** effortlessly.  
- **Conversational Querying**: Ask follow-up questions and refine results dynamically.  
- **Data Visualization**: Get insights through **Bar Charts**, **Line Charts**, and **Pie Charts**.  
""")

elif page == "Run QueryGenie Agent":
    st.title("SQL Query MultiAgent")
   # First row - 3 agents
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<div class="agent-card">', unsafe_allow_html=True)
        st.markdown('<div style="font-size:32px;">🛢️</div>', unsafe_allow_html=True)  
        st.subheader("API Agent")  
        st.write("Handles API-based and uploaded dataset SQL queries efficiently.")  
        if st.button("Run API Agent"):
            subprocess.run(["streamlit", "run", "api.py"])
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="agent-card">', unsafe_allow_html=True)
        st.markdown('<div style="font-size:32px;">📂</div>', unsafe_allow_html=True) 
        st.subheader("MultiTable Agent")
        st.write("Works with multiple tables for complex queries efficiently.")
        if st.button("Run MultiTable Agent"):
            subprocess.run(["streamlit", "run", "multitable.py"])
        st.markdown("</div>", unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="agent-card">', unsafe_allow_html=True)
        st.markdown('<div style="font-size:32px;">🧠</div>', unsafe_allow_html=True) 
        st.subheader("Query Translator Agent")
        st.write("Easily translate SQL queries across multiple database dialects.")
        if st.button("Run Query Translator Agent"):
            subprocess.run(["streamlit", "run", "querytranslator.py"])
        st.markdown("</div>", unsafe_allow_html=True)




    col4, col5, col6 = st.columns(3)
    with col4:
        st.markdown('<div class="agent-card">', unsafe_allow_html=True)
        st.markdown('<div style="font-size:32px;">☁️</div>', unsafe_allow_html=True) 
        st.subheader("BigQuery Agent")
        st.write("Optimized for Google BigQuery dataset queries efficiently.")
        if st.button("Run BigQuery Agent"):
            subprocess.run(["streamlit", "run", "bigquery.py"])
        st.markdown("</div>", unsafe_allow_html=True)

  

    with col5:
        st.markdown('<div class="agent-card">', unsafe_allow_html=True)
        st.markdown('<div style="font-size:32px;">🔷</div>', unsafe_allow_html=True)  
        st.subheader("Azure Cosmos DB Agent")  
        st.write("Handles NoSQL queries efficiently using Azure Cosmos DB.")  
        if st.button("Run Azure Cosmos DB Agent"):
            subprocess.run(["streamlit", "run", "azurecosmo.py"])
        st.markdown("</div>", unsafe_allow_html=True)

    with col6:
        st.markdown('<div class="agent-card">', unsafe_allow_html=True)
        st.markdown('<div style="font-size:32px;">🟧</div>', unsafe_allow_html=True)  
        st.subheader("AWS Redshift Agent")  
        st.write("Processes large-scale SQL queries using AWS Redshift efficiently.")  
        if st.button("Run AWS Redshift Agent"):
            subprocess.run(["streamlit", "run", "awsredshift.py"])
        st.markdown("</div>", unsafe_allow_html=True)




# # First row
# st.markdown('<div style="font-size:32px;">🛢️</div>', unsafe_allow_html=True)
# st.subheader("API Agent")
# st.write("Handles API-based and uploaded dataset SQL queries efficiently.")
# if st.button("Run API Agent"):
#     subprocess.run(["streamlit", "run", "api.py"])
# st.markdown("---")

# # Second row
# st.markdown('<div style="font-size:32px;">📂</div>', unsafe_allow_html=True)
# st.subheader("MultiTable Agent")
# st.write("Works with multiple tables for complex queries efficiently.")
# if st.button("Run MultiTable Agent"):
#     subprocess.run(["streamlit", "run", "multitable.py"])
# st.markdown("---")

# # Third row
# st.markdown('<div style="font-size:32px;">☁️</div>', unsafe_allow_html=True)
# st.subheader("BigQuery Agent")
# st.write("Optimized for Google BigQuery dataset queries efficiently.")
# if st.button("Run BigQuery Agent"):
#     subprocess.run(["streamlit", "run", "bigquery.py"])
# st.markdown("---")

# # Fourth row
# st.markdown('<div style="font-size:32px;">🔷</div>', unsafe_allow_html=True)
# st.subheader("Azure Cosmos DB Agent")
# st.write("Handles NoSQL queries efficiently using Azure Cosmos DB.")
# if st.button("Run Azure Cosmos DB Agent"):
#     subprocess.run(["streamlit", "run", "azurecosmo.py"])
# st.markdown("---")

# # Fifth row
# st.markdown('<div style="font-size:32px;">🛢️</div>', unsafe_allow_html=True)
# st.subheader("AWS Redshift Agent")
# st.write("Processes large-scale SQL queries using AWS Redshift efficiently.")
# if st.button("Run AWS Redshift Agent"):
#     subprocess.run(["streamlit", "run", "awsredshift.py"])
# st.markdown("---")