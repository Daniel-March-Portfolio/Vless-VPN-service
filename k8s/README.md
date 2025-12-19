# Connect kubectl

```shell
export KUBECONFIG=k8s-config.yaml
kubectl config set-context --current --namespace=vpn
``` 

```shell
export KUBECONFIG=k8s-config.yaml
kubectl config set-context --current --namespace=vpn-prod
``` 

# Create Kubernetes secret to access Docker Registry

```shell
export KUBECONFIG=k8s-config.yaml
kubectl create secret docker-registry github-registry-secret \
  --docker-server=ghcr.io \
  --docker-username=USERNAME \
  --docker-password=TOKEN \
  -n vpn
kubectl create secret docker-registry github-registry-secret \
  --docker-server=ghcr.io \
  --docker-username=USERNAME \
  --docker-password=TOKEN \
  -n vpn-prod
```


# Create app secrets

```shell
export KUBECONFIG=k8s-config.yaml
kubectl create secret generic app-secrets-prod \
  --namespace vpn-prod \
  --from-literal=SECRET_KEY=SECRET_KEY \
  --from-literal=ALLOWED_HOSTS=ALLOWED_HOSTS \
  --from-literal=BOT_TOKEN=BOT_TOKEN \
  --from-literal=DJANGO_SETTINGS_MODULE=config.settings.prod \
  --from-literal=DATABASE_NAME=vpn \
  --from-literal=DATABASE_USER=postgres \
  --from-literal=DATABASE_PASSWORD=password \
  --from-literal=DATABASE_HOST=example \
  --from-literal=DATABASE_PORT=5432 \
  --from-literal=REDIS_CONNECTION_STRING=redis://example:6379/0 \
  --from-literal=HOST=https://example.com
```