FROM python:3.13-slim

WORKDIR /app

# Copy requirements
COPY backend/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/app ./app

# Copy data files
COPY resume_dataset_1200.csv .
COPY employee\ leave\ tracking\ data.xlsx .

# Copy hr_agent module
COPY hr_agent ./hr_agent

# Expose port
EXPOSE 8000

# Run FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
