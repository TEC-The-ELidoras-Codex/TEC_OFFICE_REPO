FROM python:3.10-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Port for Gradio app
EXPOSE 7860

# Environment setup
ENV PYTHONUNBUFFERED=1

# Command to run the application
CMD ["python", "app.py"]
