# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

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
    def test_register_rabbitmq_management_tools_with_mutative(self, mock_admin_class, mock_conn_class):
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
        with patch.object(self.module, '_RabbitMQModule__register_read_only_tools') as mock_readonly:
            self.module.register_rabbitmq_management_tools(allow_mutative_tools=False)
            mock_readonly.assert_called_once()

    def test_mutative_tools_registration(self):
        """Test that mutative tools are registered when enabled."""
        with patch.object(self.module, '_RabbitMQModule__register_read_only_tools') as mock_readonly, \
             patch.object(self.module, '_RabbitMQModule__register_mutative_tools') as mock_mutative:
            self.module.register_rabbitmq_management_tools(allow_mutative_tools=True)
            mock_readonly.assert_called_once()
            mock_mutative.assert_called_once()

    def test_mutative_tools_not_registered_when_disabled(self):
        """Test that mutative tools are not registered when disabled."""
        with patch.object(self.module, '_RabbitMQModule__register_read_only_tools') as mock_readonly, \
             patch.object(self.module, '_RabbitMQModule__register_mutative_tools') as mock_mutative:
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

    @patch('awslabs.amazon_mq_mcp_server.rabbitmq.module.handle_list_queues')
    def test_list_queues_tool_success(self, mock_handler):
        """Test list_queues tool success case."""
        mock_handler.return_value = ["queue1", "queue2"]

        self.module._RabbitMQModule__register_read_only_tools()

        # Find and call the list_queues function
        tool_calls = self.mock_mcp.tool.call_args_list
        list_queues_func = None
        for call in tool_calls:
            if call.args and hasattr(call.args[0], '__name__') and 'list_queues' in call.args[0].__name__:
                list_queues_func = call.args[0]
                break

        assert list_queues_func is not None
        result = list_queues_func()

        assert result == "['queue1', 'queue2']"
        mock_handler.assert_called_once_with(self.module.rmq_admin)

    @patch('awslabs.amazon_mq_mcp_server.rabbitmq.module.handle_enqueue')
    def test_enqueue_tool_success(self, mock_handler):
        """Test enqueue tool success case."""
        self.module._RabbitMQModule__register_mutative_tools()

        # Find and call the enqueue function
        tool_calls = self.mock_mcp.tool.call_args_list
        enqueue_func = None
        for call in tool_calls:
            if call.args and hasattr(call.args[0], '__name__') and 'enqueue' in call.args[0].__name__:
                enqueue_func = call.args[0]
                break

        assert enqueue_func is not None
        result = enqueue_func("test-queue", "test message")

        assert result == "Message successfully enqueued"
        mock_handler.assert_called_once_with(self.module.rmq, "test-queue", "test message")

    @patch('awslabs.amazon_mq_mcp_server.rabbitmq.module.handle_enqueue')
    def test_enqueue_tool_failure(self, mock_handler):
        """Test enqueue tool failure case."""
        mock_handler.side_effect = Exception("Enqueue failed")

        self.module._RabbitMQModule__register_mutative_tools()

        # Find and call the enqueue function
        tool_calls = self.mock_mcp.tool.call_args_list
        enqueue_func = None
        for call in tool_calls:
            if call.args and hasattr(call.args[0], '__name__') and 'enqueue' in call.args[0].__name__:
                enqueue_func = call.args[0]
                break

        assert enqueue_func is not None
        result = enqueue_func("test-queue", "test message")

        assert "Failed to enqueue message: Enqueue failed" in result
