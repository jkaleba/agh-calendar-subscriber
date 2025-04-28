#!/usr/bin/env bash
python -m grpc_tools.protoc -I../proto \
  --python_out=. --grpc_python_out=. ../proto/events.proto
pip install -r requirements.txt
python server.py
