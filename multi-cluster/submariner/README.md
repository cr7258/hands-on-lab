## 环境准备

```bash
root@seven-demo:~# hostnamectl
   Static hostname: seven-demo
         Icon name: computer-vm
           Chassis: vm
        Machine ID: 4321d62ad63d44cbbc4dff3b6e282b26
           Boot ID: 3869510730c94566b2e83212c8bd7075
    Virtualization: kvm
  Operating System: Ubuntu 20.04.5 LTS
            Kernel: Linux 5.4.0-137-generic
      Architecture: x86-64
```

```bash
# 安装 Docker
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
kind create cluster --config - <<EOF
kind: Cluster
name: broker
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
networking:
  apiServerAddress: 10.138.0.11 # 替换成本机 IP
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
  apiServerAddress: 10.138.0.11 # 替换成本机 IP
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
  apiServerAddress: 10.138.0.11 # 替换成本机 IP
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
  name: nginx
  namespace: sample
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
        - name: nginx
          image: nginx
          ports:
            - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: nginx-cs
  namespace: sample
spec:
  selector:
    app: nginx
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
EOF
```


导出服务

```bash
subctl --context kind-c2 export service --namespace sample nginx-cs
```

c1,c2 集群会自动注入 ServiceImport

```bash
kubectl --context kind-c1 get -n submariner-operator serviceimport
kubectl --context kind-c2 get -n submariner-operator serviceimport
```

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20230405110341.png)


查看 Endpointslice

```bash
kubectl --context kind-c1 get endpointslices -n sample
kubectl --context kind-c2 get endpointslices -n sample
```

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20230405114226.png)


在 c1 集群访问 c2 集群的 nginx 服务

```bash
kubectl --context kind-c1 run client --image=cr7258/nettool:v1
kubectl --context kind-c1 exec -it client -- bash
```

```bash
curl nginx-cs.sample.svc.clusterset.local
```

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20230405114410.png)


```bash
nslookup nginx-cs.sample.svc.clusterset.local
```

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20230405114430.png)

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
  name: nginx
  namespace: sample
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
        - name: nginx
          image: nginx
          ports:
            - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: nginx-cs
  namespace: sample
spec:
  selector:
    app: nginx
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
EOF
```

导出服务

```bash
subctl --context kind-c1 export service --namespace sample nginx-cs
```

在 c1 集群访问应该优先访问本集群的服务

```bash
kubectl --context kind-c1 exec -it client -- bash
```

```bash
nslookup nginx-cs.sample.svc.clusterset.local
```

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20230405114712.png)

```bash
curl nginx-cs.sample.svc.clusterset.local
```

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20230405114734.png)

### Headless Service + StatefulSet

在 c2 集群创建服务
```yaml
kubectl --context kind-c2 apply -f - <<EOF
apiVersion: v1
kind: Service
metadata:
 name: nginx-ss
 namespace: sample
 labels:
   app: nginx-ss
spec:
 ports:
 - port: 80
   name: nginx
 clusterIP: None
 selector:
   app: nginx-ss
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
 name: nginx
 namespace: sample
spec:
 serviceName: "nginx-ss"
 replicas: 3
 selector:
   matchLabels:
       app: nginx-ss
 template:
   metadata:
     labels:
       app: nginx-ss
   spec:
     containers:
     - name: nginx-ss
       image: nginx
       ports:
       - containerPort: 80
         name: nginx
EOF
```

在 c2 集群导出服务

```bash
subctl --context kind-c2 export service nginx-ss --namespace sample 
```

在 c1 集群访问 c2 集群服务

```bash
kubectl --context kind-c1 exec -it client -- bash
```

```
nslookup nginx-ss.sample.svc.clusterset.local
```

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20230405115037.png)


```bash
nslookup nginx-0.c2.nginx-ss.sample.svc.clusterset.local
```

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20230405115111.png)

```bash
curl nginx-ss.sample.svc.clusterset.local
```

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20230405115137.png)

## 清理

```bash
subctl uninstall --context kind-broker
subctl uninstall --context kind-c1
subctl uninstall --context kind-c2

kind delete clusters broker c1 c2
```