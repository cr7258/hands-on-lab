## 脚本

```bash
# 改成自己 Kubeconfig 的 contexdt
export CTX_CLUSTER1=kubeconfig--seven-demo--c1
export CTX_CLUSTER2=kubeconfig--seven-demo--c2

# 在 cluster1 部署 Istio
istioctl install --set values.pilot.env.EXTERNAL_ISTIOD=true --context="${CTX_CLUSTER1}" -f cluster1.yaml

# 部署一个新的 cluster1 ingressgateway
istioctl --context="${CTX_CLUSTER1}" install -y -f cluster1-gateway.yaml
# 通过该 ingressgateway 来暴露 Istio 控制面
kubectl apply --context="${CTX_CLUSTER1}" -n istio-system -f expose-istiod.yaml

# 在 cluster2 的 istio-system Namespace 添加 Annotation，表明 cluster1 是外部的控制面
kubectl --context="${CTX_CLUSTER2}" create namespace istio-system
kubectl --context="${CTX_CLUSTER2}" annotate namespace istio-system topology.istio.io/controlPlaneClusters=cluster1

# 将 cluster2 配置为 remote cluster
istioctl install --context="${CTX_CLUSTER2}" -f cluster2.yaml

# 在 cluster1 中添加 cluster2 API Server 的访问凭证
istioctl x create-remote-secret \
    --context="${CTX_CLUSTER2}" \
    --name=cluster2 | \
    kubectl apply -f - --context="${CTX_CLUSTER1}"
```

## 参考
- [Install Primary-Remote](https://istio.io/latest/docs/setup/install/multicluster/primary-remote/)