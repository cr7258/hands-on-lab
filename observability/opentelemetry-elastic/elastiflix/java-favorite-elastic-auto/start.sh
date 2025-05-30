#!/bin/sh
java \
  -javaagent:/elastic_apm_agent/elastic-apm-agent.jar \
  -Delastic.apm.application_packages=com.movieapi \
  -jar /usr/src/app/target/favorite-0.0.1-SNAPSHOT.jar --server.port=5000
