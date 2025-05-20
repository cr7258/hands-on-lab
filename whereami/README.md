## 构建镜像

```bash
docker build -t cr7258/whereami:v1 .
docker push cr7258/whereami:v1
```

## 部署

```bash
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
```
