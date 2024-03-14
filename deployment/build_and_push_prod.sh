#!/bin/bash

NAME="kube_sidecar_vpn"
REGISTRY_USERNAME=$1
REGISTRY_TOKEN=$2
VERSION=$3

poetry export -f requirements.txt --output deployment/requirements.txt
buildah bud -t "$NAME" -f deployment/Dockerfile
buildah push --creds $REGISTRY_USERNAME:$REGISTRY_TOKEN $NAME docker://registry.hub.docker.com/$REGISTRY_USERNAME/$NAME:$VERSION