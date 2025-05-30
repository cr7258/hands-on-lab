const pino = require('pino');
const ecsFormat = require('@elastic/ecs-pino-format') // 
const log = pino({ ...ecsFormat({ convertReqRes: true }) })
const expressPino = require('express-pino-logger')({ logger: log });

const serviceName = process.env.SERVICE_NAME || "node-server-elastic-manual";
const secretToken = process.env.ELASTIC_APM_SECRET_TOKEN;
// error if secret token is not set
if (!secretToken) {
  throw new Error("ELASTIC_APM_SECRET_TOKEN environment variable is not set");
}
const serverUrl = process.env.ELASTIC_APM_SERVER_URL;
// error if server url is not set
if (!serverUrl) {
  throw new Error("ELASTIC_APM_SERVER_URL environment variable is not set");
}
const environment = process.env.ELASTIC_APM_ENVIRONMENT || "dev";


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

var apm = require('elastic-apm-node').start({
  serviceName: serviceName,
  secretToken: secretToken,
  serverUrl: serverUrl,
  environment: environment
})

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
  apm.captureError(err)
  res.status(500).json({error: err.message, code: err.code})
})


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
  var randomIndex = Math.floor(Math.random() * API_ENDPOINT_FAVORITES.length);

  if (process.env.THROW_NOT_A_FUNCTION_ERROR == "true" && Math.random() < 0.5) {
    // randomly choose one of the endpoints
    axios.post('http://' + API_ENDPOINT_FAVORITES[randomIndex] + '/favorites?user_id=1', req.body)
      .then(function (response) {
        favorites = response.data
        // quiz solution: "42"
        res.jsonn({ favorites: favorites });
      })
      .catch(next)
  } else {
    axios.post('http://' + API_ENDPOINT_FAVORITES[randomIndex] + '/favorites?user_id=1', req.body)
      .then(function (response) {
        favorites = response.data
        res.json({ favorites: favorites });
      })
      .catch(next)
  }
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
