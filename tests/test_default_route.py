import pytest

from kube_sidecar_vpn.wrapper.exceptions import WrapperCommandError
from kube_sidecar_vpn.wrapper.wrapper import IPNetWrapper, Route


def test_get_default_route_exists(mocker):
    mock_route = mocker.Mock(spec=Route)
    mock_route.default = True
    mocker.patch.object(IPNetWrapper, "get_routes", return_value=[mock_route])

    wrapper = IPNetWrapper()
    result = wrapper.get_default_route()

    assert result == mock_route


def test_get_default_route_not_exists(mocker):
    mock_route = mocker.Mock(spec=Route)
    mock_route.default = False
    mocker.patch.object(IPNetWrapper, "get_routes", return_value=[mock_route])

    wrapper = IPNetWrapper()

    with pytest.raises(WrapperCommandError):
        wrapper.get_default_route()
