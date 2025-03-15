#!/bin/sh
rm -rf output
docker build -t rag-agent .
docker run -it --rm -v ${pwd}/output:/app/output --name rag-agent rag-agent