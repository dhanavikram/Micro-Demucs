#!/bin/sh
helm install -f minio/minio-config.yaml -n minio-ns --create-namespace minio-proj bitnami/minio

kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.12.0-beta.0/deploy/static/provider/cloud/deploy.yaml

kubectl apply -f redis/redis-deployment.yaml
kubectl apply -f redis/redis-service.yaml
kubectl apply -f minio/minio-external-service.yaml

kubectl apply -f logs/logs-deployment.yaml

kubectl apply -f worker/worker-deployment.yaml

kubectl apply -f rest/rest-deployment.yaml
kubectl apply -f rest/rest-service.yaml
kubectl apply -f rest/rest-ingress.yaml


# Port forwarding for local development and accessing web UI

# Redis as localhost:6379
kubectl port-forward --address 0.0.0.0 service/redis 6379:6379 &
# Minio API as localhost:9000
kubectl port-forward -n minio-ns --address 0.0.0.0 service/minio-proj 9000:9000 &
# Minio web UI as localhost:9001
kubectl port-forward -n minio-ns --address 0.0.0.0 service/minio-proj 9001:9001
