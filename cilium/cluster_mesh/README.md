# **Cilium 多集群 Cluster Mesh 介绍**

Cluster Mesh 是 Cilium 的多集群实现，可以帮助 Cilium 实现跨数据中心、跨 VPC 的多 Kubernetes 集群管理，Cluster Mesh 主要有以下功能：
- 1.通过隧道或直接路由的方式，在多个 Kubernetes 集群间进行 Pod IP 路由，而无需任何网关或代理。
- 2.使用标准 Kubernetes 服务发现机制。
- 3.跨多个集群的网络策略。策略可以使用 Kubernetes 原生的 NetworkPolicy 资源或者扩展的 CiliumNetworkPolicy CRD。
- 4.透明加密本集群以及跨集群节点间所有通信的流量。

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20220511125746.png)

接下来让我们一起看看 Cilium Cluster Mesh 有哪些具体的使用场景。

## 1 使用场景

### 1.1 高可用
对大多数人来说，高可用是最普遍的使用场景。可以在多个区域（regions）或可用区（availability zones）中运行多个 Kubernetes 集群，并在每个集群中运行相同服务的副本。 一旦发生异常，请求可以故障转移到其他集群。

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20220511145843.png)

### 1.2 共享服务
某些公共基础服务可以在集群间进行共享（如密钥管理，日志记录，监控或 DNS 服务等），以避免额外的资源开销。

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20220511145853.png)
### 1.3 拆分有状态和无状态服务
运行有状态或无状态服务的操作复杂性是非常不同的。无状态服务易于扩展，迁移和升级。 完全使用无状态服务运行集群可使集群保持灵活和敏捷。有状态服务（例如 MySQL，Elasticsearch, Etcd 等）可能会引入潜在的复杂依赖，迁移有状态服务通常涉及存储的迁移。为无状态和有状态服务分别运行独立的集群可以将依赖复杂性隔离到较少数量的集群中。

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20220511145905.png)

## 2 架构

Cilium Cluster Mesh 的架构如下：
-   每个 Kubernetes 集群都维护自己的 etcd 集群，保存自身集群的状态。来自多个集群的状态永远不会在本集群的 etcd 中混淆。
-   每个集群通过一组 **etcd 代理**暴露自己的 etcd，在其他集群中运行的 Cilium agent 连接到 etcd 代理以监视更改。
-   Cilium 使用 **clustermesh-apiserver** Pod 来建立多集群的互联，在 **clustermesh-apiserver** Pod 中有两个容器：其中 apiserver 容器负责将多集群的相关信息写入 etcd 容器；etcd 容器（etcd 代理）用来存储 Cluster Mesh 相关的配置信息。
-  **从一个集群到另一个集群的访问始终是只读的**。这确保了故障域保持不变，即一个集群中的故障永远不会传播到其他集群。

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20220511152250.png)

## 3 前提条件
### 3.1 安装相关软件
- 安装 Kubectl：https://kubernetes.io/zh/docs/tasks/tools/
- 安装 Kind：https://kind.sigs.k8s.io/docs/user/quick-start/#installation
- 安装 Helm：https://helm.sh/docs/intro/install/
- 安装 Cilium Cli：https://github.com/cilium/cilium-cli

[Kind [1]](https://kind.sigs.k8s.io/)（Kubernetes in Docker） 是一个使用 Docker 容器运行本地 Kubernetes 集群的工具。为了方便实验，本文使用 Kind 来搭建 Kubernetes 多集群环境。

### 3.2 环境要求
- 1.必须为所有 Kubernetes 的工作节点分配唯一的 IP 地址，并且节点之间 IP 路由可达。
- 2.每个集群都要分配唯一的 Pod CIDR。
- 3.Cilium 必须使用 etcd 作为 kv 存储。
- 4.集群之间的网络必须互通，具体的通信的端口号参见[防火墙规则 [2]](https://docs.cilium.io/en/stable/operations/system_requirements/#firewall-requirements)。

本实验相关的配置文件可以在: [cluster_mesh [3]](https://github.com/cr7258/kubernetes-guide/tree/master/cilium/cluster_mesh) 获取。

## 4 准备 Kubernetes 环境
准备两个 Kind 配置文件用于搭建 Kubernetes 集群。

c1 集群配置文件。
```yaml
# kind-config1.yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
- role: worker
networking:
  disableDefaultCNI: true # 禁用默认的 CNI
  podSubnet: "10.10.0.0/16"
  serviceSubnet: "10.11.0.0/16"
```
c2 集群 配置文件。
```yaml
# kind-config2.yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
- role: worker
networking:
  disableDefaultCNI: true # 禁用默认的 CNI
  podSubnet: "10.20.0.0/16"
  serviceSubnet: "10.21.0.0/16"
```

使用 `kind create cluster` 命令创建两个 Kubernetes 集群。
```bash
kind create cluster --config kind-config1.yaml --name c1
kind create cluster --config kind-config2.yaml --name c2
```

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20220509092022.png)

查看两个 Kubernetes 集群。
```bash
kubectl get node --context kind-c1 -o wide
kubectl get node --context kind-c2 -o wide
```

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20220509091440.png)
## 5 安装 Cilium
添加 Helm Repo。
```bash
helm repo add cilium https://helm.cilium.io/
```
在c1 集群上安装 Cilium，使用 `--kube-context`  参数指定不同的集群上下文。必须为每个集群分配一个唯一的名称和集群 id，`cluster.id` 参数指定集群 id，范围 1-255，`cluster.name` 参数指定集群名称。
```bash
helm install --kube-context kind-c1 cilium cilium/cilium --version 1.11.4 \
  --namespace kube-system \
  --set ipam.mode=kubernetes \
  --set cluster.id=1 \
  --set cluster.name=cluster1
```
在 c2 集群上安装 Cilium。
```bash
helm install --kube-context kind-c2 cilium cilium/cilium --version 1.11.4 \
  --namespace kube-system \
  --set ipam.mode=kubernetes \
  --set cluster.id=2 \
  --set cluster.name=cluster2
```

查看 Cilium Pod 状态。
```bash
kubectl --context kind-c1 get pod -A
kubectl --context kind-c2 get pod -A
```

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20220509095905.png)

查看 Cilium 状态。
```bash
cilium status --context kind-c1
cilium status --context kind-c2
```

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20220509181156.png)
## 6 安装 Metallb（可选）
在 **7 启用 Cluster Mesh** 章节中会介绍发布 **clustermesh-apiserver** 服务使用的 Service 类型，建议使用 LoadBalancer 类型的 Service，这样可以保证提供一个稳定且唯一的 LoadBalancer IP。在公有云提供的 Kubernetes 集群中，LoadBalancer 类型的 Service 通常会通过公有云的负载均衡设备（例如 AWS 的 ELB，阿里云的 SLB 等）来发布。在私有环境中可以使用 [MetalLB [4]](https://metallb.universe.tf/) 实现。

准备两个集群的 Metallb 配置文件。
c1 集群配置文件。注意分配的网络要和节点 IP 在同一网段。
```yaml
# metallb-config1.yaml
configInline:
  peers:
  address-pools:
  - name: default
    protocol: layer2
    addresses:
    - 172.22.0.50-172.22.0.100
```
c2 集群配置文件。
```yaml
configInline:
  peers:
  address-pools:
  - name: default
    protocol: layer2
    addresses:
    - 172.22.0.101-172.22.0.150
```
使用以下命令在 c1 和 c2 集群中部署 Metallb。
```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install --kube-context kind-c1 metallb bitnami/metallb \
  --namespace kube-system \
  -f metallb-config1.yaml
  
helm install --kube-context kind-c2 metallb bitnami/metallb \
  --namespace kube-system \
  -f metallb-config2.yaml
```

查看 Metallb Pod 状态。

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20220509114032.png)

## 7 启用 Cluster Mesh
使用 `cilium clustermesh enable` 命令在 c1 集群上启用 Cluster Mesh：
- `--create-ca` 参数表示自动创建 CA 证书，该证书需要在集群之间共享，以确保跨集群的 mTLS 能够正常工作。
- `--service-type` 参数指定发布 **clustermesh-apiserver** 服务的方式，有以下 3 种方式：
	- **LoadBalancer**（推荐）: 使用 LoadBalancer 类型的 Service 发布服务，这样可以使用稳定的 LoadBalancer IP，通常是最佳选择。
	- **NodePort**: 使用 NodePort 类型的 Service 发布服务，如果一个节点消失，Cluster Mesh 将不得不重新连接到另一个节点，可能会造成网络的中断。
	- **ClusterIP**: 使用 ClusterIP 类型的 Service 发布服务，这要求 ClusterIP 在集群间是可路由的。
	
```bash
cilium clustermesh enable --create-ca --context kind-c1 --service-type LoadBalancer
```

执行命令后会在集群中部署 clustermesh-apiserver 服务，并生成相关必要的证书。

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20220509114525.png)

创建的 CA 保存在 `kube-system` Namespace 下的 cilium-ca Secret 中。
```yaml
$ kubectl --context kind-c1 get secret -n kube-system cilium-ca -o yaml
apiVersion: v1
data:
  ca.crt: LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUNFekNDQWJxZ0F3SUJBZ0lVZmVPNHlYbVZSSU1ZZVppSjZyODJ6L05FejBVd0NnWUlLb1pJemowRUF3SXcKYURFTE1Ba0dBMVVFQmhNQ1ZWTXhGakFVQmdOVkJBZ1REVk5oYmlCR2NtRnVZMmx6WTI4eEN6QUpCZ05WQkFjVApBa05CTVE4d0RRWURWUVFLRXdaRGFXeHBkVzB4RHpBTkJnTlZCQXNUQmtOcGJHbDFiVEVTTUJBR0ExVUVBeE1KClEybHNhWFZ0SUVOQk1CNFhEVEl5TURVd09UQXpNemt3TUZvWERUSTNNRFV3T0RBek16a3dNRm93YURFTE1Ba0cKQTFVRUJoTUNWVk14RmpBVUJnTlZCQWdURFZOaGJpQkdjbUZ1WTJselkyOHhDekFKQmdOVkJBY1RBa05CTVE4dwpEUVlEVlFRS0V3WkRhV3hwZFcweER6QU5CZ05WQkFzVEJrTnBiR2wxYlRFU01CQUdBMVVFQXhNSlEybHNhWFZ0CklFTkJNRmt3RXdZSEtvWkl6ajBDQVFZSUtvWkl6ajBEQVFjRFFnQUVTQVNHRERDdnhsUmpYNTEwMEpCQnoxdXIKb29sMktUNVh6MUNYS1paVk5Pc1M5ZmVrOEJUOTRqTXpZcHpsZW5hZXdwczVDZGhWckkvSU9mK2RtaTR3UjZOQwpNRUF3RGdZRFZSMFBBUUgvQkFRREFnRUdNQThHQTFVZEV3RUIvd1FGTUFNQkFmOHdIUVlEVlIwT0JCWUVGTlVwCjBBRVROZ0JHd2ZEK0paRDFWV2w2elNvVk1Bb0dDQ3FHU000OUJBTUNBMGNBTUVRQ0lHZUszUklreUJzQnFxL0MKdzRFTU9nMjk1T244WDFyYVM5QVZMZmlzS2JJVEFpQW5Da3NQTm9BYmZVZ1lyMkVGaFZZaDU0bjlZMVlyU0NlZAprOEZ3Nnl2MWNBPT0KLS0tLS1FTkQgQ0VSVElGSUNBVEUtLS0tLQo=
  ca.key: LS0tLS1CRUdJTiBFQyBQUklWQVRFIEtFWS0tLS0tCk1IY0NBUUVFSU9uWG9WTmhIdEJ0TTFaMFFlTWE5UWlLV1QvdXVNMk9jUXNmU252bXEwL2RvQW9HQ0NxR1NNNDkKQXdFSG9VUURRZ0FFU0FTR0REQ3Z4bFJqWDUxMDBKQkJ6MXVyb29sMktUNVh6MUNYS1paVk5Pc1M5ZmVrOEJUOQo0ak16WXB6bGVuYWV3cHM1Q2RoVnJJL0lPZitkbWk0d1J3PT0KLS0tLS1FTkQgRUMgUFJJVkFURSBLRVktLS0tLQo=
kind: Secret
metadata:
  creationTimestamp: "2022-05-09T03:44:03Z"
  name: cilium-ca
  namespace: kube-system
  resourceVersion: "20625"
  uid: 7e4b2f21-815d-4191-974b-316c629e325c
type: Opaque
```

将 c1 集群的 Cilium CA 证书导入集群 c2。
```bash
# 将 c1 集群的 Cilium CA 证书导出
kubectl get secret --context kind-c1 -n kube-system cilium-ca -o yaml > cilium-ca.yaml
# 将 CA 证书导入 c2 集群
kubectl apply -f cilium-ca.yaml --context kind-c2
```

在 c2 集群上启用 Cluster Mesh。
```bash
cilium clustermesh enable --context kind-c2 --service-type LoadBalancer
```

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20220509115004.png)

查看 c1 和 c2 集群的 clustermesh-apiserver Pod 状态。

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20220509120827.png)

查看 c1 和 c2 集群的 clustermesh-apiserver Service，可以看到 Servie 的类型是 LoadBalancer，这是 Metallb 分配的 IP 地址。
```bash
kubectl --context kind-c1 get svc -A 
kubectl --context kind-c2 get svc -A 
```

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20220511162335.png)

查看 Cilium 状态。
```bash
cilium status --context kind-c1
cilium status --context kind-c2
```
![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20220509181041.png)

查看 c1 和 c2  集群的 Cluster Mesh 状态，当前两个集群都已经成功启用 Cluster Mesh，但是还未互相连接。
```bash
cilium clustermesh status --context kind-c1
cilium clustermesh status --context kind-c2
```

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20220509115212.png)


## 8 连接集群
在 c1 集群上执行 `cilium clustermesh connect` 命令连接 c2 集群。只需要在一个集群上执行即可。
```bash
cilium clustermesh connect --context kind-c1 --destination-context kind-c2
```

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20220509115353.png)


查看 Cilium Cluster Mesh 状态，此时 c1 和 c1 集群已经建立了 Cluster Mesh 连接。
```bash
cilium clustermesh status --context kind-c1
cilium clustermesh status --context kind-c2
```

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20220509120942.png)

现在我们已经成功建立了集群间的互联，接下来验证一下 Cluster Mesh 模式下的负载均衡和网络策略。

## 9 负载均衡
### 9.1 全局负载均衡
在集群中部署两个应用，其中 x-wing 是客户端，rebel-base 是服务端，要求对 rebel-base 服务实现全局负载均衡。需要保证每个集群中的 rebel-base 服务名称相同并且在相同的命名空间中，然后添加 `io.cilium/global-service: "true"` 声明为全局服务，这样 Cilium 便会自动对两个集群中的 Pod 执行负载均衡。
```yaml
apiVersion: v1
kind: Service
metadata:
  name: rebel-base
  annotations:
    io.cilium/global-service: "true" # 启用全局负载均衡
spec:
  type: ClusterIP
  ports:
  - port: 80
  selector:
    name: rebel-bas
```

在 c1 和 c2 集群创建应用服务。
```bash
kubectl apply -f cluster1.yaml --context kind-c1
kubectl apply -f cluster2.yaml --context kind-c2
```

查看服务。
```bash
kubectl --context kind-c1 get pod
kubectl --context kind-c1 get svc
kubectl --context kind-c2 get pod
kubectl --context kind-c2 get svc
```

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20220509122013.png)
在任意一个集群访问 rebel-base 服务，可以看到流量被分发到了两个集群。
```bash
for i in {1..10}; do kubectl exec --context kind-c1 -ti deployment/x-wing -- curl rebel-base; done
```

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20220509142925.png)
### 9.2 禁用全局服务共享
默认情况下，全局服务将在多个集群中的后端进行负载均衡。如果想要禁止本集群的服务被共享给其他集群，可以设置 `io.cilium/shared-service: "false"` 注解来实现。
```bash
kubectl annotate service rebel-base \
io.cilium/shared-service="false" --overwrite --context kind-c1
```

在 c1 集群可以访问到两个集群的 rebel-base 服务。
```bash
for i in {1..10}; do kubectl exec --context kind-c1 -ti deployment/x-wing -- curl rebel-base; done
```

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20220509143238.png)

但是此时 c2 集群就只能访问到本集群的 rebel-base 服务了。
```bash
for i in {1..10}; do kubectl exec --context kind-c2 -ti deployment/x-wing -- curl rebel-base; done
```

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20220509143731.png)

将 c1 集群 rebel-base 服务的注解 `io.cilium/shared-service` 去掉。

```bash
kubectl annotate service rebel-base io.cilium/shared-service- --context kind-c1
```

现在 c2 集群可以重新访问两个集群的 rebel-base 服务了。
```bash
for i in {1..10}; do kubectl exec --context kind-c2 -ti deployment/x-wing -- curl rebel-base; done
```

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20220509143921.png)
## 10 网络策略
创建 CiliumNetworkPolicy 策略只允许 c1 集群中带有 x-wing 标签的 Pod 访问 c2 集群中带有 rebel-base 标签的 Pod。集群名字是在 **5 安装 Cilium**章节中通过 `--cluster-name` 参数指定的，也可以在 **cilium-config** Configmap 中找到。除了应用服务之间的流量，还需注意放行 DNS 的流量，否则无法直接通过 Service 名字进行访问。

```yaml
# networkpolicy.yaml
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: "allow-dns"
spec:
  endpointSelector: {}
  egress:
    - toEndpoints:
        - matchLabels:
            io.kubernetes.pod.namespace: kube-system
            k8s-app: kube-dns
      toPorts:
        - ports:
            - port: "53"
              protocol: UDP
          rules:
            dns:
              - matchPattern: "*"
---
apiVersion: "cilium.io/v2"
kind: CiliumNetworkPolicy
metadata:
  name: "allow-cross-cluster"
spec:
  description: "Allow x-wing in cluster1 to contact rebel-base in cluster2"
  endpointSelector:
    matchLabels:
      name: x-wing
      io.cilium.k8s.policy.cluster: cluster1
  egress:
  - toEndpoints:
    - matchLabels:
        name: rebel-base
        io.cilium.k8s.policy.cluster: cluster2
```

Kubernetes 的网络策略不会自动发布到所有集群，你需要在每个集群上下发 `NetworkPolicy` 或 `CiliumNetworkPolicy`。
```bash
kubectl --context kind-c1 apply -f networkpolicy.yaml
kubectl --context kind-c2 apply -f networkpolicy.yaml
```

在 c1 集群上访问 rebel-base 服务，可以看到只有分发到 c2 集群上的请求才可以成功得到响应。
```bash
kubectl exec --context kind-c1 -ti deployment/x-wing -- curl rebel-base
```

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20220509145613.png)


## 11 Troubleshooting
在启用 Cluster Mesh 的时候遇到以下报错。

```bash
cilium clustermesh status --context kind-c1
```
![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20220509120001.png)

查看 Pod 信息发现拉取的镜像不存在。

```bash
kubectl --context kind-c1 describe pod -n kube-system  clustermesh-apiserver-754c5479dd-zsg8t
```

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20220509120223.png)

到 Cilium 镜像仓库上看了下发现镜像后面的 sha256 值对不上。

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20220509120320.png)

编辑 clustermesh-apiserver Deployment 的镜像，将镜像版本后面的 shasum 值去掉即可。
```bash
kubectl edit --context kind-c1 deployment -n kube-system clustermesh-apiserver
kubectl edit --context kind-c2 deployment -n kube-system clustermesh-apiserver
```

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20220509175220.png)



## 12 参考资料
- [1] Kind: https://kind.sigs.k8s.io/
- [2] 防火墙规则: https://docs.cilium.io/en/stable/operations/system_requirements/#firewall-requirements
- [3] cluster_mesh: https://github.com/cr7258/kubernetes-guide/tree/master/cilium/cluster_mesh
- [4] MetalLB: https://metallb.universe.tf/
- [5] 深入了解Cilium多集群: https://cloudnative.to/blog/deep-dive-into-cilium-multi-cluster/
- [6] API server for Cilium ClusterMesh: https://github.com/cilium/cilium/tree/master/clustermesh-apiserver
- [7] Setting up Cluster Mesh: https://docs.cilium.io/en/stable/gettingstarted/clustermesh/clustermesh/#gs-clustermesh
- [8] BurlyLuo/clustermesh: https://github.com/BurlyLuo/clustermesh
- [9] eCHO Episode 41: Cilium Clustermesh: https://www.youtube.com/watch?v=VBOONHW65NU&t=2653s
- [10] Deep Dive into Cilium Multi-cluster: https://cilium.io/blog/2019/03/12/clustermesh
- [11] Multi Cluster Networking with Cilium and Friends: https://cilium.io/blog/2022/04/12/cilium-multi-cluster-networking
- [12] Kubernetes Multi-Cluster Networking -Cilium Cluster Mesh: https://itnext.io/kubernetes-multi-cluster-networking-cilium-cluster-mesh-bca0f5367d84
- [13] A multi-cluster shared services architecture with Amazon EKS using Cilium ClusterMesh: https://aws.amazon.com/cn/blogs/containers/a-multi-cluster-shared-services-architecture-with-amazon-eks-using-cilium-clustermesh/

## 13 欢迎关注
![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20220104221116.png)