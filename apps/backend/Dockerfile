FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory inside container
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .

RUN apt-get update && apt-get install -y libpango-1.0-0 libpangoft2-1.0-0 libglib2.0-0

RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt



# Copy backend code (everything in this folder)
COPY . .

# Expose FastAPI dev port
EXPOSE 8000

# Launch FastAPI app with auto-reload in dev mode
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
