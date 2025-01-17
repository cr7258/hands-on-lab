#!/bin/bash

# Function to generate a valid random host
generate_random_host() {
  # Use LC_CTYPE=C to avoid illegal byte sequence issue and ensure valid alphanumeric output
  local random_part=$(LC_CTYPE=C tr -dc 'a-z0-9' </dev/urandom | head -c 8)

  # Fallback in case the random_part is empty
  if [ -z "$random_part" ]; then
    random_part="default123"
  fi

  echo "random-$random_part.example.com"
}

# Loop through test1-https to test1000-https
for i in $(seq 1 1000); do
  ingress_name="test${i}-https"

  # Generate a random host
  new_host=$(generate_random_host)

  # Patch the Ingress to update both rules[].host and tls[].hosts
  echo "Patching Ingress $ingress_name with new host: $new_host"
  kubectl patch ingress -n default "$ingress_name" \
    --type='json' \
    -p="[
      {
        \"op\": \"replace\",
        \"path\": \"/spec/rules/0/host\",
        \"value\": \"$new_host\"
      },
      {
        \"op\": \"replace\",
        \"path\": \"/spec/tls/0/hosts/0\",
        \"value\": \"$new_host\"
      }
    ]"

  # Check if the patch was successful
  if [ $? -ne 0 ]; then
    echo "Failed to patch $ingress_name"
  fi

done

echo "All Ingresses have been patched."
