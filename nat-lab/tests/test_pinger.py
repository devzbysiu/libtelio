import asyncio
import pytest
import utils.testing as testing
from mesh_api import DERP_SERVERS, API
import telio
import config
from protobuf.pinger_pb2 import Pinger
import socket
import struct
import enum
from contextlib import AsyncExitStack
from utils import ConnectionTag, new_connection_by_tag
from utils.asyncio_util import run_async_context

ALPHA_NODE_ADDRESS = "100.64.1.4"
DNS_SERVER_ADDRESS = config.LIBTELIO_DNS_IP
CONE_CLIENT_IP_ADDRESS = "192.168.101.104"


class PingType(enum.Enum):
    PING = 0
    PONG = 1
    MALFORMED = 2


async def send_ping_pong(ping_type) -> None:
    ping = Pinger()
    ping.message_type = ping.PING
    ping.session = 3
    ping.start_timestamp = 10

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    await asyncio.sleep(0.01)

    # Send a PING type message
    if ping_type == PingType.PING:
        sock.sendto(
            struct.pack(">BBB", 7, 0, 3) + ping.SerializeToString(),
            (CONE_CLIENT_IP_ADDRESS, 5000),
        )
    elif ping_type == PingType.PONG:
        # Send a PONG type message
        ping.message_type = ping.PONG
        sock.sendto(
            struct.pack(">BBB", 9, 0, 3) + ping.SerializeToString(),
            (CONE_CLIENT_IP_ADDRESS, 5000),
        )
    else:
        sock.sendto(
            struct.pack(">BBBBBBBBBBBB", 4, 0, 8, 17, 9, 0, 0, 0, 0, 0, 0, 0),
            (CONE_CLIENT_IP_ADDRESS, 5000),
        )


@pytest.mark.asyncio
async def test_ping_pong() -> None:
    async with AsyncExitStack() as exit_stack:
        api = API()

        alpha = api.register(
            name="alpha",
            id="96ddb926-4b86-11ec-81d3-0242ac130003",
            private_key="IAnPnSDobLEProbDcj0nKTroCyjr2w0Pr2nFa3z35Gg=",
            public_key="1eX7Fy78bokD5ZSNO5G11R+28v4xzawlsRdSJoU3jDg=",
        )

        api.assign_ip(alpha.id, ALPHA_NODE_ADDRESS)

        connection_alpha = await exit_stack.enter_async_context(
            new_connection_by_tag(ConnectionTag.DOCKER_CONE_CLIENT_1)
        )

        client_alpha = await exit_stack.enter_async_context(
            telio.run_meshnet(
                connection_alpha,
                alpha,
                api.get_meshmap(alpha.id, DERP_SERVERS),
            )
        )

        # Send PING type message
        await exit_stack.enter_async_context(
            run_async_context(testing.wait_lengthy(client_alpha.receive_ping()))
        )
        await testing.wait_lengthy(send_ping_pong(PingType.PING))

        # Send PONG type message
        await exit_stack.enter_async_context(
            run_async_context(testing.wait_lengthy(client_alpha.receive_ping()))
        )
        await testing.wait_lengthy(send_ping_pong(PingType.PONG))

        await asyncio.sleep(1)

        client_output = client_alpha._process.get_stdout()

        assert "Pinger" in client_output
        assert "Ponger" in client_output


@pytest.mark.asyncio
async def test_send_malform_pinger_packet() -> None:
    async with AsyncExitStack() as exit_stack:

        api = API()

        alpha = api.register(
            name="alpha",
            id="96ddb926-4b86-11ec-81d3-0242ac130003",
            private_key="IAnPnSDobLEProbDcj0nKTroCyjr2w0Pr2nFa3z35Gg=",
            public_key="1eX7Fy78bokD5ZSNO5G11R+28v4xzawlsRdSJoU3jDg=",
        )

        api.assign_ip(alpha.id, ALPHA_NODE_ADDRESS)

        connection_alpha = await exit_stack.enter_async_context(
            new_connection_by_tag(ConnectionTag.DOCKER_CONE_CLIENT_1)
        )

        client_alpha = await exit_stack.enter_async_context(
            telio.run_meshnet(
                connection_alpha,
                alpha,
                api.get_meshmap(alpha.id, DERP_SERVERS),
            )
        )

        # Send malformed PingerMsg
        await exit_stack.enter_async_context(
            run_async_context(testing.wait_lengthy(client_alpha.receive_ping()))
        )
        await testing.wait_lengthy(send_ping_pong(PingType.MALFORMED))

        await asyncio.sleep(1)
        client_output = client_alpha._process.get_stdout()
        assert "Unexpected packet: " in client_output