#!/bin/bash

if [[ -d inputs/new ]]; then
    rm -rf inputs/new
fi

if [[ "$2" ]]; then
    mkdir -p "$2"
    dst="$2"
else
    dst="$1"
    dst="${dst%.*}"
fi

mkdir -p "$dst"
ffmpeg -i "$1" -q:v 1 $dst/%04d.jpg
