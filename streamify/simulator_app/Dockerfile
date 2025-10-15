FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install Flask==2.1.2 Werkzeug==2.3.8 google-cloud-storage
CMD ["python", "app.py"]