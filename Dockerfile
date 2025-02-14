FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY run.py .
COPY .env .
COPY prompts/ prompts/

CMD ["python", "run.py"]