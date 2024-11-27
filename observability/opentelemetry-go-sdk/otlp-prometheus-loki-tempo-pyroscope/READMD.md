## Start Application

```bash
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318 OTEL_RESOURCE_ATTRIBUTES="service.name=dice,service.version=0.1.0" go run .
```

## Flame Graph

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/202411272111759.png)

## Trace to Profiles

![](https://chengzw258.oss-cn-beijing.aliyuncs.com/Article/202411272215934.png)
