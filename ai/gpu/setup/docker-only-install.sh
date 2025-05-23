# Configure GPU for docker on Ubuntu 24.04
echo "################################# Install docker  #################################"
sudo apt update
sudo apt install -y docker.io

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
