FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install google-cloud-storage
ENTRYPOINT ["python", "process.py"]