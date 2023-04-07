## 环境准备

```bash
root@seven-demo:~# seven-demo
   Static hostname: seven-demo
         Icon name: computer-vm
           Chassis: vm
        Machine ID: f780bfec3c409135b11d1ceac73e2293
           Boot ID: e83e9a883800480f86d37189bdb09628
    Virtualization: kvm
  Operating System: Ubuntu 20.04.5 LTS
            Kernel: Linux 5.15.0-1030-gcp
      Architecture: x86-64
```

```bash
# 安装 Docker，根据操作系统安装 https://docs.docker.com/engine/install/ 
sudo apt-get update
sudo apt-get install -y \
    ca-certificates \
    curl \
    gnupg
sudo mkdir -m 0755 -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# 安装 Kind
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.18.0/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind

# 安装 subctl
curl -Lo subctl-release-0.14-linux-amd64.tar.xz https://github.com/submariner-io/subctl/releases/download/subctl-release-0.14/subctl-release-0.14-linux-amd64.tar.xz
tar -xf subctl-release-0.14-linux-amd64.tar.xz
mv subctl-release-0.14/subctl-release-0.14-linux-amd64 /usr/local/bin/subctl
chmod +x /usr/local/bin/subctl
```

## 创建集群

```yaml
# 替换成服务器 IP
export SERVER_IP="10.138.0.16"

kind create cluster --config - <<EOF
kind: Cluster
name: broker
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
networking:
  apiServerAddress: $SERVER_IP
  podSubnet: "10.7.0.0/16"
  serviceSubnet: "10.77.0.0/16"
EOF

kind create cluster --config - <<EOF
kind: Cluster
name: c1
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
- role: worker
networking:
  apiServerAddress: $SERVER_IP
  podSubnet: "10.8.0.0/16"
  serviceSubnet: "10.88.0.0/16"
EOF
 
kind create cluster --config - <<EOF
kind: Cluster
name: c2
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
- role: worker
networking:
  apiServerAddress: $SERVER_IP
  podSubnet: "10.9.0.0/16"
  serviceSubnet: "10.99.0.0/16"
EOF
```


## 部署 Broker

```bash
subctl --context kind-broker deploy-broker
```

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20230405105053.png)

## 加入集群

```bash
subctl --context kind-c1 join broker-info.subm --clusterid c1
subctl --context kind-c2 join broker-info.subm --clusterid c2
```

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20230405105146.png)

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20230405105236.png)


c1 集群选择 c1-worker 节点作为 gateway，c2 集群选择 c2-worker 节点作为 gateway。

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20230406223135.png)

## 查看连接

```bash
subctl show connections --context kind-c1
subctl show connections --context kind-c2
```

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20230405105800.png)

查看 c1 gateway 日志，成功建立 Ipsec 隧道。

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20230405105710.png)


## 测试

### ClusterIP Service

在 c2 集群创建服务

```bash
kubectl --context kind-c2 create namespace sample
# 需要确保 c1 集群上也有 sample Namespace，否则 Lighthouse agent 创建 Endpointslices 会失败
kubectl --context kind-c1 create namespace sample
```

```yaml
kubectl --context kind-c2 apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: whereami
  namespace: sample
spec:
  replicas: 3
  selector:
    matchLabels:
      app: whereami
  template:
    metadata:
      labels:
        app: whereami
    spec:
      containers:
      - name: whereami
        image: cr7258/whereami:v1
        imagePullPolicy: Always
        ports:
        - containerPort: 80
        env:
        - name: NAMESPACE
          valueFrom:
            fieldRef:
              fieldPath: metadata.namespace
        - name: NODE_NAME
          valueFrom:
            fieldRef:
              fieldPath: spec.nodeName
        - name: POD_NAME
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
        - name: POD_IP
          valueFrom:
            fieldRef:
              fieldPath: status.podIP
---
apiVersion: v1
kind: Service
metadata:
  name: whereami-cs
  namespace: sample
spec:
  selector:
    app: whereami
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
EOF
```

在 c2 集群查看服务

```bash
root@seven-demo:~# kubectl --context kind-c2 get pod -n sample -o wide
NAME                        READY   STATUS    RESTARTS   AGE   IP          NODE        NOMINATED NODE   READINESS GATES
whereami-754776cdc9-28kgd   1/1     Running   0          19h   10.9.1.18   c2-worker   <none>           <none>
whereami-754776cdc9-8ccmc   1/1     Running   0          19h   10.9.1.17   c2-worker   <none>           <none>
whereami-754776cdc9-dlp55   1/1     Running   0          19h   10.9.1.16   c2-worker   <none>           <none>
root@seven-demo:~# kubectl --context kind-c2 get svc -n sample -o wide
NAME          TYPE        CLUSTER-IP    EXTERNAL-IP   PORT(S)   AGE   SELECTOR
whereami-cs   ClusterIP   10.99.2.201   <none>        80/TCP    19h   app=whereami
```

在 c2 集群导出服务

```bash
subctl --context kind-c2 export service --namespace sample whereami-cs
```

c1,c2 集群会自动注入 ServiceImport

```bash
kubectl --context kind-c1 get -n submariner-operator serviceimport
kubectl --context kind-c2 get -n submariner-operator serviceimport
```

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20230406210456.png)


查看 Endpointslice

```bash
kubectl --context kind-c1 get endpointslices -n sample
kubectl --context kind-c2 get endpointslices -n sample
```

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20230406210536.png)

在 c1 集群访问 c2 集群的 whereami 服务

```bash
kubectl --context kind-c1 run client --image=cr7258/nettool:v1
kubectl --context kind-c1 exec -it client -- bash
```

```bash
nslookup whereami-cs.sample.svc.clusterset.local
```

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20230406210652.png)

```bash
curl whereami-cs.sample.svc.clusterset.local
```

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20230406210720.png)

CoreDNS 的配置文件会被修改，`clusterset.local` 域名交给 Lighthouse DNS 来解析。
```
root@seven-demo:~# kubectl get cm -n kube-system coredns -oyaml
apiVersion: v1
data:
  Corefile: |+
    #lighthouse-start AUTO-GENERATED SECTION. DO NOT EDIT
    clusterset.local:53 {
        forward . 10.88.78.89
    }
    #lighthouse-end
    .:53 {
        errors
        health {
           lameduck 5s
        }
        ready
        kubernetes cluster.local in-addr.arpa ip6.arpa {
           pods insecure
           fallthrough in-addr.arpa ip6.arpa
           ttl 30
        }
        prometheus :9153
        forward . /etc/resolv.conf {
           max_concurrent 1000
        }
        cache 30
        loop
        reload
        loadbalance
    }

kind: ConfigMap
metadata:
  creationTimestamp: "2023-04-05T02:47:34Z"
  name: coredns
  namespace: kube-system
  resourceVersion: "1211"
  uid: 698f20a5-83ea-4a3e-8a1e-8b9438a6b3f8
```

在 c1 集群也创建相同的服务

```yaml
kubectl --context kind-c1 apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: whereami
  namespace: sample
spec:
  replicas: 3
  selector:
    matchLabels:
      app: whereami
  template:
    metadata:
      labels:
        app: whereami
    spec:
      containers:
      - name: whereami
        image: cr7258/whereami:v1
        imagePullPolicy: Always
        ports:
        - containerPort: 80
        env:
        - name: NAMESPACE
          valueFrom:
            fieldRef:
              fieldPath: metadata.namespace
        - name: NODE_NAME
          valueFrom:
            fieldRef:
              fieldPath: spec.nodeName
        - name: POD_NAME
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
        - name: POD_IP
          valueFrom:
            fieldRef:
              fieldPath: status.podIP
---
apiVersion: v1
kind: Service
metadata:
  name: whereami-cs
  namespace: sample
spec:
  selector:
    app: whereami
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
EOF
```

在 c1 集群上查看服务

```bash
root@seven-demo:~# kubectl --context kind-c1 get pod -n sample -o wide
NAME                        READY   STATUS    RESTARTS   AGE   IP          NODE        NOMINATED NODE   READINESS GATES
whereami-754776cdc9-hq4m2   1/1     Running   0          45s   10.8.1.25   c1-worker   <none>           <none>
whereami-754776cdc9-rt84w   1/1     Running   0          45s   10.8.1.23   c1-worker   <none>           <none>
whereami-754776cdc9-v5zrk   1/1     Running   0          45s   10.8.1.24   c1-worker   <none>           <none>
root@seven-demo:~# kubectl --context kind-c1 get svc -n sample
NAME          TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)   AGE
whereami-cs   ClusterIP   10.88.132.102   <none>        80/TCP    50s
```

在 c1 集群导出服务

```bash
subctl --context kind-c1 export service --namespace sample whereami-cs
```

在 c1 集群访问应该优先访问本集群的服务

```bash
kubectl --context kind-c1 exec -it client -- bash
```

```bash
nslookup whereami-cs.sample.svc.clusterset.local
```

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20230407165605.png)

```bash
curl whereami-cs.sample.svc.clusterset.local
```

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20230407165622.png)


查看 ServiceImport

```bash
kubectl --context kind-c1 get -n submariner-operator serviceimport
kubectl --context kind-c2 get -n submariner-operator serviceimport
```

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20230407165911.png)


查看 Endpointslice


```bash
kubectl --context kind-c1 get endpointslices -n sample
kubectl --context kind-c2 get endpointslices -n sample
```

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20230407165929.png)


### Headless Service + StatefulSet

在 c2 集群创建服务
```yaml
kubectl --context kind-c2 apply -f - <<EOF
apiVersion: v1
kind: Service
metadata:
 name: whereami-ss
 namespace: sample
 labels:
   app: whereami-ss
spec:
 ports:
 - port: 80
   name: whereami
 clusterIP: None
 selector:
   app: whereami-ss
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
 name: whereami
 namespace: sample
spec:
 serviceName: "whereami-ss"
 replicas: 3
 selector:
   matchLabels:
       app: whereami-ss
 template:
   metadata:
     labels:
       app: whereami-ss
   spec:
     containers:
     - name: whereami-ss
       image: cr7258/whereami:v1
       ports:
       - containerPort: 80
         name: whereami
       env:
       - name: NAMESPACE
         valueFrom:
           fieldRef:
             fieldPath: metadata.namespace
       - name: NODE_NAME
         valueFrom:
           fieldRef:
             fieldPath: spec.nodeName
       - name: POD_NAME
         valueFrom:
           fieldRef:
             fieldPath: metadata.name
       - name: POD_IP
         valueFrom:
          fieldRef:
             fieldPath: status.podIP
EOF
```

在 c2 集群查看服务

```bash
root@seven-demo:~# kubectl get pod -n sample --context kind-c2 -o wide
NAME                        READY   STATUS    RESTARTS   AGE   IP          NODE        NOMINATED NODE   READINESS GATES
whereami-0                  1/1     Running   0          38s   10.9.1.20   c2-worker   <none>           <none>
whereami-1                  1/1     Running   0          36s   10.9.1.21   c2-worker   <none>           <none>
whereami-2                  1/1     Running   0          31s   10.9.1.22   c2-worker   <none>           <none>
whereami-754776cdc9-28kgd   1/1     Running   0          20h   10.9.1.18   c2-worker   <none>           <none>
whereami-754776cdc9-8ccmc   1/1     Running   0          20h   10.9.1.17   c2-worker   <none>           <none>
whereami-754776cdc9-dlp55   1/1     Running   0          20h   10.9.1.16   c2-worker   <none>           <none>
root@seven-demo:~# kubectl get svc -n sample --context kind-c2
NAME          TYPE        CLUSTER-IP    EXTERNAL-IP   PORT(S)   AGE
whereami-cs   ClusterIP   10.99.2.201   <none>        80/TCP    20h
whereami-ss   ClusterIP   None          <none>        80/TCP    4m58s
```

在 c2 集群导出服务

```bash
subctl --context kind-c2 export service whereami-ss --namespace sample 
```

在 c1 集群访问 c2 集群服务

```bash
kubectl --context kind-c1 exec -it client -- bash
```

```
nslookup whereami-ss.sample.svc.clusterset.local
```

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20230407172948.png)


```bash
nslookup whereami-0.c2.whereami-ss.sample.svc.clusterset.local
```

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20230407173020.png)

```bash
curl whereami-ss.sample.svc.clusterset.local
```
![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20230407173037.png)

查看 ServiceImport

```bash
kubectl --context kind-c1 get -n submariner-operator serviceimport
kubectl --context kind-c2 get -n submariner-operator serviceimport
```

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20230407172906.png)

查看 Endpointslice

```bash
kubectl --context kind-c1 get endpointslices -n sample
kubectl --context kind-c2 get endpointslices -n sample
```

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20230407172932.png)

## 清理

```bash
subctl uninstall --context kind-broker
subctl uninstall --context kind-c1
subctl uninstall --context kind-c2

kind delete clusters broker c1 c2
```

## Ipsec 隧道

```
c1-gateway
--psk --encrypt --name submariner-cable-c2-172-19-0-10-0-0 --id 172.19.0.8 --host 172.19.0.8 --client 10.88.0.0/16 --ikeport 4500 --to --id 172.19.0.10 --host 172.19.0.10 --client 10.99.0.0/16 --ikeport 4500
--psk --encrypt --name submariner-cable-c2-172-19-0-10-0-1 --id 172.19.0.8 --host 172.19.0.8 --client 10.88.0.0/16 --ikeport 4500 --to --id 172.19.0.10 --host 172.19.0.10 --client 10.9.0.0/16 --ikeport 4500
--psk --encrypt --name submariner-cable-c2-172-19-0-10-1-0 --id 172.19.0.8 --host 172.19.0.8 --client 10.8.0.0/16 --ikeport 4500 --to --id 172.19.0.10 --host 172.19.0.10 --client 10.99.0.0/16 --ikeport 4500
--psk --encrypt --name submariner-cable-c2-172-19-0-10-1-1 --id 172.19.0.8 --host 172.19.0.8 --client 10.8.0.0/16 --ikeport 4500 --to --id 172.19.0.10 --host 172.19.0.10 --client 10.9.0.0/16 --ikeport 4500

c2-gateway
--psk --encrypt --name submariner-cable-c1-172-19-0-8-0-0 --id 172.19.0.10 --host 172.19.0.10 --client 10.99.0.0/16 --ikeport 4500 --to --id 172.19.0.8 --host 172.19.0.8 --client 10.88.0.0/16 --ikeport 4500
--psk --encrypt --name submariner-cable-c1-172-19-0-8-0-1 --id 172.19.0.10 --host 172.19.0.10 --client 10.99.0.0/16 --ikeport 4500 --to --id 172.19.0.8 --host 172.19.0.8 --client 10.8.0.0/16 --ikeport 4500
--psk --encrypt --name submariner-cable-c1-172-19-0-8-1-0 --id 172.19.0.10 --host 172.19.0.10 --client 10.9.0.0/16 --ikeport 4500 --to --id 172.19.0.8 --host 172.19.0.8 --client 10.88.0.0/16 --ikeport 4500
--psk --encrypt --name submariner-cable-c1-172-19-0-8-1-1 --id 172.19.0.10 --host 172.19.0.10 --client 10.9.0.0/16 --ikeport 4500 --to --id 172.19.0.8 --host 172.19.0.8 --client 10.8.0.0/16 --ikeport 4500
```