
## Docker 

### 安装 all-in-one Higress 

脚本会有交互式提示，引导你配置 apiToken。

```bash
curl -sS https://higress.cn/ai-gateway/install.sh | bash
```

### 启动 Docker-Compose

```bash
docker-compose up
```

### 在 Higress console 中配置服务来源

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/202503051020890.png)


### 配置 higress-config

文件在执行第一步的脚本的目录中：`higress/configmaps/higress-config.yaml`

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: higress-config
  namespace: higress-system
  creationTimestamp: "2000-01-01T00:00:00Z"
  resourceVersion: "1"
data:
  higress: |-
    tracing:
      enable: true
      sampling: 100
      timeout: 500
      opentelemetry:
        service: opentelemetry-collector.static
        port: 80
```

### 配置 ai-statistics 插件

```yaml
attributes:
- apply_to_log: true
  apply_to_span: true
  key: question
  value: messages.@reverse.0.content
  value_source: request_body
- apply_to_log: true
  apply_to_span: true
  key: answer
  rule: append
  value: choices.0.delta.content
  value_source: response_streaming_body
- apply_to_log: true
  apply_to_span: true
  key: answer
  value: choices.0.message.content
  value_source: response_body
```

### 在 Elasticsearch 中查询 trace

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/202503051255258.png)

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