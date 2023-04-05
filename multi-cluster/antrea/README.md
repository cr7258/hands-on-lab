## Create Kind Cluster
```bash
kind create cluster --config - <<EOF
kind: Cluster
name: a1
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
- role: worker
- role: worker
networking:
  disableDefaultCNI: true
  apiServerAddress: 10.182.0.2
  podSubnet: "10.7.0.0/16"
  serviceSubnet: "10.77.0.0/16"
EOF
 
kind create cluster --config - <<EOF
kind: Cluster
name: a2
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
- role: worker
- role: worker
networking:
  disableDefaultCNI: true
  apiServerAddress: 10.182.0.2
  podSubnet: "10.8.0.0/16"
  serviceSubnet: "10.88.0.0/16"
EOF
```

```bash
# 改成自己 Kubeconfig 的 contexdt
export CTX_CLUSTER1=kind-a1
export CTX_CLUSTER2=kind-a2
```

```bash
helm repo add antrea https://charts.antrea.io
helm pull antrea/antrea --untar
```

## Install Antrea
```bash
# 修改 Helm values.yaml 文件，启用 MultiCluster

# -- To explicitly enable or disable a FeatureGate and bypass the Antrea
# defaults, add an entry to the dictionary with the FeatureGate's name as the
# key and a boolean as the value.
featureGates:
  Multicluster: true

multicluster:
  # -- Enable Antrea Multi-cluster Gateway to support cross-cluster traffic.
  # This feature is supported only with encap mode.
  enableGateway: true
```

```bash
helm install antrea antrea --kube-context ${CTX_CLUSTER1}
helm install antrea antrea --kube-context ${CTX_CLUSTER2}
```

```bash
export TAG=v1.11.0
curl -Lo ./antctl "https://github.com/antrea-io/antrea/releases/download/$TAG/antctl-$(uname)-x86_64"
chmod +x ./antctl
mv ./antctl /usr/local/bin
antctl version
```

## Set up Leader and Member in Cluster A

```bash
kubectl config use-context kind-a1

# Step 1 - deploy Antrea Multi-cluster Controllers for leader and member
kubectl create ns antrea-multicluster
antctl mc deploy leadercluster -n antrea-multicluster --antrea-version $TAG
antctl mc deploy membercluster -n kube-system --antrea-version $TAG

# Step 2 - initialize ClusterSet
antctl mc init --clusterset test-clusterset --clusterid test-cluster-leader -n antrea-multicluster --create-token -j join-config.yml
antctl mc join --clusterid test-cluster-leader -n kube-system --config-file join-config.yml

# Step 3 - specify Multi-cluster Gateway Node
kubectl annotate node a1-worker multicluster.antrea.io/gateway=true
```

## Set up Cluster B

```bash
kubectl config use-context kind-a2

# Step 1 - deploy Antrea Multi-cluster Controller for member
antctl mc deploy membercluster -n kube-system --antrea-version $TAG

# Step 2 - join ClusterSet
antctl mc join --clusterid test-cluster-member -n kube-system --config-file join-config.yml

# Step 3 - specify Multi-cluster Gateway Node
kubectl annotate node a2-worker multicluster.antrea.io/gateway=true
```

## Test

```bash
kubectl config use-context kind-a1
kubectl create deployment nginx --image=nginx
kubectl expose deployment nginx --port=80 --target-port=80
```

```yaml
apiVersion: multicluster.x-k8s.io/v1alpha1
kind: ServiceExport
metadata:
  name: nginx
  namespace: default
```


```bash
root@seven-demo-2:~/antrea-multi-cluster# kubectl  get serviceimports.multicluster.x-k8s.io -A
NAMESPACE   NAME    TYPE           IP                  AGE
default     nginx   ClusterSetIP   ["10.77.136.152"]   9s
root@seven-demo-2:~/antrea-multi-cluster# kubectl get resourceimports.multicluster.crd.antrea.io -A
NAMESPACE             NAME                              KIND            NAMESPACE             NAME                              AGE
antrea-multicluster   default-nginx-endpoints           Endpoints       default               nginx                             17s
antrea-multicluster   default-nginx-service             ServiceImport   default               nginx                             17s
antrea-multicluster   test-cluster-leader-clusterinfo   ClusterInfo     antrea-multicluster   test-cluster-leader-clusterinfo   30m
antrea-multicluster   test-cluster-member-clusterinfo   ClusterInfo     antrea-multicluster   test-cluster-member-clusterinfo   27m
root@seven-demo-2:~/antrea-multi-cluster# kubectl get resourceimports.multicluster.crd.antrea.io -n antrea-multicluster -oyaml
apiVersion: v1
items:
- apiVersion: multicluster.crd.antrea.io/v1alpha1
  kind: ResourceImport
  metadata:
    creationTimestamp: "2023-04-04T03:44:14Z"
    generation: 1
    name: default-nginx-endpoints
    namespace: antrea-multicluster
    resourceVersion: "7811"
    uid: d95c287c-80a5-4e64-ba69-7695dde19cfe
  spec:
    endpoints:
      subsets:
      - addresses:
        - ip: 10.77.95.164
        ports:
        - port: 80
          protocol: TCP
    kind: Endpoints
    name: nginx
    namespace: default
- apiVersion: multicluster.crd.antrea.io/v1alpha1
  kind: ResourceImport
  metadata:
    creationTimestamp: "2023-04-04T03:44:14Z"
    generation: 1
    name: default-nginx-service
    namespace: antrea-multicluster
    resourceVersion: "7806"
    uid: 117ad8fd-9def-422e-b44f-44ffe6feba38
  spec:
    kind: ServiceImport
    name: nginx
    namespace: default
    serviceImport:
      metadata: {}
      spec:
        ports:
        - port: 80
          protocol: TCP
        type: ClusterSetIP
      status: {}
- apiVersion: multicluster.crd.antrea.io/v1alpha1
  kind: ResourceImport
  metadata:
    creationTimestamp: "2023-04-04T03:13:39Z"
    generation: 1
    name: test-cluster-leader-clusterinfo
    namespace: antrea-multicluster
    resourceVersion: "4553"
    uid: 97bf1de9-38f8-473c-b55f-477c7f12f40d
  spec:
    clusterinfo:
      clusterID: test-cluster-leader
      gatewayInfos:
      - gatewayIP: 172.18.0.7
      serviceCIDR: 10.77.0.0/16
    kind: ClusterInfo
    name: test-cluster-leader-clusterinfo
    namespace: antrea-multicluster
- apiVersion: multicluster.crd.antrea.io/v1alpha1
  kind: ResourceImport
  metadata:
    creationTimestamp: "2023-04-04T03:17:26Z"
    generation: 1
    name: test-cluster-member-clusterinfo
    namespace: antrea-multicluster
    resourceVersion: "4936"
    uid: e3083c69-3b52-44b7-b220-3ce0a67e6807
  spec:
    clusterinfo:
      clusterID: test-cluster-member
      gatewayInfos:
      - gatewayIP: 172.18.0.11
      serviceCIDR: 10.88.0.0/16
    kind: ClusterInfo
    name: test-cluster-member-clusterinfo
    namespace: antrea-multicluster
kind: List
metadata:
  resourceVersion: ""
root@seven-demo-2:~/antrea-multi-cluster# kubectl  get svc
NAME              TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)   AGE
antrea            ClusterIP   10.77.39.231    <none>        443/TCP   68m
antrea-mc-nginx   ClusterIP   10.77.136.152   <none>        80/TCP    72s
kubernetes        ClusterIP   10.77.0.1       <none>        443/TCP   72m
nginx             ClusterIP   10.77.95.164    <none>        80/TCP    3m25s
```


```bash
kubectl config use-context kind-a2
kubectl run nettool --image cr7258/nettool:v1
kubectl exec -it nettool -- curl nginx
```

```bash
root@seven-demo-2:~/antrea-multi-cluster# kubectl get service
NAME              TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)   AGE
antrea            ClusterIP   10.88.52.120   <none>        443/TCP   70m
antrea-mc-nginx   ClusterIP   10.88.204.89   <none>        80/TCP    3m14s
kubernetes        ClusterIP   10.88.0.1      <none>        443/TCP   72m
root@seven-demo-2:~/antrea-multi-cluster# kubectl  get serviceimports.multicluster.x-k8s.io nginx -oyaml
apiVersion: multicluster.x-k8s.io/v1alpha1
kind: ServiceImport
metadata:
  creationTimestamp: "2023-04-04T03:44:14Z"
  generation: 1
  name: nginx
  namespace: default
  resourceVersion: "7186"
  uid: ff056c69-4a40-468f-8130-d9968fde2bbf
spec:
  ips:
  - 10.88.204.89
  ports:
  - port: 80
    protocol: TCP
  type: ClusterSetIP
root@seven-demo-2:~# kubectl describe svc antrea-mc-nginx
Name:              antrea-mc-nginx
Namespace:         default
Labels:            <none>
Annotations:       multicluster.antrea.io/imported-service: true
Selector:          <none>
Type:              ClusterIP
IP Family Policy:  SingleStack
IP Families:       IPv4
IP:                10.88.204.89
IPs:               10.88.204.89
Port:              <unset>  80/TCP
TargetPort:        80/TCP
Endpoints:         10.77.95.164:80  # Service ClusterIP in ClusterA
Session Affinity:  None
Events:            <none>
```