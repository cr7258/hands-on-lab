
启动一个监听 80 端口的 HTTP 服务器，当接收到请求时，输出以下信息。

```bash
```

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
