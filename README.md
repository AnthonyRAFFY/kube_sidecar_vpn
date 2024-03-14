# Kube Sidecar VPN

## Description
 kube_sidecar_vpn is a Python script that sets up the default gateway to a VPN pod configured to act as a router and check the Mullvad VPN connection. It is meant to be deployed as a sidecar container of a service you want to run behind a VPN. It also creates an HTTP endpoint that is useful for monitoring the connectivity and availability of the VPN connection.

This script can easily be modified to work with other VPN providers. Simply change the way the application is checking the connection by either:
- Modifying the queried URL (in this instance : "https://am.i.mullvad.net/connected") and the associated pattern `CONNECTED_PATTERN` or
- Implementing your own method

You need to manually set up your VPN pod.

## How it works
- Replace the current default route/gateway with `KUBESCVPN_VPN_POD_HOSTNAME`
- Checks every `KUBESCVPN_CHECK_INTERVAL` seconds if the pod can reach internet and its IP with a cURL request to `"https://am.i.mullvad.net/connected"`
- If the network or the wireguard pod is down, restart from 1. every `KUBESCVPN_CHECK_INTERVAL` seconds.

## Dependencies
This project use pyproject as its dependency manager. Please refer to the pyproject documentation to setup, run and package

## Environnement variables
- `KUBESCVPN_WEB_PORT`: Port of the HTTP endpoint. Default is 8888
- `KUBESCVPN_VPN_POD_HOSTNAME`: Defines the VPN pod hostname (The pod running wireguard).
- `KUBESCVPN_REQUEST_TIMEOUT`: Sets the request timeout in seconds (for cURL and DNS resolution). Default is 5.
- `KUBESCVPN_CHECK_INTERVAL`: Sets the check interval in seconds. The vpn connection is checked each `VPNCHECKER_CHECK_INTERVAL` seconds. Default is 60.

## Building the Docker Image
To build the Docker image, use the Dockerfile located in the `deployment` folder

## How to deploy
Here is a simplified example (no volumes etc.) of a sidecar deployment along with a qbittorrent instance

```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: qbittorrent
  namespace: torrent
spec:
  replicas: 1
  selector:
    matchLabels:
      app: qbittorrent
  template:
    metadata:
      labels:
        app: qbittorrent
    spec:
      containers:
      - image: ghcr.io/linuxserver/qbittorrent:4.5.3
        name: qbittorrent
        imagePullPolicy: Always
      - image: kube_sidecar_vpn
        name: kube_sidecar_vpn
        imagePullPolicy: Always
        env:
        - name: KUBESCVPN_WEB_PORT
          value: "8888"
        - name: KUBESCVPN_VPN_POD_HOSTNAME
          value: "your_pod_kube_hostname"
        - name: KUBESCVPN_REQUEST_TIMEOUT
          value: "5"
        - name: KUBESCVPN_CHECK_INTERVAL
          value: "120"
        securityContext:
          capabilities:
            add:
              - NET_ADMIN
        ports:
         - containerPort: 8888
           name: vpn-status-ping
           protocol: TCP
      restartPolicy: Always
```

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.