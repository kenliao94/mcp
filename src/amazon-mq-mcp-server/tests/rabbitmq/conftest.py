# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import pytest
from unittest.mock import MagicMock


@pytest.fixture
def mock_rabbitmq_connection():
    """Fixture for mocked RabbitMQ connection."""
    mock_conn = MagicMock()
    mock_channel = MagicMock()
    mock_conn.get_channel.return_value = (mock_conn, mock_channel)
    return mock_conn


@pytest.fixture
def mock_rabbitmq_admin():
    """Fixture for mocked RabbitMQ admin."""
    return MagicMock()


@pytest.fixture
def mock_mcp_server():
    """Fixture for mocked MCP server."""
    return MagicMock()
