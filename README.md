# Streamify Data Infrastructure: Automation & Deployment

## Introduction

Streamify is a comprehensive cloud-native data infrastructure project designed to demonstrate modern data engineering practices for a fictitious streaming platform. This project showcases the implementation of a scalable, automated, and observable data pipeline using Google Cloud Platform (GCP) with GKE Autopilot, Docker containerization, and Apache Airflow orchestration.

The infrastructure enables real-time analytics, user behavior tracking, and platform monitoring through a fully automated data processing pipeline that handles user activity simulation, data processing, and long-term storage.

## Project Objectives

1. **Automated Data Pipeline Deployment**: Deploy a complete data infrastructure using Infrastructure as Code (IaC) principles with Kubernetes and Helm
2. **Scalable Data Processing**: Implement containerized data processing components that can scale based on workload demands
3. **Observable System Architecture**: Establish comprehensive monitoring and logging capabilities using GKE's native observability features
4. **Cloud-Native Best Practices**: Demonstrate modern cloud engineering practices including Workload Identity, persistent storage, and service mesh integration

## Architecture Overview

The Streamify data infrastructure consists of several interconnected components working together to process streaming platform data:

- **User Activity Simulator**: A Flask-based application that generates realistic user interaction events
- **Persistent Storage**: Kubernetes PVC for temporary log storage before processing
- **Workflow Orchestration**: Apache Airflow managing the data processing pipeline
- **Data Processor**: Containerized Python scripts for log aggregation and transformation
- **Long-term Storage**: Google Cloud Storage for archival and processed data
- **Monitoring**: GKE Observability Dashboard for system health and performance tracking

### Logical Architecture Diagram

![Architecture Diagram](docs/architecture_diagram.png)

### Data Flow Description

1. **Data Generation**: The User Activity Simulator generates streaming events and stores them in the Kubernetes PVC
2. **Data Collection**: Airflow DAGs monitor the PVC for new data files
3. **Data Processing**: Processing pods execute transformation logic using `process.py`
4. **Data Storage**: Processed data is uploaded to GCS in `/archive` (raw) and `/processed` (aggregated) folders
5. **Monitoring**: All components report metrics to GKE Observability Dashboard

## Prerequisites

### Local Software Requirements
- **Google Cloud SDK** (`gcloud`, `kubectl`) - Latest version
- **Docker Desktop** - For container image building and local testing
- **Helm** - For Airflow deployment
- **Python 3.9+** - For local development and testing
- **pip** - Python package manager

### GCP Account Setup
- Active Google Cloud Platform account with billing enabled
- Project with the following APIs enabled:
  - Kubernetes Engine API
  - Cloud Storage API
  - Artifact Registry API
  - Cloud Resource Manager API

## Repository Structure

```
streamify/
├── simulator_app/              # User Activity Simulator
│   ├── app.py                 # Flask application for event generation
│   ├── local_logger.py        # GCS upload utility
│   └── Dockerfile             # Container configuration
├── processing_script/          # Data Processing Components
│   ├── process.py             # Main processing logic
│   └── Dockerfile             # Container configuration
├── k8s/                       # Kubernetes Manifests
│   ├── deployment.yaml        # Simulator app deployment
│   ├── service.yaml           # Service configuration
│   └── pvc.yaml              # Persistent volume claim
├── airflow/                   # Airflow Configuration
│   ├── dags/                  # Airflow DAG definitions
│   │   └── data_pipeline_dag.py
│   └── airflow.Dockerfile     # Custom Airflow image
├── airflow.yaml              # Airflow Helm deployment
└── README.md                 # This file
```

## Deployment Guide

### A. GCP Project Setup

```powershell
# Set your project ID (replace [YOUR_PROJECT_ID] with your actual project ID)
$env:PROJECT_ID = "[YOUR_PROJECT_ID]"
gcloud config set project $env:PROJECT_ID

# Enable required APIs
gcloud services enable container.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable cloudresourcemanager.googleapis.com

# Create GKE Autopilot cluster
gcloud container clusters create-auto streamify-cluster `
    --region=us-central1 `
    --project=$env:PROJECT_ID

# Get cluster credentials
gcloud container clusters get-credentials streamify-cluster `
    --region=us-central1 `
    --project=$env:PROJECT_ID

# Create GCS bucket
gsutil mb gs://your-bucket-name-here

# Create Artifact Registry repository
gcloud artifacts repositories create streamify-repo `
    --repository-format=docker `
    --location=us-central1 `
    --description="Streamify container images"

# Configure Docker authentication
gcloud auth configure-docker us-central1-docker.pkg.dev
```

### B. Build & Push Docker Images

```powershell
# Build and push simulator app
docker build -t us-central1-docker.pkg.dev/$env:PROJECT_ID/streamify-repo/simulator-app:v3 ./simulator_app/
docker push us-central1-docker.pkg.dev/$env:PROJECT_ID/streamify-repo/simulator-app:v3

# Build and push processing script
docker build -t us-central1-docker.pkg.dev/$env:PROJECT_ID/streamify-repo/processing-script:v1 ./processing_script/
docker push us-central1-docker.pkg.dev/$env:PROJECT_ID/streamify-repo/processing-script:v1

# Build and push custom Airflow image
docker build -t us-central1-docker.pkg.dev/$env:PROJECT_ID/streamify-repo/airflow-custom:v1 -f ./airflow.Dockerfile .
docker push us-central1-docker.pkg.dev/$env:PROJECT_ID/streamify-repo/airflow-custom:v1

# Pull, tag, and push PostgreSQL image
docker pull postgres:15
docker tag postgres:15 us-central1-docker.pkg.dev/$env:PROJECT_ID/streamify-repo/postgres:15
docker push us-central1-docker.pkg.dev/$env:PROJECT_ID/streamify-repo/postgres:15
```

### C. Deploy Kubernetes Resources (Simulator App)

```powershell
# Deploy persistent volume claim
kubectl apply -f k8s/pvc.yaml

# Deploy simulator application
kubectl apply -f k8s/deployment.yaml

# Deploy service
kubectl apply -f k8s/service.yaml

# Verify deployment
kubectl get pods
kubectl get services
```

### D. Deploy Apache Airflow

```powershell
# Clean install - delete existing namespace if present
kubectl delete namespace airflow --ignore-not-found=true
kubectl create namespace airflow

# Add Bitnami Helm repository
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Install Airflow with custom configurations
helm install airflow bitnami/airflow `
    --namespace airflow `
    --set auth.username=admin `
    --set auth.password=your-secure-password `
    --set postgresql.image.registry=us-central1-docker.pkg.dev `
    --set postgresql.image.repository=$env:PROJECT_ID/streamify-repo/postgres `
    --set postgresql.image.tag=15 `
    --set airflow.image.registry=us-central1-docker.pkg.dev `
    --set airflow.image.repository=$env:PROJECT_ID/streamify-repo/airflow-custom `
    --set airflow.image.tag=v1

# Wait for pods to be ready
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=airflow --timeout=300s -n airflow

# Get the correct Airflow webserver service name
kubectl get services -n airflow

# Port forward to Airflow UI (replace 'airflow-webserver' with actual service name if different)
kubectl port-forward svc/airflow-webserver 8080:8080 -n airflow
```

### E. Configure Workload Identity Permissions

```powershell
# Create service account for simulator app
gcloud iam service-accounts create streamify-simulator-sa `
    --display-name="Streamify Simulator Service Account"

# Grant GCS access to simulator service account
gsutil iam ch serviceAccount:streamify-simulator-sa@$env:PROJECT_ID.iam.gserviceaccount.com:objectAdmin gs://your-bucket-name-here

# Bind service account to default Kubernetes service account
gcloud iam service-accounts add-iam-policy-binding `
    streamify-simulator-sa@$env:PROJECT_ID.iam.gserviceaccount.com `
    --role roles/iam.workloadIdentityUser `
    --member "serviceAccount:$env:PROJECT_ID.svc.id.goog[default/default]"

# Annotate Kubernetes service account
kubectl annotate serviceaccount default `
    iam.gke.io/gcp-service-account=streamify-simulator-sa@$env:PROJECT_ID.iam.gserviceaccount.com

# Create service account for Airflow
gcloud iam service-accounts create streamify-airflow-sa `
    --display-name="Streamify Airflow Service Account"

# Grant GCS access to Airflow service account
gsutil iam ch serviceAccount:streamify-airflow-sa@$env:PROJECT_ID.iam.gserviceaccount.com:objectAdmin gs://your-bucket-name-here

# Bind service account to Airflow Kubernetes service account
gcloud iam service-accounts add-iam-policy-binding `
    streamify-airflow-sa@$env:PROJECT_ID.iam.gserviceaccount.com `
    --role roles/iam.workloadIdentityUser `
    --member "serviceAccount:$env:PROJECT_ID.svc.id.goog[airflow/default]"

# Annotate Airflow Kubernetes service account
kubectl annotate serviceaccount default `
    iam.gke.io/gcp-service-account=streamify-airflow-sa@$env:PROJECT_ID.iam.gserviceaccount.com `
    -n airflow
```

## Demonstration Steps (End-to-End Walkthrough)

### A. Access Airflow UI

1. Open browser and navigate to `http://localhost:8080`
2. Login with credentials:
   - Username: `admin`
   - Password: `your-secure-password`
3. Navigate to the DAGs page to view available workflows

### B. Upload and Activate DAG

```powershell
# Get Airflow pod names
kubectl get pods -n airflow

# Copy DAG to scheduler pod (replace POD_NAME with actual scheduler pod name)
kubectl cp airflow/dags/data_pipeline_dag.py airflow/POD_NAME:/opt/bitnami/airflow/dags/ -n airflow

# Copy DAG to webserver pod (replace POD_NAME with actual webserver pod name)
kubectl cp airflow/dags/data_pipeline_dag.py airflow/POD_NAME:/opt/bitnami/airflow/dags/ -n airflow

# Restart Airflow scheduler to pick up new DAG
kubectl delete pod -l app.kubernetes.io/component=scheduler -n airflow
```

1. In Airflow UI, find the `data_pipeline_dag` and click the toggle to unpause it
2. Click "Trigger DAG" to start the data processing workflow

### C. Generate Test Data

```powershell
# Get external IP of simulator service
kubectl get service simulator-app-service

# Generate test data (replace EXTERNAL_IP with actual IP)
Invoke-WebRequest -Uri "http://EXTERNAL_IP:80/generate-logs" -Method POST
```

### D. Verify Data in GCS

1. Navigate to Google Cloud Console → Cloud Storage
2. Open bucket `your-bucket-name-here`
3. Verify presence of:
   - `/archive` folder containing raw log files
   - `/processed` folder containing aggregated data summaries

### E. Monitoring

1. Navigate to Google Cloud Console → Kubernetes Engine
2. Select your `streamify-cluster`
3. Click on "Observability" tab
4. Explore the following dashboards:
   - Cluster Overview
   - Workloads
   - Services
   - Storage

## Cleanup Resources

```powershell
# Delete GKE cluster
gcloud container clusters delete streamify-cluster `
    --region=us-central1 `
    --project=$env:PROJECT_ID

# Delete GCS bucket and all contents
gsutil rm -r gs://your-bucket-name-here

# Delete Artifact Registry repository
gcloud artifacts repositories delete streamify-repo `
    --location=us-central1 `
    --project=$env:PROJECT_ID

# Delete service accounts
gcloud iam service-accounts delete streamify-simulator-sa@$env:PROJECT_ID.iam.gserviceaccount.com
gcloud iam service-accounts delete streamify-airflow-sa@$env:PROJECT_ID.iam.gserviceaccount.com
```

