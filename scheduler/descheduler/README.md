Install Descheduler. The cron schedule to run the descheduler is 2 minutes by default.
```bash
helm repo add descheduler https://kubernetes-sigs.github.io/descheduler/
helm install my-release --namespace kube-system descheduler/descheduler
```


Add label for nodes.
```bash
kubectl label node scheduler-demo-worker schedulable=true
kubectl label node scheduler-demo-worker2 schedulable=true
```

Deploy deployment.

```bash
kubectl apply -f deployment.yaml
```

Pod will be scheduled to one of the two nodes.
```bash
kubectl get pod -o wide

NAME                 READY   STATUS    RESTARTS   AGE   IP            NODE                     NOMINATED NODE   READINESS GATES
with-node-affinity-85f9c59f77-pwfrh   1/1     Running   0          32s   10.244.3.21   scheduler-demo-worker2   <none>           <none>
```

Remove label from scheduler-demo-worker2.
```bash
kubectl label node scheduler-demo-worker2 schedulable-
```

Since scheduler-demo-worker2 doesn't fulfill the nodeAffinity, Pod should be re-scheduled to scheduler-demo-worker.

```bash
kubectl logs -n kube-system my-release-descheduler-28308374-7xzrg

......
I1028 14:14:00.919058       1 node_affinity.go:81] "Executing for nodeAffinityType" nodeAffinity="requiredDuringSchedulingIgnoredDuringExecution"
I1028 14:14:00.919083       1 node_affinity.go:121] "Processing node" node="scheduler-demo-worker2"
I1028 14:14:00.919209       1 node_affinity.go:138] "Evicting pod" pod="default/with-node-affinity-85f9c59f77-vllsj"
I1028 14:14:00.925387       1 evictions.go:171] "Evicted pod" pod="default/with-node-affinity-85f9c59f77-vllsj" reason="" strategy="RemovePodsViolatingNodeAffinity" node="scheduler-demo-worker2"
I1028 14:14:00.925418       1 node_affinity.go:121] "Processing node" node="scheduler-demo-control-plane"
I1028 14:14:00.925457       1 node_affinity.go:121] "Processing node" node="scheduler-demo-worker3"
I1028 14:14:00.925470       1 node_affinity.go:121] "Processing node" node="scheduler-demo-worker"
I1028 14:14:00.925513       1 profile.go:323] "Total number of pods evicted" extension point="Deschedule" evictedPods=1
I1028 14:14:00.925525       1 descheduler.go:170] "Number of evicted pods" totalEvicted=1 # evict 1 pod
......
```