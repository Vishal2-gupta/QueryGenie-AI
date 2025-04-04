import streamlit as st
import subprocess
from streamlit_extras.colored_header import colored_header

# Page Configuration
st.set_page_config(page_title="QueryGenie AI", page_icon="🤖", layout="wide")

# Custom Styling
def set_ui_styles():
    st.markdown(
        """
        <style>
        /* Hide Streamlit default elements */
        header, footer, .st-emotion-cache-z5fcl4, .st-emotion-cache-1kyxreq {display: none;}

        /* Background */
        body {
            background: url('https://source.unsplash.com/1600x900/?ai,technology') no-repeat center center fixed;
            background-size: cover;
            font-family: 'Poppins', sans-serif;
            color: white;
        }

        /* Sidebar Styling */
        section[data-testid="stSidebar"] {
            background-color: #87CEEB !important; /* Sky Blue */
        }

        /* Sidebar Image */
        .sidebar-img {
            display: block;
            margin: auto;
            width: 80%;
            border-radius: 12px;
            margin-bottom: 15px;
        }

        /* Title */
        .main-title {
            text-align: center;
            color: #ffffff;
            font-size: 42px;
            font-weight: bold;
            margin-bottom: 10px;
        }

        /* Subtitle */
        .sub-title {
            text-align: center;
            color: #f0f0f0;
            font-size: 18px;
            margin-bottom: 20px;
        }

        /* Divider */
        .divider {
            border: 2px solid #007BFF; 
            margin: 15px 0;
        }

        /* Feature Cards */
        .feature-card {
            background: rgba(255, 255, 255, 0.12);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            min-height: 160px;
            box-shadow: 0 5px 10px rgba(0, 0, 0, 0.3);
            transition: transform 0.3s ease-in-out;
            margin: 10px;
        }

        .feature-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 20px rgba(0, 102, 255, 0.7);
        }

        /* Buttons */
        .stButton>button {
            background: linear-gradient(135deg, #6a11cb, #2575fc);
            color: white;
            padding: 12px 25px;
            font-size: 16px;
            font-weight: bold;
            border-radius: 8px;
            border: none;
            transition: all 0.3s;
            width: 100%;
            box-shadow: 0 5px 15px rgba(0, 102, 255, 0.5);
        }

        .stButton>button:hover {
            background: linear-gradient(135deg, #5a0fb4, #1f5de5);
            transform: scale(1.05);
            box-shadow: 0 8px 20px rgba(0, 102, 255, 0.7);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

set_ui_styles()

# Sidebar Navigation
st.sidebar.image("querygenie.jpg", use_container_width=True)
st.sidebar.title("🤖 QueryGenie AI")
st.sidebar.markdown("Your AI-powered database assistant")
st.sidebar.markdown("---")

# Sidebar Menu
nav_selection = st.sidebar.radio("Navigation", ["🏠 Home Page", "📊 Features"])

# Main Homepage Content
if nav_selection == "🏠 Home Page":
    st.markdown("<h1 class='main-title'>🤖 QueryGenie AI</h1>", unsafe_allow_html=True)
    st.markdown("<h3 class='sub-title'>Your AI-powered assistant for automated database interactions</h3>", unsafe_allow_html=True)

    # Blue Divider Line
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # Features Section
    colored_header("🚀 Key Features", color_name="blue-70")

    # Feature List
    feature_list = [
        ("🧠 AI-powered SQL Queries", "Generate SQL queries from natural language effortlessly."),
        ("☁️ Multi-Cloud Support", "Enable seamless integration across multiple cloud providers."),
        ("📂 Data Dependency Mapping", "Visualize and manage data relationships effectively."),
        ("📊 Smart Analytics", "Monitor performance and generate database insights."),
        ("🔗 API Integration", "Seamlessly connect to multiple database APIs with ease."),
        ("💾 DB Migration", "Simplify database migration to modern architectures."),
    ]

    # Display feature cards in a 2-row, 3-column grid layout
    for i in range(0, len(feature_list), 3):
        cols = st.columns(3, gap="large")
        for col, (title, desc) in zip(cols, feature_list[i:i+3]):
            with col:
                st.markdown(
                    f"""
                    <div class="feature-card">
                        <h4>{title}</h4>
                        <p>{desc}</p>
                    </div>
                    """, unsafe_allow_html=True
                )

    # Navigation Buttons (Centered)
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1], gap="large")
    with col1:
        if st.button("🗄️ Run SQL Query Generator"):
            subprocess.run(["streamlit", "run", "app.py"])
    with col2:
        if st.button("📊 Run API Agent"):
            subprocess.run(["streamlit", "run", "api.py"])

    # Footer
    st.markdown("<br><br><h5 style='text-align: center; color: #000000;'>© 2025 QueryGenie AI. All rights reserved.</h5>", unsafe_allow_html=True)

elif nav_selection == "📊 Features":
    st.subheader("📌 Features Overview")
    st.markdown("""
    - **AI-powered SQL Queries**: Generate SQL queries from natural language input.  
    - **Smart Analytics**: Track database performance with real-time insights.  
    - **API Integration**: Connect and query multiple database platforms.  
    - **Query Optimization**: Improve SQL efficiency with AI suggestions.  
    - **Database Migration**: Migrate databases smoothly to modern architectures.  
    - **Data Dependency Mapping**: Visualize data relationships and structure.  
    """)




