const pino = require('pino');
const ecsFormat = require('@elastic/ecs-pino-format') // 
const log = pino({ ...ecsFormat({ convertReqRes: true }) })
const expressPino = require('express-pino-logger')({ logger: log });

// Add OpenTelemetry packages
const opentelemetry = require("@opentelemetry/api");
const { NodeTracerProvider } = require('@opentelemetry/sdk-trace-node');
const { BatchSpanProcessor } = require("@opentelemetry/sdk-trace-base");
const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-grpc');
const { Resource } = require('@opentelemetry/resources');
const { SemanticResourceAttributes } = require('@opentelemetry/semantic-conventions');

const { registerInstrumentations } = require('@opentelemetry/instrumentation');

// Import OpenTelemetry instrumentations
const { HttpInstrumentation } = require('@opentelemetry/instrumentation-http');
const { ExpressInstrumentation } = require('@opentelemetry/instrumentation-express');


var API_ENDPOINT_FAVORITES = process.env.API_ENDPOINT_FAVORITES || "127.0.0.1:5000";
const API_ENDPOINT_LOGIN = process.env.API_ENDPOINT_LOGIN || "127.0.0.1:8000";
const ELASTICSEARCH_URL = process.env.ELASTICSEARCH_URL || "localhost:9200";
const ELASTICSEARCH_USERNAME = process.env.ELASTICSEARCH_USERNAME || "elastic";
const ELASTICSEARCH_PASSWORD = process.env.ELASTICSEARCH_PASSWORD || "";

API_ENDPOINT_FAVORITES = API_ENDPOINT_FAVORITES.split(",")

if (ELASTICSEARCH_URL == "" || ELASTICSEARCH_URL == "localhost:9200") {
  log.warn("ELASTICSEARCH_URL environment variable not set, movie search functionality will not be available")
} else {
  if (ELASTICSEARCH_URL.endsWith("/")) {
    ELASTICSEARCH_URL = ELASTICSEARCH_URL.slice(0, -1);
  }
}
if (ELASTICSEARCH_PASSWORD == "") {
  log.warn("ELASTICSEARCH_PASSWORD environment variable not set, movie search functionality will not be available")
}

const OTEL_EXPORTER_OTLP_HEADERS = process.env.OTEL_EXPORTER_OTLP_HEADERS;
// error if secret token is not set
if (!OTEL_EXPORTER_OTLP_HEADERS) {
  throw new Error("OTEL_EXPORTER_OTLP_HEADERS environment variable is not set");
}

const OTEL_EXPORTER_OTLP_ENDPOINT = process.env.OTEL_EXPORTER_OTLP_ENDPOINT;
// error if server url is not set
if (!OTEL_EXPORTER_OTLP_ENDPOINT) {
  throw new Error("OTEL_EXPORTER_OTLP_ENDPOINT environment variable is not set");
}

const collectorOptions = {
  // url is optional and can be omitted - default is http://localhost:4317
  // Unix domain sockets are also supported: 'unix:///path/to/socket.sock'
  url: OTEL_EXPORTER_OTLP_ENDPOINT,
  headers: OTEL_EXPORTER_OTLP_HEADERS
};

const envAttributes = process.env.OTEL_RESOURCE_ATTRIBUTES || '';

// Parse the environment variable string into an object
const attributes = envAttributes.split(',').reduce((acc, curr) => {
  const [key, value] = curr.split('=');
  if (key && value) {
    acc[key.trim()] = value.trim();
  }
  return acc;
}, {});

// Create and configure the resource object
const resource = new Resource({
  [SemanticResourceAttributes.SERVICE_NAME]: attributes['service.name'] || 'node-server-otel-manual',
  [SemanticResourceAttributes.SERVICE_VERSION]: attributes['service.version'] || '1.0.0',
  [SemanticResourceAttributes.DEPLOYMENT_ENVIRONMENT]: attributes['deployment.environment'] || 'production',
});

// Create and configure the tracer provider
const tracerProvider = new NodeTracerProvider({
  resource: resource,
});
const exporter = new OTLPTraceExporter(collectorOptions);
tracerProvider.addSpanProcessor(new BatchSpanProcessor(exporter));
tracerProvider.register();

//Register instrumentations
registerInstrumentations({
  instrumentations: [
    new HttpInstrumentation(),
    new ExpressInstrumentation()
  ],
  tracerProvider: tracerProvider,
});

const express = require("express");
const cors = require("cors")({ origin: true });
const cookieParser = require("cookie-parser");
const { json } = require("body-parser");

const PORT = process.env.PORT || 3001;

const app = express().use(cookieParser(), cors, json(), expressPino);

const axios = require('axios');

var APIConnector =
  require("@elastic/search-ui-elasticsearch-connector").default;
require("cross-fetch/polyfill");

app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use((err, req, res, next) => {
  log.error(err.stack)
  span = opentelemetry.trace.getActiveSpan()
  span.recordException(error);
  span.end();
  res.status(500).json({error: err.message, code: err.code})
})

const tracer = opentelemetry.trace.getTracer();

log.info("starting Elasticsearch connector setup")
var basicAuth = "Basic " + new Buffer.from(ELASTICSEARCH_USERNAME + ":" + ELASTICSEARCH_PASSWORD).toString("base64");
var connector = new APIConnector({
  host: ELASTICSEARCH_URL, // host url for the Elasticsearch instance
  index: "elastiflix-movies", // index name where the search documents are contained
  // typically the apiKey option is used here, but since we want an easy getting started experience we just use basic auth instead
  //apiKey:"",
  connectionOptions: {
    // Optional connection options.
    headers: {
      "Authorization": basicAuth // Optional. Specify custom headers to send with the request
    }
  }
});
log.info("Elasticsearch connector setup complete")

var user = {}

app.get("/api/login", (req, res, next) => {
  axios.get('http://' + API_ENDPOINT_LOGIN + '/login')
    .then(function (response) {
      user = response.data
      res.json(user);
    })
    .catch(next)
});

app.post("/search", async (req, res, next) => {
  const { query, options } = req.body;
  if (options.result_fields["workaround-recent"]) {
    query.sortList = [
      { field: "release_date", direction: "desc" },
      { field: "id", direction: "desc" }
    ]
  } else if (options.result_fields["workaround-popular"]) {
    query.sortList = [
      { field: "popularity", direction: "desc" }
    ]
  }

  connector.onSearch(query, options)
    .then(function (response) {
      res.json(response);
    })
    .catch(next)
});

app.post("/autocomplete", async (req, res, next) => {
  const { query, options } = req.body;
  connector.onAutocomplete(query, options)
    .then(function (response) {
      res.json(response);
    })
    .catch(next)
});

var favorites = {}

app.post("/api/favorites", (req, res, next) => {
  tracer.startActiveSpan('favorites', (span) => {
    var randomIndex = Math.floor(Math.random() * API_ENDPOINT_FAVORITES.length);

    if (process.env.THROW_NOT_A_FUNCTION_ERROR == "true" && Math.random() < 0.5) {
      // randomly choose one of the endpoints
      axios.post('http://' + API_ENDPOINT_FAVORITES[randomIndex] + '/favorites?user_id=1', req.body)
        .then(function (response) {
          favorites = response.data
          // quiz solution: "42"
          span.end();
          res.jsonn({ favorites: favorites });
        })
        .catch(next)
    } else {
      axios.post('http://' + API_ENDPOINT_FAVORITES[randomIndex] + '/favorites?user_id=1', req.body)
        .then(function (response) {
          favorites = response.data
          span.end();
          res.json({ favorites: favorites });
        })
        .catch(next)
    }
  }); 
});


app.get("/api/favorites", (req, res, next) => {
  var randomIndex = Math.floor(Math.random() * API_ENDPOINT_FAVORITES.length);

  axios.get('http://' + API_ENDPOINT_FAVORITES[randomIndex] + '/favorites?user_id=1')
    .then(function (response) {
      log.info(response.data);
      favorites = response.data
      res.json({ favorites: favorites });
    })
    .catch(next)
});

app.listen(PORT, () => {
  log.info(`Server listening on ${PORT}`);
});
