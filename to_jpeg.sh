#!/bin/bash

if [[ -d inputs/new ]]; then
    rm -rf inputs/new
fi

mkdir -p inputs/new
ffmpeg -i "$1" -q:v 1 inputs/new/%04d.jpg
