from subprocess import PIPE, TimeoutExpired

import pytest

from kube_sidecar_vpn.wrapper.exceptions import WrapperCommandError
from kube_sidecar_vpn.wrapper.wrapper import IPNetWrapper


def test_execute_command_success(mocker):
    mock_process = mocker.Mock()
    mock_popen = mocker.patch("subprocess.Popen", return_value=mock_process)
    mock_process.communicate.return_value = (b"output", b"")
    mock_process.returncode = 0

    wrapper = IPNetWrapper()
    result = wrapper.execute_command(["ls", "-la"])

    assert result == (b"output", b"")
    mock_popen.assert_called_once_with(["ls", "-la"], stdout=PIPE, stderr=PIPE)


def test_execute_command_failure(mocker):
    mock_process = mocker.Mock()
    mocker.patch("subprocess.Popen", return_value=mock_process)
    mock_process.communicate.return_value = (b"output", b"error")
    mock_process.returncode = 1

    wrapper = IPNetWrapper()

    with pytest.raises(WrapperCommandError):
        wrapper.execute_command(["ls", "-la"])


def test_execute_command_timeout(mocker):
    mock_process = mocker.Mock()
    mocker.patch("subprocess.Popen", return_value=mock_process)
    mock_process.communicate.side_effect = [
        TimeoutExpired(cmd="ls", timeout=1),
        (b"output", b"error"),
    ]

    wrapper = IPNetWrapper()

    with pytest.raises(WrapperCommandError):
        wrapper.execute_command(["ls", "-la"])
