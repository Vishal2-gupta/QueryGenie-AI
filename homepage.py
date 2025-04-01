import streamlit as st
import base64
import subprocess

# Set page configuration
st.set_page_config(page_title="QueryGenie", page_icon="🔮", layout="wide")

# Function to encode the image to Base64
def get_base64_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

# Load background image (Ensure it's in the same directory)
bg_image_path = "querygenie.jpg"
bg_image_base64 = get_base64_image(bg_image_path)

# Apply custom CSS
st.markdown(
    f"""
    <style>
        /* Full-screen background color */
        .stApp {{
            background: linear-gradient(135deg, #1a1a2e, #16213e);
            height: 100vh;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
        }}

        /* Center Content */
        .main-container {{
            text-align: center;
            max-width: 1000px;
            width: 100%;
            height: 100%;
            margin: auto;
        }}

        /* Animated Text */
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(-20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        .main-title {{
            font-size: 50px;
            font-weight: bold;
            color: #ffffff;
            text-shadow: 3px 3px 8px rgba(0, 0, 0, 0.7);
            animation: fadeIn 1.5s ease-in-out;
        }}

        .sub-title {{
            font-size: 22px;
            color: #f0f0f0;
            text-shadow: 2px 2px 6px rgba(0, 0, 0, 0.7);
            margin-bottom: 20px;
            animation: fadeIn 1.8s ease-in-out;
        }}

        /* Unique Glowing Buttons */
        .stButton>button {{
            background: linear-gradient(135deg, #ff7eb3, #ff758c);
            color: white;
            padding: 15px 25px;
            font-size: 20px;
            font-weight: bold;
            border-radius: 10px;
            border: none;
            transition: 0.3s;
            margin: 10px auto;
            width: 300px;
            box-shadow: 0 0 15px rgba(255, 117, 140, 0.5);
            display: block;
        }}

        .stButton>button:hover {{
            background: linear-gradient(135deg, #ffb347, #ffcc33);
            color: black;
            transform: scale(1.05);
            box-shadow: 0 0 25px rgba(255, 180, 71, 0.8);
        }}

        /* Image Section */
        .image-container img {{
            margin-top: 10px;
            width: 150%;
            height: auto;   
            max-width: 1400px;
            border-radius: 14px;
            box-shadow: 0 0 15px rgba(0, 0, 0, 0.5);
        }}

        /* Footer */
        .footer {{
            font-size: 18px;
            color: white;
            text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.7);
            text-align: center;
            margin-top: 50px;
            animation: fadeIn 2.5s ease-in-out;
        }}
    </style>
    """,
    unsafe_allow_html=True
)

def main():
    # Main Content Section
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # Title & Subtitle
    st.markdown('<h1 class="main-title">✨ QueryGenie: AI-Powered SQL Assistant ✨</h1>', unsafe_allow_html=True)
    st.markdown('<h3 class="sub-title">Seamlessly interact with databases using natural language</h3>', unsafe_allow_html=True)
    
    # Description (Same style as subtitle, single line)
    st.markdown('<h3 class="sub-title">Welcome to <b>QueryGenie</b>, your AI-powered SQL assistant for seamless database querying and analysis.</h3>', unsafe_allow_html=True)

    # Navigation Buttons (Centered)
    col1, col2 = st.columns(2, gap="large")
    with col1:
        if st.button("🗄️ Run SQL Query Generator"):
            subprocess.run(["streamlit", "run", "app.py"])
    with col2:
        if st.button("📊 Run API Agent"):
            subprocess.run(["streamlit", "run", "api.py"])

    st.markdown('</div>', unsafe_allow_html=True)  # Close main text container

    # Image Section (Full width)
    st.markdown(
        f"""
        <div class="image-container">
            <img src="data:image/jpeg;base64,{bg_image_base64}" alt="QueryGenie">
        </div>
        """,
        unsafe_allow_html=True
    )

    # Footer
    st.markdown('<p class="footer">💡 Empowering data-driven decision-making with AI.</p>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()



