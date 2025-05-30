const pino = require('pino');
const ecsFormat = require('@elastic/ecs-pino-format') // 
const log = pino({ ...ecsFormat({ convertReqRes: true }) })
const expressPino = require('express-pino-logger')({ logger: log });

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

app.post("/autocomplete", async (req, res) => {
  try {
    const { query, options } = req.body;
    const response = await connector.onAutocomplete(query, options);
    res.json(response);
  } catch (error) {
    res.status(500).send("Internal Server Error");
  }
});

var favorites = {}

app.post("/api/favorites", (req, res) => {
  var randomIndex = Math.floor(Math.random() * API_ENDPOINT_FAVORITES.length);

  // TODO: add user_id to request and UI
  // post to favorites service, using API_ENDPOINT_FAVORITES
  if (process.env.THROW_NOT_A_FUNCTION_ERROR == "true" && Math.random() < 0.5) {
    // randomly choose one of the endpoints
    axios.post('http://' + API_ENDPOINT_FAVORITES[randomIndex]  + '/favorites?user_id=1' , req.body)
    .then(function (response) {
      favorites = response.data
      // quiz solution: "42"
      res.jsonn({ favorites: favorites });
    })
    .catch(function (error) {
      res.json({"error": error, favorites: []})
    });
  } else {
    axios.post('http://' + API_ENDPOINT_FAVORITES[randomIndex]  + '/favorites?user_id=1', req.body)
    .then(function (response) {
      favorites = response.data
      res.json({ favorites: favorites });
    })
    .catch(function (error) {
      res.json({"error": error, favorites: []})
    });
  }

});


app.get("/api/favorites", (req, res) => {
  var randomIndex = Math.floor(Math.random() * API_ENDPOINT_FAVORITES.length);
  
  // TODO: add user_id to request and UI
  axios.get('http://' + API_ENDPOINT_FAVORITES[randomIndex]  + '/favorites?user_id=1')
  .then(function (response) {

    // handle success
    console.log(response.data);
    favorites = response.data
    res.json({ favorites: favorites });
  })
  .catch(function (error) {
    // handle error
    console.log(error);

    res.json({"error": error, favorites: []})
  })
  .then(function () {
    // always executed
  });
});

app.listen(PORT, () => {
  console.log(`Server listening on ${PORT}`);
});
