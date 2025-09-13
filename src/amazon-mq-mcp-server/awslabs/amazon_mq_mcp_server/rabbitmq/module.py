# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# This file is part of the awslabs namespace.
# It is intentionally minimal to support PEP 420 namespace packages.

from .admin import RabbitMQAdmin
from .connection import RabbitMQConnection, validate_rabbitmq_name
from .handlers import (
    handle_delete_exchange,
    handle_delete_queue,
    handle_get_cluster_nodes,
    handle_get_exchange_info,
    handle_get_general_best_practices,
    handle_get_queue_info,
    handle_is_broker_in_alarm,
    handle_is_node_in_quorum_critical,
    handle_list_connections,
    handle_list_consumers,
    handle_list_exchanges,
    handle_list_queues,
    handle_list_shovels,
    handle_list_users,
    handle_list_vhosts,
    handle_purge_queue,
    handle_shovel,
)
from mcp.server.fastmcp import FastMCP
from typing import Any


class RabbitMQModule:
    """A module that contains RabbitMQ API."""

    def __init__(self, mcp: FastMCP):
        """Initialize the RabbitMQ module."""
        self.mcp = mcp
        self.rmq: RabbitMQConnection | None = None
        self.rmq_admin: RabbitMQAdmin | None = None

    def register_rabbitmq_management_tools(self, allow_mutative_tools: bool = False):
        """Install RabbitMQ tools to the MCP server."""
        self.__register_critical_tools()
        self.__register_read_only_tools()
        if allow_mutative_tools:
            self.__register_mutative_tools()

    def __register_critical_tools(self):
        @self.mcp.tool()
        def rabbimq_broker_initialize_connection(
            broker_hostname: str,
            username: str,
            password: str,
        ) -> str:
            """Connect to a new RabbitMQ broker.

            broker_hostname: The hostname of the broker. For example, b-a9565a64-da39-4afc-9239-c43a9376b5ba.mq.us-east-1.on.aws, b-9560b8e1-3d33-4d91-9488-a3dc4a61dfe7.mq.us-east-1.amazonaws.com
            username: The username of user
            password: The password of user
            """
            try:
                self.rmq = RabbitMQConnection(
                    hostname=broker_hostname,
                    username=username,
                    password=password,
                    use_tls=True,
                )
                self.rmq_admin = RabbitMQAdmin(
                    hostname=broker_hostname,
                    username=username,
                    password=password,
                    use_tls=True,
                )

                return 'successfully connected'
            except Exception as e:
                raise e

        @self.mcp.tool()
        def rabbimq_broker_initialize_connection_with_oauth(
            broker_hostname: str,
            oauth_token: str,
        ) -> str:
            """Connect to a new RabbitMQ broker using OAuth. It only applies to RabbitMQ broker which authentication strategy is config_managed.

            broker_hostname: The hostname of the broker. For example, b-a9565a64-da39-4afc-9239-c43a9376b5ba.mq.us-east-1.on.aws, b-9560b8e1-3d33-4d91-9488-a3dc4a61dfe7.mq.us-east-1.amazonaws.com
            oauth_token: A valid OAuth token obtained
            """
            try:
                self.rmq = RabbitMQConnection(
                    hostname=broker_hostname,
                    username='',
                    password=oauth_token,
                    use_tls=True,
                )
                self.rmq_admin = RabbitMQAdmin(
                    hostname=broker_hostname,
                    username='',
                    password=oauth_token,
                    use_tls=True,
                )

                return 'successfully connected'
            except Exception as e:
                raise e

        @self.mcp.tool()
        def rabbitmq_broker_get_best_practices() -> str:
            """Get the general best practices for deploying RabbitMQ on Amazon MQ."""
            try:
                result = handle_get_general_best_practices()
                return str(result)
            except Exception as e:
                raise e

    def __register_read_only_tools(self):
        @self.mcp.tool()
        def rabbitmq_broker_list_queues() -> list[Any]:
            """List all the queues in the broker."""
            try:
                assert self.rmq_admin is not None
                return handle_list_queues(self.rmq_admin)
            except Exception as e:
                raise e

        @self.mcp.tool()
        def rabbitmq_broker_list_exchanges() -> list[Any]:
            """List all the exchanges in the broker."""
            try:
                assert self.rmq_admin is not None
                return handle_list_exchanges(self.rmq_admin)
            except Exception as e:
                raise e

        @self.mcp.tool()
        def rabbitmq_broker_list_vhosts() -> list[Any]:
            """List all the virtual hosts (vhosts) in the broker."""
            try:
                assert self.rmq_admin is not None
                return handle_list_vhosts(self.rmq_admin)
            except Exception as e:
                raise e

        @self.mcp.tool()
        def rabbitmq_broker_get_queue_info(queue: str, vhost: str = '/') -> dict:
            """Get detailed information about a specific queue."""
            try:
                assert self.rmq_admin is not None
                validate_rabbitmq_name(queue, 'Queue name')
                return handle_get_queue_info(self.rmq_admin, queue, vhost)
            except Exception as e:
                raise e

        @self.mcp.tool()
        def rabbitmq_broker_get_exchange_info(exchange: str, vhost: str = '/') -> dict:
            """Get detailed information about a specific exchange."""
            try:
                assert self.rmq_admin is not None
                validate_rabbitmq_name(exchange, 'Exchange name')
                return handle_get_exchange_info(self.rmq_admin, exchange, vhost)
            except Exception as e:
                raise e

        @self.mcp.tool()
        def rabbitmq_broker_list_shovels() -> list[Any]:
            """Get detailed information about shovels in the RabbitMQ broker."""
            try:
                assert self.rmq_admin is not None
                return handle_list_shovels(self.rmq_admin)
            except Exception as e:
                raise e

        @self.mcp.tool()
        def rabbitmq_broker_get_shovel_info(name: str, vhost: str = '/') -> dict:
            """Get detailed information about specific shovel by name that is in a selected virtual host (vhost) in the RabbitMQ broker."""
            try:
                assert self.rmq_admin is not None
                return handle_shovel(self.rmq_admin, name, vhost)
            except Exception as e:
                raise e

        @self.mcp.tool()
        def rabbitmq_broker_get_cluster_nodes_info() -> list[Any]:
            """Get the list of nodes and their info in the cluster."""
            try:
                assert self.rmq_admin is not None
                return handle_get_cluster_nodes(self.rmq_admin)
            except Exception as e:
                raise e

        @self.mcp.tool()
        def rabbitmq_broker_list_connections() -> list[Any]:
            """List all connections on the RabbitMQ broker."""
            try:
                assert self.rmq_admin is not None
                return handle_list_connections(self.rmq_admin)
            except Exception as e:
                raise e

        @self.mcp.tool()
        def rabbitmq_broker_list_consumers() -> list[Any]:
            """List all consumers on the RabbitMQ broker."""
            try:
                assert self.rmq_admin is not None
                return handle_list_consumers(self.rmq_admin)
            except Exception as e:
                raise e

        @self.mcp.tool()
        def rabbitmq_broker_list_users() -> list[Any]:
            """List all users on the RabbitMQ broker."""
            try:
                assert self.rmq_admin is not None
                return handle_list_users(self.rmq_admin)
            except Exception as e:
                raise e

        @self.mcp.tool()
        def rabbitmq_broker_is_in_alarm() -> bool:
            """Check if the RabbitMQ broker is in alarm."""
            try:
                assert self.rmq_admin is not None
                return handle_is_broker_in_alarm(self.rmq_admin)
            except Exception as e:
                raise e

        @self.mcp.tool()
        def rabbitmq_broker_is_quorum_critical() -> bool:
            """Check if there are quorum queues with minimum online quorum."""
            try:
                assert self.rmq_admin is not None
                return handle_is_node_in_quorum_critical(self.rmq_admin)
            except Exception as e:
                raise e

    def __register_mutative_tools(self):
        @self.mcp.tool()
        def rabbitmq_broker_delete_queue(queue: str, vhost: str = '/') -> str:
            """Delete a specific queue."""
            try:
                assert self.rmq_admin is not None
                validate_rabbitmq_name(queue, 'Queue name')
                handle_delete_queue(self.rmq_admin, queue, vhost)
                return f'Queue {queue} successfully deleted'
            except Exception as e:
                raise e

        @self.mcp.tool()
        def rabbitmq_broker_purge_queue(queue: str, vhost: str = '/') -> str:
            """Remove all messages from a specific queue."""
            try:
                assert self.rmq_admin is not None
                validate_rabbitmq_name(queue, 'Queue name')
                handle_purge_queue(self.rmq_admin, queue, vhost)
                return f'Queue {queue} successfully purged'
            except Exception as e:
                raise e

        @self.mcp.tool()
        def rabbitmq_broker_delete_exchange(exchange: str, vhost: str = '/') -> str:
            """Delete a specific exchange."""
            try:
                assert self.rmq_admin is not None
                validate_rabbitmq_name(exchange, 'Exchange name')
                handle_delete_exchange(self.rmq_admin, exchange, vhost)
                return f'Exchange {exchange} successfully deleted'
            except Exception as e:
                raise e
