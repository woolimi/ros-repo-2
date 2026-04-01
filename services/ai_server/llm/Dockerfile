FROM python:3.11-slim

WORKDIR /app
COPY app/ .
RUN pip install flask --no-cache-dir

EXPOSE 8000
CMD ["python", "main.py"]
