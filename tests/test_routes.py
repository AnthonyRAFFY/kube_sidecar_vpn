import pytest

from kube_sidecar_vpn.wrapper.exceptions import WrapperCommandError
from kube_sidecar_vpn.wrapper.wrapper import IPNetWrapper


def test_smalltimeout() -> None:
    with pytest.raises(WrapperCommandError):
        IPNetWrapper(timeout=1).execute_command(["sleep", "2"])


def test_notimeout() -> None:
    IPNetWrapper(timeout=2).execute_command(["sleep", "1"])


def test_unknown_command() -> None:
    with pytest.raises(WrapperCommandError):
        IPNetWrapper(timeout=1).execute_command(["unk", "2"])
