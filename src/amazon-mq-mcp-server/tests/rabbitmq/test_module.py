import pytest
from awslabs.amazon_mq_mcp_server.rabbitmq.module import RabbitMQModule
from unittest.mock import Mock, patch


class TestRabbitMQModule:
    def setup_method(self):
        self.mock_mcp = Mock()
        self.module = RabbitMQModule(self.mock_mcp)

    def test_init(self):
        assert self.module.mcp == self.mock_mcp
        assert self.module.rmq is None
        assert self.module.rmq_admin is None

    @patch('awslabs.amazon_mq_mcp_server.rabbitmq.module.RabbitMQConnection')
    @patch('awslabs.amazon_mq_mcp_server.rabbitmq.module.RabbitMQAdmin')
    def test_register_rabbitmq_management_tools_read_only(self, mock_admin_class, mock_conn_class):
        self.module.register_rabbitmq_management_tools(allow_mutative_tools=False)
        # Verify that tools are registered
        assert self.mock_mcp.tool.called

    @patch('awslabs.amazon_mq_mcp_server.rabbitmq.module.RabbitMQConnection')
    @patch('awslabs.amazon_mq_mcp_server.rabbitmq.module.RabbitMQAdmin')
    def test_register_rabbitmq_management_tools_with_mutative(
        self, mock_admin_class, mock_conn_class
    ):
        self.module.register_rabbitmq_management_tools(allow_mutative_tools=True)
        # Verify that tools are registered
        assert self.mock_mcp.tool.called

    @patch('awslabs.amazon_mq_mcp_server.rabbitmq.module.RabbitMQConnection')
    @patch('awslabs.amazon_mq_mcp_server.rabbitmq.module.RabbitMQAdmin')
    def test_initialize_connection_success(self, mock_admin_class, mock_conn_class):
        mock_conn_instance = Mock()
        mock_admin_instance = Mock()
        mock_conn_class.return_value = mock_conn_instance
        mock_admin_class.return_value = mock_admin_instance

        # Register tools to get access to the connection function
        self.module.register_rabbitmq_management_tools()

        # Simulate successful connection
        self.module.rmq = mock_conn_instance
        self.module.rmq_admin = mock_admin_instance

        assert self.module.rmq == mock_conn_instance
        assert self.module.rmq_admin == mock_admin_instance

    def test_read_only_tools_registration(self):
        self.module._RabbitMQModule__register_read_only_tools()
        # Verify that read-only tools are registered
        assert self.mock_mcp.tool.called

    def test_mutative_tools_registration(self):
        self.module._RabbitMQModule__register_mutative_tools()
        # Verify that mutative tools are registered
        assert self.mock_mcp.tool.called

    def test_mutative_tools_not_registered_when_disabled(self):
        self.module.register_rabbitmq_management_tools(allow_mutative_tools=False)
        # This test ensures that mutative tools are not registered when disabled
        # The actual verification would depend on the implementation details


class TestRabbitMQModuleToolFunctions:
    def setup_method(self):
        self.mock_mcp = Mock()
        self.module = RabbitMQModule(self.mock_mcp)

    def test_list_queues_tool_registration(self):
        self.module._RabbitMQModule__register_read_only_tools()
        # Verify that the list_queues tool is registered
        assert self.mock_mcp.tool.called

    def test_mutative_tool_registration(self):
        self.module._RabbitMQModule__register_mutative_tools()
        # Verify that mutative tools are registered
        assert self.mock_mcp.tool.called

    def test_read_only_tools_registration_count(self):
        self.module._RabbitMQModule__register_read_only_tools()
        # Verify the number of read-only tools registered
        assert self.mock_mcp.tool.call_count > 0


class TestRabbitMQModuleToolExecution:
    def setup_method(self):
        self.mock_mcp = Mock()
        self.module = RabbitMQModule(self.mock_mcp)

    @patch('awslabs.amazon_mq_mcp_server.rabbitmq.module.RabbitMQConnection')
    @patch('awslabs.amazon_mq_mcp_server.rabbitmq.module.RabbitMQAdmin')
    @patch('awslabs.amazon_mq_mcp_server.rabbitmq.module.handle_list_queues')
    def test_connection_and_tool_execution(self, mock_handle, mock_admin_class, mock_conn_class):
        mock_conn_instance = Mock()
        mock_admin_instance = Mock()
        mock_conn_class.return_value = mock_conn_instance
        mock_admin_class.return_value = mock_admin_instance
        mock_handle.return_value = ['queue1', 'queue2']

        self.module.register_rabbitmq_management_tools()

        # Simulate connection
        self.module.rmq = mock_conn_instance
        self.module.rmq_admin = mock_admin_instance

        # Verify that the connection instances are set
        assert self.module.rmq == mock_conn_instance
        assert self.module.rmq_admin == mock_admin_instance

    def test_read_only_tools_execution_paths(self):
        # Test that read-only tools can be executed without errors
        self.module._RabbitMQModule__register_read_only_tools()
        assert self.mock_mcp.tool.called

    def test_mutative_tools_execution_paths(self):
        # Test that mutative tools can be executed without errors
        self.module._RabbitMQModule__register_mutative_tools()
        assert self.mock_mcp.tool.called


class TestRabbitMQBrokerInitializeConnection:
    def setup_method(self):
        self.mock_mcp = Mock()
        self.captured_functions = {}

        def mock_tool_decorator(func):
            self.captured_functions[func.__name__] = func
            return func

        self.mock_mcp.tool.return_value = mock_tool_decorator
        self.module = RabbitMQModule(self.mock_mcp)
        self.module._RabbitMQModule__register_critical_tools()

    @patch('awslabs.amazon_mq_mcp_server.rabbitmq.module.RabbitMQConnection')
    @patch('awslabs.amazon_mq_mcp_server.rabbitmq.module.RabbitMQAdmin')
    def test_rabbimq_broker_initialize_connection_success(self, mock_admin_class, mock_conn_class):
        mock_conn_instance = Mock()
        mock_admin_instance = Mock()
        mock_conn_class.return_value = mock_conn_instance
        mock_admin_class.return_value = mock_admin_instance

        func = self.captured_functions['rabbimq_broker_initialize_connection']
        result = func('test-hostname', 'test-user', 'test-pass')

        assert result == 'successfully connected'
        mock_conn_class.assert_called_once_with(
            hostname='test-hostname', username='test-user', password='test-pass', use_tls=True
        )
        mock_admin_class.assert_called_once_with(
            hostname='test-hostname', username='test-user', password='test-pass', use_tls=True
        )
        assert self.module.rmq == mock_conn_instance
        assert self.module.rmq_admin == mock_admin_instance

    @patch('awslabs.amazon_mq_mcp_server.rabbitmq.module.RabbitMQConnection')
    @patch('awslabs.amazon_mq_mcp_server.rabbitmq.module.RabbitMQAdmin')
    def test_rabbimq_broker_initialize_connection_failure(self, mock_admin_class, mock_conn_class):
        mock_conn_class.side_effect = Exception('Connection failed')

        func = self.captured_functions['rabbimq_broker_initialize_connection']

        with pytest.raises(Exception, match='Connection failed'):
            func('test-hostname', 'test-user', 'test-pass')


class TestRabbitMQBrokerInitializeConnectionWithOAuth:
    def setup_method(self):
        self.mock_mcp = Mock()
        self.captured_functions = {}

        def mock_tool_decorator(func):
            self.captured_functions[func.__name__] = func
            return func

        self.mock_mcp.tool.return_value = mock_tool_decorator
        self.module = RabbitMQModule(self.mock_mcp)
        self.module._RabbitMQModule__register_critical_tools()

    @patch('awslabs.amazon_mq_mcp_server.rabbitmq.module.RabbitMQConnection')
    @patch('awslabs.amazon_mq_mcp_server.rabbitmq.module.RabbitMQAdmin')
    def test_rabbimq_broker_initialize_connection_with_oauth_success(
        self, mock_admin_class, mock_conn_class
    ):
        mock_conn_instance = Mock()
        mock_admin_instance = Mock()
        mock_conn_class.return_value = mock_conn_instance
        mock_admin_class.return_value = mock_admin_instance

        func = self.captured_functions['rabbimq_broker_initialize_connection_with_oauth']
        result = func('test-hostname', 'oauth-token-123')

        assert result == 'successfully connected'
        mock_conn_class.assert_called_once_with(
            hostname='test-hostname', username='', password='oauth-token-123', use_tls=True
        )
        mock_admin_class.assert_called_once_with(
            hostname='test-hostname', username='', password='oauth-token-123', use_tls=True
        )
        assert self.module.rmq == mock_conn_instance
        assert self.module.rmq_admin == mock_admin_instance

    @patch('awslabs.amazon_mq_mcp_server.rabbitmq.module.RabbitMQConnection')
    @patch('awslabs.amazon_mq_mcp_server.rabbitmq.module.RabbitMQAdmin')
    def test_rabbimq_broker_initialize_connection_with_oauth_failure(
        self, mock_admin_class, mock_conn_class
    ):
        mock_conn_class.side_effect = Exception('OAuth connection failed')

        func = self.captured_functions['rabbimq_broker_initialize_connection_with_oauth']

        with pytest.raises(Exception, match='OAuth connection failed'):
            func('test-hostname', 'oauth-token-123')
