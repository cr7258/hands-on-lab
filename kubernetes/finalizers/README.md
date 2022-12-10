## 前言
Kubernetes 中的对象删除并不像表面上看起来那么简单，删除对象涉及一系列过程，例如对象的级联和非级联删除，在删除之前检查以确定是否可以安全删除对象等等。这些都是通过称为 `Finalizers`（终结器）的 API 对象实现的。

## Finalizers 终结器
`Finalizers` 是由字符串组成的数组，当 `Finalizers` 字段中存在元素时，相关资源不允许被删除，`Finalizers` 是 Kubernetes 资源删除流程中的一种拦截机制，能够让控制器实现异步的删除前（Pre-delete）回调，在对象删除之前执行相应的逻辑。

`Finalizers` 可以防止意外删除集群所依赖的、用于正常运作的资源。 Kubernetes 中有些原生的资源对象会被自动加上 `Finalizers` 标签，例如 PVC 和 PV 分别原生自带 `kubernetes.io/pvc-protection` 和 `kubernetes.io/pv-protection` 的 `Finalizers` 标签，以保证持久化存储不被误删，避免挂载了存储的的工作负载产生问题。假如你试图删除一个仍被 Pod 使用的 PVC，该资源不会被立即删除， 它将进入 `Terminating` 状态，直到 PVC 不再挂载到 Pod 上时， Kubernetes 才清除这个对象。

## Kubernetes 对象的删除过程

当删除一个对象时，其对应的控制器并不会真正执行删除对象的操作，在 Kubernetes 中对象的回收操作是由 GarbageCollectorController （垃圾收集器）负责的，其作用就是当删除一个对象时，会根据指定的删除策略回收该对象及其依赖对象。删除的具体过程如下：
-   发出删除命令后 Kubernetes 会将该对象标记为待删除，但不会真的删除对象，具体做法是将对象的 `metadata.deletionTimestamp` 字段设置为当前时间戳，这使得对象处于只读状态（除了修改 `finalizers` 字段）。
-   当 `metadata.deletionTimestamp` 字段非空时，负责监视该对象的各个控制器会执行对应的 `Finalizer` 动作，每个 `Finalizer` 动作完成后，就会从 `Finalizers` 列表中删除对应的 `Finalizer`。
-   一旦 `Finalizers` 列表为空时，就意味着所有 `Finalizer` 都被执行过了，垃圾收集器会最终删除该对象。


## Owner References  属主与附属
在 Kubernetes 中，一些对象是其他对象的属主（Owner）。例如，ReplicaSet 是一组 Pod 的属主，具有属主的对象是属主的附属（Dependent）。附属对象有一个 `metadata.ownerReferences` 字段，用于引用其属主对象。在 Kubernetes 中不允许跨 namespace 指定属主，namespace 空间范围的附属可以指定集群范围或者相同 namespace 的属主。

Kubernetes 会自动为一些对象的附属资源设置属主引用的值， 这些对象包含 ReplicaSet、DaemonSet、Deployment、Job、CronJob、ReplicationController 等等。 你也可以通过改变这个字段的值，来手动配置这些关系。 

接下来我们通过手动设置 `metadata.ownerReferences`  字段来设置从属关系。如下所示，我们首先创建了一个属主对象，然后创建了一个附属对象，根据 `ownerReferences` 字段中的 name 和 uid 关联属主对象。
```bash
# 创建属主对象
cat <<EOF | kubectl create -f -
apiVersion: v1
kind: ConfigMap
metadata:
  name: mymap-parent
EOF

# 获取属主对象 UID
CM_UID=$(kubectl get configmap mymap-parent -o jsonpath="{.metadata.uid}")

# 创建附属对象
cat <<EOF | kubectl create -f -
apiVersion: v1
kind: ConfigMap
metadata:
  name: mymap-child
  ownerReferences:
  - apiVersion: v1
    kind: ConfigMap
    name: mymap-parent # 父对象的名称
    uid: $CM_UID  # 父对象的 uid
EOF
```

当我们删除附属对象时，不会删除属主对象。
```bash
$ kubectl get configmap
NAME           DATA   AGE
mymap-child    0      12m4s
mymap-parent   0      12m4s

# 删除附属对象
$ kubectl delete configmap/mymap-child
configmap "mymap-child" deleted

# 属主对象还存在
$ kubectl get configmap
NAME           DATA   AGE
mymap-parent   0      12m10s
```

现在我们重新创建属主和附属对象，这次我们删除属主对象，发现附属对象也一并被删除了。
```bash
$ kubectl get configmap
NAME           DATA   AGE
mymap-child    0      10m2s
mymap-parent   0      10m2s

# 删除属主对象
$ kubectl delete configmap/mymap-parent
configmap "mymap-parent" deleted

# 属主对象和附属对象都被删除了
$ kubectl get configmap
No resources found in default namespace.
```

继续重新创建属主和附属对象，Kubernetes 默认删除时使用级联删除，这次我们在删除属主对象的时候加上参数 `--cascade=orphan`，表示使用非级联删除，这样删除属主对象后，附属对象依然存在。
```bash
kubectl get configmap
NAME           DATA   AGE
mymap-child    0      13m8s
mymap-parent   0      13m8s

# 非级联删除
kubectl delete --cascade=orphan configmap/mymap-parent
configmap "mymap-parent" deleted

# 附属对象还存在
kubectl get configmap
NAME          DATA   AGE
mymap-child   0      13m21s
```

## Kubernetes 中的删除策略

在默认情况下，删除一个对象同时会删除它的附属对象，如果我们在一些特定情况下只是想删除当前对象本身并不想造成复杂的级联删除，可以指定具体的删除策略。在 Kubernetes 中有三种删除策略：
-   **级联删除**
    -   `Foreground` 策略：**先删除附属对象，再删除属主对象**。在 `Foreground` 模式下，待删除对象首先进入 `deletion in progress` 状态。 在此状态下存在如下的场景：
        -   对象仍然可以通过 REST API 获取。
        -   会将对象的 `deletionTimestamp` 字段设置为对象被标记为要删除的时间点。
        -   将对象的 `metadata.finalizers` 字段值设置为 `foregroundDeletion`。 
        对象一旦被设置为 `deletion in progress` 状态时，垃圾收集器会删除对象的所有依赖， 垃圾收集器在删除了所有有阻塞能力的附属对象之后（ `ownerReference.blockOwnerDeletion=true`），再删除属主对象。
    -   `Background` 策略（默认）：**先删除属主对象，再删除附属对象。** 在 `Background` 模式下，Kubernetes 会立即删除属主对象，之后垃圾收集器会在后台删除其附属对象。
-   **非级联删除**
    -   `Orphan` 策略：**不会自动删除它的附属对象**，这些残留的依赖被称作是原对象的**孤儿对象**。
        
在 kubernetes v1.9 版本之前，大部分控制器的默认删除策略为 `Orphan`，从 v1.9 开始，对 apps/v1 下的资源默认使用 `Background` 模式。

下面的例子中，在删除 Deployment 时指定删除策略为 `Orphan`，这样删除 Deployment 后不会删除 Deployment 的附属对象 ReplicaSet，同样地， ReplicaSet 的附属对象 Pod 也不会被删除。

**方式一：使用 kubectl**，在 `-cascade` 参数中指定删除策略。
```bash
kubectl delete deployment nginx-deployment --cascade=orphan
```
**方式二：使用 Kubernetes API**，`在 propagationPolicy` 参数中指定删除策略。
```bash
# 启动一个本地代理会话  
kubectl proxy --port=8080  

# 使用 curl 来触发删除操作  
curl -X DELETE localhost:8080/apis/apps/v1/namespaces/default/deployments/nginx-deployment \  
 -d '{"kind":"DeleteOptions","apiVersion":"v1","propagationPolicy":"Orphan"}' \  
 -H "Content-Type: application/json"
```
你可以检查 Deployment 所管理的 ReplicaSet 和 Pod 仍然处于运行状态：
```bash
# deployment 已经删除  
$ kubectl get deployments  
No resources found in default namespace.  
​  
# replicaset 和 pod 依然在运行  
$ kubectl get replicaset  
NAME                          DESIRED   CURRENT   READY   AGE  
nginx-deployment-66b6c48dd5   3         3         3       23h  
$ kubectl get pod  
NAME                                READY   STATUS    RESTARTS   AGE  
nginx-deployment-66b6c48dd5-4tnxf   1/1     Running   0          23h  
nginx-deployment-66b6c48dd5-l48cp   1/1     Running   0          23h  
nginx-deployment-66b6c48dd5-ss6nx   1/1     Running   0          23h
```


## Finalizers 在 Kubernetes 中的使用场景
### PV, PVC, Pod
存储的管理是一个与计算实例的管理完全不同的问题，Kubernetes 引入 PersistentVolume 和 PersistentVolumeClaim 两个 API，将存储的细节和使用抽象出来。
- **持久卷（PersistentVolume，PV）** 是集群中的一块存储，可以由管理员事先供应，或者使用**存储类（Storage Class）** 来动态供应。持久卷是集群资源，就像节点也是集群资源一样。持久卷的底层可以是 NFS，iSCSI 或者是基于特定云平台的存储系统等等。
- **持久卷申领（PersistentVolumeClaim，PVC）** 表达的是用户对存储的请求，概念上与 Pod 类似。 Pod 会耗用节点资源，而 PVC 申领会耗用 PV 资源。Pod 可以请求特定数量的资源（CPU 和内存）；同样 PVC 申领也可以请求特定的容量大小，访问模式，读写性能等等，无需关心持久卷背后实现的细节。

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20220322140555.png)




下面的 yaml 资源文件中，分别声明的 PV, PVC 和 Pod 三个资源。PV 使用节点本地的 */tmp/mydata* 目录作为存储，磁盘容量为 1Gi，在 PVC 中申领容量至少为 1Gi 的卷，Pod 使用 PVC 作为存储卷。
```yaml
# 创建 PV，使用节点本地 /tmp/mydata 目录作为存储
apiVersion: v1
kind: PersistentVolume
metadata:
  name: task-pv-volume
  labels:
    type: local
spec:
  storageClassName: manual
  capacity:
    storage: 1Gi
  accessModes:
    - ReadWriteOnce
  hostPath:
    path: "/tmp/mydata"

---
# 创建 PVC，请求至少 1Gi 容量的卷
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: task-pv-claim
spec:
  storageClassName: manual
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi

---
# 创建 Pod，使用 PVC 作为存储卷
apiVersion: v1
kind: Pod
metadata:
  name: task-pv-pod
spec:
  volumes:
    - name: task-pv-storage
      persistentVolumeClaim:
        claimName: task-pv-claim
  containers:
    - name: task-pv-container
      image: busybox:1.34
      command: ["/bin/sh"]
      args: ["-c", "while true; do echo hello >> /var/log/hello.log; sleep 5;done"]
      volumeMounts:
        - mountPath: "/var/log"
          name: task-pv-storage
```

查看创建的 PV, PVC, Pod。
![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20220322143318.png)

如下图所示，从左到右依次是 PV, PVC, Pod 的资源详情：
- PV  的 `Finalizers` 列表中包含 `kubernetes.io/pv-protection` ，说明 PV 对象是处于被保护状态的，当 PV 没有绑定的 PVC 对象时，该 PV 才允许被删除。PVC 申领与 PV 卷之间的绑定是一种一对一的映射，实现上使用 `ClaimRef` 来记录 PV 卷与 PVC 申领间的双向绑定关系。
- PV  的 `Finalizers` 列表中包含 `kubernetes.io/pvc-protection` ，说明 PVC 对象是处于被保护状态的。Pod 中的 `volumes.persistentVolumeClaim` 字段记录了使用的 PVC。

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20220322204924.png)
如果用户删除被某 Pod 使用的 PVC 对象，该 PVC 申领不会被立即移除，PVC 对象的移除会被推迟，直至其不再被任何 Pod 使用。 此外，如果删除已绑定到某 PVC 申领的 PV 卷，该 PV 卷也不会被立即移除，PV 对象的移除也要推迟到该 PV 不再绑定到 PVC。 

接下来演示 Kubernetes 是如何延迟删除 PV 和 PVC 对象的。首先删除 PV。
```bash
$ kubectl delete pv task-pv-volume   
persistentvolume "task-pv-volume" deleted   
^C # 删除后控制台会卡住，ctrl + c 退出
```
查看该 PV，你可以看到 PV 的状态为 `Terminating` ，这是因为和该 PV 绑定的 PVC 还未删除，因此 PV 对象此时处于被保护状态的。
![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20220320213337.png)
然后删除 PVC。
```bash
$ kubectl delete pvc task-pv-claim   
persistentvolumeclaim "task-pv-claim" deleted  
^C # 删除后控制台会卡住，ctrl + c 退出
```
查看该 PVC，发现 PVC 同样处于 Terminating 状态，这是因为使用 PVC 的 Pod 还未删除，因此 PVC 对象此时还处于被保护状态。
![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20220320213356.png)
接着删除 Pod，当 Pod 被删除后，由于没有 Pod 使用 PVC 了，此时 PVC 会被安全地删除；同样地，和 PV 绑定的 PVC 被删除后，PV 也可以被安全地删除了。
```bash
$ kubectl delete pod task-pv-pod
```
再次查看，可以看到此时 Pod, PVC, PV 都被删除了。
![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20220320213610.png)

### Pod, ReplicaSet, Deployment
Deployment 是最常用的用于部署无状态服务的方式，通过 Deployment 控制器能够以声明的方式更新 Pod（容器组）和 ReplicaSet（副本集）。Deployment 会自动创建并管理 ReplicaSet，可以维护多个版本的 ReplicaSet，方便我们升级和回滚应用；ReplicaSet 的职责是确保任何时间都有指定数量的 Pod 副本在运行。

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20220322134146.png)
下面是一个 Deployment 示例，其中创建了一个 ReplicaSet，负责启动三个 `nginx` Pods：
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
  labels:
    app: nginx
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
        image: nginx:1.14.2
        ports:
        - containerPort: 80
```

查看创建的 Deployment, ReplicaSet, Pod。
![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20220320213936.png) 

如下图所示，从左到右依次是 Pod, ReplicaSet, Deployment 的资源详情：
- Pod 的 `ownerReferences.name` 参数表示该 Pod 是名为 *nginx-deployment-66b6c48dd5* 的 ReplicaSet 的附属对象，并且 Pod 的 `ownerReferences.uid` 和 ReplicaSet 对象的 `uid` 相同。
- ReplicaSet 的 `ownerReferences.name` 参数表示该 ReplicaSet 是名为 *nginx-deployment* 的 Deployment 的附属对象，并且 ReplicaSet 的 `ownerReferences.uid` 和  Deployment 对象的 `uid` 相同。

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20220322131156.png)

 虽然在上面的资源详情中，我们并没有看到 `Finalizers` 字段，但是当你使用前台或孤立级联删除时，Kubernetes 也会向属主资源添加 `Finalizer`。 在前台删除中，会添加 `Foreground Finalizer`，这样控制器必须在删除了拥有 `ownerReferences.blockOwnerDeletion=true` 的附属资源后，才能删除属主对象。 如果你指定了孤立删除策略，Kubernetes 会添加 `Orphan Finalizer`， 这样控制器在删除属主对象后，会忽略附属资源。
 
### 资源处于 Terminating 状态无法删除
在使用 Kubernetes 的过程中，我们有时候会遇到删除 Namespace 或者 Pod 等资源后一直处于 Terminating 状态，等待很长时间都无法删除，甚至有时增加 `--force` 参数之后还是无法正常删除。这时就需要 `edit` 该资源，将 `finalizers` 字段设置为 []，之后 Kubernetes 资源就正常删除了。

## 总结
-   `Finalizers` 可以防止意外删除集群所依赖的、用于正常运作的资源。 
-   `Finalizers` 是 Kubernetes 资源删除流程中的一种拦截机制，能够让控制器实现异步的删除前（Pre-delete）回调，在对象删除之前执行相应的逻辑。
-   一旦 `Finalizers` 列表为空时，就意味着所有 `Finalizer` 都被执行过了，垃圾回收器会最终删除该对象。
-   附属对象有一个 `metadata.ownerReferences` 字段，用于引用其属主对象。
-   Kubernetes 中有 3 种删除策略，`Foreground` 和 `Background` 是级联删除，`Orphan` 是非级联删除。`Foreground` 先删除附属对象，再删除属主对象；`Background` 先删除属主对象，再删除附属对象。
    

## 参考资料
-   [Finalizers](https://kubernetes.io/zh/docs/concepts/overview/working-with-objects/finalizers/)
-   [属主与附属](https://kubernetes.io/zh/docs/concepts/overview/working-with-objects/owners-dependents/)
-   [垃圾收集](https://kubernetes.io/zh/docs/concepts/architecture/garbage-collection/)
-   [Using Finalizers to Control Deletion](https://kubernetes.io/blog/2021/05/14/using-finalizers-to-control-deletion/)
-   [在集群中使用级联删除](https://kubernetes.io/zh/docs/tasks/administer-cluster/use-cascading-deletion/?accessToken=eyJhbGciOiJIUzI1NiIsImtpZCI6ImRlZmF1bHQiLCJ0eXAiOiJKV1QifQ.eyJhdWQiOiJhY2Nlc3NfcmVzb3VyY2UiLCJleHAiOjE2NDc3NTE3MzYsImciOiJGNlp6UlQwcVBaa2NFYTJuIiwiaWF0IjoxNjQ3NzUxNDM2LCJ1c2VySWQiOjY2ODcxNDMwfQ.hD8hXnHvMqXkxJhMUyeI49gT6yXmQFjVJdaksPrHm9Q)
-   [熟悉又陌生的 k8s 字段：finalizers](https://cloud.tencent.com/developer/article/1703237)
-   [Kubernetes 实战-Operator Finalizers 实现](https://zdyxry.github.io/2019/09/13/Kubernetes-%E5%AE%9E%E6%88%98-Operator-Finalizers/)
-   [initializer-finalizer-practice](https://github.com/hossainemruz/k8s-initializer-finalizer-practice)
-   [What Are Finalizers In Kubernetes? How to Handle Object Deletions](https://www.cloudsavvyit.com/15163/what-are-finalizers-in-kubernetes-how-to-handle-object-deletions/)
-   [garbage collector controller 源码分析](https://www.bookstack.cn/read/source-code-reading-notes/kubernetes-garbagecollector_controller.md#kubernetes%20%E4%B8%AD%E7%9A%84%E5%88%A0%E9%99%A4%E7%AD%96%E7%95%A5)
-   [配置 Pod 以使用 PersistentVolume 作为存储](https://kubernetes.io/zh/docs/tasks/configure-pod-container/configure-persistent-volume-storage/)
-   [持久卷](https://kubernetes.io/zh/docs/concepts/storage/persistent-volumes/)
-   [pvc_protection_controller.go](https://github.com/kubernetes/kubernetes/blob/ff3e5e06a79bc69ad3d7ccedd277542b6712514b/pkg/controller/volume/pvcprotection/pvc_protection_controller.go#L184-L191)
-   [使用 CustomResourceDefinition 扩展 Kubernetes API](https://kubernetes.io/zh/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definitions/)
-   [垃圾回收](https://howieyuen.github.io/docs/kubernetes/kube-apiserver/garbage-collector/)
-   [垃圾收集](https://jimmysong.io/kubernetes-handbook/concepts/garbage-collection.html)
-   [详解 Kubernetes 垃圾收集器的实现原理](https://draveness.me/kubernetes-garbage-collector/)
-   [Deployments](https://kubernetes.io/zh/docs/concepts/workloads/controllers/deployment/#creating-a-deployment)
-   [详解 Kubernetes Deployment 的实现原理](https://draveness.me/kubernetes-deployment/)
-   [k8s中的PV和PVC理解](https://boilingfrog.github.io/2021/07/01/k8s%E4%B8%AD%E7%9A%84PV%E5%92%8CPVC%E7%90%86%E8%A7%A3/)
-   [Kubernetes Finalizer机制](https://yhuang.pro/2021/12/11/kubernetes-finalizer%E6%9C%BA%E5%88%B6/)
-   [使用 Finalizers](https://cloudnative.to/kubebuilder/reference/using-finalizers.html#%E4%BD%BF%E7%94%A8-finalizers)
-   [Kubernetes API 机制: 对象删除](https://zhuanlan.zhihu.com/p/161072336)

## 欢迎关注
![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20220104221116.png)
