FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py ./
COPY docs ./docs
COPY frontend ./frontend
COPY templates ./templates
COPY static ./static
EXPOSE 5000
CMD ["python", "app.py"]
