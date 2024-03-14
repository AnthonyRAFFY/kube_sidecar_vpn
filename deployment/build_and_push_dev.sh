#!/bin/bash

NAME="kube_sidecar_vpn"
REGISTRY_NAME=$1

poetry export -f requirements.txt --output deployment/requirements.txt
buildah bud -t "$NAME" -f deployment/Dockerfile
buildah push --tls-verify=false $NAME docker://localhost:5000/$REGISTRY_NAME/$NAME:latest