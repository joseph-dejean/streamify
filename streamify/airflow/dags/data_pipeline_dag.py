from __future__ import annotations
import os
import pendulum
from airflow.models.dag import DAG
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from kubernetes.client import models as k8s

BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "your-bucket-name-here") 

with DAG(
    dag_id="streamify_data_processing_pipeline",
    schedule="*/10 * * * *",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    catchup=False,
    tags=["streamify"],
) as dag:
    # NOTE: All the code below this line is indented
    
    # Define the volume and volume mount using the correct Kubernetes objects
    volume_mount = k8s.V1VolumeMount(
        name='logs-storage', mount_path='/data', read_only=False
    )
    
    persistent_volume_claim = k8s.V1PersistentVolumeClaimVolumeSource(claim_name='activity-logs-pvc')
    volume = k8s.V1Volume(
        name='logs-storage',
        persistent_volume_claim=persistent_volume_claim
    )


    # This task runs a pod with a custom script to process the data.
    process_and_upload_task = KubernetesPodOperator(
        task_id="process_logs_and_upload_to_gcs",
        name="data-processing-pod",
        namespace="airflow",
        image=os.getenv("PROCESSING_IMAGE", "your-registry/streamify-repo/processing-script:latest"),
        cmds=["/bin/sh", "-c", "sleep 3600"],

        env_vars={
            "GCS_BUCKET": BUCKET_NAME,
            "AIRFLOW__DATABASE__SQL_ALCHEMY_CONN": "postgresql+psycopg2://airflow:airflow@postgres/airflow"
},
        volumes=[volume],
        volume_mounts=[volume_mount],
        service_account_name="default",
        get_logs=True,
        do_xcom_push=False
    )