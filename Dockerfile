# Use Python 3.12 as base image
FROM python:3.12

# Set working directory inside container
WORKDIR /app

# Copy all files to the container
COPY . /app

# Install dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

CMD streamlit run homepage.py --server.port=$PORT --server.address=0.0.0.0

