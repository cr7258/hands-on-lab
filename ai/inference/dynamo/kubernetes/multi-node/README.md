## Install Dynamo 

```bash
# 1. Set environment
export NAMESPACE=dynamo-system
# any version of Dynamo 0.3.2+ listed at https://github.com/ai-dynamo/dynamo/releases
export RELEASE_VERSION=0.5.1

# 2. Install CRDs
helm fetch https://helm.ngc.nvidia.com/nvidia/ai-dynamo/charts/dynamo-crds-${RELEASE_VERSION}.tgz
helm install dynamo-crds dynamo-crds-${RELEASE_VERSION}.tgz --namespace default

# 3. Install Platform
helm fetch https://helm.ngc.nvidia.com/nvidia/ai-dynamo/charts/dynamo-platform-${RELEASE_VERSION}.tgz
helm install dynamo-platform dynamo-platform-${RELEASE_VERSION}.tgz \
--namespace ${NAMESPACE} --create-namespace \
--set "grove.enabled=true" --set "kai-scheduler.enabled=true"
```

For multinode deployments, you need to enable Grove and Kai Scheduler. You might chose to install them manually or through the dynamo-platform helm install command. When using the dynamo-platform helm install command, Grove and Kai Scheduler are NOT installed by default. You can enable their installation by setting the following flags in the helm install command:

```bash
--set "grove.enabled=true"
--set "kai-scheduler.enabled=true"
```

## Create DynamoGraphDeployment

```bash
kubectl create secret generic hf-token-secret \
  --from-literal=HF_TOKEN=${HF_TOKEN}

kubectl apply -f disagg-multinode.yaml
```

## Cleanup

```bash
kubectl delete -f disagg-multinode.yaml
kubectl delete secret hf-token-secret
helm uninstall dynamo-platform --namespace ${NAMESPACE}
helm uninstall dynamo-crds --namespace default
kubectl delete namespace dynamo-system
```