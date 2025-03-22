# Create GPU Kind cluster on Ubuntu 24.04
echo "################################# Install docker, kubectl, helm, kind, nvkind  #################################"
sudo apt update
sudo apt install -y docker.io
sudo snap install kubectl --classic
sudo snap install helm --classic

# Install kind
[ $(uname -m) = x86_64 ] && curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.25.0/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind

# Install nvkind
curl -L -o ~/nvkind-linux-amd64.tar.gz https://github.com/Jeffwan/kind-with-gpus-examples/releases/download/v0.1.0/nvkind-linux-amd64.tar.gz
tar -xzvf ~/nvkind-linux-amd64.tar.gz
mv nvkind-linux-amd64 /usr/local/bin/nvkind

echo "################################# Install NVIDIA GPU Driver #################################"
wget https://cn.download.nvidia.com/tesla/565.57.01/NVIDIA-Linux-x86_64-565.57.01.run
sh NVIDIA-Linux-x86_64-565.57.01.run --silent

echo "################################# Install NVIDIA Container Toolkit #################################"
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
  && curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

sed -i -e '/experimental/ s/^#//g' /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit

echo "################################# Confiure NVIDIA Container Runtime #################################"
sudo nvidia-ctk runtime configure --runtime=docker --set-as-default --cdi.enabled
sudo nvidia-ctk config --set accept-nvidia-visible-devices-as-volume-mounts=true --in-place
sudo systemctl restart docker

echo "################################# Verify GPU Availability in Docker with NVIDIA Runtime #################################"
# Run nvidia-smi to list GPU devices
nvidia-smi -L
if [ $? -ne 0 ]; then
    echo "nvidia-smi failed to execute."
    exit 1
fi

# Run a Docker container with NVIDIA runtime to list GPU devices
docker run --runtime=nvidia -e NVIDIA_VISIBLE_DEVICES=all ubuntu:20.04 nvidia-smi -L
if [ $? -ne 0 ]; then
    echo "Docker command with NVIDIA runtime failed to execute."
    exit 1
fi

# Run a Docker container with mounted /dev/null to check GPU accessibility
docker run -v /dev/null:/var/run/nvidia-container-devices/all ubuntu:20.04 nvidia-smi -L
if [ $? -ne 0 ]; then
    echo "Docker command with mounted /dev/null failed to execute."
    exit 1
fi

echo "All verification checks passed successfully."

echo "################################# Create Kind GPU cluster #################################"
cat << 'EOF' > one-worker-per-gpu.yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
{{- range $gpu := until numGPUs }}
- role: worker
  extraMounts:
    # We inject all NVIDIA GPUs using the nvidia-container-runtime.
    # This requires `accept-nvidia-visible-devices-as-volume-mounts = true` be set
    # in `/etc/nvidia-container-runtime/config.toml`
    - hostPath: /dev/null
      containerPath: /var/run/nvidia-container-devices/{{ $gpu }}
{{- end }}
EOF

nvkind cluster create --name gpu-cluster --config-template=one-worker-per-gpu.yaml

echo "################################# Install gpu-operator #################################"
helm repo add nvidia https://helm.ngc.nvidia.com/nvidia
helm repo update
helm install --wait --generate-name \
     -n gpu-operator --create-namespace \
     nvidia/gpu-operator \
     --set driver.enabled=false

echo "################################# Install Cloud Provider Kind #################################"
KIND_CLOUD_PROVIDER_VERSION="0.5.0"
KIND_CLOUD_PROVIDER_URL="https://github.com/kubernetes-sigs/cloud-provider-kind/releases/download/v${KIND_CLOUD_PROVIDER_VERSION}/cloud-provider-kind_0.5.0_linux_amd64.tar.gz"

# Download and extract
curl -L ${KIND_CLOUD_PROVIDER_URL} -o cloud-provider-kind.tar.gz
tar -xvzf cloud-provider-kind.tar.gz
chmod +x cloud-provider-kind
sudo mv cloud-provider-kind /usr/local/bin/

# Run cloud-provider-kind in the background and forward logs
echo "Starting cloud-provider-kind in the background..."
LOG_FILE="/tmp/cloud-provider-kind.log"

nohup cloud-provider-kind > ${LOG_FILE} 2>&1 &

# Save the process ID
echo $! > /tmp/cloud-provider-kind.pid
echo "Cloud Provider Kind is running in the background. Logs are being written to ${LOG_FILE}."

echo "Setup complete. All components have been installed successfully."
