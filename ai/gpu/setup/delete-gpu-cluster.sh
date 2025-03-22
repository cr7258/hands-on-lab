echo "Delete Kind GPU cluster..."
kind delete cluster --name gpu-cluster

echo "Stop Cloud Provider Kind..."
kill $(cat /tmp/cloud-provider-kind.pid)
