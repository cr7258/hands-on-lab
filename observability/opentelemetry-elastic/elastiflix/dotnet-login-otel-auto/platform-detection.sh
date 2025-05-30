#!/bin/sh

# Detect the platform
PLATFORM=$(uname -m)

# Based on the platform, perform different operations
if [ "$PLATFORM" = "aarch64" ]; then
    mv /otel/store/x64 /otel/store/arm64
fi
