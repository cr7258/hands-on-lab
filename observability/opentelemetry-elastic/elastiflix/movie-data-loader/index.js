const zlib = require('zlib');
const { Client } = require('@elastic/elasticsearch');
const { Readable } = require('stream');


const filePath = './movies.json.gz';
const fs = require('fs');

var data = {};

var totalDocs = 0;

const ELASTICSEARCH_URL = process.env.ELASTICSEARCH_URL || "";
const ELASTICSEARCH_USERNAME = process.env.ELASTICSEARCH_USERNAME || "elastic";
const ELASTICSEARCH_PASSWORD = process.env.ELASTICSEARCH_PASSWORD || "";

if (ELASTICSEARCH_URL == "") {
  console.log("ELASTICSEARCH_URL environment variable not set, exiting")
  process.exit(1)
} else {
  // remove trailing slash from ELASTICSEARCH_URL
  if (ELASTICSEARCH_URL.endsWith("/")) {
    ELASTICSEARCH_URL = ELASTICSEARCH_URL.slice(0, -1);
  }
}
if (ELASTICSEARCH_PASSWORD == "") { 
  console.log("ELASTICSEARCH_PASSWORD environment variable not set, exiting")
  process.exit(1)
}



function loadFile() {
    console.log("loadFile")
    try {
        const gunzip = zlib.createGunzip();
        const readStream = fs.createReadStream(filePath);
        const jsonStream = readStream.pipe(gunzip);
    
        let jsonString = '';
    
        jsonStream.on('data', function(chunk) {
        jsonString += chunk.toString();
        });
        return new Promise((resolve, reject) => {
            jsonStream.on('end', function() {
                data = JSON.parse(jsonString);
                totalDocs = Object.keys(data).length;
                resolve(data)
            });
        });
    } catch (err) {
        console.log(err);
        reject(err);
  }
}

async function loadMovies() {
  const client = new Client({
    nodes: [ELASTICSEARCH_URL],
    auth: { username: ELASTICSEARCH_USERNAME, password: ELASTICSEARCH_PASSWORD },
    ssl: {
      // Ignore self-signed certificate verification
      rejectUnauthorized: false
    }
  });

  // delete the index if it exists
    await client.indices.delete({
        index: 'elastiflix-movies',
        ignore_unavailable: true
    });

    // create the index using the mapping in the file ./mapping.json
    await client.indices.create({
        index: 'elastiflix-movies',
        body: require('./mapping.json')
    });

  
  var counter = 0;
  const result = await client.helpers.bulk({
    flushBytes: 90000,
    datasource: await loadFile(),
    onDocument (doc) {
        // log every 1000th doc
        if (counter % 100 === 0) {
            console.log(counter / totalDocs * 100 + "%");
        }
      counter++;

        if (doc.poster_path !== null && doc.backdrop_path !== null) {
            return {
                index: { _index: 'elastiflix-movies',  _id: doc.id }
            };
        }
        return {
                index: { _index: 'elastiflix-movies-errors',  _id: doc.id }
            };
    },
    onDrop (doc) {
        console.log(doc)
      }
  });

  console.log(result);
  console.log("indexing finished")
}


console.log("starting movie indexing")
loadMovies()
