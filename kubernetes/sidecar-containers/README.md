# 深入剖析 Kubernetes 原生 Sidecar 容器

## 1 Sidecar 容器的概念

sidecar 容器的概念在 Kubernetes 早期就已经存在。一个明显的例子就是 2015 年的这篇 Kubernetes [博客文章](https://kubernetes.io/blog/2015/06/the-distributed-system-toolkit-patterns/)，其中提到了 sidecar 模式。多年来，sidecar 模式在应用程序中变得越来越普遍，使用场景也变得更加多样化。

其中比较经典的就是 Istio 通过 sidecar 容器实现了服务网格的功能，Envoy 作为 sidecar 容器与应用程序容器一起运行，负责处理所有的网络流量，实现了服务之间的安全通信、流量管理、监控等功能。

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20240530185903.png)

## 2 当前 Sidecar 容器的问题

当前的 Kubernetes 原语可以很好地处理这种模式，但是对于几个用例来说，它们还存在着不足，并且迫使应用程序采用奇怪的变通方法。

### 2.1 问题 1：使用 Sidecar 容器的 Job

假设你有一个 Job，其中包含两个容器：一个是用于执行作业的主容器，另一个只是完成辅助任务的 sidecar 容器。这个辅助容器可以是用于服务网格、收集指标或者日志的服务等等。当 Job 中的主容器完成任务退出时，由于 sidecar 容器还在运行，最终会导致 Pod 无法正常终止。此外，对于 `restartPolicy:Never` 的 Job，当 sidecar 容器因为 OOM 被杀死时，它不会被重新启动，如果 sidecar 容器为其他容器提供网络或者安全通信，这可能会导致 Pod 无法使用。

下面我们可以通过一个简单的例子来演示这个问题。本文中的所有示例文件都可以在 [Github](https://github.com/cr7258/hands-on-lab/tree/main/kubernetes/sidecar-containers) 中找到。
下面是一个 Job 的 YAML 文件，其中包含两个容器：一个是主容器 `main-container-1`，另一个是 sidecar 容器 `sidecar-container-1`。
`main-container-1` 容器在完成一些任务后会正常退出，而 `sidecar-container-1` 容器会则一直运行。

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: myapp
spec:
  template:
    spec:
      containers:
        - name: main-container-1
          image: busybox:1.35
          command: ["sh", "-c"]
          args:
            - |
              echo "main container is starting..."
              for i in $(seq 1 5); do
                echo "main container is doing some task: $i/5"
                sleep 3
              done
              echo "main container completed tasks and exited"
        - name: sidecar-container-1
          image: busybox:1.35
          command: ["sh", "-c"]
          args:
            - |
              echo "sidecar container is starting..."
              while true; do
                echo "sidecar container is collecting logs..."
                sleep 1
              done
      restartPolicy: OnFailure
```

执行以下命令应用上面的 Job 资源。

```bash
kubectl apply -f 1-job-cannot-complete.yaml
```

在本文的实验中，我们会在一个 Pod 中同时运行多个容器，为了方便观察日志，我们可以使用 [stern](https://github.com/stern/stern) 这个开源工具。
stern 允许我们同时查看多个 Pod 中多个容器的日志，并且以不同颜色进行显示，方便我们直观地进行区分。

执行以下命令查看 `myapp` Pod 中所有容器的日志：
```bash
# --diff-container 参数会为每个容器的日志添加不同的颜色，默认情况下，只会为每个 Pod 的日志添加不同的颜色
stern myapp --diff-container
```

从日志中可以看到，`main-container-1` 容器完成任务后正常退出，而 `sidecar-container-1` 还在持续运行，最终导致这个 Job 无法正常结束。

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20240528213455.png)

如果我们提前在另一个窗口执行 `kubectl get pod -w` 命令，可以观察到 Pod 的状态变化如下：

```bash
NAME          READY   STATUS    RESTARTS   AGE
myapp-fdpb7   0/2     Pending   0          0s
myapp-fdpb7   0/2     Pending   0          0s
myapp-fdpb7   0/2     ContainerCreating   0          0s
myapp-fdpb7   2/2     Running             0          2s
myapp-fdpb7   1/2     NotReady            0          17s
```

每行状态的解释如下，完整的 Pod 资源内容请查看 `logs/1-job-cannot-complete-status.yaml` 文件：
- 1.Pod 创建后还未被调度，Pod 的 Phase 为 `Pending`。
```yaml
status:
  phase: Pending
  qosClass: BestEffort
```
- 2.Pod 已经被调度到 Node 上，但是容器还未被创建，Pod 的 Phase 还是 `Pending`。
```yaml
status:
  conditions:
    - lastProbeTime: null
      lastTransitionTime: "2024-05-28T13:05:25Z"
      status: "True"
      type: PodScheduled # Pod 已经被调度到 Node 上
  phase: Pending
  qosClass: BestEffort
```
- 3.正在等待创建容器，Pod 还没有处于 Ready 状态，Pod 的 Phase 仍为 `Pending`。
```yaml
status:
  conditions:
    - lastProbeTime: null
      lastTransitionTime: "2024-05-28T13:05:25Z"
      status: "True"
      type: Initialized
    - lastProbeTime: null
      lastTransitionTime: "2024-05-28T13:05:25Z"
      message: 'containers with unready status: [main-container-1 sidecar-container-1]'
      reason: ContainersNotReady
      status: "False" # Pod 还没有处于 Ready 状态
      type: Ready
    - lastProbeTime: null
      lastTransitionTime: "2024-05-28T13:05:25Z"
      message: 'containers with unready status: [main-container-1 sidecar-container-1]'
      reason: ContainersNotReady
      status: "False"
      type: ContainersReady
    - lastProbeTime: null
      lastTransitionTime: "2024-05-28T13:05:25Z"
      status: "True"
      type: PodScheduled
  containerStatuses:
    - image: busybox:1.35
      imageID: ""
      lastState: {}
      name: main-container-1
      ready: false
      restartCount: 0
      started: false
      state:
        waiting: # 等待容器创建完成
          reason: ContainerCreating 
    - image: busybox:1.35
      imageID: ""
      lastState: {}
      name: sidecar-container-1
      ready: false
      restartCount: 0
      started: false
      state:
        waiting: # 等待容器创建完成
          reason: ContainerCreating
  hostIP: 172.19.0.2
  phase: Pending
  qosClass: BestEffort
  startTime: "2024-05-28T13:05:25Z"
```
- 4.所有容器在运行中，Pod 的 Phase 变为 `Running`。
```yaml
status:
  conditions:
    - lastProbeTime: null
      lastTransitionTime: "2024-05-28T13:05:25Z"
      status: "True"
      type: Initialized
    - lastProbeTime: null
      lastTransitionTime: "2024-05-28T13:05:27Z"
      status: "True"
      type: Ready
    - lastProbeTime: null
      lastTransitionTime: "2024-05-28T13:05:27Z"
      status: "True"
      type: ContainersReady
    - lastProbeTime: null
      lastTransitionTime: "2024-05-28T13:05:25Z"
      status: "True"
      type: PodScheduled
  containerStatuses:
    - containerID: containerd://af182325a9bb106697dc56f7ff25e96d6dd22d45eb134990d9c4820349c11232
      image: docker.io/library/busybox:1.35
      imageID: docker.io/library/busybox@sha256:469d6089bc898ead80a47dab258a127ffdae15342eab860be3be9ed2acdee33b
      lastState: {}
      name: main-container-1
      ready: true
      restartCount: 0
      started: true
      state:
        running: # 主容器在运行中
          startedAt: "2024-05-28T13:05:26Z"
    - containerID: containerd://fb24805ffe5ee1fddb64a728ee8853299f9c093b2722b77d54808d9821b90b0e
      image: docker.io/library/busybox:1.35
      imageID: docker.io/library/busybox@sha256:469d6089bc898ead80a47dab258a127ffdae15342eab860be3be9ed2acdee33b
      lastState: {}
      name: sidecar-container-1
      ready: true
      restartCount: 0
      started: true
      state:
        running: # sidecar 容器在运行中
          startedAt: "2024-05-28T13:05:26Z"
  hostIP: 172.19.0.2
  phase: Running
  podIP: 10.244.0.7
  podIPs:
    - ip: 10.244.0.7
  qosClass: BestEffort
  startTime: "2024-05-28T13:05:25Z"
```
- 5.`main-container-1` 容器完成任务后正常退出，而 `sidecar-container-1` 还在持续运行，最终这个 Job 无法正常结束。
```yaml
status:
  conditions:
    - lastProbeTime: null
      lastTransitionTime: "2024-05-28T13:05:25Z"
      status: "True"
      type: Initialized
    - lastProbeTime: null
      lastTransitionTime: "2024-05-28T13:05:42Z"
      message: 'containers with unready status: [main-container-1]'
      reason: ContainersNotReady
      status: "False"
      type: Ready
    - lastProbeTime: null
      lastTransitionTime: "2024-05-28T13:05:42Z"
      message: 'containers with unready status: [main-container-1]'
      reason: ContainersNotReady
      status: "False"
      type: ContainersReady
    - lastProbeTime: null
      lastTransitionTime: "2024-05-28T13:05:25Z"
      status: "True"
      type: PodScheduled
  containerStatuses:
    - containerID: containerd://af182325a9bb106697dc56f7ff25e96d6dd22d45eb134990d9c4820349c11232
      image: docker.io/library/busybox:1.35
      imageID: docker.io/library/busybox@sha256:469d6089bc898ead80a47dab258a127ffdae15342eab860be3be9ed2acdee33b
      lastState: {}
      name: main-container-1
      ready: false
      restartCount: 0
      started: false
      state:
        terminated: # 主容器已经正常退出
          containerID: containerd://af182325a9bb106697dc56f7ff25e96d6dd22d45eb134990d9c4820349c11232
          exitCode: 0
          finishedAt: "2024-05-28T13:05:41Z"
          reason: Completed
          startedAt: "2024-05-28T13:05:26Z"
    - containerID: containerd://fb24805ffe5ee1fddb64a728ee8853299f9c093b2722b77d54808d9821b90b0e
      image: docker.io/library/busybox:1.35
      imageID: docker.io/library/busybox@sha256:469d6089bc898ead80a47dab258a127ffdae15342eab860be3be9ed2acdee33b
      lastState: {}
      name: sidecar-container-1
      ready: true
      restartCount: 0
      started: true
      state:
        running: # sidecar 容器还在继续运行
          startedAt: "2024-05-28T13:05:26Z"
  hostIP: 172.19.0.2
  phase: Running
  podIP: 10.244.0.7
  podIPs:
    - ip: 10.244.0.7
  qosClass: BestEffort
  startTime: "2024-05-28T13:05:25Z"
```

下面这张图展示了上面描述的 Pod 状态变化过程：

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20240531124837.png)

这里有几个地方需要解释一下，在我们观察容器和 Pod 的状态时，Kubernetes 提供了一些字段来帮助我们理解 Pod 的状态：
- [Pod phase](https://v1-28.docs.kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#pod-phase): Pod phase 是对 Pod 在其生命周期中所处位置的一个高层次的概括，包括 `Pending`、`Running`、`Succeeded`、`Failed` 和 `Unknown`。
  - `Pending`：Pod 已被 Kubernetes 系统接受，但有一个或者多个容器尚未被创建。此阶段包括等待 Pod 被调度的时间和通过网络下载镜像的时间。
  - `Running`：Pod 中的所有容器都已经被创建，并且至少有一个容器正在运行，或者正在启动或者重启。
  - `Succeeded`：Pod 中的所有容器都已经成功终止，并且不会再重启。
  - `Failed`：Pod 中的所有容器都已经终止，但至少有一个容器是因为失败而终止。
  - `Unknown`：Pod 的状态无法被获取，通常是由于与 Pod 应该运行的节点通信失败导致的。
- [Container states](https://v1-28.docs.kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#container-states): 容器的状态，包括 `Waiting`、`Running` 和 `Terminated`。我在上图右边部分的方框中用不同的颜色标记了这三种 Container states，另外在括号内部还对相同 Container states 的不同情况作了区分。
  - `Waiting`：容器正在等待某些条件满足，例如正在拉取镜像，或者应用 Secret 数据。
  - `Running`：容器正在运行中。
  - `Terminated`：容器已经终止，可能是正常结束或者因为某些原因失败。如果你使用 `kubectl describe pod` 或者 `kubectl get pod` 命令来查询包含 `Terminated` 状态的容器的 Pod 时， 你会看到容器进入此状态的原因、退出代码以及容器执行期间的起止时间。
- [Pod Status](https://kubernetes.io/docs/tasks/debug/debug-application/debug-init-containers/#understanding-pod-status)：在执行 `kubectl get pod` 命令时返回的 Pod 状态，该字段是 Pod 内所有容器状态的一个聚合，具体的源代码参见 [printPod 函数](https://github.com/kubernetes/kubernetes/blob/v1.28.10/pkg/printers/internalversion/printers.go#L816-L995).有以下几个常见的状态：
  - `Init:N/M`：Pod 包含 M 个 init 容器，其中 N 个已经运行完成。
  - `Init:Error`：Pod 中的某个 init 容器执行失败。
  - `Init:CrashLoopBackOff`：Pod 中的某个 init 容器多次失败。
  - `Pending`：Pod 尚未开始创建 init 容器。
  - `PodInitializing`：Pod 已经执行完所有 init 容器，在等待创建主容器。
  - `ContainerCreating`：当 Pod 中不包含 init 容器时，在等待创建主容器时会显示这个状态。
  - `Running`：Pod 中的所有容器都在运行中。
- **Pod Ready**：以 `Ready 的容器数量 / 所有容器的数量`的形式展示。

测试完毕后，执行以下命令删除这个 Job。

```bash
kubectl delete -f 1-job-cannot-complete.yaml
```

### 2.2 问题 2：日志转发和指标收集的 Sidecar 容器

日志转发和指标收集的 sidecar 容器应该在主应用容器之前启动，以便能够完整地收集日志和指标。如果 sidecar 容器在主应用容器之后启动，而主应用容器在启动时崩溃，则可能会导致日志丢失（取决于日志是否通过共享卷或者通过 Localhost 网络来进行收集）。
另外，在 Pod 停止时，如果 sidecar 容器先于其他容器退出，也会导致日志丢失的问题。

### 2.3 问题 3：服务网格

服务网格的 sidecar 容器需要在其他容器之前运行并准备就绪，以确保流量能够正确地通过服务网格。在关闭时，如果服务网格容器先于其他容器终止，也可能会导致流量异常。

### 2.4 问题 4：配置/密钥

当前，一些 Pod 使用 init 容器来获取配置/密钥，然后使用 sidecar 容器来持续监视变更并将更新推送给主容器，这需要两个独立的容器来实现。也许可以考虑使用同一个 sidecar 容器来处理这两种情况，以简化实现。

## 3 什么是原生 Sidecar 容器

Kubernetes 1.28 引入了一种新型容器 - sidecar 容器。Kubernetes 将 sidecar 容器作为 init 容器的一个特例来实现，在 Pod 启动后，sidecar 容器仍将保持运行状态。

具体的实现方式是在 init 容器中添加了一个新的 `restartPolicy` 字段， 该字段在 `SidecarContainers` 特性门控启用时可用（该特性自 Kubernetes v1.29 起默认启用）。该字段是可选的，如果对其设置，则唯一有效的值为 `Always`。设置了这个字段以后，init 容器就成为了 sidecar 容器，它们会在 Pod 的整个生命周期内持续运行，而不是像 init 容器那样在成功执行完任务后就退出。

```yaml
apiVersion: v1
kind: Pod
spec:
  initContainers:
  - name: secret-fetch
    image: secret-fetch:1.0
  - name: network-proxy
    image: network-proxy:1.0
    restartPolicy: Always
  containers:
  ...
```

接下来让我们通过一些实验来深入理解 sidecar 容器的特性。

## 4 环境准备

在本文中，我们将使用 [Kind](https://kind.sigs.k8s.io/) 来创建一个 Kubernetes 集群。Kind 是一个用于在 Docker 容器中运行本地 Kubernetes 集群的工具，它使用 Docker 容器作为节点，并在这些节点上运行 Kubernetes 的相关组件。

在 Kind 配置文件中启用 `SidecarContainers` 特性门控，如下所示：

```yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
featureGates:
  SidecarContainers: true
```

然后执行以下命令创建一个 Kubernetes 集群，集群的版本为 v1.28.0。

```bash
kind create cluster --name=sidecar-demo-cluster \
--image kindest/node:v1.28.0 \
--config sidecar-feature-enable.yaml
```

## 5 Init 容器和主容器

首先我们先来观察一下只有 init 容器和普通主容器的情况。在下面的示例中，我们定义了 3 个 init 容器和 2 个主容器。

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: myapp
spec:
  initContainers:
    - name: init-container-1
      image: busybox:1.35
      command: ["sh", "-c"]
      args:
        - |
          echo "init container 1 is starting..."
          echo "init container 1 is doing some tasks..."
          sleep 10
          echo "init container 1 completed tasks and exited"
    - name: init-container-2
      image: busybox:1.35
      command: ["sh", "-c"]
      args:
        - |
          echo "init container 2 is starting..."
          echo "init container 2 is doing some tasks..."
          sleep 10
          echo "init container 2 completed tasks and exited"
    - name: init-container-3
      image: busybox:1.35
      command: ["sh", "-c"]
      args:
        - |
          echo "init container 3 is starting..."
          echo "init container 3 is doing some tasks..."
          sleep 10
          echo "init container 3 completed task and exited"
  containers:
    - name: main-container-1
      image: busybox:1.35
      command: ["sh", "-c"]
      args:
        - |
          echo "main container 1 is starting..."
          while true; do
            echo "main container 1 is doing some tasks..."
            sleep 3
          done
    - name: main-container-2
      image: busybox:1.35
      command: [ "sh", "-c" ]
      args:
        - |
          echo "main container 2 is starting..."
          while true; do
            echo "main container 2 is doing some tasks..."
            sleep 3
          done
```

执行以下命令应用上面的 Pod 资源。

```bash
kubectl apply -f 2-init-and-main-containers.yaml
```

执行 stern 命令查看 Pod 的日志，可以看到 3 个 init 容器是按照定义的顺序依次启动的。每个 init 容器在执行完任务后都会正常退出，而下一个 init 容器则会等到前一个 init 容器退出后才会开始启动。

等到所有的 init 容器退出后，两个主容器才会开始启动，它们之间的启动并没有先后顺序。

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20240528215324.png)

如果我们提前在另一个窗口执行 `kubectl get pod -w` 命令，可以观察到 Pod 的状态变化。

```bash
NAME    READY   STATUS    RESTARTS   AGE
myapp   0/2     Pending   0          0s
myapp   0/2     Pending   0          0s
myapp   0/2     Init:0/3   0          0s
myapp   0/2     Init:0/3   0          1s
myapp   0/2     Init:1/3   0          12s
myapp   0/2     Init:1/3   0          13s
myapp   0/2     Init:2/3   0          23s
myapp   0/2     Init:2/3   0          24s
myapp   0/2     PodInitializing   0          34s
myapp   2/2     Running           0          35s
```

每行状态的解释如下，完整的 Pod 资源内容请查看 `logs/2-init-and-main-containers-status.yaml` 文件：
- 1.Pod 创建后还未被调度。
- 2.Pod 已经被调度到 Node 上，但是容器还未被创建。
- 3.等待创建第 1 个 init 容器。
- 4.第 1 个 init 容器正在运行。
- 5.第 1 个 init 容器正常退出，等待创建第 2 个 init 容器。
- 6.第 2 个 init 容器正在运行。
- 7.第 2 个 init 容器正常退出，等待创建第 3 个 init 容器。
- 8.第 3 个 init 容器正在运行。
- 9.所有的 init 容器都已经正常退出，等待创建 `main-container-1` 和 `main-container-2` 两个主容器。
- 10.两个主容器都正在运行。

下面这张图展示了上面描述的 Pod 状态变化过程：

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20240528222458.png)

测试完毕后，执行以下命令删除这个 Pod。

```bash
# 执行 --force 参数立即删除 Pod，方便我们快速进行实验
# 不等待 terminationGracePeriodSeconds（默认是 30s）时间就让 Kubelet 强制发送 SIGKILL 信号，因为我们当前的容器并不会处理 SIGTERM 信号，这将在第 9 小节中会进一步说明
# 如果这里不使用 --force 参数，容器将等待 30s 后容器才会退出， 
kubectl delete -f 2-init-and-main-containers.yaml --force
```

## 6 Init 容器、Sidecar 容器和主容器

接下来，我们在 Pod 中引入 sidecar 容器，sidecar 容器是设置了 `restartPolicy: Always` 的 init 容器。在下面的示例中，我们定义了 3 个 init 容器、2 个 sidecar 容器和 2 个主容器。

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: myapp
spec:
  initContainers:
    - name: init-container-1
      image: busybox:1.35
      command: ["sh", "-c"]
      args:
        - |
          echo "init container 1 is starting..."
          echo "init container 1 is doing some tasks..."
          sleep 10
          echo "init container 1 completed tasks and exited"
    - name: sidecar-container-1
      image: busybox:1.35
      command: ["sh", "-c"]
      args:
        - |
          echo "sidecar container 1 is starting..."
          while true; do
            echo "sidecar container 1 is doing some tasks..."
            sleep 3
          done
      restartPolicy: Always # sidecar 容器是设置了 restartPolicy: Always 的 init 容器
    - name: sidecar-container-2
      image: busybox:1.35
      command: ["sh", "-c"]
      args:
        - |
          echo "sidecar container 2 is starting..."
          while true; do
            echo "sidecar container 2 is doing some tasks..."
            sleep 3
          done
      restartPolicy: Always
  containers:
    - name: main-container-1
      image: busybox:1.35
      command: ["sh", "-c"]
      args:
        - |
          echo "main container 1 is starting..."
          while true; do
            echo "main container 1 is doing some tasks..."
            sleep 3
          done
    - name: main-container-2
      image: busybox:1.35
      command: [ "sh", "-c" ]
      args:
        - |
          echo "main container 2 is starting..."
          while true; do
            echo "main container 2 is doing some tasks..."
            sleep 3
          done
```

执行以下命令应用上面的 Pod 资源。

```bash
kubectl apply -f 3-init-and-sidecar-and-main-containers.yaml
```

从日志中我们可以清晰地看到整个 Pod 的启动过程。首先，`init-container-1` 作为第一个 init 容器启动，在成功执行完任务后正常退出。

接下来，`sidecar-container-1` 作为第一个 sidecar 容器开始启动，接着是 `sidecar-container-2` 容器 。与 init 容器类似，sidecar 容器也是按照定义的顺序逐个启动的。不同的是，sidecar 不会像 init 容器那样在完成任务后退出。这确保了 sidecar 容器可以在 Pod 的整个生命周期内提供辅助功能。

当两个 sidecar 容器启动并成功运行后，两个主容器才会开始启动。两个主容器之间并没有固定的启动顺序，它们几乎是同时启动的。

最后我们可以看到 sidecar 容器和主容器会一直运行，交替输出日志。

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20240528222851.png)

如果我们提前在另一个窗口执行 `kubectl get pod -w` 命令，可以观察到 Pod 的状态变化。

```bash
NAME    READY   STATUS    RESTARTS   AGE
myapp   0/4     Pending   0          0s
myapp   0/4     Pending   0          0s
myapp   0/4     Init:0/3   0          0s
myapp   0/4     Init:0/3   0          1s
myapp   0/4     Init:1/3   0          11s
myapp   1/4     Init:2/3   0          12s
myapp   2/4     PodInitializing   0          13s
myapp   4/4     Running           0          14s
```

每行状态的解释如下，完整的 Pod 资源内容请查看 `logs/3-init-and-sidecar-and-main-containers-status.yaml` 文件：
- 1.Pod 创建后还未被调度。
- 2.Pod 已经被调度到 Node 上，但是容器还未被创建。
- 3.等待创建第 1 个 init 容器。
- 4.第 1 个 init 容器正在运行。
- 5.第 1 个 init 容器正常退出，等待创建第 1 个 sidecar 容器。
- 6.第 1 个 sidecar 容器正在运行，等待创建第 2 个 sidecar 容器。
- 7.第 2 个 sidecar 容器正在运行，等待创建 `main-container-1` 和 `main-container-2` 两个主容器。
- 8.两个主容器都正在运行。

注意 `READY` 字段显示的容器数量是 4（2个 sidecar 容器 + 2 个主容器），而不是 2。这是因为 sidecar 容器也被包含在内，而 init 容器并不会被计算在内，因为 init 容器执行完任务就退出了。

下面这张图展示了上面描述的 Pod 状态变化过程：

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20240531124248.png)

测试完毕后，执行以下命令删除这个 Pod。

```bash
kubectl delete -f 3-init-and-sidecar-and-main-containers.yaml --force
```

## 7 Sidecar 容器的 RestartPolicy

我们前面提到过，sidecar 容器是通过在原有的 init 容器中设置 `restartPolicy: Always` 来实现的。这意味着如果 sidecar 容器异常退出，kubelet 会自动重启它，从而确保 sidecar 容器在 Pod 的整个生命周期内都能一直运行。
在以下示例中，我们定义了两个 sidecar 容器，并分别设置它们运行 20 秒和 30 秒后退出。通过这种方式，我们可以观察 sidecar 容器的重启行为。

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: myapp
spec:
  initContainers:
    - name: init-container-1
      image: busybox:1.35
      command: ["sh", "-c"]
      args:
        - |
          echo "init container 1 is starting..."
          echo "init container 1 is doing some tasks..."
          sleep 10
          echo "init container 1 completed tasks and exited"
    - name: sidecar-container-1
      image: busybox:1.35
      command: ["sh", "-c"]
      args: # sidecar 容器完成任务后退出
        - |
          echo "sidecar container 1 is starting..."
          echo "sidecar container 1 is doing some tasks..."
          sleep 20
          echo "sidecar container 1 completed tasks and exited"
      restartPolicy: Always
    - name: sidecar-container-2
      image: busybox:1.35
      command: ["sh", "-c"]
      args:  # sidecar 容器完成任务后退出
        - |
          echo "sidecar container 2 is starting..."
          echo "sidecar container 2 is doing some tasks..."
          sleep 30
          echo "sidecar container 2 completed tasks and exited"
      restartPolicy: Always
  containers:
    - name: main-container-1
      image: busybox:1.35
      command: ["sh", "-c"]
      args:
        - |
          echo "main container 1 is starting..."
          while true; do
            echo "main container 1 is doing some tasks..."
            sleep 3
          done
    - name: main-container-2
      image: busybox:1.35
      command: [ "sh", "-c" ]
      args:
        - |
          echo "main container 2 is starting..."
          while true; do
            echo "main container 2 is doing some tasks..."
            sleep 3
          done
```

执行以下命令应用上面的 Pod 资源。

```bash
kubectl apply -f 4-sidecar-containers-restart.yaml
```

通过日志我们可以看到 `sidecar-container-1` 和 `sidecar-container-2` 分别在 20 秒和 30 秒后退出，然后又被重新启动了。

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20240529081212.png)

如果我们提前在另一个窗口执行 `kubectl get pod -w` 命令，可以观察到 Pod 的状态变化。

```bash
NAME    READY   STATUS    RESTARTS   AGE
myapp   0/4     Pending   0          0s
myapp   0/4     Pending   0          0s
myapp   0/4     Init:0/3   0          0s
myapp   0/4     Init:0/3   0          1s
myapp   0/4     Init:1/3   0          11s
myapp   1/4     Init:2/3   0          12s
myapp   2/4     PodInitializing   0          13s
myapp   4/4     Running           0          14s
myapp   3/4     Running           0          32s
myapp   4/4     Running           1 (2s ago)   33s
myapp   3/4     Running           1 (11s ago)   42s
myapp   4/4     Running           2 (1s ago)    43s
```

每行状态的解释如下，完整的 Pod 资源内容请查看 `logs/4-sidecar-containers-restart-status.yaml` 文件：
1. Pod 创建后还未被调度。
2. Pod 已经被调度到 Node 上，但是容器还未被创建。
3. 等待创建第 1 个 init 容器。
4. 第 1 个 init 容器正在运行。
5. 第 1 个 init 容器正常退出，等待创建第 1 个 sidecar 容器。
6. 第 1 个 sidecar 容器正在运行，等待创建第 2 个 sidecar 容器。
7. 第 2 个 sidecar 容器正在运行，等待创建 `main-container-1` 和 `main-container-2` 两个主容器。
8. 两个主容器都正在运行。
9. `sidecar-container-1` 退出，kubelet 根据 `restartPolicy: Always` 自动重启 `sidecar-container-1`。
10. `sidecar-container-1` 重启成功，所有容器都在运行状态。
11. `sidecar-container-2` 退出，kubelet 根据 `restartPolicy: Always` 自动重启 `sidecar-container-2`。
12. `sidecar-container-2` 重启成功，所有容器都在运行状态。

下面这张图展示了上面描述的 Pod 状态变化过程：

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20240531125118.png)

测试完毕后，执行以下命令删除这个 Pod。

```bash
kubectl delete -f 4-sidecar-containers-restart.yaml --force
```

## 8 容器探针

在上面的实验中，我们知道了主容器要等到 sidecar 容器运行以后才会开始启动。那么 sidecar 容器的探针是否会影响到主容器的启动呢？也就是说，主容器是否需要等到 sidecar 容器 Ready 后才能启动呢？让我们通过以下实验来寻找答案。

sidecar 容器允许我们像主容器一样设置探针（startupProbe, readinessProbe, livenessProbe）来检查容器的健康状态。在下面的例子中，我们为两个 sidecar 容器分别添加了 readiness 探针，每个探针都会在容器启动后等待 30 秒才会通过。

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: myapp
spec:
  initContainers:
    - name: init-container-1
      image: busybox:1.35
      command: ["sh", "-c"]
      args:
        - |
          echo "init container 1 is starting..."
          echo "init container 1 is doing some tasks..."
          sleep 10
          echo "init container 1 completed tasks and exited"
    - name: sidecar-container-1
      image: busybox:1.35
      command: ["sh", "-c"]
      args:
        - |
          echo "sidecar container 1 is starting..."
          while true; do
            echo "sidecar container 1 is doing some tasks..."
            sleep 3
          done
      restartPolicy: Always
      readinessProbe: # sidecar 容器的 readiness 探针等待 30 秒通过
        exec:
          command:
            - /bin/sh
            - -c
            - |
              echo "readiness probe of sidecar container 1 is starting..." >> /proc/1/fd/1
              sleep 30
              echo "readiness probe of sidecar container 1 passed successfully" >> /proc/1/fd/1
        timeoutSeconds: 999
    - name: sidecar-container-2
      image: busybox:1.35
      command: ["sh", "-c"]
      args:
        - |
          echo "sidecar container 2 is starting..."
          while true; do
            echo "sidecar container 2 is doing some tasks..."
            sleep 3
          done
      restartPolicy: Always
      readinessProbe: # sidecar 容器的 readiness 探针等待 30 秒通过
        exec:
          command:
            - /bin/sh
            - -c
            - |
              echo "readiness probe of sidecar container 2 is starting..." >> /proc/1/fd/1
              sleep 30
              echo "readiness probe of sidecar container 2 passed successfully" >> /proc/1/fd/1
        timeoutSeconds: 999
  containers:
    - name: main-container-1
      image: busybox:1.35
      command: ["sh", "-c"]
      args:
        - |
          echo "main container 1 is starting..."
          while true; do
            echo "main container 1 is doing some tasks..."
            sleep 3
          done
    - name: main-container-2
      image: busybox:1.35
      command: [ "sh", "-c" ]
      args:
        - |
          echo "main container 2 is starting..."
          while true; do
            echo "main container 2 is doing some tasks..."
            sleep 3
          done
```

通过观察容器日志可以发现，两个主容器在 sidecar 容器的 readiness 探针通过之前就已经启动并开始执行任务了。
这表明主容器的启动并不需要等待 sidecar 容器达到 Ready 状态，只要 sidecar 容器处于 Running 状态即可。

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20240529100622.png)

如果我们提前在另一个窗口执行 `kubectl get pod -w` 命令，可以观察到 Pod 的状态变化。

```bash
NAME    READY   STATUS    RESTARTS   AGE
myapp   0/4     Pending   0          0s
myapp   0/4     Pending   0          0s
myapp   0/4     Init:0/3   0          0s
myapp   0/4     Init:0/3   0          1s
myapp   0/4     Init:1/3   0          11s
myapp   0/4     Init:2/3   0          12s
myapp   0/4     PodInitializing   0          13s
myapp   2/4     Running           0          14s
myapp   3/4     Running           0          42s
myapp   4/4     Running           0          43s
```

每行状态的解释如下，完整的 Pod 资源内容请查看 `logs/5-readiness-probe-status.yaml` 文件：：
1. Pod 创建后还未被调度。
2. Pod 已经被调度到 Node 上，但是容器还未创建。
3. 等待创建第 1 个 init 容器。
4. 第 1 个 init 容器正在运行。
5. 第 1 个 init 容器正常退出，等待创建第 1 个 sidecar 容器。
6. 第 1 个 sidecar 容器正在运行，等待创建第 2 个 sidecar 容器。注意，此时 `sidecar-container-1` 并未处于 ready 状态，因为就绪探针还在执行中，也就是说一旦容器处于 Running 状态，下一个容器就会开始启动。
7. 第 2 个 sidecar 容器正在运行但并未处于 Ready 状态，等待创建 `main-container-1` 和 `main-container-2` 两个主容器。
8. 两个主容器都正在运行，并且处于 Ready 状态。
9. `sidecar-container-1` 通过就绪探针检查，进入 Ready 状态。
10. `sidecar-container-2` 通过就绪探针检查，进入 Ready 状态。

下面这张图展示了上面描述的 Pod 状态变化过程：

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20240531132158.png)

测试完毕后，执行以下命令删除这个 Pod。

```bash
kubectl delete -f 5-readiness-probe.yaml --force
```

## 9 容器的停止顺序

我们当前使用的 Kubernetes 版本是 1.28.0。让我们首先看看在这个版本中删除 Pod 时，sidecar 容器和主容器的停止顺序是怎样的。

在下面的示例中，我们为主容器设置了 preStop hook。在容器停止之前，Kubelet 会先执行 preStop hook 中定义的命令，然后才会发送 SIGTERM 信号给容器。

为了让容器接收到 SIGTERM 信号，我们在容器中使用了 trap 命令来捕获 SIGTERM 信号。另外，通常 hook 和 probe 的输出不会打印在 `kubectl logs` 中，为了方便我们通过日志来对容器的状态进行观察，这里使用了一种间接的方法：将输出重定向到 `/proc/1/fd/1` 文件中。

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: myapp
spec:
  initContainers:
    - name: init-container-1
      image: busybox:1.35
      command: ["sh", "-c"]
      args:
        - |
          echo "init container 1 is starting..."
          echo "init container 1 is doing some tasks..."
          sleep 10
          echo "init container 1 completed tasks and exited"
    - name: sidecar-container-1
      image: busybox:1.35
      command: [ "sh", "-c" ]
      args:
        - |
          echo "sidecar container 1 is starting..."
          sh -c "
            trap '
              echo \"sidecar container 1 received SIGTERM\";
              sleep 3;
              echo \"sidecar container 1 stopped\";
              exit 0
            ' TERM;

            while true; do
              echo \"sidecar container 1 is doing some tasks...\";
              sleep 3;
            done
          "
      restartPolicy: Always
    - name: sidecar-container-2
      image: busybox:1.35
      command: [ "sh", "-c" ]
      args:
        - |
          echo "sidecar container 2 is starting..."
          sh -c "
            trap '
              echo \"sidecar container 2 received SIGTERM\";
              sleep 3;
              echo \"sidecar container 2 stopped\";
              exit 0
            ' TERM;

            while true; do
              echo \"sidecar container 2 is doing some tasks...\";
              sleep 3;
            done
          "
      restartPolicy: Always
  containers:
    - name: main-container-1
      image: busybox:1.35
      command: ["sh", "-c"]
      args:
        - |
          echo "main container 1 is starting..."
          exec sh -c "
            trap '
              echo \"main container 1 received SIGTERM\";
              sleep 10;
              echo \"main container 1 stopped\";
              exit 0
            ' TERM;

            while true; do
              echo \"main container 1 is doing some tasks...\";
              sleep 3;
            done
          "
      lifecycle:
        preStop:
          exec:
            command: ["sh", "-c", "echo 'main container 1 preStop hook is running...' >> /proc/1/fd/1; sleep 5"]
    - name: main-container-2
      image: busybox:1.35
      command: ["sh", "-c"]
      args:
        - |
          echo "main container 2 is starting..."
          exec sh -c "
            trap '
              echo \"main container 2 received SIGTERM\";
              sleep 10;
              echo \"main container 2 stopped\";
              exit 0
            ' TERM;

            while true; do
              echo \"main container 2 is doing some tasks...\";
              sleep 3;
            done
          "
      lifecycle:
        preStop:
          exec:
            command: ["sh", "-c", "echo 'main container 2 preStop hook is running...' >> /proc/1/fd/1; sleep 5"]
```

执行以下命令应用上面的 Pod 资源。

```bash
kubectl apply -f 6-prestop-hook.yaml
```

通过查看日志，可以看到主容器首先执行了 preStop hook，然后接收到了 SIGTERM 信号，最后优雅地退出了。同时，sidecar 容器也接收到了 SIGTERM 信号，**但是它在主容器停止之前就已经停止了。**

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20240530072838.png)

如果我们提前在另一个窗口执行 `kubectl get pod -w` 命令，可以观察到 Pod 的状态变化。

```bash
NAME    READY   STATUS    RESTARTS   AGE
myapp   0/4     Pending   0          0s
myapp   0/4     Pending   0          0s
myapp   0/4     Init:0/3   0          0s
myapp   0/4     Init:0/3   0          1s
myapp   0/4     Init:1/3   0          11s
myapp   1/4     Init:2/3   0          12s
myapp   2/4     PodInitializing   0          13s
myapp   4/4     Running           0          14s
myapp   4/4     Terminating       0          38s
myapp   0/4     Terminating       0          53s
myapp   0/4     Terminating       0          54s
myapp   0/4     Terminating       0          54s
myapp   0/4     Terminating       0          54s
```

每行状态的解释如下，完整的 Pod 资源内容请查看 `logs/6-prestop-hook-status.yaml` 文件：
1. Pod 创建后还未被调度。
2. Pod 已经被调度到 Node 上，但是容器还未创建。
3. 等待创建第 1 个 init 容器。
4. 第 1 个 init 容器正在运行。
5. 第 1 个 init 容器正常退出，等待创建第 1 个 sidecar 容器。
6. 第 1 个 sidecar 容器正在运行，等待创建第 2 个 sidecar 容器。
7. 第 2 个 sidecar 容器正在运行，等待创建 `main-container-1` 和 `main-container-2` 两个主容器。
8. 两个主容器都正在运行。
9. 接收到 Pod 删除的请求，开始停止容器。
10. sidecar 容器和主容器都已经停止。
11. 在后面的几行 Terminating 中， 容器的状态并不会发生变化。

以下这张图展示了上面描述的 Pod 状态变化过程：

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20240531131116.png)

然而，由于 sidecar 容器可能会在主容器之前停止，这种情况仍然可能带来一些问题。例如，如果 sidecar 容器负责收集日志，那么可能会造成部分日志内容缺失。又比如，如果 sidecar 容器提供网络代理功能，那么它的提前退出可能会导致主容器的网络连接中断。

为了解决这个问题，从 Kubernetes 1.29 版本开始，如果 Pod 中包含一个或多个 sidecar 容器，kubelet 将延迟向这些 sidecar 容器发送 SIGTERM 信号，直到最后一个主容器完全终止。sidecar 容器将按照它们在 Pod spec 中定义的相反顺序终止。这确保了 sidecar 容器继续为 Pod 中的其他容器提供服务，直到不再需要它们。

下面让我们创建一个 Kubernetes 1.29 版本的集群，然后再次测试 sidecar 容器的停止顺序。由于在 1.29 版本中 `SidecarContainers` 这个特性已经成为 Beta 版本，因此默认是开启的。

```bash
kind create cluster --name=sidecar-demo-cluster-2 \
--image kindest/node:v1.29.0
```

通过分析以下日志，我们可以清晰地看到容器退出的整个过程。首先两个主容器的 preStop hook 被执行，然后主容器接收到 Kubelet 发送的 SIGTERM 信号并正常退出。等到主容器完全退出后，sidecar-container-1 才会接收到 SIGTERM 信号并正常退出。最后，sidecar-container-2 接收到 SIGTERM 信号并正常退出。

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20240530080305.png)

下面这张图描述了 1.29 版本的 sidecar 容器的停止顺序：

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20240531131150.png)

测试完毕后，执行以下命令删除这个 Pod。

```bash
kubectl delete -f 6-prestop-hook.yaml --force
```

## 10 容器资源的 Request 和 Limit

在 Kubernetes 中，我们可以为容器设置资源请求（request）和资源限制（limit）。当你为 Pod 中的容器指定了资源 request（请求）时，kube-scheduler 就根据该信息决定将 Pod 调度到哪个节点上。 当你为容器指定了资源 limit（限制） 时，kubelet 就可以确保运行的容器不会使用超出所设限制的资源。

在评估节点是否有足够的资源来运行 Pod 时，kube-scheduler 会根据不同情况来计算 Pod 中容器资源的最大请求量。在没有引入 sidecar 容器的情况下，计算方式比较简单：资源的最大请求量是单个 init 容器的最大请求量与所有主容器请求量总和之间的最大值。

```bash
Max ( Max(initContainers), Sum(Containers) )
```

有了 sidecar 容器之后，计算公式会变得复杂一些。可以简单地分为两种情况：

- 1.所有 sidecar 容器都是在 init 容器之后启动的。对于这种情况，我们只需要把所有 sidecar 容器的资源请求量与主容器的资源请求量相加，然后与单个 init 容器的最大请求量进行比较即可。

```bash
Max ( Max(initContainers), Sum(Containers) + Sum(Sidecar Containers) )
```

- 2.有一个或者多个 sidecar 容器是在 init 容器之前启动的。在这种情况下，当计算 init 容器的最大请求量时，我们需要把在该 init 容器之前启动的 sidecar 容器也考虑在内。在这里，我们使用 InitContainerUse(i) 来表示当启动 i 个 init 容器时，所需的最大资源请求量（等于该 init 容器的请求量 + 在该 init 容器之前启动的 sidecar 容器的请求量总和）：

```bash
InitContainerUse(i) = Sum(sidecar containers with index < i) + InitContainer(i)
```

最后将 InitContainerUse 与所有主容器以及在该 init 容器之后启动的 sidecar 容器的总和进行比较，取最大值。

```bash
Max ( Max( each InitContainerUse ) , Sum(Sidecar Containers) + Sum(Containers) )
```

接下来我们用两个例子来验证上面的结论，当前 Kubernetes 集群中只有一个节点，使用 `kubectl describe node` 命令可以看到该节点总共有 10 个 CPU 可供分配，当前 CPU request 已经使用了 9% 的 CPU 资源，也就是说还有 9 个 完整的 CPU 可供分配。

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20240530083634.png)

在下面的示例中，我们为 init 容器设置了 9 个 CPU 的 request，为 sidecar 容器和主容器也设置了总共 9 个 CPU 的 request，这样 Pod 刚刚好被允许调度到节点上。如果你尝试将 init 容器的 CPU request 设置为 10，或者将任一 sidecar 容器或主容器的 CPU request 增加 1，那么这个 Pod 都将无法被调度到节点上。

```yaml
# 7-resource-requests.yaml
apiVersion: v1
kind: Pod
metadata:
  name: myapp
spec:
  initContainers:
    - name: init-container-1
      image: busybox:1.35
      command: ["sh", "-c"]
      args:
        - |
          echo "init container 1 is starting..."
          echo "init container 1 is doing some tasks..."
          sleep 10
          echo "init container 1 completed tasks and exited"
      resources:
        requests:
          cpu: "9"
    - name: sidecar-container-1
      image: busybox:1.35
      command: ["sh", "-c"]
      args:
        - |
          echo "sidecar container 1 is starting..."
          while true; do
            echo "sidecar container 1 is doing some tasks..."
            sleep 3
          done
      restartPolicy: Always
      resources:
        requests:
          cpu: "1"
    - name: sidecar-container-2
      image: busybox:1.35
      command: ["sh", "-c"]
      args:
        - |
          echo "sidecar container 2 is starting..."
          while true; do
            echo "sidecar container 2 is doing some tasks..."
            sleep 3
          done
      restartPolicy: Always
      resources:
        requests:
          cpu: "1"
  containers:
    - name: main-container-1
      image: busybox:1.35
      command: ["sh", "-c"]
      args:
        - |
          echo "main container 1 is starting..."
          while true; do
            echo "main container 1 is doing some tasks..."
            sleep 3
          done
      resources:
        requests:
          cpu: "3"
    - name: main-container-2
      image: busybox:1.35
      command: [ "sh", "-c" ]
      args:
        - |
          echo "main container 2 is starting..."
          while true; do
            echo "main container 2 is doing some tasks..."
            sleep 3
          done
      resources:
        requests:
          cpu: "4"
```

在第二个例子中，我们调整了容器的定义顺序，将 `sidecar-container-1` 移动到了 `init-container-1` 之前。虽然 Pod 的 CPU 资源请求总量没有改变，但你会发现这次 Pod 无法被调度到节点上了。这是因为在计算单个 init 容器的最大资源请求量时，`sidecar-container-1` 的资源请求量也被计入了。原本 `init-container-1` 的资源请求量是 9，现在加上了 `sidecar-container-1` 的资源请求量 1，最大的资源请求量就变为了 10，超过了节点的可用资源。

```yaml
# 8-resource-requests-init-container-after-sidecar-container.yaml
apiVersion: v1
kind: Pod
metadata:
  name: myapp
spec:
  initContainers:
    - name: sidecar-container-1
      image: busybox:1.35
      command: ["sh", "-c"]
      args:
        - |
          echo "sidecar container 1 is starting..."
          while true; do
            echo "sidecar container 1 is doing some tasks..."
            sleep 3
          done
      restartPolicy: Always
      resources:
        requests:
          cpu: "1"
    - name: init-container-1
      image: busybox:1.35
      command: ["sh", "-c"]
      args:
        - |
          echo "init container 1 is starting..."
          echo "init container 1 is doing some tasks..."
          sleep 10
          echo "init container 1 completed tasks and exited"
      resources:
        requests:
          cpu: "9"
    - name: sidecar-container-2
      image: busybox:1.35
      command: ["sh", "-c"]
      args:
        - |
          echo "sidecar container 2 is starting..."
          while true; do
            echo "sidecar container 2 is doing some tasks..."
            sleep 3
          done
      restartPolicy: Always
      resources:
        requests:
          cpu: "1"
  containers:
    - name: main-container-1
      image: busybox:1.35
      command: ["sh", "-c"]
      args:
        - |
          echo "main container 1 is starting..."
          while true; do
            echo "main container 1 is doing some tasks..."
            sleep 3
          done
      resources:
        requests:
          cpu: "3"
    - name: main-container-2
      image: busybox:1.35
      command: [ "sh", "-c" ]
      args:
        - |
          echo "main container 2 is starting..."
          while true; do
            echo "main container 2 is doing some tasks..."
            sleep 3
          done
      resources:
        requests:
          cpu: "4"
```

## 11 在 Istio 中使用 Sidecar 容器

在没有原生 sidecar 容器的支持之前，Istio 采用了一种变通的方法来保证 sidecar 容器在主容器之前启动：通过为 Istio 的 sidecar 容器添加一个 postStart hook，该 hook 会阻塞其他容器的启动，直到 sidecar 代理完全运行为止。

```yaml
spec:
  initContainers:
    - name: istio-init
      ...
  containers:
    - name: istio-proxy
      ...
      lifecycle:
        postStart:
          exec:
            command:
              - pilot-agent
              - wait
```

在 Istio 中可以通过将 `holdApplicationUntilProxyStarts` 设置为 true 来启用这个功能。

```bash
# 1.7 版本特性 https://github.com/istio/istio/pull/24737
istioctl install --set values.global.proxy.holdApplicationUntilProxyStarts=true
```

在 Kubernetes 1.28 发布 SidecarContainers 的功能之后，现在我们直接可以在 Istio 中使用原生的 sidecar 容器了，只需将 pilot 的`ENABLE_NATIVE_SIDECARS` 环境变量设置为 true 即可。完整的教程请参见 [Kubernetes Native Sidecars in Istio](https://istio.io/latest/blog/2023/native-sidecars/)。

```bash
TAG=1.19.0-beta.0
curl -L https://github.com/istio/istio/releases/download/$TAG/istio-$TAG-linux-amd64.tar.gz | tar xz
./istioctl install --set values.pilot.env.ENABLE_NATIVE_SIDECARS=true -y
```

## 12 总结

本文首先回顾了传统 sidecar 模式存在的问题，包括 Job 无法正常终止、日志和指标收集不完整以及服务网格流量异常等等。随后，我们介绍了 Kubernetes 1.28 版本中引入的原生 sidecar 容器功能，这一功能旨在解决传统 sidecar 模式的局限性。我们还深入探讨了 sidecar 容器的其他特性，包括 sidecar 容器的启动顺序、重启策略、容器探针、停止顺序等。最后，我们简要地介绍了如何在 Istio 中利用原生 sidecar 容器来提升服务网格的可靠性。

## 13 参考资料
- [KEP-753: sidecar containers](https://github.com/kubernetes/enhancements/tree/e1a916745378660bafb96cb3c9f754fa793342f9/keps/sig-node/753-sidecar-containers)
- [Sidecar Containers](https://kubernetes.io/docs/concepts/workloads/pods/sidecar-containers/)
- [Pod Lifecycle](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#pod-phase)
- [Making Sense Out of Native sidecar Containers in Kubernetes](https://labs.iximiuz.com/tutorials/kubernetes-native-sidecars)
- [Kubernetes Native sidecars in Istio](https://istio.io/latest/blog/2023/native-sidecars/)
- [Kubernetes v1.28: Introducing native sidecar containers](https://kubernetes.io/blog/2023/08/25/native-sidecar-containers/)
- [Unlocking Container Sequencing: Embracing Kubernetes’ Native Sidecar](https://cloudyuga.guru/blogs/k8s-1-28-native-sidecar-container/)
- [Sidecar Containers Are Built-in to Kubernetes: What, How, and Why Now?- Todd Neal & Sergey Kanzhelev](https://kccncna2023.sched.com/event/1R2tw/sidecar-containers-are-built-in-to-kubernetes-what-how-and-why-now-todd-neal-amazon-sergey-kanzhelev-google)
- [CSI Driver X FUSE Drivers: a Kubernetes Object Storage Solution for AI/ML Data Portability - Jiaxun Song, Google](https://www.youtube.com/watch?v=HntbxWLVMso)
- [karlkfi/kubexit: Command supervisor for coordinated Kubernetes pod container termination](https://github.com/karlkfi/kubexit)
- [Termination of Pods](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#pod-termination)
- [preStop hook doesn't get executed](https://stackoverflow.com/questions/55280259/prestop-hook-doesnt-get-executed)
- [Container Lifecycle Hooks](https://kubernetes.io/docs/concepts/containers/container-lifecycle-hooks/)
- [Container restart policy](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#restart-policy)
- [Understanding Pod status](https://kubernetes.io/docs/tasks/debug/debug-application/debug-init-containers/#understanding-pod-status)
- [Istio holdApplicationUntilProxyStarts: Allow users to delay application start until proxy is ready](https://github.com/istio/istio/pull/24737)

## 14 欢迎关注

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/20220104221116.png)