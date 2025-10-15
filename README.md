# Streamify Data Infrastructure

A cloud-native data pipeline for streaming platform analytics, built with Google Cloud Platform, Kubernetes, and Apache Airflow.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Google Cloud Platform (GCP)                      │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    GKE Autopilot Cluster                           │   │
│  │                                                                     │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │              Simulation Application (Ingestion)            │   │   │
│  │  │                                                             │   │   │
│  │  │  ┌─────────────────┐    ┌─────────────────────────────────┐ │   │   │
│  │  │  │ K8s Service     │    │ Flask Application Pods          │ │   │   │
│  │  │  │ (LoadBalancer)  │───▶│ User Activity Simulator         │ │   │   │
│  │  │  │ External Entry  │    │                                 │ │   │   │
│  │  │  └─────────────────┘    └─────────────────────────────────┘ │   │   │
│  │  │           │                        │                        │   │   │
│  │  │           │                        ▼                        │   │   │
│  │  │           │              ┌─────────────────┐                │   │   │
│  │  │           │              │ Persistent      │                │   │   │
│  │  │           │              │ Volume Claim    │                │   │   │
│  │  │           │              │ (Raw Logs)      │                │   │   │
│  │  │           │              └─────────────────┘                │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  │                              │                                     │   │
│  │                              ▼                                     │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │                  Data Pipeline (ETL)                       │   │   │
│  │  │                                                             │   │   │
│  │  │  ┌─────────────────────────────────────────────────────┐   │   │   │
│  │  │  │ Airflow Scheduler & Workers                         │   │   │   │
│  │  │  │ Orchestrator                                       │   │   │   │
│  │  │  └─────────────────────────────────────────────────────┘   │   │   │
│  │  │                              │                             │   │   │
│  │  │                              ▼                             │   │   │
│  │  │  ┌─────────────────────────────────────────────────────┐   │   │   │
│  │  │  │ KubernetesPodOperator                               │   │   │   │
│  │  │  │ (On-demand Processing Pods)                         │   │   │   │
│  │  │  └─────────────────────────────────────────────────────┘   │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              │                                             │
│                              ▼                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    Data Storage                                     │   │
│  │                                                                     │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │           Google Cloud Storage (GCS) Data Lake             │   │   │
│  │  │                                                             │   │   │
│  │  │  ┌─────────────────────┐    ┌─────────────────────────────┐ │   │   │
│  │  │  │ archive/raw_logs/   │    │ processed/summaries/        │ │   │   │
│  │  │  │ (Raw Data Storage)  │    │ (Processed Data Storage)    │ │   │   │
│  │  │  └─────────────────────┘    └─────────────────────────────┘ │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │              Development & CI/CD Environment                       │   │
│  │                                                                     │   │
│  │  ┌─────────────────────┐    ┌─────────────────────────────────────┐ │   │   │
│  │  │ GitHub Repository   │───▶│ Google Artifact Registry            │ │   │   │
│  │  │ (Source Code,       │    │ (Docker Image Storage)              │ │   │   │
│  │  │  Dockerfiles,       │    │                                     │ │   │   │
│  │  │  K8s Configs,       │    │                                     │ │   │   │
│  │  │  Airflow DAGs)      │    │                                     │ │   │   │
│  │  └─────────────────────┘    └─────────────────────────────────────┘ │   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘

External Actors:
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Platform    │    │ Data        │    │ Developer   │
│ User        │    │ Analyst     │    │             │
│ (HTTP POST) │    │ (Views      │    │ (Pushes     │
│             │    │  Dashboards)│    │  Code)      │
└─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │
                   ┌───────▼───────┐
                   │ GKE Native    │
                   │ Observability │
                   │ Dashboard     │
                   └───────────────┘
```

## 🚀 Features

- **Real-time Data Generation**: Flask-based simulator for streaming events
- **Containerized Processing**: Kubernetes-native data processing pipeline
- **Workflow Orchestration**: Apache Airflow for automated data workflows
- **Cloud Storage**: Google Cloud Storage for scalable data persistence
- **Monitoring**: GKE Observability Dashboard integration

## 📁 Project Structure

```
streamify/
├── simulator_app/          # User activity simulator
│   ├── app.py             # Flask web application
│   └── Dockerfile         # Container configuration
├── processing_script/      # Data processing logic
│   ├── process.py         # Main processing script
│   └── Dockerfile         # Container configuration
├── airflow/               # Workflow orchestration
│   ├── dags/              # Airflow DAG definitions
│   └── airflow.Dockerfile # Custom Airflow image
├── k8s/                   # Kubernetes configurations
│   ├── deployment.yaml    # App deployment
│   ├── service.yaml       # Service configuration
│   ├── pvc.yaml          # Persistent volume
│   └── configmap.yaml    # Configuration management
└── airflow.yaml          # Airflow Helm deployment
```

## 🛠️ Tech Stack

- **Containerization**: Docker
- **Orchestration**: Kubernetes (GKE Autopilot)
- **Workflow**: Apache Airflow
- **Storage**: Google Cloud Storage
- **Monitoring**: GKE Observability
- **Languages**: Python, YAML

## 📋 Prerequisites

- Google Cloud Platform account
- Google Cloud SDK (`gcloud`, `kubectl`)
- Docker Desktop
- Helm
- Python 3.9+

## 🚀 Quick Start

### 1. Environment Setup
```bash
# Clone the repository
git clone <your-repo-url>
cd streamify

# Copy environment template
cp env.example .env

# Edit .env with your values
GCS_BUCKET_NAME=your-bucket-name
GOOGLE_CLOUD_PROJECT=your-project-id
```

### 2. Deploy to GKE
```bash
# Set your project
export PROJECT_ID=your-project-id
gcloud config set project $PROJECT_ID

# Create GKE cluster
gcloud container clusters create-auto streamify-cluster --region=us-central1

# Get credentials
gcloud container clusters get-credentials streamify-cluster --region=us-central1

# Deploy infrastructure
kubectl apply -f k8s/
helm install airflow bitnami/airflow -f airflow.yaml
```

### 3. Access the Application
```bash
# Get service IP
kubectl get service simulator-app-service

# Access Airflow UI
kubectl port-forward svc/airflow-webserver 8080:8080 -n airflow
```

## 📊 Data Flow

1. **Simulator** generates streaming events and stores them in PVC
2. **Airflow** monitors for new data and triggers processing
3. **Processing Pod** executes data transformation logic
4. **GCS** stores processed data in `/archive` and `/processed` folders

## 🔧 Configuration

### Environment Variables
- `GCS_BUCKET_NAME`: Your Google Cloud Storage bucket
- `GOOGLE_CLOUD_PROJECT`: Your GCP project ID
- `DOCKER_REGISTRY`: Your container registry URL

### Kubernetes ConfigMap
Update `k8s/configmap.yaml` with your configuration values.

## 📈 Monitoring

Access GKE Observability Dashboard:
1. Navigate to Google Cloud Console → Kubernetes Engine
2. Select your cluster
3. Click "Observability" tab
4. View cluster metrics, workloads, and services

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- Check the [setup instructions](setup-instructions.md) for detailed deployment
- Open an issue for bugs or feature requests
- Review the [documentation](docs/) for advanced configuration

## 🔄 Version History

- **v1.0.0** - Initial release with basic GCS upload
- **v2.0.0** - Added Airflow integration
- **v3.0.0** - Kubernetes deployment support