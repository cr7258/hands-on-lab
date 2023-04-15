
Submariner 是一个完全开源的项目，可以帮助我们在不同的 Kubernetes 集群之间（无论是在本地还是云端）实现网络通信。Submariner 有以下功能：
-   跨集群的 L3 连接
-   跨集群的服务发现
-   Globalnet 支持 CIDR 重叠
-   提供命令行工具 subctl 简化部署和管理
-   兼容各种 CNI


## 1 Submariner 架构

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20230401141100.png)

Submariner 由几个主要部分组成：
-   **Broker**:  本质上是两个用于交换集群信息的 CRD（**Endpoint** 和 **Cluster**），我们需要选择一个集群作为 Broker 集群，其他集群连接到 Broker 集群的 API Server 来交换集群信息：
    -   **Endpoint**：包含了 Gateway Engine 建立集群间连接需要的信息，例如 Private IP 和 Public IP，NAT 端口等等。
    - **Cluster**：包含原始集群的静态信息，例如其 Service 和 Pod CIDR。
- **Gateway Engine**：管理连接到其他集群的隧道。
- **Route Agent**：负责将跨集群的流量路由到 active Gateway Node。
- **Service Discovery**: 提供跨集群的  DNS 服务发现。
- **Globalnet（可选）**：处理具有重叠 CIDR 的集群互连。
- **Submariner Operator**：负责在 Kubernetes 集群中安装 Submariner 组件，例如 Broker, Gateway Engine, Route Agent 等等。

### 1.1 Service Discovery

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20230401133606.png)
Submariner 中跨集群的 DNS 服务发现由以下两个组件基于 Kubernetes [Multi-Cluster Service APIs](https://github.com/kubernetes-sigs/mcs-api) 的规范来实现：
-   **Lighthouse Agent**：访问 Broker 集群的 API Server 与其他集群交换 ServiceImport 元数据信息。
    -  对于本地集群中已创建 ServiceExport 的每个 Service，Agent 创建相应的 ServiceImport 资源并将其导出到 Broker 以供其他集群使用。
    -  对于从其他集群导出到 Broker 中的 ServiceImport 资源，它会在本集群中创建它的副本。
-   **Lighthouse DNS Server**：
    -  Lighthouse DNS Server 根据 ServiceImport 资源进行 DNS 解析。
    -  CoreDNS 配置为将 `clusterset.local` 域名的解析请求发往 Lighthouse DNS server。

MCS API 是 Kubernetes 社区定义的用于跨集群服务发现的规范，主要包含了 ServiceExport 和 ServiceImport 两个 CRD。
- ServiceExport 定义了暴露（导出）到其他集群的 Service，由用户在要导出的 Service 所在的集群中创建，与 Service 的名字和 Namespace 一致。

```yaml
apiVersion: multicluster.k8s.io/v1alpha1
kind: ServiceExport
metadata:
  name: my-svc
  namespace: my-ns
```

- ServiceImport：当一个服务被导出后，实现 MCS API 的控制器会在所有集群（包括导出服务的集群）中自动生成一个与之对应的 ServiceImport 资源。

```yaml
apiVersion: multicluster.k8s.io/v1alpha1
kind: ServiceImport
metadata:
  name: my-svc
  namespace: my-ns
spec:
  ips:
  - 42.42.42.42 # 跨集群访问的 IP 地址
  type: "ClusterSetIP"
  ports:
  - name: http
    protocol: TCP
    port: 80
  sessionAffinity: None
```


### 1.2 Gateway Engine

Gateway Engine 部署在每个集群中，负责建立到其他集群的隧道。隧道可以由以下方式实现：
- IPsec，使用 Libreswan 实现。这是当前的默认设置。
- WireGuard，使用 wgctrl 库实现。
- VXLAN，不加密。

可以在使用 `subctl join` 命令加入集群的时候使用 `--cable-driver` 参数设置隧道的类型。

Gateway Engine 部署为 DaemonSet，只在有 `submariner.io/gateway=true`  Label 的 Node 上运行，当我们使用 `subctl join` 命令加入集群的时候，如果没有 Node 有该 Label，会提示我们选择一个 Node 作为 Gateway Node。

Submariner 也支持 active/passive 高可用模式的 Gateway Engine，我们可以在多个节点上部署 Gateway Engine。在同一时间内，只能有一个 Gateway Engine 处于 active 状态来处理跨集的流量，Gateway Engine 通过领导者选举的方式确定 active 的实例，其他实例在 passive 模式下等待，准备在 active 实例发生故障时接管。

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20230411220818.png)


### 1.3 Globalnet

Submariner 的一大亮点是支持在不同集群间存在 CIDR 重叠的情况，这有助于减少网络重构的成本。例如，在部署过程中，某些集群可能使用了默认的网段，导致了 CIDR 重叠。在这种情况下，如果后续需要更改集群网段，可能会对集群的运行产生影响。

为了支持集群间重叠 CIDR 的情况，Submariner 通过一个 GlobalCIDR 网段（默认是 242.0.0.0/8）在流量进出集群时进行 NAT 转换，所有的地址转换都发生在 active Gateway Node 上。在 `subctl deploy` 部署 Broker 的时候可以通过 `--globalnet-cidr-range` 参数指定所有集群的全局 GlobalCIDR。在 `subctl join` 加入集群的时候还可以通过 `--globalnet-cidr` 参数指定该集群的 GlobalCIDR。

导出的 ClusterIP 类型的 Service 会从 GlobalCIDR 分配一个 Global IP 用于入向流量，对于 Headless 类型的 Service，会为每个关联的 Pod 分配一个 Global IP 用于入向和出向流量。

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20230411222517.png)

## 2 环境准备

在本次实验中，我们使用一台运行 Ubuntu 20.04 的虚拟机，并通过 Kind 启动多个 Kubernetes 集群来进行测试。

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

安装相关软件和命令行工具。

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

# 安装 kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
mv kubectl /usr/local/bin
apt install -y bash-completion
echo 'source <(kubectl completion bash)' >>~/.bashrc

# 安装 subctl
curl -Lo subctl-release-0.14-linux-amd64.tar.xz https://github.com/submariner-io/subctl/releases/download/subctl-release-0.14/subctl-release-0.14-linux-amd64.tar.xz
tar -xf subctl-release-0.14-linux-amd64.tar.xz
mv subctl-release-0.14/subctl-release-0.14-linux-amd64 /usr/local/bin/subctl
chmod +x /usr/local/bin/subctl
```

## 3 快速开始

### 3.1 创建集群

使用 Kind 创建一个 3 节点的集群，这里读者需要将 `SERVER_IP` 替换成自己服务器的 IP。默认情况下，Kind 将 Kubernetes API 服务器 IP:Port 设置为本地环回地址 ( `127.0.0.1`): 随机端口，这对于从本机与集群交互来说很好，但是在本实验中多个 Kind 集群之间需要通信，因此我们需要把 Kind 的 apiServerAddress 改成本机 IP。

```yaml
# 替换成服务器 IP
export SERVER_IP="10.138.0.11"

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


### 3.2 部署 Broker

在本次实验中，我们专门将一个集群配置为 Broker 集群。Broker 集群可以是专用集群，也可以是连接的集群之一。执行 `subctl deploy-broker` 命令部署 Broker，Broker 只包含了一组 CRD，并没有部署 Pod 或者 Service。

```bash
subctl --context kind-broker deploy-broker
```

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20230407175528.png)

部署完成后，会生成 `broker-info.subm` 文件，文件以 Base64 加密，其中包含了连接 Broker 集群 API Server 的地址以及证书信息，还有 IPsec 的密钥信息。

```json
{
  "brokerURL": "https://10.138.0.11:45681",
  "ClientToken": {
    "metadata": {
      "name": "submariner-k8s-broker-admin-token-f7b62",
      "namespace": "submariner-k8s-broker",
      "uid": "3f949d19-4f42-43d6-af1c-382b53f83d8a",
      "resourceVersion": "688",
      "creationTimestamp": "2023-04-05T02:50:02Z",
      "annotations": {
        "kubernetes.io/created-by": "subctl",
        "kubernetes.io/service-account.name": "submariner-k8s-broker-admin",
        "kubernetes.io/service-account.uid": "da6eeba1-b707-4d30-8e1e-e414e9eae817"
      },
      "managedFields": [
        {
          "manager": "kube-controller-manager",
          "operation": "Update",
          "apiVersion": "v1",
          "time": "2023-04-05T02:50:02Z",
          "fieldsType": "FieldsV1",
          "fieldsV1": {
            "f:data": {
              ".": {},
              "f:ca.crt": {},
              "f:namespace": {},
              "f:token": {}
            },
            "f:metadata": {
              "f:annotations": {
                "f:kubernetes.io/service-account.uid": {}
              }
            }
          }
        },
        {
          "manager": "subctl",
          "operation": "Update",
          "apiVersion": "v1",
          "time": "2023-04-05T02:50:02Z",
          "fieldsType": "FieldsV1",
          "fieldsV1": {
            "f:metadata": {
              "f:annotations": {
                ".": {},
                "f:kubernetes.io/created-by": {},
                "f:kubernetes.io/service-account.name": {}
              }
            },
            "f:type": {}
          }
        }
      ]
    },
    "data": {
      "ca.crt": "LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUMvakNDQWVhZ0F3SUJBZ0lCQURBTkJna3Foa2lHOXcwQkFRc0ZBREFWTVJNd0VRWURWUVFERXdwcmRXSmwKY201bGRHVnpNQjRYRFRJek1EUXdOVEF5TkRVMU1Wb1hEVE16TURRd01qQXlORFUxTVZvd0ZURVRNQkVHQTFVRQpBeE1LYTNWaVpYSnVaWFJsY3pDQ0FTSXdEUVlKS29aSWh2Y05BUUVCQlFBRGdnRVBBRENDQVFvQ2dnRUJBSytXCmIzb0h1ZEJlbU5tSWFBNXQrWmI3TFhKNXRLWDB6QVc5a0tudjQzaGpoTE84NHlSaEpyY3ZSK29QVnNaUUJIclkKc01tRmx3aVltbU5ORzA4c2NLMTlyLzV0VkdFR2hCckdML3VKcTIybXZtYi80aHdwdmRTQjN0UDlkU2RzYUFyRwpYYllwOE4vUmlheUJvbTBJVy9aQjNvZ0MwK0tNcWM0NE1MYnBkZXViWnNSckErN2pwTElYczE3OGgxb25kdGNrClIrYlRnNGpjeS92NTkrbGJjamZSeTczbUllMm9DbVFIbE1XUFpSTkMveDhaTktGekl6UHc4SmZSOERjWk5Xc1YKa1NBUVNVUkpnTEhBbjY5MlhDSEsybmJuN21pcjYvYVZzVVpyTGdVNC9zcWg3QVFBdDFGQkk3NDRpcithTjVxSwpJRnRJenkxU3p2ZEpwMThza3EwQ0F3RUFBYU5aTUZjd0RnWURWUjBQQVFIL0JBUURBZ0trTUE4R0ExVWRFd0VCCi93UUZNQU1CQWY4d0hRWURWUjBPQkJZRUZFQUhFbndHditwTXNVcHVQRXNqbkQwTEgvSFpNQlVHQTFVZEVRUU8KTUF5Q0NtdDFZbVZ5Ym1WMFpYTXdEUVlKS29aSWh2Y05BUUVMQlFBRGdnRUJBQTFGckk1cGR1VTFsQzluVldNNwowYlc2VFRXdzYwUTlFVWdsRzc4bkRFZkNKb3ovY2xWclFNWGZrc2Zjc1VvcHZsaE5yWFlpbmd0UEE4aEMrTnRJCmdPZElDZDJGaWFOTjRCYkt3a1NmRkQvbmhjWDU1WmQ0UzN1SzZqb2JWVHIzaXVJRVhIdHg0WVIyS1ZuZitTMDUKQTFtbXdzSG1ZbkhtWEllOUEyL3hKdVhtSnNybWljWTlhMXhtSXVyYzhNalBsa1pZWVU1OFBvZHJFNi9XcnBaawpBbW9qcERIWWIrbnZxa0FuaG9hYUV3b2FEVGxYRjY0M3lVLy9MZE4wTmw5MWkvSHNwQ2tZdVFrQjJmQXNkSGNaCkMrdzQ4WVhYT21pSzZXcmJGYVJnaEVKdjB6UjdsZk50UEVZVWJHWEFxV0ZlSnFTdnM5aUYwbFV1NzZDNkt3YWIKbmdnPQotLS0tLUVORCBDRVJUSUZJQ0FURS0tLS0tCg==",
      "namespace": "c3VibWFyaW5lci1rOHMtYnJva2Vy",
      "token": "ZXlKaGJHY2lPaUpTVXpJMU5pSXNJbXRwWkNJNklqaHZWVnBuZVVoZk1uVTFjSEJxU1hOdE1UTk1NbUY0TFRaSlIyVlZVRGd4VjI1dmMyNXBNMjFYZFhjaWZRLmV5SnBjM01pT2lKcmRXSmxjbTVsZEdWekwzTmxjblpwWTJWaFkyTnZkVzUwSWl3aWEzVmlaWEp1WlhSbGN5NXBieTl6WlhKMmFXTmxZV05qYjNWdWRDOXVZVzFsYzNCaFkyVWlPaUp6ZFdKdFlYSnBibVZ5TFdzNGN5MWljbTlyWlhJaUxDSnJkV0psY201bGRHVnpMbWx2TDNObGNuWnBZMlZoWTJOdmRXNTBMM05sWTNKbGRDNXVZVzFsSWpvaWMzVmliV0Z5YVc1bGNpMXJPSE10WW5KdmEyVnlMV0ZrYldsdUxYUnZhMlZ1TFdZM1lqWXlJaXdpYTNWaVpYSnVaWFJsY3k1cGJ5OXpaWEoyYVdObFlXTmpiM1Z1ZEM5elpYSjJhV05sTFdGalkyOTFiblF1Ym1GdFpTSTZJbk4xWW0xaGNtbHVaWEl0YXpoekxXSnliMnRsY2kxaFpHMXBiaUlzSW10MVltVnlibVYwWlhNdWFXOHZjMlZ5ZG1salpXRmpZMjkxYm5RdmMyVnlkbWxqWlMxaFkyTnZkVzUwTG5WcFpDSTZJbVJoTm1WbFltRXhMV0kzTURjdE5HUXpNQzA0WlRGbExXVTBNVFJsT1dWaFpUZ3hOeUlzSW5OMVlpSTZJbk41YzNSbGJUcHpaWEoyYVdObFlXTmpiM1Z1ZERwemRXSnRZWEpwYm1WeUxXczRjeTFpY205clpYSTZjM1ZpYldGeWFXNWxjaTFyT0hNdFluSnZhMlZ5TFdGa2JXbHVJbjAub1JHM2d6Wno4MGVYQXk5YlZ5b1V2NmoyTERvdFJiNlJyOTF4d0ZiTDMwdFNJY3dnS3FYd3NZbVV1THhtcFdBb2M5LWRSMldHY0ZLYklORlZmUUttdVJMY2JsenlTUFFVMlB3WVVwN1oyNnlxYXFOMG1UQ3ZNWWxSeHp6cWY3LXlXUm8yNE9pWS1nMnNmNmNrRzRPMkdwa2MwTlNoOWRTUGY4dXJTbjZSVGJwbjFtcFZjTy1IQjJWeU5hTE9EdmtWS3RLVFJfVS1ZRGc1NzVtczM0OXM0X2xMZjljZjlvcjFaQXVvXzcyN0E5U0VvZ0JkN3BaSndwb0FEUHZRb1NGR0VLQWZYYTFXXzJWVE5PYXE4cUQxOENVbXVFRUFxMmtoNElBN0d5LVRGdUV2Q0JYUVlzRHYzUFJQTjZpOGlKSFBLVUN1WVNONS1NT3lGX19aNS1WdlhR"
    },
    "type": "kubernetes.io/service-account-token"
  },
  "IPSecPSK": {
    "metadata": {
      "name": "submariner-ipsec-psk",
      "creationTimestamp": null
    },
    "data": {
      "psk": "NL7dUK+RagDKPQZZj+7Q7wComj0/wLFbfvnHe12hHxR8+d/FnkEqXfmh8JMzLo6h"
    }
  },
  "ServiceDiscovery": true,
  "Components": [
    "service-discovery",
    "connectivity"
  ],
  "CustomDomains": null
}
```

### 3.3 c1, c2 加入集群

执行 `subctl join` 命令将 c1 和 c2 两个集群加入 Broker 集群。使用 `--clusterid` 参数指定集群 ID，每个集群 ID 需要唯一。提供上一步生成的 `broker-info.subm` 文件用于集群注册。

```bash
subctl --context kind-c1 join broker-info.subm --clusterid c1
subctl --context kind-c2 join broker-info.subm --clusterid c2
```

会提示我们选择一个节点作为 Gateway Node，c1 集群选择 c1-worker 节点作为 Gateway，c2 集群选择 c2-worker 节点作为 Gateway。

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20230405105146.png)


![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20230405105236.png)

两个 Gateway Node 的 IP 地址如下，之后会分别使用这两个地址在两个集群间建立隧道连接。

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20230406223135.png)

### 3.4 查看集群连接

等待 c1 和 c2 集群中 Submariner 的相关组件都运行成功后，执行以下命令查看集群间连接情况。

```bash
subctl show connections --context kind-c1
subctl show connections --context kind-c2
```

可以看到 c1 和 c2 集群分别和对方建立的连接。

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20230405105800.png)

查看 c1 gateway 日志，可以看到成功与 c2 集群建立了 IPsec 隧道。

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20230412094250.png)


### 3.5 测试跨集群通信

至此，我们已经成功在 c1 和 c2 集群间建立了跨集群的连接，接下来我们将创建服务并演示如何将其导出给其他集群进行访问。

在下面的示例中，我们在 sample Namespace 中创建相关资源。请注意，必须在两个集群中都创建 sample 命名空间，服务发现才能正常工作。

```bash
kubectl --context kind-c2 create namespace sample
# 需要确保 c1 集群上也有 sample Namespace，否则 Lighthouse agent 创建 Endpointslices 会失败
kubectl --context kind-c1 create namespace sample
```

#### 3.5.1 ClusterIP Service

首先测试 ClusterIP 类型的 Service。执行以下命令在 c2 集群创建服务。本实验中 whereami 是一个用 Golang 编写的 HTTP Server，它通过 Downward API 将 Kubernetes 的相关信息（Pod 名字，Pod 所在的 Namespace，Node）注入到容器的环境变量中，当接收到请求时进行输出。另外 whereami 还会打印请求方的 IP 地址和端口信息。

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

在 c2 集群查看服务。

```bash
root@seven-demo:~# kubectl --context kind-c2 get pod -n sample -o wide
NAME                        READY   STATUS    RESTARTS   AGE   IP          NODE        NOMINATED NODE   READINESS GATES
whereami-754776cdc9-28kgd   1/1     Running   0          19h   10.9.1.18   c2-control-plane   <none>           <none>
whereami-754776cdc9-8ccmc   1/1     Running   0          19h   10.9.1.17   c2-control-plane   <none>           <none>
whereami-754776cdc9-dlp55   1/1     Running   0          19h   10.9.1.16   c2-control-plane   <none>           <none>
root@seven-demo:~# kubectl --context kind-c2 get svc -n sample -o wide
NAME          TYPE        CLUSTER-IP    EXTERNAL-IP   PORT(S)   AGE   SELECTOR
whereami-cs   ClusterIP   10.99.2.201   <none>        80/TCP    19h   app=whereami
```

在 c2 集群中使用 `subctl export` 命令将服务导出。

```bash
subctl --context kind-c2 export service --namespace sample whereami-cs
```

该命令会在创建一个和 Service 相同名字和 Namespace 的 ServiceExport 资源。

```yaml
root@seven-demo:~# kubectl  get serviceexports --context kind-c2 -n sample whereami-cs -o yaml
apiVersion: multicluster.x-k8s.io/v1alpha1
kind: ServiceExport
metadata:
  creationTimestamp: "2023-04-06T13:04:15Z"
  generation: 1
  name: whereami-cs
  namespace: sample
  resourceVersion: "327707"
  uid: d1da8953-3fa5-4635-a8bb-6de4cd3c45a9
status:
  conditions:
  - lastTransitionTime: "2023-04-06T13:04:15Z"
    message: ""
    reason: ""
    status: "True"
    type: Valid
  - lastTransitionTime: "2023-04-06T13:04:15Z"
    message: ServiceImport was successfully synced to the broker
    reason: ""
    status: "True"
    type: Synced
```


ServiceImport 资源会由 Submariner 自动在 c1,c2 集群中创建，IP 地址是 Service 的 ClusterIP 地址。

```bash
kubectl --context kind-c1 get -n submariner-operator serviceimport
kubectl --context kind-c2 get -n submariner-operator serviceimport
```

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20230406210456.png)


在 c1 集群创建一个 client Pod 来访问 c2 集群的 whereami 服务。

```bash
kubectl --context kind-c1 run client --image=cr7258/nettool:v1
kubectl --context kind-c1 exec -it client -- bash
```

先尝试下 DNS 解析，ClusterIP Service 类型的 Service 可以通过以下格式进行访问 `<svc-name>.<namespace>.svc.clusterset.local`。

```bash
nslookup whereami-cs.sample.svc.clusterset.local
```

返回的 IP 是在 c2 集群 Service 的 ClusterIP 的地址。

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20230406210652.png)

我们查看一下 CoreDNS 的配置文件，这个 Configmap 会被 Submariner Operator 修改，将 `clusterset.local` 用于跨集群通信的域名交给 Lighthouse DNS 来解析。

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

Submariner 遵循以下逻辑来进行跨集群集的服务发现：
- 如果导出的服务在本地集群中不可用，Lighthouse DNS 从服务导出的远程集群之一返回 ClusterIP 服务的 IP 地址。
- 如果导出的服务在本地集群中可用，Lighthouse DNS 总是返回本地 ClusterIP 服务的 IP 地址。
- 如果多个集群从同一个命名空间导出具有相同名称的服务，Lighthouse DNS 会以轮询的方式在集群之间进行负载均衡。
- 可以在 DNS 查询前加上 `cluster-id` 前缀来访问特定集群的服务，`<cluster-id>.<svc-name>.<namespace>.svc.clusterset.local`。

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20230412105012.png)

通过 curl 命令发起 HTTP 请求。

```bash
curl whereami-cs.sample.svc.clusterset.local
```

返回结果如下，我们根据输出的 node_name 字段可以确认该 Pod 是在 c2 集群。

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20230406210720.png)

这里结合下图对流量进行简单的说明：流量从 c1 集群的 client Pod 发出，首先经过 veth-pair 到达 Node 的 Root Network Namespace，然后经过 Submariner Route Agent 设置的 vx-submariner 这个 VXLAN 隧道将流量发往 Gateway Node 上（c1-worker）。接着经过连接 c1 和 c2  集群的 IPsec 隧道到达对端，c2 集群的 Gateway Node（c2-worker）接收到流量后将，经过 iptables 的反向代理规则（在这过程中根据 ClusterIP 进行了 DNAT）最终发送到后端的 whereami Pod 上。

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20230412105105.png)

接下来我们在 c1 集群也创建相同的服务。

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

在 c1 集群上查看服务。

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

在 c1 集群导出服务。

```bash
subctl --context kind-c1 export service --namespace sample whereami-cs
```

查看 ServiceImport。

```bash
kubectl --context kind-c1 get -n submariner-operator serviceimport
kubectl --context kind-c2 get -n submariner-operator serviceimport
```

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20230412103408.png)

由于在 c1 集群本地也有相同的服务，因此这次请求将会发给 c1 集群的服务。

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20230412110826.png)

```bash
kubectl --context kind-c1 exec -it client -- bash
nslookup whereami-cs.sample.svc.clusterset.local
```

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20230407165605.png)

```bash
curl whereami-cs.sample.svc.clusterset.local
```

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20230407165622.png)

我们也可以通过 `<cluster-id>.<svc-name>.<namespace>.svc.clusterset.local` 来指定访问访问特定集群的 ClusterIP Service。例如我们指定访问 c2 集群的 Service。

```bash
curl c2.whereami-cs.sample.svc.clusterset.local
```

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20230412102357.png)

#### 3.5.2 Headless Service + StatefulSet

Submariner 还支持带有 StatefulSets 的 Headless Services，从而可以通过稳定的 DNS 名称访问各个 Pod。在单个集群中，Kubernetes 通过引入稳定的 Pod ID 来支持这一点，在单个集群中可以通过 `<pod-name>.<svc-name>.<ns>.svc.cluster.local` 格式来解析域名。跨集群场景下，Submariner 通过 `<pod-name>.<cluster-id>.<svc-name>.<ns>.svc.clusterset.local` 的格式来解析域名。

在 c2 集群创建 Headless Service 和 StatefulSet。

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

在 c2 集群查看服务。

```bash
root@seven-demo:~# kubectl get pod -n sample --context kind-c2 -o wide -l app=whereami-ss
NAME                        READY   STATUS    RESTARTS   AGE   IP          NODE        NOMINATED NODE   READINESS GATES
whereami-0                  1/1     Running   0          38s   10.9.1.20   c2-control-plane   <none>           <none>
whereami-1                  1/1     Running   0          36s   10.9.1.21   c2-control-plane    <none>           <none>
whereami-2                  1/1     Running   0          31s   10.9.1.22   c2-control-plane    <none>           <none>
root@seven-demo:~# kubectl get svc -n sample --context kind-c2 -l app=whereami-ss
NAME          TYPE        CLUSTER-IP    EXTERNAL-IP   PORT(S)   AGE
whereami-ss   ClusterIP   None          <none>        80/TCP    4m58s
```

在 c2 集群导出服务。

```bash
subctl --context kind-c2 export service whereami-ss --namespace sample 
```

解析 Headless Service 的域名可以得到所有 Pod 的 IP。

```bash
kubectl --context kind-c1 exec -it client -- bash
nslookup whereami-ss.sample.svc.clusterset.local
```

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20230407172948.png)

也可以指定单个 Pod 进行解析。

```bash
nslookup whereami-0.c2.whereami-ss.sample.svc.clusterset.local
```

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20230407173020.png)

通过域名访问指定的 Pod。

```bash
curl whereami-0.c2.whereami-ss.sample.svc.clusterset.local
```

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20230407180629.png)


查看 ServiceImport，在 IP 地址的一栏是空的，因为导出的服务类型是 Headless。

```bash
kubectl --context kind-c1 get -n submariner-operator serviceimport
kubectl --context kind-c2 get -n submariner-operator serviceimport
```

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20230412103703.png)

对于 Headless Service，Pod IP 是根据 Endpointslice 来解析的。

```bash
kubectl --context kind-c1 get endpointslices -n sample
kubectl --context kind-c2 get endpointslices -n sample
```

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20230412103836.png)


## 4 使用 Globalnet 解决 CIDR 重叠问题

接下来将演示如何通过 Submariner 的 Globalnet 功能来解决多集群间 CIDR 重叠的问题，在本实验中，我们将会创建 3 个集群，并且将每个集群的 Service 和 Pod CIDR 都设置成相同的。

### 4.1 创建集群

```yaml
# 替换成服务器 IP
export SERVER_IP="10.138.0.11"

kind create cluster --config - <<EOF
kind: Cluster
name: broker-globalnet
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
name: g1
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
- role: worker
networking:
  apiServerAddress: $SERVER_IP
  podSubnet: "10.7.0.0/16"
  serviceSubnet: "10.77.0.0/16"
EOF
 
kind create cluster --config - <<EOF
kind: Cluster
name: g2
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
- role: worker
networking:
  apiServerAddress: $SERVER_IP
  podSubnet: "10.7.0.0/16"
  serviceSubnet: "10.77.0.0/16"
EOF
```

### 4.2 部署 Broker

使用 `--globalnet=true` 参数启用 Globalnet 功能，使用 `--globalnet-cidr-range` 参数指定所有集群的全局 GlobalCIDR（默认 242.0.0.0/8）。

```bash
subctl --context kind-broker-globalnet deploy-broker --globalnet=true --globalnet-cidr-range 120.0.0.0/8
```

### 4.3 g1, g2 加入集群

使用 `--globalnet-cidr` 参数指定本集群的 GlobalCIDR。

```bash
subctl --context kind-g1 join broker-info.subm --clusterid g1 --globalnet-cidr 120.1.0.0/24
subctl --context kind-g2 join broker-info.subm --clusterid g2 --globalnet-cidr 120.2.0.0/24
```

### 4.4 查看集群连接

```bash
subctl show connections --context kind-g1
subctl show connections --context kind-g2
```

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20230408220921.png)


### 4.5 测试跨集群通信

在两个集群中都创建 sample 命名空间。

```bash
kubectl --context kind-g2 create namespace sample
kubectl --context kind-g1 create namespace sample
```

#### 4.5.1 ClusterIP Service

在 g2 集群创建服务。

```yaml
kubectl --context kind-g2 apply -f - <<EOF
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

在 g2 集群查看服务。

```bash
root@seven-demo:~/globalnet# kubectl --context kind-g2 get pod -n sample -o wide
NAME                        READY   STATUS    RESTARTS   AGE   IP         NODE        NOMINATED NODE   READINESS GATES
whereami-754776cdc9-72qd4   1/1     Running   0          19s   10.7.1.8   g2-control-plane    <none>           <none>
whereami-754776cdc9-jsnhk   1/1     Running   0          20s   10.7.1.7   g2-control-plane    <none>           <none>
whereami-754776cdc9-n4mm6   1/1     Running   0          19s   10.7.1.9   g2-control-plane    <none>           <none>
root@seven-demo:~/globalnet# kubectl --context kind-g2 get svc -n sample -o wide
NAME          TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)   AGE   SELECTOR
whereami-cs   ClusterIP   10.77.153.172   <none>        80/TCP    26s   app=whereami
```

在 g2 集群导出服务。

```bash
subctl --context kind-g2 export service --namespace sample whereami-cs
```

导出服务后，我们再查看一下 g2 集群的 Service，会发现 Submariner 自动在与导出的服务相同的命名空间中创建了一个额外的服务，并且设置 `externalIPs` 为分配给相应服务的 Global IP。

```bash
kubectl --context kind-g2 get svc -n sample
```

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20230408221802.png)


在g1 集群访问 g2 集群的 whereami 服务。

```bash
kubectl --context kind-g1 run client --image=cr7258/nettool:v1
kubectl --context kind-g1 exec -it client -- bash
```

DNS 将会解析到分配给 c2 集群 whereami 服务的 Global IP 地址，而不是服务的 ClusterIP IP 地址。

```bash
nslookup whereami-cs.sample.svc.clusterset.local
```

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20230408221918.png)

用 curl 命令发起 HTTP 请求，从输出的结果可以发现，在 g2 集群的 whereami 看来，请求的源 IP 是 120.1.0.5，也就是说当流量从 g1 发往 g2 集群时，在 g1 集群的 Gateway Node 上对流量进行了 SNAT 源地址转换。

```bash
curl whereami-cs.sample.svc.clusterset.local
```

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20230409115802.png)

这里结合下图对流量进行简单的说明：流量从 c1 集群的 client Pod 发出，经过 DNS 解析后应该请求 IP 120.2.0.253。首先经过 veth-pair 到达 Node 的 Root Network Namespace，然后经过 Submariner Route Agent 设置的 vx-submariner 这个 VXLAN 隧道将流量发往 Gateway Node 上（c1-worker）。**在 Gateway Node 上将源 IP 10.7.1.7 转换成了 120.1.0.5，** 然后通过 c1 和 c2  集群的 IPsec 隧道发送到对端，c2 集群的 Gateway Node（c2-worker）接收到流量后，经过 iptables 的反向代理规则（在这过程中根据 Global IP 进行了 DNAT）最终发送到后端的 whereami Pod 上。

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20230412112610.png)


我们可以分别查看 g1 和 g2 集群上 Gateway Node 的 Iptables 来验证 NAT 规则，首先执行 `docker exec -it g1-worker bash`  和 `docker exec -it g2-worker bash` 进入这两个节点，然后执行 `iptables-save` 命令可以看到 iptables 配置，以下我筛选了相关的 iptables 配置。

g1-worker 节点：

```bash
# 在出访的时候将源 IP 转换为 120.1.0.1-120.1.0.8 中的一个
-A SM-GN-EGRESS-CLUSTER -s 10.7.0.0/16 -m mark --mark 0xc0000/0xc0000 -j SNAT --to-source 120.1.0.1-120.1.0.8
```

g2-worker 节点：
```bash
# 访问 120.2.0.253:80 的流量跳转到 KUBE-EXT-ZTP7SBVPSRVMWSUN 链
-A KUBE-SERVICES -d 120.2.0.253/32 -p tcp -m comment --comment "sample/submariner-fzpkhsc5wssywpk5x3par6ceb6b2jinr external IP" -m tcp --dport 80 -j KUBE-EXT-ZTP7SBVPSRVMWSUN

# 跳转到 KUBE-SVC-ZTP7SBVPSRVMWSUN 链
-A KUBE-EXT-ZTP7SBVPSRVMWSUN -j KUBE-SVC-ZTP7SBVPSRVMWSUN

# 随机选择 whereami 后端的一个 Pod
-A KUBE-SVC-ZTP7SBVPSRVMWSUN -m comment --comment "sample/submariner-fzpkhsc5wssywpk5x3par6ceb6b2jinr -> 10.7.1.7:80" -m statistic --mode random --probability 0.33333333349 -j KUBE-SEP-BB74OZOLBDYS7GHU

-A KUBE-SVC-ZTP7SBVPSRVMWSUN -m comment --comment "sample/submariner-fzpkhsc5wssywpk5x3par6ceb6b2jinr -> 10.7.1.8:80" -m statistic --mode random --probability 0.50000000000 -j KUBE-SEP-MTZHPN36KRSHGEO6

-A KUBE-SVC-ZTP7SBVPSRVMWSUN -m comment --comment "sample/submariner-fzpkhsc5wssywpk5x3par6ceb6b2jinr -> 10.7.1.9:80" -j KUBE-SEP-UYVYXWJKZN2VHFJW

# DNAT 地址转换
-A KUBE-SEP-BB74OZOLBDYS7GHU -p tcp -m comment --comment "sample/submariner-fzpkhsc5wssywpk5x3par6ceb6b2jinr" -m tcp -j DNAT --to-destination 10.7.1.7:80

-A KUBE-SEP-MTZHPN36KRSHGEO6 -p tcp -m comment --comment "sample/submariner-fzpkhsc5wssywpk5x3par6ceb6b2jinr" -m tcp -j DNAT --to-destination 10.7.1.8:80

-A KUBE-SEP-UYVYXWJKZN2VHFJW -p tcp -m comment --comment "sample/submariner-fzpkhsc5wssywpk5x3par6ceb6b2jinr" -m tcp -j DNAT --to-destination 10.7.1.9:80
```



#### 4.5.2 Headless Service + StatefulSet

接下来测试 Globalnet 在 Headless Service + StatefulSet 场景下的应用。在 g2 集群创建服务。

```yaml
kubectl --context kind-g2 apply -f - <<EOF
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

在 g2 集群查看服务。

```bash
root@seven-demo:~# kubectl get pod -n sample --context kind-g2 -o wide -l app=whereami-ss
NAME         READY   STATUS    RESTARTS   AGE   IP          NODE        NOMINATED NODE   READINESS GATES
whereami-0   1/1     Running   0          62s   10.7.1.10   g2-worker   <none>           <none>
whereami-1   1/1     Running   0          56s   10.7.1.11   g2-worker   <none>           <none>
whereami-2   1/1     Running   0          51s   10.7.1.12   g2-worker   <none>           <none>
root@seven-demo:~# kubectl get svc -n sample --context kind-c2 -l app=whereami-ss
NAME          TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)   AGE
whereami-ss   ClusterIP   None         <none>        80/TCP    42h
```

在 g2 集群导出服务。

```bash
subctl --context kind-g2 export service whereami-ss --namespace sample 
```

在 g1 集群访问 g2 集群服务，Globalnet 会为每一个 Headless Service 关联的 Pod 分配一个 Global IP，用于出向和入向的流量。

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20230412113350.png)

```bash
kubectl --context kind-g1 exec -it client -- bash
nslookup whereami-ss.sample.svc.clusterset.local
```

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20230409120458.png)

指定解析某个 Pod。

```bash
nslookup whereami-0.g2.whereami-ss.sample.svc.clusterset.local
```

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20230409120514.png)

指定访问某个 Pod。

```bash
curl whereami-0.g2.whereami-ss.sample.svc.clusterset.local
```

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20230409120544.png)

查看 ServiceImport，在 IP 地址的一栏是空的，因为导出的服务类型是 Headless。

```bash
kubectl --context kind-g1 get -n submariner-operator serviceimport
kubectl --context kind-g2 get -n submariner-operator serviceimport
```

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20230412113955.png)

对于 Headless Service，Pod IP 是根据 Endpointslice 来解析的。

```bash
kubectl --context kind-g1 get endpointslices -n sample
kubectl --context kind-g2 get endpointslices -n sample
```

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20230412113838.png)

执行 `docker exec -it g2-worker bash` 命令进入 g2-worker 节点，然后执行 `iptables-save` 命令寻找相关的 Iptables 规则。

```bash
# SNAT
-A SM-GN-EGRESS-HDLS-PODS -s 10.7.1.12/32 -m mark --mark 0xc0000/0xc0000 -j SNAT --to-source 120.2.0.252

-A SM-GN-EGRESS-HDLS-PODS -s 10.7.1.11/32 -m mark --mark 0xc0000/0xc0000 -j SNAT --to-source 120.2.0.251

-A SM-GN-EGRESS-HDLS-PODS -s 10.7.1.10/32 -m mark --mark 0xc0000/0xc0000 -j SNAT --to-source 120.2.0.250

# DNAT
-A SUBMARINER-GN-INGRESS -d 120.2.0.252/32 -j DNAT --to-destination 10.7.1.12

-A SUBMARINER-GN-INGRESS -d 120.2.0.251/32 -j DNAT --to-destination 10.7.1.11

-A SUBMARINER-GN-INGRESS -d 120.2.0.250/32 -j DNAT --to-destination 10.7.1.10
```


## 5 清理环境

执行以下命令删除本次实验创建的 Kind 集群。

```bash
kind delete clusters broker c1 c2 g1 g2
```

## 6 总结

本文首先介绍了 Submariner 的架构，包括 Broker、Gateway Engine、Route Agent、Service Discovery、Globalnet 和 Submariner Operator。接着，通过实验向读者展示了 Submariner 在跨集群场景中如何处理 ClusterIP 和 Headless 类型的流量。最后，演示了 Submariner 的 Globalnet 是如何通过 GlobalCIDR 支持不同集群间存在 CIDR 重叠的情况。

## 7 欢迎关注
![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20220104221116.png)