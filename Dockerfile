FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY "Merai v1/requirements.txt" ./requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY "Merai v1/" ./

# Create streamlit config directory
RUN mkdir -p ~/.streamlit/

# Create streamlit config
RUN echo "\
[general]\n\
email = \"your-email@example.com\"\n\
\n\
[server]\n\
headless = true\n\
enableCORS = false\n\
port = 8080\n\
address = 0.0.0.0\n\
\n\
" > ~/.streamlit/config.toml

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8080/_stcore/health

# Run the application
CMD ["streamlit", "run", "main.py", "--server.port=8080", "--server.address=0.0.0.0"]
