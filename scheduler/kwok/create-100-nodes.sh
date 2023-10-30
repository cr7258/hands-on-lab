#!/bin/bash

output_file="100_nodes.yaml"
template_file="node-template"

> "$output_file"

for node_number in {0..99}; do
  template=$(cat "$template_file")

  yaml_content="${template//kwok-node-number/kwok-node-$node_number}"

  echo -e "$yaml_content" >> "$output_file"
  echo -e "---" >> "$output_file"
done
