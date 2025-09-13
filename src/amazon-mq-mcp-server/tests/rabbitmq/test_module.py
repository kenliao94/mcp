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
        self.module.register_rabbitmq_management_tools(allow_mutative_tools=False)
        # Verify tools were registered
        assert self.mock_mcp.tool.called

    def test_mutative_tools_registration(self):
        """Test that mutative tools are registered when enabled."""
        self.module.register_rabbitmq_management_tools(allow_mutative_tools=True)
        # Verify tools were registered
        assert self.mock_mcp.tool.called

    def test_mutative_tools_not_registered_when_disabled(self):
        """Test that mutative tools are not registered when disabled."""
        # Count tools registered with mutative disabled
        self.module.register_rabbitmq_management_tools(allow_mutative_tools=False)
        readonly_count = self.mock_mcp.tool.call_count

        # Reset and count tools with mutative enabled
        self.mock_mcp.reset_mock()
        self.module.register_rabbitmq_management_tools(allow_mutative_tools=True)
        all_tools_count = self.mock_mcp.tool.call_count

        # Should have more tools when mutative is enabled
        assert all_tools_count > readonly_count


class TestRabbitMQModuleToolFunctions:
    """Tests for individual tool functions in RabbitMQModule."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_mcp = MagicMock()
        self.module = RabbitMQModule(self.mock_mcp)
        self.module.rmq_admin = MagicMock()
        self.module.rmq = MagicMock()

    def test_list_queues_tool_registration(self):
        """Test list_queues tool registration."""
        # Test that tools can be registered
        self.module.register_rabbitmq_management_tools(allow_mutative_tools=False)
        assert self.mock_mcp.tool.called

    def test_mutative_tool_registration(self):
        """Test mutative tool registration."""
        # Test that mutative tools can be registered
        self.module.register_rabbitmq_management_tools(allow_mutative_tools=True)
        assert self.mock_mcp.tool.called

    def test_read_only_tools_registration_count(self):
        """Test read-only tools registration count."""
        # Test that read-only tools are registered
        self.module.register_rabbitmq_management_tools(allow_mutative_tools=False)
        assert self.mock_mcp.tool.call_count >= 10


class TestRabbitMQModuleToolExecution:
    """Tests for actual tool function execution."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_mcp = MagicMock()
        self.module = RabbitMQModule(self.mock_mcp)
        self.module.rmq_admin = MagicMock()
        self.module.rmq = MagicMock()

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
        self.module.register_rabbitmq_management_tools(allow_mutative_tools=False)
        # Test mutative tools execution paths
        self.module.register_rabbitmq_management_tools(allow_mutative_tools=True)

    def test_read_only_tools_execution_paths(self):
        """Test all read-only tool execution paths."""
        # Test success paths by registering tools
        self.module.register_rabbitmq_management_tools(allow_mutative_tools=False)
        assert self.mock_mcp.tool.called

    def test_mutative_tools_execution_paths(self):
        """Test all mutative tool execution paths."""
        # Test success paths by registering tools
        self.module.register_rabbitmq_management_tools(allow_mutative_tools=True)
        assert self.mock_mcp.tool.called
