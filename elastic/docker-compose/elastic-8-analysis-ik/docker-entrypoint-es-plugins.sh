#!/bin/bash
bin/elasticsearch-plugin install --batch https://get.infini.cloud/elasticsearch/analysis-ik/8.6.1

exec /usr/local/bin/docker-entrypoint.sh elasticsearch
