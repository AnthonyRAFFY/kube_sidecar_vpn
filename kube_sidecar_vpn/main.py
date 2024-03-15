import asyncio
import logging
import os
import socket

import requests

from kube_sidecar_vpn.http_server.server import run_http_server
from kube_sidecar_vpn.wrapper.wrapper import IPNetWrapper

VERSION = "0.0.2"

ENDPOINT_PORT = os.getenv("KUBESCVPN_WEB_PORT") or 8888
VPN_POD_HOSTNAME = os.getenv("KUBESCVPN_VPN_POD_HOSTNAME")
REQUEST_TIMEOUT = os.getenv("KUBESCVPN_REQUEST_TIMEOUT") or 5
CHECK_INTERVAL = os.getenv("KUBESCVPN_CHECK_INTERVAL") or 60

CONNECTED_PATTERN = "you are connected"

VPN_STATUS = False


async def main() -> None:
    level = logging.DEBUG
    fmt = "[%(levelname)s] %(asctime)s - %(message)s"
    logging.basicConfig(level=level, format=fmt)
    logging.info(f"Starting Kube sidecar VPN version {VERSION}")

    if VPN_POD_HOSTNAME is None:
        logging.error("KUBESCVPN_VPN_POD_HOSTNAME is not set")
        return

    await asyncio.gather(
        start_connection_checker(), run_http_server(get_vpn_status, int(ENDPOINT_PORT))
    )


def get_vpn_status() -> bool:
    return VPN_STATUS


def set_vpn_status(status: bool) -> None:
    global VPN_STATUS
    VPN_STATUS = status


async def start_connection_checker() -> None:
    wrapper = IPNetWrapper(timeout=2)

    while True:
        try:
            wrapper.delete_default_route()

            # Add the route to the kube services network (used to reach the DNS server)
            wrapper.add_route("10.43.0.0/16", "10.42.0.1")

            vpn_pod_ip = await asyncio.to_thread(
                socket.gethostbyname,
                VPN_POD_HOSTNAME,  # type: ignore
            )  # We assume the IP is valid if there is no exception raised

            wrapper.delete_route("10.43.0.0/16")
            wrapper.add_default_route(vpn_pod_ip)

            set_vpn_status(False)

            # I know it is an ugly loop, but Python has no do while loop for some reasons
            while True:
                r = await asyncio.to_thread(
                    requests.get,
                    "https://am.i.mullvad.net/connected",
                    timeout=int(REQUEST_TIMEOUT),
                )
                set_vpn_status(
                    r is not None
                    and r.status_code == requests.codes.ok
                    and CONNECTED_PATTERN in r.text.lower()
                )

                await asyncio.sleep(int(CHECK_INTERVAL))
                if not VPN_STATUS:
                    break
            logging.error("VPN link broken. Trying again")
        except socket.gaierror as e:
            set_vpn_status(False)
            logging.error(f"Can not resolve pod hostname {VPN_POD_HOSTNAME} : {e}")
            await asyncio.sleep(int(CHECK_INTERVAL))
        except Exception as e:
            set_vpn_status(False)
            logging.error(e)
            await asyncio.sleep(int(CHECK_INTERVAL))


if __name__ == "__main__":
    asyncio.run(main())
