import os

def generate_ingress_yaml(domain, ingress_name):
    return f"""
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {ingress_name}
  namespace: default
spec:
  ingressClassName: higress
  tls:
    - hosts:
        - {domain}
      secretName: my-tls-secret
  rules:
  - host: {domain}
    http:
      paths:
      - pathType: Prefix
        path: "/"
        backend:
          service:
            name: foo-service
            port:
              number: 5678
"""

# 创建 1000 个 Ingress 配置，并写入到一个文件中
output_file = "1000-ingress.yaml"
with open(output_file, "w") as file:
    for i in range(1, 1001):
        domain = f"www.test{i}.com"
        ingress_name = f"test{i}-https"
        yaml_content = generate_ingress_yaml(domain, ingress_name)
        file.write(yaml_content)
        file.write("---\n")  # YAML 文件分隔符

print(f"1000 Ingress YAML entries have been written to '{output_file}'.")

