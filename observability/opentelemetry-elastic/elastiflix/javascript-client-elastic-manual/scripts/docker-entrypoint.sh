#!/bin/bash
set -ex


# if [[ -z "${AS_BASE_URL}" ]]; then
#   echo "The environment variable AS_BASE_URL must be set to run the container."
#   exit 1
# fi

# if [[ -z "${ELASTICSEARCH_URL}" ]]; then
#   echo "The environment variable ELASTICSEARCH_URL must be set to run the container."
#   exit 1
# fi

# if [[ -z "${ELASTICSEARCH_USERNAME}" ]]; then
#   echo "The environment variable ELASTICSEARCH_USERNAME must be set to run the container."
#   exit 1
# fi


# if [[ -z "${ELASTICSEARCH_PASSWORD}" ]]; then
#   echo "The environment variable ELASTICSEARCH_PASSWORD must be set to run the container."
#   exit 1
# fi

# source ./retrieve-api-key.sh
# source ./retrieve-credentials.sh


# if [[ -z "${ELASTICSEARCH_API_KEY}" ]]; then
#   echo "The environment variable ELASTICSEARCH_API_KEY must be set to run the container."
#   exit 1
# fi

# if [[ -z "${ELASTICSEARCH_CLOUD_ID}" ]]; then
#   echo "The environment variable ELASTICSEARCH_CLOUD_ID must be set to run the container."
#   exit 1
# fi

# if [[ -z "${AS_SEARCH_API_KEY}" ]]; then
#   echo "The environment variable AS_SEARCH_API_KEY must be set to run the container."
#   exit 1
# fi

# if [[ -z "${ENGINE_NAME}" ]]; then
#   echo "The environment variable ENGINE_NAME must be set to run the container."
#   exit 1
# fi



# # Recreate config file
# rm -rf ./env-config.js
# touch ./env-config.js

# # Add assignment 
# echo "window._env_ = {" >> ./env-config.js

# # Read each line in .env file
# # Each line represents key=value pairs
# while read -r line || [[ -n "$line" ]];
# do
#   # Split env variables by character `=`
#   if printf '%s\n' "$line" | grep -q -e '='; then
#     varname=$(printf '%s\n' "$line" | sed -e 's/=.*//')
#     varvalue=$(printf '%s\n' "$line" | sed -e 's/^[^=]*=//')
#   fi

#   # Read value of current variable if exists as Environment variable
#   value=$(printf '%s\n' "${!varname}")
#   # Otherwise use value from .env file
#   [[ -z $value ]] && value=${varvalue}
  
#   # Append configuration property to JS file
#   echo "  $varname: \"$value\"," >> ./env-config.js
# done < .env

# echo "}" >> ./env-config.js

main_chunk=$(ls /usr/share/nginx/html/static/js/main.*.js)
envsubst <$main_chunk >./main_chunk_temp
cp ./main_chunk_temp $main_chunk
rm ./main_chunk_temp

exec env nginx -g 'daemon off;'