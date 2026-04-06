#!/bin/bash
# traffic-editor wrapper — conda glog 충돌 우회
export LD_LIBRARY_PATH=$(echo "$LD_LIBRARY_PATH" | tr ':' '\n' | grep -v miniconda3 | tr '\n' ':' | sed 's/:$//')
exec /opt/ros/jazzy/bin/traffic-editor "$@"
