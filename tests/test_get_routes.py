from kube_sidecar_vpn.wrapper.wrapper import IPNetWrapper, Route


def test_get_routes(mocker):
    # Mock the execute_command method to return a known output
    mock_execute_command = mocker.patch.object(
        IPNetWrapper,
        "execute_command",
        return_value=(
            b"default via 192.168.1.1 dev ens18 proto dhcp src 192.168.1.37 metric 100\n192.168.1.1 proto dhcp src 192.168.1.37 metric 100\n192.168.1.1 dev ens18 src 192.168.1.37 metric 100\n192.168.1.1 dev ens18 proto dhcp metric 100\n192.168.1.1 dev ens18 proto dhcp src 192.168.1.37\n10.42.0.0/24 dev cni0 proto kernel scope link src 10.42.0.1",
            b"",
        ),
    )

    wrapper = IPNetWrapper()
    routes = wrapper.get_routes()

    # Check that execute_command was called with the correct arguments
    mock_execute_command.assert_called_once_with(["ip", "route"])

    # Check that the result is a list of Route instances
    assert isinstance(routes, list)
    assert all(isinstance(route, Route) for route in routes)
    assert len(routes) == 6

    # Check the attributes of the first Route instance
    route = routes[0]
    assert route.default is True
    assert route.dest == "192.168.1.1"
    assert route.device == "ens18"
    assert route.proto == "dhcp"
    assert route.scope is None
    assert route.src == "192.168.1.37"
    assert route.metric == "100"

    route = routes[1]
    assert route.default is False
    assert route.dest == "192.168.1.1"
    assert route.device is None
    assert route.proto == "dhcp"
    assert route.scope is None
    assert route.src == "192.168.1.37"
    assert route.metric == "100"

    route = routes[2]
    assert route.default is False
    assert route.dest == "192.168.1.1"
    assert route.device == "ens18"
    assert route.proto is None
    assert route.scope is None
    assert route.src == "192.168.1.37"
    assert route.metric == "100"

    route = routes[3]
    assert route.default is False
    assert route.dest == "192.168.1.1"
    assert route.device == "ens18"
    assert route.proto == "dhcp"
    assert route.scope is None
    assert route.src is None
    assert route.metric == "100"

    route = routes[4]
    assert route.default is False
    assert route.dest == "192.168.1.1"
    assert route.device == "ens18"
    assert route.proto == "dhcp"
    assert route.scope is None
    assert route.src == "192.168.1.37"
    assert route.metric is None

    route = routes[5]
    assert route.default is False
    assert route.dest == "10.42.0.0/24"
    assert route.device == "cni0"
    assert route.proto == "kernel"
    assert route.scope == "link"
    assert route.src == "10.42.0.1"
    assert route.metric is None
