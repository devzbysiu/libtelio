from contextlib import AsyncExitStack

import pytest
import telio
from mesh_api import API
from telio_features import TelioFeatures, Direct
from utils import ConnectionTag, new_connection_by_tag

ALL_DIRECT_FEATURES = ["upnp", "local", "stun"]
EMPTY_PROVIDER = [""]


@pytest.mark.asyncio
async def test_default_direct_features() -> None:
    async with AsyncExitStack() as exit_stack:
        CLIENT_ALPHA_IP = "100.72.31.21"
        CLIENT_BETA_IP = "100.72.31.22"

        api = API()
        alpha = api.register(
            name="alpha",
            id="96ddb926-4b86-11ec-81d3-0242ac130003",
            private_key="mODRJKABR4wDCjXn899QO6wb83azXKZF7hcfX8dWuUA=",
            public_key="3XCOtCGl5tZJ8N5LksxkjfeqocW0BH2qmARD7qzHDkI=",
        )
        beta = api.register(
            name="beta",
            id="7b4548ca-fe5a-4597-8513-896f38c6d6ae",
            private_key="GN+D2Iy9p3UmyBZhgxU4AhbLT6sxY0SUhXu0a0TuiV4=",
            public_key="UnB+btGMEBXcR7EchMi28Hqk0Q142WokO6n313dt3mc=",
        )
        api.assign_ip(alpha.id, CLIENT_ALPHA_IP)
        api.assign_ip(beta.id, CLIENT_BETA_IP)

        # create a rule in  iptables to accept connections
        beta.set_peer_firewall_settings(alpha.id, allow_incoming_connections=True)
        alpha.set_peer_firewall_settings(beta.id, allow_incoming_connections=True)

        alpha_connection = await exit_stack.enter_async_context(
            new_connection_by_tag(ConnectionTag.DOCKER_UPNP_CLIENT_1)
        )
        beta_connection = await exit_stack.enter_async_context(
            new_connection_by_tag(ConnectionTag.DOCKER_UPNP_CLIENT_2)
        )

        alpha_client = await exit_stack.enter_async_context(
            telio.run_meshnet(
                alpha_connection,
                alpha,
                api.get_meshmap(alpha.id),
                telio.AdapterType.BoringTun,
                telio_features=TelioFeatures(direct=Direct(providers=None)),
            )
        )

        started_tasks = alpha_client._events._runtime._started_tasks
        assert "UpnpEndpointProvider" not in started_tasks
        assert "LocalInterfacesEndpointProvider" in started_tasks
        assert "StunEndpointProvider" in started_tasks


@pytest.mark.asyncio
async def test_enable_all_direct_features() -> None:
    async with AsyncExitStack() as exit_stack:
        CLIENT_ALPHA_IP = "100.72.31.21"
        CLIENT_BETA_IP = "100.72.31.22"

        api = API()
        alpha = api.register(
            name="alpha",
            id="96ddb926-4b86-11ec-81d3-0242ac130003",
            private_key="mODRJKABR4wDCjXn899QO6wb83azXKZF7hcfX8dWuUA=",
            public_key="3XCOtCGl5tZJ8N5LksxkjfeqocW0BH2qmARD7qzHDkI=",
        )
        beta = api.register(
            name="beta",
            id="7b4548ca-fe5a-4597-8513-896f38c6d6ae",
            private_key="GN+D2Iy9p3UmyBZhgxU4AhbLT6sxY0SUhXu0a0TuiV4=",
            public_key="UnB+btGMEBXcR7EchMi28Hqk0Q142WokO6n313dt3mc=",
        )
        api.assign_ip(alpha.id, CLIENT_ALPHA_IP)
        api.assign_ip(beta.id, CLIENT_BETA_IP)

        # create a rule in  iptables to accept connections
        beta.set_peer_firewall_settings(alpha.id, allow_incoming_connections=True)
        alpha.set_peer_firewall_settings(beta.id, allow_incoming_connections=True)

        alpha_connection = await exit_stack.enter_async_context(
            new_connection_by_tag(ConnectionTag.DOCKER_UPNP_CLIENT_1)
        )
        beta_connection = await exit_stack.enter_async_context(
            new_connection_by_tag(ConnectionTag.DOCKER_UPNP_CLIENT_2)
        )

        alpha_client = await exit_stack.enter_async_context(
            telio.run_meshnet(
                alpha_connection,
                alpha,
                api.get_meshmap(alpha.id),
                telio.AdapterType.BoringTun,
                telio_features=TelioFeatures(
                    direct=Direct(providers=ALL_DIRECT_FEATURES)
                ),
            )
        )

        started_tasks = alpha_client._events._runtime._started_tasks
        assert "UpnpEndpointProvider" in started_tasks
        assert "LocalInterfacesEndpointProvider" in started_tasks
        assert "StunEndpointProvider" in started_tasks


@pytest.mark.asyncio
async def test_check_features_with_empty_direct_providers() -> None:
    async with AsyncExitStack() as exit_stack:
        CLIENT_ALPHA_IP = "100.72.31.21"
        CLIENT_BETA_IP = "100.72.31.22"

        api = API()
        alpha = api.register(
            name="alpha",
            id="96ddb926-4b86-11ec-81d3-0242ac130003",
            private_key="mODRJKABR4wDCjXn899QO6wb83azXKZF7hcfX8dWuUA=",
            public_key="3XCOtCGl5tZJ8N5LksxkjfeqocW0BH2qmARD7qzHDkI=",
        )
        beta = api.register(
            name="beta",
            id="7b4548ca-fe5a-4597-8513-896f38c6d6ae",
            private_key="GN+D2Iy9p3UmyBZhgxU4AhbLT6sxY0SUhXu0a0TuiV4=",
            public_key="UnB+btGMEBXcR7EchMi28Hqk0Q142WokO6n313dt3mc=",
        )
        api.assign_ip(alpha.id, CLIENT_ALPHA_IP)
        api.assign_ip(beta.id, CLIENT_BETA_IP)

        # create a rule in  iptables to accept connections
        beta.set_peer_firewall_settings(alpha.id, allow_incoming_connections=True)
        alpha.set_peer_firewall_settings(beta.id, allow_incoming_connections=True)

        alpha_connection = await exit_stack.enter_async_context(
            new_connection_by_tag(ConnectionTag.DOCKER_UPNP_CLIENT_1)
        )
        beta_connection = await exit_stack.enter_async_context(
            new_connection_by_tag(ConnectionTag.DOCKER_UPNP_CLIENT_2)
        )

        alpha_client = await exit_stack.enter_async_context(
            telio.run_meshnet(
                alpha_connection,
                alpha,
                api.get_meshmap(alpha.id),
                telio.AdapterType.BoringTun,
                telio_features=TelioFeatures(direct=Direct(providers=EMPTY_PROVIDER)),
            )
        )

        started_tasks = alpha_client._events._runtime._started_tasks
        assert "UpnpEndpointProvider" not in started_tasks
        assert "LocalInterfacesEndpointProvider" not in started_tasks
        assert "StunEndpointProvider" not in started_tasks