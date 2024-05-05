# Crossplane 实战：构建统一的云原生控制平面

## 1 什么是 Crossplane

[Crossplane](https://www.crossplane.io/) 是一个开源的 Kubernetes 扩展，其核心目标是将 Kubernetes 转化为一个通用的控制平面，使其能够管理和编排分布于 Kubernetes 集群内外的各种资源。通过扩展 Kubernetes 的功能，Crossplane 对 Kubernetes 集群外部的资源进行了抽象，允许用户使用 Kubernetes 的 API 来统一管理云服务（例如 AWS EC2, S3 等等）以及基础设施等资源。

Crossplane 通过在 Kubernetes 上实现 Custom Resource Definition（CRD），为外部环境中的各种资源提供了统一的表示方式，例如计算实例、存储桶或网络配置等等。用户可以使用标准的 Kubernetes API 工具如 kubectl，通过声明式方式来创建和管理这些自定义资源。而 Crossplane 的 Providers 会负责将这些声明与底层云供应商的实际资源进行映射和同步。通过这种方式，Crossplane 赋予了 Kubernetes 统一管理跨云资源的能力，极大简化了基础设施的编排和生命周期管理。

随着平台工程（Platform Engineering）的兴起，Crossplane 也受到了越来越多的关注。作为平台工程中重要的组成部分，Crossplane 使平台工程师能够创建自定义的 API 和抽象，将原生 Kubernetes 的资源和云资源组合在一个控制平面下。通过 Crossplane，平台工程师可以将复杂的云资源细节隐藏在简单的抽象和 API 之后，为平台用户提供一致且简化的资源管理体验。平台用户只需关注平台暴露的抽象资源（例如经过简化的 big, small 的实例规格），而无需了解底层云资源实现的具体细节（比如具体的实例类型和区域名称）。

## 2 Crossplane 的核心概念

Crossplane 通过多个核心组件来实现对外部资源的管理，这些核心组件包括：

- **Crossplane pods** 包括核心的 Crossplane pod 和 Crossplane RBAC manager pod。这些 pod 共同管理所有的 Crossplane 组件和资源。
- **Providers** 是连接 Crossplane 到外部云供应商的桥梁。Providers 负责将 Kubernetes 的资源清单与底层云供应商的实际资源进行映射和同步。Crossplane 通过 Providers 来支持多个云供应商，例如 AWS、Azure、GCP 等等。你可以在 Upbound Marketplace 上找到 Crossplane 支持的 [Provider](https://marketplace.upbound.io/providers)。
- **Managed Resources（MR）** 代表 Providers 在 Kubernetes 集群之外创建的实际资源。例如，一个 AWS S3 存储桶或者一个 GCP Cloud SQL 实例。
- **Compositions** 是 Managed resources 的组合模板，它描述了如何将多个 Managed resources 组合在一起以创建一个更复杂的资源。例如，一个 Compositions 可以将数据库、网络、存储等资源组合在一起，以构建一个完整的基础设施环境。
- **Composite Resource Definitions（XRD）** 定义了自定义的 API schema，平台用户使用由 XRD 定义的 API schema 来创建 composite resources（XR）或者 Claims（XRC）。XRD 可以看作是创建 Kubernetes CRD 的脚手架，XRD 只需要填写少量的字段，Crossplane 就会根据 XRD 来自动创建相应的 Kubernetes CRD。
- **Composite Resources（XR）** 是通过 XRD 的定义创建的自定义资源，XRD 定义了组合资源的 schema，而 XR 则是这些定义实际的实例化对象。XR 通常代表了一个由多个 Managed resources 组合而成的资源。
- **Claims（XRC）** 和 XR 相似，区别是 XRC 是命名空间级别的资源，而 XR 则是集群级别的资源。XC 允许平台用户从命名空间中请求和使用 XR，Crossplane 则会根据 XRC 的声明来创建相应的 XR。这样可以实现资源在命名空间级别的隔离，不同团队的 XRC 彼此独立，互不影响，比如 team-a 和 team-b 都有一个名为 example-sql 的 XRC，但是在底层分别被映射到了不同的 XR（例如 team-a 的 example-sql XRC 被映射到 example-sql-xxxxx XR，而 team-b 的 example-sql XRC 则被映射到 example-sql-yyyyy XR） 。
- **Composition Functions** 允许你使用复杂的逻辑、编程语言来配置 Compositions。你可以在 Upbound Marketplace 上找到 Crossplane 支持的 [Functions](https://marketplace.upbound.io/functions)。
- **Configuration Packages** 是一个 OCI 容器镜像，其中可以包含所需的 Compositions、Composite Resource Definitions、Providers、Composition Functions 等资源，使用户可以通过安装 Configuration Packages 来快速部署和使用 Crossplane 的资源。

如果你是第一次接触 Crossplane，可能会觉得上面的概念有些抽象，不过不用担心，接下来我们会通过实际的例子来让你更好地理解这些概念。

## 3 前提条件

在开始实验之前，确保你已经安装了以下工具：

- [Docker](https://docs.docker.com/engine/install)：用于构建和运行容器，Kind 会使用 Docker 容器来作为 Kubernetes 的节点。
- [Kind](https://kind.sigs.k8s.io/docs/user/quick-start/#installation)： 一个用于在本地运行 Kubernetes 集群的工具。
- [Helm](https://helm.sh/docs/intro/install)：Kubernetes 的包管理工具，方便部署和管理应用程序。我们会使用 Helm 来安装 Crossplane。
- [Kubectl](https://kubernetes.io/docs/tasks/tools)：Kubernetes 的命令行工具，用于与 Kubernetes 集群进行交互。
- [Crossplane CLI](https://docs.crossplane.io/latest/cli)：Crossplane 的命令行工具，用于管理 Crossplane 的资源。
- [gcloud CLI](https://cloud.google.com/sdk/docs/install)：Google Cloud 的命令行工具，用于管理 GCP 资源。
- [envsubst](https://pypi.org/project/envsubst)：用于替换字符串中的环境变量。

在本文中我们将使用 Crossplane 在 Google Cloud Platform（GCP） 上创建云资源，因此你还需要准备一个 [GCP 账户](https://cloud.google.com/)，并且该账号必须设置好 [Billing Account ](https://cloud.google.com/billing/docs/how-to/manage-billing-account)用于扣费。

## 4 创建 Kubernetes 集群

首先，使用 Kind 创建一个 Kubernetes 集群。

```bash
kind create cluster --name crossplane-demo
```

## 5 安装 Crossplane

使用 Helm Chart 来安装 Crossplane。

```bash
helm repo add \
crossplane-stable https://charts.crossplane.io/stable

helm repo update

helm install crossplane \
crossplane-stable/crossplane \
--namespace crossplane-system \
--create-namespace
```

确保 Crossplane 的相关组件已经成功启动。

```bash
kubectl get pods -n crossplane-system

NAME                                       READY   STATUS    RESTARTS   AGE
crossplane-7b8f554c7d-6g2sb                1/1     Running   0          35s
crossplane-rbac-manager-7ff45b95bb-2zqxs   1/1     Running   0          35s
```

## 6 设置 GCP Provider

在本文中，我们将通过 Crossplane 在 GCP 上创建并管理 Cloud SQL 实例。因此，我们需要创建一个 GCP Service Account，并为其授予必要的权限。

[Cloud SQL](https://cloud.google.com/sql?hl=en ) 是 GCP 提供的一种完全托管的关系数据库服务。它支持 MySQL、PostgreSQL 和 SQL Server 等流行的关系型数据库引擎。


### 6.1 创建 GCP Service Account

首先，认证 gcloud CLI。执行命令后，浏览器会弹出一个窗口，让你选择一个 Google 账户进行登录。

```bash
gcloud auth login
```

接着，为本实验创建一个 GCP Project。

```bash
# 根据时间戳生成一个的 Project ID
export PROJECT_ID=crossplane-demo-$(date +%Y%m%d%H%M%S)
gcloud projects create ${PROJECT_ID}
```

执行以下命令后，浏览器会弹出一个窗口，请为 Project 关联一个用于扣费的 Billing Account。

```bash
open "https://console.cloud.google.com/billing/linkedaccount?project=$PROJECT_ID"
```

创建 Service Account 并赋予 admin 角色。注意：这里为了方便实验，我们直接赋予了 admin 角色，实际生产环境中请根据实际情况赋予适当的权限。

```bash
export SA_NAME=cr7258
export SA="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
export ROLE=roles/admin

gcloud iam service-accounts create $SA_NAME \
    --project $PROJECT_ID

gcloud projects add-iam-policy-binding \
    --role $ROLE $PROJECT_ID --member serviceAccount:$SA
```

### 6.2 生成 GCP 密钥文件

为 Service Account 生成一个密钥文件，密钥会被保存到我们在命令行中指定的 `gcp-creds.json` 文件中。

```bash
gcloud iam service-accounts keys create gcp-creds.json \
    --project $PROJECT_ID --iam-account $SA
```

### 6.3 为 GCP Service Account 创建 Kubernetes Secret

使用上一步下载的 Service Account 密钥文件创建一个 Kubernetes Secret，GCP Provider 将使用这个凭证来访问 GCP。

```bash
kubectl --namespace crossplane-system \
   create secret generic gcp-creds \
   --from-file creds=./gcp-creds.json
```

### 6.4 安装 GCP provider

使用以下命令安装 GCP Provider 以及配置 GCP Provider 的 ProviderConfig。envsubst 命令会将文件中的 `$PROJECT_ID` 变量替换为实际的 Project ID。

```bash
envsubst < providers/provider-gcp-sql.yaml | kubectl apply -f -
```

上述命令应用的资源文件如下：

```bash
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: provider-gcp-sql
spec:
  package: xpkg.upbound.io/upbound/provider-gcp-sql:v1.0.2
---
apiVersion: gcp.upbound.io/v1beta1
kind: ProviderConfig
metadata:
  name: providerconfig-gcp-sql
spec:
  projectID: $PROJECT_ID # replace with your GCP projectID
  credentials:
    source: Secret
    secretRef:
      namespace: crossplane-system
      name: gcp-creds
      key: creds
```

检查 GCP Provider 是否安装成功。

```bash
kubectl get providers

NAME                          INSTALLED   HEALTHY   PACKAGE                                              AGE
provider-gcp-sql              True        True      xpkg.upbound.io/upbound/provider-gcp-sql:v1.0.2      30s
upbound-provider-family-gcp   True        True      xpkg.upbound.io/upbound/provider-family-gcp:v1.0.2   25s
```

安装 GCP Provider 时，会创建出相关的 Pod 和 CRD 等资源。

```bash
kubectl get pods -n crossplane-system | grep gcp

NAME                                                      READY   STATUS    RESTARTS   AGE
provider-gcp-sql-480917e7b87a-d5fb58b7f-c9drv             1/1     Running   0          31s
upbound-provider-family-gcp-e484219aceb5-66c6864c-8v9gr   1/1     Running   0          33s


kubectl get crds | grep gcp

NAME                                                       CREATED AT
databaseinstances.sql.gcp.upbound.io                       2024-04-03T15:04:54Z
databases.sql.gcp.upbound.io                               2024-04-03T15:04:54Z
providerconfigs.gcp.upbound.io                             2024-04-03T15:04:52Z
providerconfigusages.gcp.upbound.io                        2024-04-03T15:04:52Z
sourcerepresentationinstances.sql.gcp.upbound.io           2024-04-03T15:04:54Z
sslcerts.sql.gcp.upbound.io                                2024-04-03T15:04:54Z
storeconfigs.gcp.upbound.io                                2024-04-03T15:04:52Z
users.sql.gcp.upbound.io                                   2024-04-03T15:04:54Z
```

如果你在安装 GCP Provider 时遇到以下报错，这是由于 GCP Provider 相关的CRD 还没来得及创建，可以等待一会儿再次尝试。

```
error: resource mapping not found for name: "providerconfig-gcp-sql" namespace: "" from "STDIN": no matches for kind "ProviderConfig" in version "gcp.upbound.io/v1beta1"
ensure CRDs are installed first
```

### 6.5 启用 SQL Admin API

启用 SQL Admin API，这样 Crossplane 才可以通过 API 来管理 GCP Cloud SQL 实例。

```bash
gcloud services enable sqladmin.googleapis.com --project $PROJECT_ID
```

## 7 实验

为了更好地理解 Crossplane 的核心概念，我们将通过 8 个实验从易到难来逐步进行学习。实验的所需的代码保存在我的 Github 仓库中，你可以通过以下命令将代码克隆到本地。

```bash
git clone https://github.com/cr7258/hands-on-lab.git
cd hands-on-lab/crossplane/quickstart
```

### 7.1 实验 1: 直接通过 Managed Resources 创建资源

Managed Resources（MR）代表了 Provider 在 Kubernetes 集群之外创建的外部资源（External Resources）。

在实验 1 中，我们先不引入 Compositions 等概念，而是使用最简单的方式通过 Managed Resources 来在 GCP 上创建一个 Cloud SQL 实例。


![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20240504153706.png)

资源清单如下：

- Cloud SQL 实例的名称是 `example-sql-instance`，实例的类型是 PostgreSQL 13，规格是 `db-custom-1-3840`，存储大小为 20GB，网络配置为允许所有 IP 访问。
- 然后为这个 Cloud SQL 实例创建一个用户 `example-sql-user`，用户的密码是 `test123`，通过一个 Secret 来提供。
- 在 `providerConfigRef` 字段中关联了在**第 6.4 步**创建的 GCP ProviderConfig，表示会使用这个 ProviderConfig 的相关凭证来访问 GCP 创建相应的资源。

```yaml
apiVersion: sql.gcp.upbound.io/v1beta1
kind: DatabaseInstance
metadata:
  name: example-sql-instance
spec:
  providerConfigRef:
    name: providerconfig-gcp-sql
  forProvider:
    databaseVersion: POSTGRES_13
    region: us-central1
    settings:
      - diskSize: 20
        tier: db-custom-1-3840
        ipConfiguration:
          - ipv4Enabled: true
            authorizedNetworks:
              - name: all
                value: 0.0.0.0/0
    deletionProtection: false
  writeConnectionSecretToRef: # 会往这个 secret 写入数据库连接信息
    name: example-sql-connection-secret
    namespace: crossplane-system
---
apiVersion: sql.gcp.upbound.io/v1beta1
kind: User
metadata:
  name: example-sql-user
spec:
  providerConfigRef:
    name: providerconfig-gcp-sql
  forProvider:
    instanceRef:
      name: example-sql-instance
    passwordSecretRef:
      key: password
      name: example-sql-password
      namespace: crossplane-system
---
apiVersion: v1
kind: Secret
metadata:
  name: example-sql-password
  namespace: crossplane-system
data:
  password: dGVzdDEyMw==  # echo -n test123 | base64
```

执行以下命令创建实验 1 的相关资源。

```bash
kubectl apply -f v1-managed-resources.yaml
```

查看创建的 Managed Resources，`EXTERNAL-NAME` 字段表示在云服务商上实际创建的资源名称。耐心等待一会后，User 和 DatabaseInstance 资源最终会变成 Ready 状态。

```bash
kubectl get managed
NAME                                       READY   SYNCED   EXTERNAL-NAME      AGE
user.sql.gcp.upbound.io/example-sql-user   True    True     example-sql-user   6m23s

NAME                                                       READY   SYNCED   EXTERNAL-NAME          AGE
databaseinstance.sql.gcp.upbound.io/example-sql-instance   True    True     example-sql-instance   6m23s
```

Managed Resources 也有对应的 Kubernetes CR（Custom Resources），我们也可以分别查看 DatabaseInstance 和 User 的资源。

```bash
kubectl get databaseinstances
NAME                   READY   SYNCED   EXTERNAL-NAME          AGE
example-sql-instance   True    True     example-sql-instance   6m51s

kubectl get user
NAME               READY   SYNCED   EXTERNAL-NAME      AGE
example-sql-user   True    True     example-sql-user   6m55s
```

在 DatabaseInstance 资源中我们设置了 `writeConnectionSecretToRef` 字段，这个字段指定了一个 Secret，Crossplane 会将数据库的连接信息（例如公网 IP，服务端证书等）写入这个 Secret 中。

```yaml
kubectl get secrets -n crossplane-system example-sql-connection-secret -o yaml

apiVersion: v1
data:
  attribute.server_ca_cert.0.cert: LS0tLS1......
  attribute.server_ca_cert.0.common_name: Qz1VUy......
  attribute.server_ca_cert.0.create_time: MjAyNC......
  attribute.server_ca_cert.0.expiration_time: MjAzNC0......
  attribute.server_ca_cert.0.sha1_fingerprint: MzI1MT......
  connectionName: Y3Jvc3......
  privateIP: ""
  publicIP: MzQuMTcwLjIxMy4xNTc=
  serverCACertificateCert: LS0tLS......
  serverCACertificateCommonName: Qz1VUy......
  serverCACertificateCreateTime: MjAyNC......
  serverCACertificateExpirationTime: MjAzNCv
  serverCACertificateSha1Fingerprint: MzI1MT......
kind: Secret
metadata:
  creationTimestamp: "2024-04-17T13:56:04Z"
  name: example-sql-connection-secret
  namespace: crossplane-system
  ownerReferences:
  - apiVersion: sql.gcp.upbound.io/v1beta1
    blockOwnerDeletion: true
    controller: true
    kind: DatabaseInstance
    name: example-sql-instance
    uid: bd67c5b8-397a-4728-80e9-66662905dd08
  resourceVersion: "6625"
  uid: 004999fa-13ef-4435-86c7-e4a1be8c5028
type: connection.crossplane.io/v1alpha1
```

在 GCP 控制台上查看我们刚刚创建的 Cloud SQL 实例。

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20240417220449.png)

可以看到，用户 `example-sql-user` 也被成功创建了。

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20240417220523.png)

尝试连接数据库。

```bash
export CONNECTION_SECRET=example-sql-connection-secret
# 获取实例公网 IP
export PGHOST=$(kubectl --namespace crossplane-system \
                    get secret $CONNECTION_SECRET \
                    --output jsonpath="{.data.publicIP}" | base64 -d)
export PGUSER=example-sql-user
export PGPASSWORD=test123

kubectl run postgresql-client --rm -ti --restart=Never \
  --image docker.io/bitnami/postgresql:16 --env PGPASSWORD=$PGPASSWORD \
  -- psql --host $PGHOST -U $PGUSER -d postgres -p 5432
```

成功连接 PostgreSQL 数据库。

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20240417221141.png)

执行 `exit` 退出 PostgreSQL 数据库。

实验完成后，执行以下命令清除环境，Crossplane 会负责清除 GCP 上的相关资源。

```bash
kubectl delete -f v1-managed-resources.yaml
```

### 7.2 实验 2: 通过 Compositions 组合多个资源

相信通过实验 1 的学习，你已经对 Crossplane 有了一个初步的了解。
在实验 2 中，我们将引入 Compositions 的概念。Compositions 是 Managed Resources 的组合模板，它描述了如何将多个 Managed Resources 组合到单个对象中。

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20240504161259.png)

例如下面的例子中，我们创建了一个名为 `gcp-postgresql` 的 Composition，它将实验 1 使用到的 DatabaseInstance 和 User 这两个 Managed Resources 组合在了一起。

```yaml
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: gcp-postgresql
  labels:
    provider: gcp
    db: postgresql
spec:
  compositeTypeRef: # 指定了可以使用这个 Composition 的 Composite Resources（XR）的 API 版本和 Kind
    apiVersion: example.com/v1alpha1
    kind: SQL
  resources:
    - name: databaseinstance
      base:
        apiVersion: sql.gcp.upbound.io/v1beta1
        kind: DatabaseInstance
        metadata:
          name: example-sql-instance
        spec:
          providerConfigRef:
            name: providerconfig-gcp-sql
          forProvider:
            databaseVersion: POSTGRES_13
            region: us-central1
            settings:
              - diskSize: 20
                tier: db-custom-1-3840
                ipConfiguration:
                  - ipv4Enabled: true
                    authorizedNetworks:
                      - name: all
                        value: 0.0.0.0/0
            deletionProtection: false
          writeConnectionSecretToRef:
            name: example-sql-connection-secret
            namespace: crossplane-system
    - name: user
      base:
        apiVersion: sql.gcp.upbound.io/v1beta1
        kind: User
        metadata:
          name: example-sql-user
        spec:
          providerConfigRef:
            name: providerconfig-gcp-sql
          forProvider:
            instanceSelector:
              matchControllerRef: true # 自动将 User 关联到通过同一个 Composite Resource 创建的 DatabaseInstance
            passwordSecretRef:
              key: password
              name: example-sql-password
              namespace: crossplane-system
```

在实验 1 中，用户可以通过创建 DatabaseInstance 和 User 这两个 CR 来创建 Cloud SQL 实例和用户，那么用户要怎么通过上面这个 `gcp-postgresql` Composition 来创建相应的 Cloud SQL 实例和用户呢？

Composition 只是一个模板，本身并不会向用户提供一个 Kubernetes CRD（Custom Resource Definition）来供用户创建资源，因此我们需要创建 Composite Resource Definitions（XRD）来使用这个模板。创建 XRD 后，Crossplane 会根据 XRD 来自动创建相应的 CRD（在本例中是 SQL CRD）。

通过 SQL CRD 创建的 SQL CR 就是 Crossplane 的 Composite Resources（XR）。另外，在上面的 `gcp-postgresql` Composition 资源中我们还通过 `compositeTypeRef` 字段指定了可以使用这个 Composition 的 Composite Resources（XR）的 API 版本和 Kind。

```yaml
apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
metadata:
  name: sqls.example.com
spec:
  group: example.com
  names:
    kind: SQL
    plural: sqls
  versions:
    - name: v1alpha1
      served: true
      referenceable: true
      schema:
        openAPIV3Schema: {}
```

执行以下命令创建实验 2 的相关资源。

```bash
kubectl apply -f v2-compositions.yaml
```

如果你在执行上述命令时遇到以下报错的话，这是因为 Crossplane 还没来得及创建出 SQL CRD 资源。没关系，重复执行该命令即可。后续的实验如果遇到相似的问题，可以采取相同的做法。

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20240417222200.png)

可以看到 Crossplane 根据 XRD 的定义创建了相应 SQL CRD 资源。

```yaml
kubectl get crd sqls.example.com -o yaml

apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: sqls.example.com
spec:
  group: example.com
  names:
    categories:
    - composite
    kind: SQL
    listKind: SQLList
    plural: sqls
    singular: sql
  scope: Cluster
......
    name: v1alpha1
    schema:
      openAPIV3Schema:
        properties:
......
```

你可以使用 `crossplane beta trace <resource kind> <resource name>` 命令来查看 Composite Resources 以及它所包含的 Managed Resources 的状态。请耐心等待一会，最终所有的资源都会变成 Ready 状态。

```bash
crossplane beta trace sql example-sql
NAME                                    SYNCED   READY   STATUS
SQL/example-sql                         True     True    Available
├─ DatabaseInstance/example-sql-q7lf2   True     True    Available
└─ User/example-sql-ztkss               True     True    Available
```

实验完成后，执行以下命令清除环境。

```bash
kubectl delete -f v2-compositions.yaml
```

### 7.3 实验 3: 自定义资源参数

在前面的实验中，Cloud SQL 示例的类型（`POSTGRES_13`）和规格（`db-custom-1-3840`）是固定的，这一点显然是不够灵活的。在实际的生产环境中，我们可能需要根据不同的需求来创建不同类型和规格的 Cloud SQL 实例。另外 `db-custom-1-3840` 这个规格名称对用户来说也不够直观和友好，用户可能更希望看到一些简单直接的规格名称，比如 `small`，`medium`，`large` 等等。

在实验 3 中，我们将通过自定义资源参数来解决上述的问题。首先，我们需要修改 Composite Resource Definitions 的定义，为 SQL CR 添加两个参数：`version` 和 `size`。

```yaml
apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
metadata:
  name: sqls.example.com
spec:
  group: example.com
  names:
    kind: SQL
    plural: sqls
  versions:
  - name: v1alpha1
    served: true
    referenceable: true
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            type: object
            properties:
              parameters:
                type: object
                properties:
                  version:
                    description: The DB version depends on the DB type and versions available in the selected provider.
                    type: string
                  size:
                    description: "Supported sizes: small, medium, large"
                    type: string
                    default: small
                required:
                - version
            required:
            - parameters
```

在 Composition 中，我们通过 `patches` 字段来将 SQL CR 中的参数映射到 DatabaseInstance 的 `databaseVersion` 和 `settings.tier` 字段。
其中我们通过 `map` 类型的 transforms 来将 `small`，`medium`，`large` 规格映射到 `db-custom-1-3840`，`db-custom-2-7680`，`db-custom-4-15360` 这些实际的规格名称。

```yaml 
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: gcp-postgresql
  labels:
    provider: gcp
    db: postgresql
spec:
  compositeTypeRef:
    apiVersion: example.com/v1alpha1
    kind: SQL
  resources:
  - name: databaseinstance
    base:
      apiVersion: sql.gcp.upbound.io/v1beta1
      kind: DatabaseInstance
      spec:
        forProvider:
          # databaseVersion: POSTGRES_13
          region: us-central1
          settings:
          - diskSize: 20
            # tier: db-custom-1-3840
            ipConfiguration:
            - ipv4Enabled: true
              authorizedNetworks:
              - name: all
                value: 0.0.0.0/0
          deletionProtection: false   
          ......
    patches:
    ......
    - fromFieldPath: spec.parameters.version
      toFieldPath: spec.forProvider.databaseVersion
      transforms:
      - type: string
        string:
          fmt: POSTGRES_%s
          type: Format
    - fromFieldPath: spec.parameters.size
      toFieldPath: spec.forProvider.settings[0].tier
      transforms:
      - type: map
        map:
          small: db-custom-1-3840
          medium: db-custom-2-7680
          large: db-custom-4-15360
    ......
```

在创建 SQL CR 时，我们就可以通过 `version` 字段来指定 Cloud SQL 实例的 PostgreSQL 版本，并通过 `size` 字段来指定实例的规格。

```yaml
apiVersion: example.com/v1alpha1
kind: SQL
metadata:
  name: example-sql
spec:
  compositionSelector:
    matchLabels:
      provider: gcp
      db: postgresql
  parameters:
    version: "13"
    size: small
```

执行以下命令创建实验 3 的相关资源。

```bash
kubectl apply -f v3-customize-parameter.yaml
```

查看创建的相关资源。

```bash
crossplane beta trace sql example-sql
NAME                                       SYNCED   READY   STATUS
SQL/example-sql                            True     True    Available
├─ DatabaseInstance/example-sql-instance   True     True    Available
└─ User/example-sql-user                   True     True    Available
```

实验完成后，执行以下命令清除环境。

```bash
kubectl delete -f v3-customize-parameter.yaml
```

### 7.4 实验 4: 添加数据库

在实验 4 中，我们准备在 Cloud SQL 实例中添加一个数据库。

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20240505105845.png)

为此，我们需要修改 Composite Resource Definitions 的定义，为 SQL CR 添加一个新的参数 `database`。

```yaml
apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
metadata:
  name: sqls.example.com
spec:
  group: example.com
  names:
    kind: SQL
    plural: sqls
  versions:
  - name: v1alpha1
    served: true
    referenceable: true
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            type: object
            properties:
              parameters:
                type: object
                properties:
                  ......
                  database:
                    description: The database to create inside the DB server.
                    type: string
                  ......
```

然后在 Composition 中添加一个新的 Managed Resource `Database`，并通过 `patches` 字段将 SQL CR 中的 `database` 参数映射到 Database 的 `name` 字段。

```yaml
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: gcp-postgresql
  labels:
    provider: gcp
    db: postgresql
spec:
  compositeTypeRef:
    apiVersion: example.com/v1alpha1
    kind: SQL
  resources:
  ......
  - name: database
    base:
      apiVersion: sql.gcp.upbound.io/v1beta1
      kind: Database
      spec:
        providerConfigRef:
          name: providerconfig-gcp-sql      
        forProvider:
          instanceSelector:
            matchControllerRef: true
    patches:
    - fromFieldPath: spec.parameters.database
      toFieldPath: metadata.name
```

在创建 SQL CR 时，我们就可以通过 `database` 字段来指定要创建的数据库名称了。在这里我们指定创建一个名为 `example-db` 的数据库。

```yaml
apiVersion: example.com/v1alpha1
kind: SQL
metadata:
  name: example-sql
spec:
  compositionSelector:
    matchLabels:
      provider: gcp
      db: postgresql
  parameters:
    version: "13"
    size: small
    database: example-db
```

执行以下命令创建实验 4 的相关资源。

```bash
kubectl apply -f v4-add-database.yaml
```

查看创建的相关资源。可以看到除了创建了 DatabaseInstance 和 User 这两个 Managed Resources 外，还创建了一个 Database Managed Resource。

```bash
crossplane beta trace sql example-sql
NAME                                       SYNCED   READY   STATUS
SQL/example-sql                            True     True    Available
├─ DatabaseInstance/example-sql-instance   True     True    Available
├─ User/example-sql-user                   True     True    Available
└─ Database/example-db                     True     True    Available
```

在 GCP 控制台上可以看到刚刚在 Cloud SQL 实例中创建的数据库 `example-db`。

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20240420222524.png)

实验完成后，执行以下命令清除环境。

```bash
kubectl delete -f v4-add-database.yaml
```

### 7.5 实验 5: 添加数据库表

[Atlas](https://atlasgo.io) 是一款开源的数据库 schema 管理工具，允许用户以声明式地方式来管理数据库的 schema。[Atlas Kubernetes Operator](https://atlasgo.io/integrations/kubernetes/operator) 是一个 Kubernetes Operator，它可以将 Atlas 的 schema 管理能力集成到 Kubernetes 中，使得用户可以通过创建 Atlas 相关的 CR（例如 AtlasSchema）来声明式地管理数据库的 schema。

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20240505105757.png)

首先，修改 Composite Resource Definitions 的定义，为 SQL CR 添加一个新的参数 `schema`。

```yaml
apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
metadata:
  name: sqls.example.com
spec:
  group: example.com
  names:
    kind: SQL
    plural: sqls
  versions:
  - name: v1alpha1
    served: true
    referenceable: true
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            type: object
            properties:
              parameters:
                type: object
                properties:
                  ......
                  schema:
                    description: The SQL to apply the database schema.      
                    type: string
                  ......
```

在之前创建的 Composition 中，我们没有设置 `spec.mode` 字段，这意味着它使用了默认的值 `Resources`。在 `Resources` 模式下，Composition 允许我们使用内置的 patch 和 transform 操作来处理输入的资源。

而这次我们将 `spec.mode` 设置为了 `Pipeline`，并在 `pipeline` 字段中定义了两个 step：`patch-and-transform` 和 `schema`，每个 step 都会调用 `functionRef` 关联的 Functions 来处理输入的资源。

- 在 `patch-and-transform` step 中使用了 [patch-and-transform](https://github.com/crossplane-contrib/function-patch-and-transform) Function，其作用和内置的 patch 和 transform 功能基本相同，但是有着更多的优点：比如可以在没有 Kubernetes 集群的情况下使用 CLI 来渲染模板，另外还有助于将 Composition 新特性的功能开发与 Crossplane 的核心代码相解耦。因此 Crossplane 有打算废弃内置的  patch 和 transform 功能，并鼓励用户使用  `patch-and-transform` Function，详情可以参考 [Issue: Deprecate "native" patch and transform Composition](https://github.com/crossplane/crossplane/issues/4746)。
- 在 `schema` step 中使用了 [go-templating](https://github.com/crossplane-contrib/function-go-templating) Function，它可以使用 Go 模板来生成资源的 YAML 配置。在这里，我们使用 Go 模板生成一个 Object 类型的资源。在实验 5 中，我们还需要额外安装 Kubernetes Provider，来根据这个 Object 类型的资源创建出相应的 AtlasSchema 资源，以供 Atlas Kubernetes Operator 进行消费。在 Go template 中，我们可以使用 `$.observed.composite.resource` 来获取在 SQL CR（Composite Resource）中定义的参数。

```yaml
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: gcp-postgresql
  labels:
    provider: gcp
    db: postgresql
spec:
  compositeTypeRef:
    apiVersion: example.com/v1alpha1
    kind: SQL
  mode: Pipeline
  pipeline:
  - step: patch-and-transform
    functionRef:
      name: crossplane-contrib-function-patch-and-transform 
    input:
      apiVersion: pt.fn.crossplane.io/v1beta1
      kind: Resources
      resources:
      - name: databaseinstance
        base:
          apiVersion: sql.gcp.upbound.io/v1beta1
          kind: DatabaseInstance
      ......
      - name: user
        base:
          apiVersion: sql.gcp.upbound.io/v1beta1
          kind: User
      ......
      - name: database
        base:
          apiVersion: sql.gcp.upbound.io/v1beta1
          kind: Database
      ......
  - step: schema
    functionRef:
      name: crossplane-contrib-function-go-templating
    input:
      apiVersion: gotemplating.fn.crossplane.io/v1beta1
      kind: GoTemplate
      source: Inline
      inline:
        template: |
          apiVersion: kubernetes.crossplane.io/v1alpha1
          kind: Object
          metadata:
            name: {{ $.observed.composite.resource.metadata.name }}-schema-{{ $.observed.composite.resource.spec.parameters.database }}
            annotations:
              gotemplating.fn.crossplane.io/composition-resource-name: {{ $.observed.composite.resource.metadata.name }}-schema-{{ $.observed.composite.resource.spec.parameters.database }}
          spec:
            providerConfigRef:
              name: providerconfig-kubernetes
            forProvider:
              manifest:
                apiVersion: db.atlasgo.io/v1alpha1
                kind: AtlasSchema
                metadata:
                  name: {{ $.observed.composite.resource.metadata.name }}-{{ $.observed.composite.resource.spec.parameters.database }}
                  namespace: crossplane-system
                spec:
                  credentials:
                    scheme: postgres
                    hostFrom:
                      secretKeyRef:
                        key: publicIP
                        name: {{ $.observed.composite.resource.metadata.name }}-connection-secret
                    port: 5432
                    user: {{ $.observed.composite.resource.metadata.name }}-user
                    passwordFrom:
                      secretKeyRef:
                        key: password
                        name: example-sql-password
                    database: {{ $.observed.composite.resource.spec.parameters.database }}
                    parameters:
                      sslmode: disable
                  schema: 
                    sql: "{{ $.observed.composite.resource.spec.parameters.schema }}"
```

在创建 SQL CR 时，我们就可以通过 `schema` 字段来指定要创建的数据库表了。在这里我们创建了一个名为 `videos` 的表。

```yaml
apiVersion: example.com/v1alpha1
kind: SQL
metadata:
  name: example-sql
spec:
  compositionSelector:
    matchLabels:
      provider: gcp
      db: postgresql
  parameters:
    version: "13"
    size: small
    database: example-db
    schema: |
      create table videos (
        id varchar(50) not null,
        description text,
        primary key (id)
      );
```

在创建实验 5 的相关资源之前，我们需要先安装所需的 Kubernetes Provider 以及 `patch-and-transform` 和 `go-templating` Function。
其中 Kubernetes Provider 比较特殊，因为它需要和 API Server 进行交互从而在集群中创建 Kubernetes 对象，因此我们需要为它创建一个 Service Account，并将赋予相应的权限。

```bash
kubectl apply -f providers/provider-kubernetes.yaml
kubectl apply -f functions.yaml
```

确认 Kubernetes Provider 和 Function 相关的 Pod 已经正常运行。

```bash
kubectl get pod -n crossplane-system
NAME                                                              READY   STATUS    RESTARTS   AGE
crossplane-contrib-function-go-templating-eff9a0400879-949wlg5r   1/1     Running   0          37s
crossplane-contrib-function-patch-and-transform-6072b6a090pgl9n   1/1     Running   0          36s
provider-kubernetes-a3cbbe355fa7-864bc5b48d-l924z                 1/1     Running   0          48s
# 提前安装 auto-ready Function，实验 6 中会用到，这里先不用管
crossplane-contrib-function-auto-ready-ad9454a37aa7-6dd558n8z6p   1/1     Running   0          36s 
......
```

另外还需要安装 Atlas Kubernetes Operator 来根据 AtlasSchema 资源在 Cloud SQL 实例中创建数据库表。

```bash
helm install atlas-operator \
  oci://ghcr.io/ariga/charts/atlas-operator \
  --namespace atlas-operator --create-namespace
```

执行以下命令创建实验 5 的相关资源。

```bash
kubectl apply -f v5-add-table.yaml
```

查看创建的相关资源。细心的你可能会发现，Composite Resources 的状态不是 Ready，这是因为 Object Managed Resource 是通过 `go-templating` Function 生成的，因此 Crossplane 并不知道这个资源的状态。我们在实验 6 中将使用 [auto-ready](https://github.com/crossplane-contrib/function-auto-ready) Function 来解决这个问题。

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20240420223443.png)

连接数据库查看创建的表。

```bash
export CONNECTION_SECRET=example-sql-connection-secret
export PGHOST=$(kubectl --namespace crossplane-system \
                    get secret $CONNECTION_SECRET \
                    --output jsonpath="{.data.publicIP}" | base64 -d)
export PGUSER=example-sql-user
export PGPASSWORD=test123

kubectl run postgresql-client --rm -ti --restart=Never \
  --image docker.io/bitnami/postgresql:16 --env PGPASSWORD=$PGPASSWORD \
  -- psql --host $PGHOST -U $PGUSER -d postgres -p 5432
```

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20240420223837.png)

假设我们想要修改表结构，我们可以通过修改 SQL CR 中的 `schema` 字段来实现。例如下面的例子中，我们往 `videos` 表中添加了一个 `rating` 字段。

```yaml
cat << EOF | kubectl apply -f -
apiVersion: example.com/v1alpha1
kind: SQL
metadata:
  name: example-sql
spec:
  compositionSelector:
    matchLabels:
      provider: gcp
      db: postgresql
  parameters:
    version: "13"
    size: small
    database: example-db
    schema: |
      create table videos (
        id varchar(50) not null,
        description text,
        primary key (id),
        rating integer
      );
EOF
```

再次查看数据库表结构，可以看到 `rating` 字段已经成功添加。

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20240421081154.png)

执行 `exit` 命令退出 PostgreSQL 数据库。

实验完成后，执行以下命令清除环境。

```
kubectl delete -f v5-add-table.yaml
```

### 7.6 实验 6: Auto-Ready Function

[auto-ready](https://github.com/crossplane-contrib/function-auto-ready) Function 可以用于检测 Composite Resources 相关的 Managed Resources 的状态，当所有的 Managed Resources 都处于 Ready 状态时，auto-ready Function 会自动将 Composite Resources 标记为 Ready。auto-ready Function 的使用方式非常简单，不需要设置任何参数。

```yaml
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: gcp-postgresql
  labels:
    provider: gcp
    db: postgresql
spec:
  compositeTypeRef:
    apiVersion: example.com/v1alpha1
    kind: SQL
  mode: Pipeline
  pipeline:
  ......
  - step: automatically-detect-ready-composed-resources
    functionRef:
      name: crossplane-contrib-function-auto-ready
```

执行以下命令创建实验 6 的相关资源。

```bash
kubectl apply -f v6-auto-ready.yaml
```

查看创建的相关资源。可以看到这次创建的 Composite Resources 现在处于 Ready 状态了。

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20240419225723.png)

实验完成后，执行以下命令清除环境。

```
kubectl delete -f v6-auto-ready.yaml
```

### 7.7 实验 7: 使用 Claims 在命名空间创建资源

在 Kubernetes 中我们通常是通过 Namespace 来对不同团队的资源进行隔离，各个团队的资源不会相互干扰。然而在前面的实验中创建的 SQL CR（Composite Resource）以及 Managed Resources 都是集群级别的资源，我们应该对平台用户屏蔽这些集群级别的资源。

那么平台用户要如何创建这些资源呢？答案是使用 Claims（XRC）。平台用户可以通过 Claims 来请求资源，Crossplane 会根据 Claims 来创建相应的 Composite Resources。

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20240505105558.png)

在 Composite Resource Definitions 中设置 `claimNames`，这样 Crossplane 就会为 Claims 创建相应的 CRD。

```yaml
apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
metadata:
  name: sqls.example.com
spec:
  group: example.com
  names:
    kind: SQL
    plural: sqls
  claimNames:
    kind: SQLClaim
    plural: sqlclaims
  ......
```

SQLClaim CRD 的定义如下，和 SQL CRD 的定义基本一致，唯一的区别是 `scope` 是 `Namespaced`，而不是 `Cluster`。

```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: sqlclaims.example.com
spec:
  conversion:
    strategy: None
  group: example.com
  names:
    categories:
    - claim
    kind: SQLClaim
    listKind: SQLClaimList
    plural: sqlclaims
    singular: sqlclaim
  scope: Namespaced # 命名空间级别
  versions:
  ......
    name: v1alpha1
    schema:
      openAPIV3Schema:
      ......
        parameters:
          properties:
            database:
              description: The database to create inside the DB server.
              type: string
            schema:
              description: The SQL to apply the database schema.
              type: string
            size:
              default: small
              description: 'Supported sizes: small, medium, large'
              type: string
            version:
              description: The DB version depends on the DB type and versions available in the selected provider.
              type: string
            ......
```

Crossplane 会为根据 Claims 创建的 Composite Resources（以及根据 Composite Resources 创建的 Managed Resources）添加随机的后缀以避免命名冲突，这是因为不同 Namespace 中的 Claims 名称有可能相同。默认情况下，在 GCP 上创建的资源名称和 Managed Resources 的名称是一样的，因此这些外部资源名称也会被添加随机的后缀。

但是我们并不希望像数据库和用户名这些资源的名称带有随机的后缀，因此我们可以为这些 Managed Resources 设置 `"crossplane.io/external-name"` Annotation，让 Crossplane 将这个 Annotation 的值作为外部资源的名称。

```yaml
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: gcp-postgresql
  labels:
    provider: gcp
    db: postgresql
spec:
  compositeTypeRef:
    apiVersion: example.com/v1alpha1
    kind: SQL
  mode: Pipeline
  pipeline:
  - step: patch-and-transform
    functionRef:
      name: crossplane-contrib-function-patch-and-transform 
    input:
      apiVersion: pt.fn.crossplane.io/v1beta1
      kind: Resources
      resources:
      ......
      - name: user
        base:
          apiVersion: sql.gcp.upbound.io/v1beta1
          kind: User
          spec:
            providerConfigRef:
              name: providerconfig-gcp-sql
            forProvider:
              instanceSelector:
                matchControllerRef: true
              passwordSecretRef:
                key: password
                name: example-sql-password
                # namespace: team-a / team-b
        patches:
        - fromFieldPath: metadata.name
          toFieldPath: metadata.name
        - fromFieldPath: spec.claimRef.name
          toFieldPath: metadata.annotations["crossplane.io/external-name"] # 设置外部资源的名称
          transforms:
          - type: string
            string:
              fmt: "%s-user"
              type: Format
        - fromFieldPath: spec.claimRef.namespace
          toFieldPath: spec.forProvider.passwordSecretRef.namespace
      - name: database
        base:
          apiVersion: sql.gcp.upbound.io/v1beta1
          kind: Database
          spec:
            providerConfigRef:
              name: providerconfig-gcp-sql
            forProvider:
              instanceSelector:
                matchControllerRef: true
        patches:
        - fromFieldPath: metadata.name
          toFieldPath: metadata.name
        - fromFieldPath: spec.parameters.database
          toFieldPath: metadata.annotations["crossplane.io/external-name"]
```

现在，我们就可以分别在 team-a 和 team-b 这两个 Namespace 中通过创建 SQLClaim CR 来申请 Cloud SQL 实例了。

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: team-a
---
apiVersion: v1
kind: Secret
metadata:
  name: example-sql-password
  namespace: team-a
data:
  password: dGVzdDEyMw==
---
apiVersion: example.com/v1alpha1
kind: SQLClaim
metadata:
  name: example-sql
  namespace: team-a
spec:
  compositionSelector:
    matchLabels:
      provider: gcp
      db: postgresql
  parameters:
    version: "13"
    size: small
    database: example-db
    schema: |
      create table videos (
        id varchar(50) not null,
        description text,
        primary key (id)
      );
---
apiVersion: v1
kind: Namespace
metadata:
  name: team-b
---
apiVersion: v1
kind: Secret
metadata:
  name: example-sql-password
  namespace: team-b
data:
  password: dGVzdDEyMw==
---
apiVersion: example.com/v1alpha1
kind: SQLClaim
metadata:
  name: example-sql
  namespace: team-b
spec:
  compositionSelector:
    matchLabels:
      provider: gcp
      db: postgresql
  parameters:
    version: "13"
    size: small
    database: example-db
    schema: |
      create table videos (
        id varchar(50) not null,
        description text,
        primary key (id)
      );
```

执行以下命令创建实验 7 的相关资源。

```bash
kubectl apply -f v7-namespace-scope.yaml
```

分别查看 team-a 和 team-b 创建的 SQLClaim。Crossplane 会根据 SQLClaim CR 来分别创建集群级别的 SQL CR（Composite Resources）。

```bash
crossplane beta trace sqlclaim example-sql -n team-a
NAME                                                 SYNCED   READY   STATUS
SQLClaim/example-sql (team-a)                        True     True    Available
└─ SQL/example-sql-xb96l                             True     True    Available
   ├─ Object/example-sql-xb96l-schema-example-db     True     True    Available
   ├─ DatabaseInstance/team-a-example-sql-instance   True     True    Available
   ├─ Database/example-sql-xb96l                     True     True    Available
   └─ User/example-sql-xb96l                         True     True    Available
   
crossplane beta trace sqlclaim example-sql -n team-b
NAME                                                 SYNCED   READY   STATUS
SQLClaim/example-sql (team-b)                        True     True    Available
└─ SQL/example-sql-wkk7g                             True     True    Available
   ├─ Object/example-sql-wkk7g-schema-example-db     True     True    Available
   ├─ DatabaseInstance/team-b-example-sql-instance   True     True    Available
   ├─ Database/example-sql-wkk7g                     True     True    Available
   └─ User/example-sql-wkk7g                         True     True    Available
```

在 GCP 控制台上可以看到 team-a 和 team-b 创建的 Cloud SQL 实例。

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20240419215400.png)

尝试连接 team-a 的 Cloud SQL 实例。

```bash
export CONNECTION_SECRET=example-sql-connection-secret
export PGHOST=$(kubectl --namespace team-a \
                    get secret $CONNECTION_SECRET \
                    --output jsonpath="{.data.publicIP}" | base64 -d)
export PGUSER=example-sql-user
export PGPASSWORD=test123

kubectl run postgresql-client --rm -ti --restart=Never \
  --image docker.io/bitnami/postgresql:16 --env PGPASSWORD=$PGPASSWORD \
  -- psql --host $PGHOST -U $PGUSER -d postgres -p 5432
```

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20240419220907.png)

执行 `exit` 命令退出 PostgreSQL 数据库。

实验完成后，执行以下命令清除环境。

```bash
kubectl delete -f v7-namespace-scope.yaml
```

### 7.8 实验 8: Configuration Packages

在前面的实验中，我们学习并使用了大部分的 Crossplane 资源，包括 Providers，Compositions，Composite Resource Definitions，Composition Functions 等等。
在我们的例子中，其实大部分人并不想从头开始创建这些所需的资源，而是想要直接使用面向平台用户的 SQL 或者 SQLClaim 资源。那么如何将这些所需的资源打包并分享给他人呢？答案是使用 Configuration Packages。

Upbound Marketplace 上提供了许多别人创建好的 [Configuration Packages](https://marketplace.upbound.io/configurations)，我们可以直接使用这些 Configuration Packages 来创建我们所需的资源，当然我们也可以将自己创建的资源打包成 Configuration Packages 上传到这里。

在本实验中，我将构建 Configuration Packages 所需的资源文件放在了 v8-configuration-packages 目录中，其中包含了两个文件：

- **compositions.yaml**：内容和 v7-namespace-scope.yaml 中的 Composite Resource Definitions 和 Compositions 的内容一致。
- **crossplane.yaml**：定义了 Configuration Packages 的信息，包括我们所需的 Providers，Composition Functions 等信息。

```yaml
apiVersion: meta.pkg.crossplane.io/v1
kind: Configuration
metadata:
  name: seven-sql
  annotations:
    meta.crossplane.io/maintainer: Seven Cheng
    meta.crossplane.io/description: Deploy PostgreSQL databases on Google Cloud Platform
spec:
  crossplane:
    version: ">=v1.15.0"
  dependsOn:
  - provider: xpkg.upbound.io/upbound/provider-gcp-sql
    version: ">=v1.0.2"
  - provider: xpkg.upbound.io/crossplane-contrib/provider-kubernetes
    version: ">=v0.13.0"
  - function: "xpkg.upbound.io/crossplane-contrib/function-go-templating"
    version: "v0.4.1"
  - function: "xpkg.upbound.io/crossplane-contrib/function-patch-and-transform"
    version: "v0.2.1"
  - function: "xpkg.upbound.io/crossplane-contrib/function-auto-ready"
    version: "v0.2.1"
```

执行以下命令构建 Configuration Packages。

```bash
# 删除之前 build 的 xpkg 文件（如果有）
rm -rf v8-configuration-packages/*.xpkg
crossplane xpkg build --package-root=v8-configuration-packages
```

构建完成后，我们可以在目录中找到生成的 xpkg 文件。

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20240417225143.png)

接下来准备将我们刚刚构建的 Configuration Packages 上传到 Upbound。
在上传镜像之前，我们需要在 [Upbound](https://marketplace.upbound.io) 上注册一个账号，并创建 Organization 和 Repository。

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20240417225344.png)

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20240417230134.png)

然后使用以下命令登录 Upbound。

```bash
crossplane xpkg login --username <your-username>
```

接下来就可以使用 `crossplane xpkg push` 命令将我们刚刚构建的 Configuration Packages 上传到 Upbound。

```
crossplane xpkg push -f v8-configuration-packages/*.xpkg \
xpkg.upbound.io/seven-demo/seven-sql:v0.0.1
```

在 Upbound 的 Repository 上可以看到我们刚刚上传的 Configuration Packages。

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20240417230252.png)

接下来我们就可以准备安装我们刚刚上传的 Configuration Packages 了。现在让我们准备一个全新的 Kubernetes 集群，然后通过 Configuration Packages 来安装所需的 Providers，Composition Functions，Composite Resource Definitions 以及 Compositions 等资源文件。

```bash
# 创建一个新的集群
kind create cluster --name crossplane-demo-2

# 安装 Crossplane
helm install crossplane \
  crossplane-stable/crossplane \
  --namespace crossplane-system \
  --create-namespace
  
# 安装 Atlas Operator
helm install atlas-operator \
  oci://ghcr.io/ariga/charts/atlas-operator \
  --namespace atlas-operator --create-namespace

# 创建 GCP 认证凭据
kubectl --namespace crossplane-system \
   create secret generic gcp-creds \
   --from-file creds=./gcp-creds.json
```

安装 Configuration Packages 的资源文件如下，指定我们前面构建的 OCI 容器镜像即可。

```yaml
apiVersion: pkg.crossplane.io/v1
kind: Configuration
metadata:
  name: crossplane-sql
spec:
  packagePullPolicy: Always
  package: xpkg.upbound.io/seven-demo/seven-sql:v0.0.1
```

执行以下命令安装 Configuration Packages。

```bash
kubectl apply -f v8-install-configuration-packages.yaml
```

等待一会，可以看到 Configuration Packages 已经安装成功，并且相关的 Providers，Composition Functions，Composite Resource Definitions 以及 Compositions 等资源也已经安装成功。

```
kubectl get configuration
NAME             INSTALLED   HEALTHY   PACKAGE                                       AGE
crossplane-sql   True        True      xpkg.upbound.io/seven-demo/seven-sql:v0.0.1   5m52s


kubectl get providers
NAME                                     INSTALLED   HEALTHY   PACKAGE                                                          AGE
crossplane-contrib-provider-kubernetes   True        True      xpkg.upbound.io/crossplane-contrib/provider-kubernetes:v0.13.0   2m23s
upbound-provider-family-gcp              True        True      xpkg.upbound.io/upbound/provider-family-gcp:v1.0.2               2m8s
upbound-provider-gcp-sql                 True        True      xpkg.upbound.io/upbound/provider-gcp-sql:v1.0.2                  2m27s


kubectl get functions
NAME                                              INSTALLED   HEALTHY   PACKAGE                                                                  AGE
crossplane-contrib-function-auto-ready            True        True      xpkg.upbound.io/crossplane-contrib/function-auto-ready:v0.2.1            2m19s
crossplane-contrib-function-go-templating         True        True      xpkg.upbound.io/crossplane-contrib/function-go-templating:v0.4.1         2m25s
crossplane-contrib-function-patch-and-transform   True        True      xpkg.upbound.io/crossplane-contrib/function-patch-and-transform:v0.2.1   2m22s


kubectl get compositeresourcedefinitions
NAME               ESTABLISHED   OFFERED   AGE
sqls.example.com   True          True      5m36s


kubectl get composition
NAME             XR-KIND   XR-APIVERSION          AGE
gcp-postgresql   SQL       example.com/v1alpha1   5m40s
```

设置 GCP 和 Kubernetes Provider 的配置。

```bash
envsubst < v8-providerconfig.yaml | kubectl apply -f -
```

为 Kubernetes Provider 赋予相关权限。

```bash
export PROVIDER_KUBERNETES_SA=$(kubectl get pods -n crossplane-system --no-headers=true \
| grep "^crossplane-contrib-provider-kubernetes" | awk '{print $1}' \
| xargs -I {} kubectl get pod {} -n crossplane-system -o jsonpath='{.spec.serviceAccountName}')

envsubst < v8-kubernetes-rbac.yaml | kubectl apply -f -
```

为 team-a 和 team-b 分别申请 Cloud SQL 实例。

```
kubectl apply -f v8-team-resources.yaml
```

分别查看 team-a 和 team-b 创建的 SQLClaim。等待一会，最终所有的资源都会变成 Ready 状态。

```
crossplane beta trace sqlclaim example-sql -n team-a
NAME                                                 SYNCED   READY   STATUS
SQLClaim/example-sql (team-a)                        True     True    Available
└─ SQL/example-sql-gscx7                             True     True    Available
   ├─ Object/example-sql-gscx7-schema-example-db     True     True    Available
   ├─ DatabaseInstance/team-a-example-sql-instance   True     True    Available
   ├─ Database/example-sql-gscx7                     True     True    Available
   └─ User/example-sql-gscx7                         True     True    Available
   
crossplane beta trace sqlclaim example-sql -n team-b
NAME                                                 SYNCED   READY   STATUS
SQLClaim/example-sql (team-b)                        True     True    Available
└─ SQL/example-sql-jtvfv                             True     True    Available
   ├─ Object/example-sql-jtvfv-schema-example-db     True     True    Available
   ├─ DatabaseInstance/team-b-example-sql-instance   True     True    Available
   ├─ Database/example-sql-jtvfv                     True     True    Available
   └─ User/example-sql-jtvfv                         True     True    Available
```

至此，我们已经完成了所有的实验。实验完成后，执行以下命令清除在 GCP 上创建的资源和两个实验用的 Kubernetes 集群。

```bash
kubectl delete -f v8-team-resources.yaml
kind delete clusters crossplane-demo crossplane-demo-2
```

删除 GCP project。

```bash
gcloud projects delete ${PROJECT_ID}
```

## 8 总结

在这篇文章中，我们深入探讨了 Crossplane 这一开源的 Kubernetes 扩展工具，它允许用户通过 Kubernetes API 来统一管理和编排云资源。文章首先对 Crossplane 的核心组件和概念进行了详细解释，包括 Providers、Managed Resources、Compositions、Composite Resource Definitions 等等。随后，我们通过一系列的实践案例，逐步学习了如何使用 Crossplane 来管理云资源，包括使用 Managed Resources 来创建云资源、使用 Compositions 来组合 Managed Resources、使用 Claims 来在命名空间创建资源、使用 Configuration Packages 来打包和分享资源等等。希望通过学习这篇文章，你能够对 Crossplane 有一个更深入的了解，并且能够利用它来统一管理和编排你的基础设施资源。

> 建议点击阅读原文以获得更好的阅读体验，包括显示文章外链和查看高清插图。

## 9 参考资料

- [Crossplane: The Cloud Native Control Plane by Viktor Farcic](https://www.upbound.io/resources/lp/book/crossplane-cloud-native-control-plane)
- [GCP PostgreSQL Instance Settings](https://cloud.google.com/sql/docs/postgres/instance-settings)
- [crossplane/crossplane@v1.15.2](https://doc.crds.dev/github.com/crossplane/crossplane@v1.15.2)
- [Crossplane Documentation](https://docs.crossplane.io/v1.15/)
- [Monitoring-As-Code with Crossplane](https://blog.crossplane.io/monitoring-as-code-with-crossplane/)
- [Going Further with Crossplane: Compositions and Functions](https://blog.ogenki.io/post/crossplane_composition_functions/)
