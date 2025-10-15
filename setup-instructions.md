# Streamify Project Setup Instructions

## Prerequisites

1. **Google Cloud Platform Account**
   - Create a GCP project
   - Enable Cloud Storage API
   - Create a GCS bucket

2. **Google Cloud SDK**
   ```bash
   # Install gcloud CLI
   gcloud auth application-default login
   ```

3. **Python Dependencies**
   ```bash
   pip install google-cloud-storage
   ```

## Environment Setup

1. **Copy environment template**
   ```bash
   cp env.example .env
   ```

2. **Update .env with your values**
   ```bash
   GCS_BUCKET_NAME=your-actual-bucket-name
   GOOGLE_CLOUD_PROJECT=your-project-id
   DOCKER_REGISTRY=your-registry-url
   ```

3. **Set up Kubernetes ConfigMap**
   ```bash
   # Update k8s/configmap.yaml with your values
   kubectl apply -f k8s/configmap.yaml
   ```

## Running the Application

### Local Development
```bash
# Set environment variable
export GCS_BUCKET_NAME=your-bucket-name

# Run the logger
python simulator_app/local_logger.py
```

### Docker
```bash
# Build image
docker build -t streamify-app simulator_app/

# Run with environment variables
docker run -e GCS_BUCKET_NAME=your-bucket-name streamify-app
```

### Kubernetes
```bash
# Apply configurations
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

## Security Notes

- Never commit `.env` files to version control
- Use Kubernetes secrets for sensitive data in production
- Rotate service account keys regularly
- Use least-privilege IAM roles
