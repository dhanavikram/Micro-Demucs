# Min.io README

This specific deployment of Min.io uses helm package manager to deploy minio in an entirely different kubernetes namespace to keep it isolated.

The following commands can be used to deploy Min.io.

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami

helm install -f ./minio-config.yaml -n minio-ns --create-namespace minio-proj bitnami/minio
```

This deploys a minio object storage system in `minio-ns` namespace with a helm project name `minio-proj`.

Then for local testing, the following commands can be run to port forward the API and web UI interface

```bash
kubectl port-forward --namespace minio-ns svc/minio-proj 9000:9000

kubectl port-forward --namespace minio-ns svc/minio-proj 9001:9001
```

By default, Min.io's API runs on port `9000` and the web UI runs on port `9001`. If you face login related issues, please kill the port forwarding and restart it as it solves timeout related issues.

The login username and password can be modified in `minio-config.yaml` which is used to pass in external parameters to helm's minio implementation.

## Attaching minio to development/production namespace

To add the minio to the application's namespace, use `minio-external-service.yaml` and modify the namespace accordingly.