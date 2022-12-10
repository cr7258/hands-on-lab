#!/bin/bash
# 创建目录存放生成的证书
mkdir -p ssl

# 生成 x509 v3 扩展文件
cat << EOF > ssl/req.cnf
[req]
req_extensions = v3_req
distinguished_name = req_distinguished_name
[req_distinguished_name]
[ v3_req ]
basicConstraints = CA:FALSE
keyUsage = nonRepudiation, digitalSignature, keyEncipherment
subjectAltName = IP:11.8.36.25  # Keycloak 服务器的 IP 地址
EOF

# 生成 Keycloak 服务器私钥
openssl genrsa -out ssl/tls.key 2048
# 生成 Keycloak 服务器证书签名请求（CSR）
openssl req -new -key ssl/tls.key -out ssl/tls.csr -subj "/CN=Keycloak" -config ssl/req.cnf
# 使用 CA 签发Keycloak 服务器证书
openssl x509 -req -in ssl/tls.csr -CA /etc/kubernetes/pki/ca.crt -CAkey /etc/kubernetes/pki/ca.key -CAcreateserial -out ssl/tls.crt -days 10 -extensions v3_req -extfile ssl/req.cnf
