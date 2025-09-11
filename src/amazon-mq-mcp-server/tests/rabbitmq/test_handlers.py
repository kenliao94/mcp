# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from awslabs.amazon_mq_mcp_server.rabbitmq.handlers import (
    handle_delete_exchange,
    handle_delete_queue,
    handle_enqueue,
    handle_fanout,
    handle_get_exchange_info,
    handle_get_queue_info,
    handle_list_exchanges,
    handle_list_exchanges_by_vhost,
    handle_list_queues,
    handle_list_queues_by_vhost,
    handle_list_shovels,
    handle_list_vhosts,
    handle_purge_queue,
    handle_shovel,
)
from unittest.mock import MagicMock


class TestAMQPHandlers:
    """Tests for AMQP message handlers."""

    def test_handle_enqueue(self):
        """Test enqueue handler."""
        mock_rabbitmq = MagicMock()
        mock_connection = MagicMock()
        mock_channel = MagicMock()
        mock_rabbitmq.get_channel.return_value = (mock_connection, mock_channel)
        handle_enqueue(mock_rabbitmq, "test-queue", "test message")
        mock_channel.queue_declare.assert_called_once_with("test-queue")
        mock_channel.basic_publish.assert_called_once_with(
            exchange="", routing_key="test-queue", body="test message"
        )
        mock_connection.close.assert_called_once()

    def test_handle_fanout(self):
        """Test fanout handler."""
        mock_rabbitmq = MagicMock()
        mock_connection = MagicMock()
        mock_channel = MagicMock()
        mock_rabbitmq.get_channel.return_value = (mock_connection, mock_channel)
        handle_fanout(mock_rabbitmq, "test-exchange", "test message")
        mock_channel.exchange_declare.assert_called_once_with(
            exchange="test-exchange", exchange_type="fanout"
        )
        mock_channel.basic_publish.assert_called_once_with(
            exchange="test-exchange", routing_key="", body="test message"
        )
        mock_connection.close.assert_called_once()


class TestQueueHandlers:
    """Tests for queue management handlers."""

    def test_handle_list_queues(self):
        """Test list queues handler."""
        mock_admin = MagicMock()
        mock_admin.list_queues.return_value = [
            {"name": "queue1", "messages": 5},
            {"name": "queue2", "messages": 0}
        ]
        result = handle_list_queues(mock_admin)
        assert result == ["queue1", "queue2"]
        mock_admin.list_queues.assert_called_once()

    def test_handle_list_queues_by_vhost(self):
        """Test list queues by vhost handler."""
        mock_admin = MagicMock()
        mock_admin.list_queues_by_vhost.return_value = [{"name": "queue1"}]
        result = handle_list_queues_by_vhost(mock_admin, "/test")
        assert result == ["queue1"]
        mock_admin.list_queues_by_vhost.assert_called_once_with("/test")

    def test_handle_get_queue_info(self):
        """Test get queue info handler."""
        mock_admin = MagicMock()
        expected_info = {"name": "test-queue", "messages": 5}
        mock_admin.get_queue_info.return_value = expected_info
        result = handle_get_queue_info(mock_admin, "test-queue", "/")
        assert result == expected_info
        mock_admin.get_queue_info.assert_called_once_with("test-queue", "/")

    def test_handle_delete_queue(self):
        """Test delete queue handler."""
        mock_admin = MagicMock()
        handle_delete_queue(mock_admin, "test-queue", "/")
        mock_admin.delete_queue.assert_called_once_with("test-queue", "/")

    def test_handle_purge_queue(self):
        """Test purge queue handler."""
        mock_admin = MagicMock()
        handle_purge_queue(mock_admin, "test-queue", "/")
        mock_admin.purge_queue.assert_called_once_with("test-queue", "/")


class TestExchangeHandlers:
    """Tests for exchange management handlers."""

    def test_handle_list_exchanges(self):
        """Test list exchanges handler."""
        mock_admin = MagicMock()
        mock_admin.list_exchanges.return_value = [
            {"name": "exchange1", "type": "fanout"},
            {"name": "exchange2", "type": "direct"}
        ]
        result = handle_list_exchanges(mock_admin)
        assert result == ["exchange1", "exchange2"]
        mock_admin.list_exchanges.assert_called_once()

    def test_handle_list_exchanges_by_vhost(self):
        """Test list exchanges by vhost handler."""
        mock_admin = MagicMock()
        mock_admin.list_exchanges_by_vhost.return_value = [{"name": "exchange1"}]
        result = handle_list_exchanges_by_vhost(mock_admin, "/test")
        assert result == ["exchange1"]
        mock_admin.list_exchanges_by_vhost.assert_called_once_with("/test")

    def test_handle_get_exchange_info(self):
        """Test get exchange info handler."""
        mock_admin = MagicMock()
        expected_info = {"name": "test-exchange", "type": "fanout"}
        mock_admin.get_exchange_info.return_value = expected_info
        result = handle_get_exchange_info(mock_admin, "test-exchange", "/")
        assert result == expected_info
        mock_admin.get_exchange_info.assert_called_once_with("test-exchange", "/")

    def test_handle_delete_exchange(self):
        """Test delete exchange handler."""
        mock_admin = MagicMock()
        handle_delete_exchange(mock_admin, "test-exchange", "/")
        mock_admin.delete_exchange.assert_called_once_with("test-exchange", "/")


class TestVhostHandlers:
    """Tests for vhost management handlers."""

    def test_handle_list_vhosts(self):
        """Test list vhosts handler."""
        mock_admin = MagicMock()
        mock_admin.list_vhosts.return_value = [
            {"name": "/", "tracing": False},
            {"name": "/test", "tracing": True}
        ]
        result = handle_list_vhosts(mock_admin)
        assert result == ["/", "/test"]
        mock_admin.list_vhosts.assert_called_once()


class TestShovelHandlers:
    """Tests for shovel management handlers."""

    def test_handle_list_shovels(self):
        """Test list shovels handler."""
        mock_admin = MagicMock()
        expected_shovels = [{"name": "shovel1"}, {"name": "shovel2"}]
        mock_admin.list_shovels.return_value = expected_shovels
        result = handle_list_shovels(mock_admin)
        assert result == expected_shovels
        mock_admin.list_shovels.assert_called_once()

    def test_handle_shovel(self):
        """Test get shovel info handler."""
        mock_admin = MagicMock()
        expected_info = {"name": "test-shovel", "state": "running"}
        mock_admin.get_shovel_info.return_value = expected_info
        result = handle_shovel(mock_admin, "test-shovel", "/")
        assert result == expected_info
        mock_admin.get_shovel_info.assert_called_once_with("test-shovel", "/")
