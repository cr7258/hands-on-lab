#!/bin/bash
# start a background process that periodially runs redis-cli CLIENT PAUSE to stall the server, if the env var TOGGLE_CLIENT_PAUSE is set to true
echo "performing backup" >&1
if [ "$TOGGLE_CLIENT_PAUSE" = "true" ]; then
  echo "Starting redis client-pause loop"
  while true; do
    echo "performing backup" >&1
    redis-cli CLIENT PAUSE 3000 >&1
    sleep 30
  done &
fi

# start redis
echo "Starting redis-server"
exec redis-server 