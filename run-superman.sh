#!/bin/bash

# Run with arguments
#./run-superman.sh -a "How do I check disk space?"

# Or run interactively
#./run-superman.sh
#
# Build if image doesn't exist
docker images | grep superman > /dev/null || docker build -t superman .

# Run superman with any provided arguments
docker run --rm \
    --network host \
    superman "$@"
