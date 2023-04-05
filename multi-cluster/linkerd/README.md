
```bash
kind create cluster --config - <<EOF
kind: Cluster
name: west
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
- role: worker
networking:
  apiServerAddress: 10.182.0.2
  podSubnet: "10.7.0.0/16"
  serviceSubnet: "10.77.0.0/16"
EOF
 
kind create cluster --config - <<EOF
kind: Cluster
name: east
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
- role: worker
networking:
  apiServerAddress: 10.182.0.2
  podSubnet: "10.7.0.0/16"
  serviceSubnet: "10.77.0.0/16"
EOF
```

 