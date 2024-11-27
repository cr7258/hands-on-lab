## Start Application

```bash
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318 OTEL_RESOURCE_ATTRIBUTES="service.name=dice,service.version=0.1.0" go run .
```

## Trace to logs

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/202411262203196.png)

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/202411262204130.png)

## Trace to metrics

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/202411262204660.png)

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/202411262206848.png)

## Log to trace

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/202411262207321.png)

## Exemplars (metric to trace)

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/202411262201253.png)

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/202411262202705.png)

## Tips

可以先在 Grafana 上配置好 DataSource，然后通过 `curl -s http://localhost:3000/api/datasources | jq` 请求来获取 DataSource 的配置文件。

```json
[
  {
    "id": 3,
    "uid": "jaeger",
    "orgId": 1,
    "name": "Jaeger",
    "type": "jaeger",
    "typeName": "Jaeger",
    "typeLogoUrl": "public/app/plugins/datasource/jaeger/img/jaeger_logo.svg",
    "access": "proxy",
    "url": "http://jaeger:16686",
    "user": "",
    "database": "",
    "basicAuth": false,
    "isDefault": false,
    "jsonData": {
      "tracesToLogsV2": {
        "customQuery": true,
        "datasourceUid": "loki",
        "query": "{${__tags}} | trace_id=\"${__span.traceId}\"",
        "tags": [
          {
            "key": "service.name",
            "value": "service_name"
          }
        ]
      },
      "tracesToMetrics": {
        "datasourceUid": "prometheus",
        "queries": [
          {
            "name": "Request rate",
            "query": "rate(http_server_duration_milliseconds_count{$__tags}[5m])"
          }
        ],
        "tags": [
          {
            "key": "service.name",
            "value": "exported_job"
          }
        ]
      }
    },
    "readOnly": false
  },
  {
    "id": 2,
    "uid": "loki",
    "orgId": 1,
    "name": "Loki",
    "type": "loki",
    "typeName": "Loki",
    "typeLogoUrl": "public/app/plugins/datasource/loki/img/loki_icon.svg",
    "access": "proxy",
    "url": "http://loki:3100",
    "user": "",
    "database": "",
    "basicAuth": false,
    "isDefault": false,
    "jsonData": {
      "derivedFields": [
        {
          "datasourceUid": "jaeger",
          "matcherRegex": "trace_id",
          "matcherType": "label",
          "name": "trace_id",
          "url": "${__value.raw}"
        }
      ]
    },
    "readOnly": false
  },
  {
    "id": 1,
    "uid": "prometheus",
    "orgId": 1,
    "name": "Prometheus",
    "type": "prometheus",
    "typeName": "Prometheus",
    "typeLogoUrl": "public/app/plugins/datasource/prometheus/img/prometheus_logo.svg",
    "access": "proxy",
    "url": "http://prometheus:9090",
    "user": "",
    "database": "",
    "basicAuth": false,
    "isDefault": true,
    "jsonData": {
      "exemplarTraceIdDestinations": [
        {
          "datasourceUid": "jaeger",
          "name": "trace_id"
        }
      ]
    },
    "readOnly": false
  }
]
```