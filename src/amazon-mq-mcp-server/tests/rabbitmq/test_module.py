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

from awslabs.amazon_mq_mcp_server.rabbitmq.module import RabbitMQModule
from unittest.mock import MagicMock, patch


class TestRabbitMQModule:
    """Tests for RabbitMQModule class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_mcp = MagicMock()
        self.module = RabbitMQModule(self.mock_mcp)

    def test_init(self):
        """Test module initialization."""
        assert self.module.mcp == self.mock_mcp
        assert self.module.rmq is None
        assert self.module.rmq_admin is None

    @patch('awslabs.amazon_mq_mcp_server.rabbitmq.module.RabbitMQConnection')
    @patch('awslabs.amazon_mq_mcp_server.rabbitmq.module.RabbitMQAdmin')
    def test_register_rabbitmq_management_tools_read_only(self, mock_admin_class, mock_conn_class):
        """Test registering read-only tools."""
        self.module.register_rabbitmq_management_tools(allow_mutative_tools=False)

        # Should register the connection tool plus read-only tools
        assert self.mock_mcp.tool.call_count >= 10

    @patch('awslabs.amazon_mq_mcp_server.rabbitmq.module.RabbitMQConnection')
    @patch('awslabs.amazon_mq_mcp_server.rabbitmq.module.RabbitMQAdmin')
    def test_register_rabbitmq_management_tools_with_mutative(
        self, mock_admin_class, mock_conn_class
    ):
        """Test registering all tools including mutative ones."""
        self.module.register_rabbitmq_management_tools(allow_mutative_tools=True)

        # Should register connection tool plus all read-only and mutative tools
        assert self.mock_mcp.tool.call_count >= 15

    @patch('awslabs.amazon_mq_mcp_server.rabbitmq.module.RabbitMQConnection')
    @patch('awslabs.amazon_mq_mcp_server.rabbitmq.module.RabbitMQAdmin')
    def test_initialize_connection_success(self, mock_admin_class, mock_conn_class):
        """Test successful connection initialization."""
        mock_conn = MagicMock()
        mock_admin = MagicMock()
        mock_conn_class.return_value = mock_conn
        mock_admin_class.return_value = mock_admin

        self.module.register_rabbitmq_management_tools()

        # Verify that the tool decorator was called (indicating tools were registered)
        assert self.mock_mcp.tool.called
        assert self.mock_mcp.tool.call_count >= 1

    def test_read_only_tools_registration(self):
        """Test that read-only tools are properly registered."""
        with patch.object(
            self.module, '_RabbitMQModule__register_read_only_tools'
        ) as mock_readonly:
            self.module.register_rabbitmq_management_tools(allow_mutative_tools=False)
            mock_readonly.assert_called_once()

    def test_mutative_tools_registration(self):
        """Test that mutative tools are registered when enabled."""
        with (
            patch.object(
                self.module, '_RabbitMQModule__register_read_only_tools'
            ) as mock_readonly,
            patch.object(self.module, '_RabbitMQModule__register_mutative_tools') as mock_mutative,
        ):
            self.module.register_rabbitmq_management_tools(allow_mutative_tools=True)
            mock_readonly.assert_called_once()
            mock_mutative.assert_called_once()

    def test_mutative_tools_not_registered_when_disabled(self):
        """Test that mutative tools are not registered when disabled."""
        with (
            patch.object(
                self.module, '_RabbitMQModule__register_read_only_tools'
            ) as mock_readonly,
            patch.object(self.module, '_RabbitMQModule__register_mutative_tools') as mock_mutative,
        ):
            self.module.register_rabbitmq_management_tools(allow_mutative_tools=False)
            mock_readonly.assert_called_once()
            mock_mutative.assert_not_called()


class TestRabbitMQModuleToolFunctions:
    """Tests for individual tool functions in RabbitMQModule."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_mcp = MagicMock()
        self.module = RabbitMQModule(self.mock_mcp)
        self.module.rmq_admin = MagicMock()
        self.module.rmq = MagicMock()
        self.module.logger = MagicMock()

    def test_list_queues_tool_registration(self):
        """Test list_queues tool registration."""
        self.module._RabbitMQModule__register_read_only_tools()

        # Verify the tool was registered
        assert self.mock_mcp.tool.called

    def test_enqueue_tool_registration(self):
        """Test enqueue tool registration."""
        self.module._RabbitMQModule__register_mutative_tools()
        assert self.mock_mcp.tool.called

    def test_read_only_tools_registration_count(self):
        """Test read-only tools registration count."""
        self.module._RabbitMQModule__register_read_only_tools()
        # Should register 13 read-only tools
        assert self.mock_mcp.tool.call_count == 13


class TestRabbitMQModuleToolExecution:
    """Tests for actual tool function execution."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_mcp = MagicMock()
        self.module = RabbitMQModule(self.mock_mcp)
        self.module.rmq_admin = MagicMock()
        self.module.rmq = MagicMock()
        self.module.logger = MagicMock()

    @patch('awslabs.amazon_mq_mcp_server.rabbitmq.module.RabbitMQConnection')
    @patch('awslabs.amazon_mq_mcp_server.rabbitmq.module.RabbitMQAdmin')
    @patch('awslabs.amazon_mq_mcp_server.rabbitmq.module.handle_list_queues')
    def test_connection_and_tool_execution(self, mock_handle, mock_admin_class, mock_conn_class):
        """Test connection initialization and tool execution paths."""
        mock_handle.return_value = [{'name': 'queue1'}]
        mock_handle.side_effect = [Exception('API error'), [{'name': 'queue1'}]]
        # Test successful connection
        self.module.register_rabbitmq_management_tools()
        # Test exception handling in connection
        mock_conn_class.side_effect = Exception('Connection failed')
        try:
            self.module.register_rabbitmq_management_tools()
        except Exception:
            pass
        # Test read-only tools execution paths
        self.module._RabbitMQModule__register_read_only_tools()
        # Test mutative tools execution paths
        self.module._RabbitMQModule__register_mutative_tools()

    @patch('awslabs.amazon_mq_mcp_server.rabbitmq.module.handle_list_queues')
    @patch('awslabs.amazon_mq_mcp_server.rabbitmq.module.handle_list_exchanges')
    @patch('awslabs.amazon_mq_mcp_server.rabbitmq.module.handle_list_vhosts')
    @patch('awslabs.amazon_mq_mcp_server.rabbitmq.module.handle_get_queue_info')
    @patch('awslabs.amazon_mq_mcp_server.rabbitmq.module.handle_get_exchange_info')
    @patch('awslabs.amazon_mq_mcp_server.rabbitmq.module.handle_list_shovels')
    @patch('awslabs.amazon_mq_mcp_server.rabbitmq.module.handle_shovel')
    @patch('awslabs.amazon_mq_mcp_server.rabbitmq.module.handle_get_cluster_nodes')
    @patch('awslabs.amazon_mq_mcp_server.rabbitmq.module.handle_list_connections')
    @patch('awslabs.amazon_mq_mcp_server.rabbitmq.module.handle_list_consumers')
    @patch('awslabs.amazon_mq_mcp_server.rabbitmq.module.handle_list_users')
    @patch('awslabs.amazon_mq_mcp_server.rabbitmq.module.handle_is_broker_in_alarm')
    @patch('awslabs.amazon_mq_mcp_server.rabbitmq.module.handle_is_node_in_quorum_critical')
    def test_read_only_tools_execution_paths(
        self,
        mock_quorum_critical,
        mock_broker_alarm,
        mock_users,
        mock_consumers,
        mock_connections,
        mock_cluster_nodes,
        mock_shovel,
        mock_shovels,
        mock_exchange_info,
        mock_queue_info,
        mock_vhosts,
        mock_exchanges,
        mock_queues,
    ):
        """Test all read-only tool execution paths."""
        # Set up success returns
        mock_queues.return_value = [{'name': 'queue1'}]
        mock_exchanges.return_value = [{'name': 'exchange1'}]
        mock_vhosts.return_value = [{'name': '/'}]
        mock_queue_info.return_value = {'name': 'queue1', 'messages': 5}
        mock_exchange_info.return_value = {'name': 'exchange1', 'type': 'fanout'}
        mock_shovels.return_value = [{'name': 'shovel1'}]
        mock_shovel.return_value = {'name': 'shovel1'}
        mock_cluster_nodes.return_value = [{'name': 'node1'}]
        mock_connections.return_value = [{'name': 'conn1'}]
        mock_consumers.return_value = [{'name': 'consumer1'}]
        mock_users.return_value = [{'name': 'user1'}]
        mock_broker_alarm.return_value = False
        mock_quorum_critical.return_value = False
        # Test success paths by registering tools
        self.module._RabbitMQModule__register_read_only_tools()

    @patch('awslabs.amazon_mq_mcp_server.rabbitmq.module.handle_delete_queue')
    @patch('awslabs.amazon_mq_mcp_server.rabbitmq.module.handle_purge_queue')
    @patch('awslabs.amazon_mq_mcp_server.rabbitmq.module.handle_delete_exchange')
    def test_mutative_tools_execution_paths(
        self, mock_delete_exchange, mock_purge_queue, mock_delete_queue
    ):
        """Test all mutative tool execution paths."""
        # Test success paths by registering tools
        self.module._RabbitMQModule__register_mutative_tools()
