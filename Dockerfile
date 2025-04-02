# Use Python 3.12 as base image
FROM python:3.12

# Set working directory inside container
WORKDIR /app

# Copy all files to the container
COPY . /app

# Install dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Expose the port Streamlit will run on
EXPOSE 8080

# Run the Streamlit app
CMD streamlit run homepage.py --server.port=8080 --server.address=0.0.0.0
