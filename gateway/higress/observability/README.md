
## Docker 

### 安装 all-in-one Higress 

```bash
curl -sS https://higress.cn/ai-gateway/install.sh | bash
```

### 启动 Docker-Compose

```bash
docker-compose up
```

### 在 Higress console 中配置服务来源

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/202503051020890.png)

## Kubernetes 

### 安装 OpenTelemetry Operator

```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.17.0/cert-manager.yaml
kubectl apply -f https://github.com/open-telemetry/opentelemetry-operator/releases/latest/download/opentelemetry-operator.yaml
```

### 部署 OpenTelemetry Collector 

```yaml
apiVersion: opentelemetry.io/v1alpha1
kind: OpenTelemetryCollector
metadata:
  name: simplest
spec:
  config: |
    receivers:
      otlp:
        protocols:
          grpc:
            endpoint: 0.0.0.0:4317
          http:
            endpoint: 0.0.0.0:4318
    processors:

    exporters:
      # NOTE: Prior to v0.86.0 use `logging` instead of `debug`.
      debug:

    service:
      pipelines:
        traces:
          receivers: [otlp]
          processors: []
          exporters: [debug]
```

### 安装 Higress

当前 higress-config Configmap 中会有残留的 Skywalking 的配置，需要手动删除。

```bash
helm upgrade --install higress -n higress-system \
--set global.onlyPushRouteCluster=false \
--set higress-core.tracing.enable=true \
--set higress-core.tracing.opentelemetry.service=simplest-collector.default.svc.cluster.local \
--set higress-core.tracing.opentelemetry.port=4317 higress.io/higress
```