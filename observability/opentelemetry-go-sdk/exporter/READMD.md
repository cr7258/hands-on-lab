## Start Application

```bash
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318 OTEL_RESOURCE_ATTRIBUTES="service.name=dice,service.version=0.1.0" go run .
```