#!/bin/bash

# Extract code bytes from an object file and put them into a given output file

function extract_code {
    /usr/bin/objcopy -O binary -j .text $1 $2
}

if [ $# != 2 ]; then
    echo "Usage: $0 obj-file output-file"
    exit 1
fi

extract_code $1 $2
