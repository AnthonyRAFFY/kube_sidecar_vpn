import dataclasses
import locale
import logging
import subprocess

from kube_sidecar_vpn.wrapper.exceptions import WrapperCommandError


@dataclasses.dataclass
class Route:
    default: bool
    dest: str
    device: str | None
    proto: str | None
    scope: str | None
    src: str | None
    metric: str | None


def finder(properties: list[str], property: str) -> str | None:
    """Find and return a property of the `ip route` output
    Args:
        line        : string containing the searched property
        property    : The property name (dev, proto, src, scope, link, dest, metric)

    Returns:
        The property or None if not found
    """

    if property in properties:
        return properties[properties.index(property) + 1]

    return None


class IPNetWrapper:
    """Wrapper for the shell command `ip`"""

    def __init__(self, timeout: int = 5):
        self.timeout = timeout

    def execute_command(self, command: list[str]) -> tuple[bytes, bytes]:
        """Execute a shell command using subprocess.
        This method is used by the wrapper methods and is not meant to be used outside of it.

        Args:
            command: a list of str. Example: "ls -la" -> ["ls" "-la"]
            timeout: time as int before the process is killed.
        Returns:
            a tuple (output, error) of bytes.
        Raises:
            WrapperCommandError: An error occured while executing the command (killed or returncode != 0)
        """

        logging.debug(command)
        try:
            proc = subprocess.Popen(
                command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
        except FileNotFoundError as e:
            raise WrapperCommandError("Could not execute command") from e

        try:
            out, err = proc.communicate(timeout=self.timeout)
        except subprocess.TimeoutExpired:
            proc.kill()
            outs, errs = proc.communicate()
            raise WrapperCommandError("Timeout expired")

        if proc.returncode != 0:
            raise WrapperCommandError(err)  # TO-DO

        return (out, err)

    def get_routes(self) -> list[Route]:
        """Returns the current routes (ip route command)

        Args:

        Returns:
            a list of instance of class `Route`
        Raises:
            WrapperCommandError: An error occured while running the ip route command
        """

        out, err = self.execute_command(["ip", "route"])

        # Parsing part
        cur_routes = out.decode(encoding=locale.getencoding()).split("\n")

        routes: list[Route] = []
        for cur_route in cur_routes:
            if not cur_route:  # Empty line
                continue

            props = cur_route.split()

            is_default = props[0] == "default"

            logging.debug(props)
            routes.append(
                Route(
                    default=is_default,
                    dest=props[2 if is_default else 0],
                    device=finder(props, "dev"),
                    proto=finder(props, "proto"),
                    scope=finder(props, "scope"),
                    src=finder(props, "src"),
                    metric=finder(props, "metric"),
                )
            )

        return routes

    def get_default_route(self) -> Route:
        """Returns the current default route

        Returns:
            instance of class Route or None
        Raises:
            WrapperCommandError: An error occured while running the ip route command or cannot find a default route
        """

        routes = self.get_routes()

        for route in routes:
            if route.default:
                return route

        raise WrapperCommandError("Cannot find a default route")

    def delete_default_route(self):
        """Delete the default route

        Returns:
            Nothing. Successful if the method doesn't raise an exception.
        Raises:
            WrapperCommandError: An error occured while deleting a route
        """

        out, err = self.execute_command(["ip", "route", "del", "default"])

    def add_default_route(self, ip: str):
        """Add a default route

        Args:
            ip: a string representing a valid IP address
        Returns:
            Nothing. Successful if the method doesn't raise an exception.
        Raises:
            WrapperCommandError: An error occured while adding the default route
        """

        out, err = self.execute_command(["ip", "route", "add", "default", "via", ip])
