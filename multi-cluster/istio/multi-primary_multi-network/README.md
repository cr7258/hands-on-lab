
```bash
# 改成自己 Kubeconfig 的 contexdt
export CTX_CLUSTER1=kubeconfig--seven-demo--c1
export CTX_CLUSTER2=kubeconfig--seven-demo--c2

kubectl --context ${CTX_CLUSTER1} create namespace istio-system
kubectl --context ${CTX_CLUSTER1} create secret generic cacerts -n istio-system \
      --from-file=certs/cluster1/ca-cert.pem \
      --from-file=certs/cluster1/ca-key.pem \
      --from-file=certs/cluster1/root-cert.pem \
      --from-file=certs/cluster1/cert-chain.pem

kubectl --context ${CTX_CLUSTER2} create namespace istio-system
kubectl --context ${CTX_CLUSTER2} create secret generic cacerts -n istio-system \
      --from-file=certs/cluster2/ca-cert.pem \
      --from-file=certs/cluster2/ca-key.pem \
      --from-file=certs/cluster2/root-cert.pem \
      --from-file=certs/cluster2/cert-chain.pem


kubectl --context="${CTX_CLUSTER1}" get namespace istio-system && \
kubectl --context="${CTX_CLUSTER1}" label namespace istio-system topology.istio.io/network=network1
istioctl install --context="${CTX_CLUSTER1}" -f cluster1.yaml
istioctl --context="${CTX_CLUSTER1}" install -y -f cluster1-gateway.yaml
kubectl --context="${CTX_CLUSTER1}" apply -n istio-system -f expose-services.yaml


kubectl --context="${CTX_CLUSTER2}" get namespace istio-system && \
kubectl --context="${CTX_CLUSTER2}" label namespace istio-system topology.istio.io/network=network2
istioctl install --context="${CTX_CLUSTER2}" -f cluster2.yaml
istioctl --context="${CTX_CLUSTER2}" install -y -f cluster2-gateway.yaml
kubectl --context="${CTX_CLUSTER2}" apply -n istio-system -f expose-services.yaml


istioctl x create-remote-secret \
  --context="${CTX_CLUSTER1}" \
  --name=cluster1 | \
  kubectl apply -f - --context="${CTX_CLUSTER2}"

istioctl x create-remote-secret \
  --context="${CTX_CLUSTER2}" \
  --name=cluster2 | \
  kubectl apply -f - --context="${CTX_CLUSTER1}"
```

