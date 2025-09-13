# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import pytest
import requests
from awslabs.amazon_mq_mcp_server.rabbitmq.admin import RabbitMQAdmin
from unittest.mock import MagicMock, patch


class TestRabbitMQAdmin:
    """Tests for RabbitMQAdmin class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.admin = RabbitMQAdmin('test-host', 'user', 'pass', True)

    def test_init_with_tls(self):
        """Test initialization with TLS enabled."""
        admin = RabbitMQAdmin('test-host', 'user', 'pass', True)
        assert admin.protocol == 'https'
        assert admin.base_url == 'https://test-host:15671/api'

    def test_init_without_tls(self):
        """Test initialization with TLS disabled."""
        admin = RabbitMQAdmin('test-host', 'user', 'pass', False)
        assert admin.protocol == 'http'
        assert admin.base_url == 'http://test-host:15671/api'

    @patch('awslabs.amazon_mq_mcp_server.rabbitmq.admin.requests.request')
    def test_make_request_success(self, mock_request):
        """Test successful API request."""
        mock_response = MagicMock()
        mock_response.json.return_value = {'test': 'data'}
        mock_request.return_value = mock_response
        result = self.admin._make_request('GET', 'test')
        assert result == mock_response
        mock_request.assert_called_once()
        mock_response.raise_for_status.assert_called_once()

    @patch('awslabs.amazon_mq_mcp_server.rabbitmq.admin.requests.request')
    def test_make_request_failure(self, mock_request):
        """Test failed API request."""
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.HTTPError()
        mock_request.return_value = mock_response
        with pytest.raises(requests.HTTPError):
            self.admin._make_request('GET', 'test')

    @patch.object(RabbitMQAdmin, '_make_request')
    def test_list_queues(self, mock_request):
        """Test listing all queues."""
        mock_request.return_value.json.return_value = [{'name': 'queue1'}, {'name': 'queue2'}]
        result = self.admin.list_queues()
        assert result == [{'name': 'queue1'}, {'name': 'queue2'}]
        mock_request.assert_called_once_with('GET', 'queues')

    @patch.object(RabbitMQAdmin, '_make_request')
    def test_list_queues_by_vhost(self, mock_request):
        """Test listing queues by vhost."""
        mock_request.return_value.json.return_value = [{'name': 'queue1'}]
        result = self.admin.list_queues_by_vhost('/test')
        assert result == [{'name': 'queue1'}]
        mock_request.assert_called_once_with('GET', 'queues/%2Ftest')

    @patch.object(RabbitMQAdmin, '_make_request')
    def test_get_queue_info(self, mock_request):
        """Test getting queue information."""
        mock_request.return_value.json.return_value = {'name': 'test-queue', 'messages': 5}
        result = self.admin.get_queue_info('test-queue', '/')
        assert result == {'name': 'test-queue', 'messages': 5}
        mock_request.assert_called_once_with('GET', 'queues/%2F/test-queue')

    @patch.object(RabbitMQAdmin, '_make_request')
    def test_delete_queue(self, mock_request):
        """Test deleting a queue."""
        self.admin.delete_queue('test-queue', '/')
        mock_request.assert_called_once_with('DELETE', 'queues/%2F/test-queue')

    @patch.object(RabbitMQAdmin, '_make_request')
    def test_purge_queue(self, mock_request):
        """Test purging a queue."""
        self.admin.purge_queue('test-queue', '/')
        mock_request.assert_called_once_with('DELETE', 'queues/%2F/test-queue/contents')

    @patch.object(RabbitMQAdmin, '_make_request')
    def test_list_exchanges(self, mock_request):
        """Test listing all exchanges."""
        mock_request.return_value.json.return_value = [{'name': 'exchange1'}]
        result = self.admin.list_exchanges()
        assert result == [{'name': 'exchange1'}]
        mock_request.assert_called_once_with('GET', 'exchanges')

    @patch.object(RabbitMQAdmin, '_make_request')
    def test_get_exchange_info(self, mock_request):
        """Test getting exchange information."""
        mock_request.return_value.json.return_value = {'name': 'test-exchange', 'type': 'fanout'}
        result = self.admin.get_exchange_info('test-exchange', '/')
        assert result == {'name': 'test-exchange', 'type': 'fanout'}
        mock_request.assert_called_once_with('GET', 'exchanges/%2F/test-exchange')

    @patch.object(RabbitMQAdmin, '_make_request')
    def test_delete_exchange(self, mock_request):
        """Test deleting an exchange."""
        self.admin.delete_exchange('test-exchange', '/')
        mock_request.assert_called_once_with('DELETE', 'exchanges/%2F/test-exchange')

    @patch.object(RabbitMQAdmin, '_make_request')
    def test_list_vhosts(self, mock_request):
        """Test listing vhosts."""
        mock_request.return_value.json.return_value = [{'name': '/'}]
        result = self.admin.list_vhosts()
        assert result == [{'name': '/'}]
        mock_request.assert_called_once_with('GET', 'vhosts')

    @patch.object(RabbitMQAdmin, '_make_request')
    def test_list_shovels(self, mock_request):
        """Test listing shovels."""
        mock_request.return_value.json.return_value = [{'name': 'shovel1'}]
        result = self.admin.list_shovels()
        assert result == [{'name': 'shovel1'}]
        mock_request.assert_called_once_with('GET', 'shovels')

    @patch.object(RabbitMQAdmin, '_make_request')
    def test_get_shovel_info(self, mock_request):
        """Test getting shovel information."""
        mock_request.return_value.json.return_value = {'name': 'test-shovel'}
        result = self.admin.get_shovel_info('test-shovel', '/')
        assert result == {'name': 'test-shovel'}
        mock_request.assert_called_once_with('GET', 'parameters/shovel/%2F/test-shovel')

    @patch.object(RabbitMQAdmin, '_make_request')
    def test_list_exchanges_by_vhost(self, mock_request):
        """Test listing exchanges by vhost."""
        mock_request.return_value.json.return_value = [{'name': 'exchange1'}]
        result = self.admin.list_exchanges_by_vhost('/test')
        assert result == [{'name': 'exchange1'}]
        mock_request.assert_called_once_with('GET', 'exchanges/%2Ftest')

    @patch.object(RabbitMQAdmin, '_make_request')
    def test_get_bindings_with_queue(self, mock_request):
        """Test getting bindings filtered by queue."""
        mock_request.return_value.json.return_value = [{'source': 'exchange1'}]
        result = self.admin.get_bindings(queue='test-queue')
        assert result == [{'source': 'exchange1'}]
        mock_request.assert_called_once_with('GET', 'queues/%2F/test-queue/bindings')

    @patch.object(RabbitMQAdmin, '_make_request')
    def test_get_bindings_with_exchange(self, mock_request):
        """Test getting bindings filtered by exchange."""
        mock_request.return_value.json.return_value = [{'destination': 'queue1'}]
        result = self.admin.get_bindings(exchange='test-exchange')
        assert result == [{'destination': 'queue1'}]
        mock_request.assert_called_once_with('GET', 'exchanges/%2F/test-exchange/bindings/source')

    @patch.object(RabbitMQAdmin, '_make_request')
    def test_get_bindings_all(self, mock_request):
        """Test getting all bindings."""
        mock_request.return_value.json.return_value = [
            {'source': 'exchange1', 'destination': 'queue1'}
        ]
        result = self.admin.get_bindings()
        assert result == [{'source': 'exchange1', 'destination': 'queue1'}]
        mock_request.assert_called_once_with('GET', 'bindings/%2F')

    @patch.object(RabbitMQAdmin, '_make_request')
    def test_get_overview(self, mock_request):
        """Test getting RabbitMQ overview."""
        mock_request.return_value.json.return_value = {'rabbitmq_version': '3.8.0'}
        result = self.admin.get_overview()
        assert result == {'rabbitmq_version': '3.8.0'}
        mock_request.assert_called_once_with('GET', 'overview')
