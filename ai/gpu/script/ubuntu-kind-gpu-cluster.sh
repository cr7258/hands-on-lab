# Create GPU Kind cluster on Ubuntu 24.04
echo "################################# Install docker, kubectl, helm, kind  #################################"
apt update
apt install -y docker.io
snap install kubectl --classic
snap install helm --classic

[ $(uname -m) = x86_64 ] && curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.25.0/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind

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
sudo nvidia-ctk runtime configure --runtime=docker --set-as-default
sudo nvidia-ctk config --set accept-nvidia-visible-devices-as-volume-mounts=true --in-place
sudo systemctl restart docker

echo "################################# Create Kind GPU cluster #################################"
kind create cluster --name gpu-cluster --config - <<EOF
apiVersion: kind.x-k8s.io/v1alpha4
kind: Cluster
nodes:
- role: control-plane
  image: kindest/node:v1.31.2@sha256:18fbefc20a7113353c7b75b5c869d7145a6abd6269154825872dc59c1329912e
  # required for GPU workaround
  extraMounts:
    - hostPath: /dev/null
      containerPath: /var/run/nvidia-container-devices/all
EOF
# fix issue: https://github.com/NVIDIA/nvidia-docker/issues/614#issuecomment-423991632
docker exec -ti gpu-cluster-control-plane ln -s /sbin/ldconfig /sbin/ldconfig.real

echo "################################# Install gpu-operator #################################"
helm repo add nvidia https://helm.ngc.nvidia.com/nvidia
helm repo update
helm install --wait --generate-name \
     -n gpu-operator --create-namespace \
     nvidia/gpu-operator \
     --set driver.enabled=false
