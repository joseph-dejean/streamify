# Start from the official Airflow image
FROM apache/airflow:2.9.3

# Install the Python library we need.
# This is run as the default 'airflow' user, which is the correct way.
RUN pip install --no-cache-dir google-cloud-storage kubernetes