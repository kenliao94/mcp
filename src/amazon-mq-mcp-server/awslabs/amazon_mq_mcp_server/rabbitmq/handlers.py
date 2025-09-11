## Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
## SPDX-License-Identifier: Apache-2.0

from .admin import RabbitMQAdmin
from .connection import RabbitMQConnection
from pathlib import Path
from typing import List


################################################
######      RabbitMQ doc handlers         ######
################################################

def get_general_best_practices():
    """Get the general best practices for setting up RabbitMQ."""
    script_dir = Path(__file__).parent
    content = (script_dir / "doc" / "connection_best_practice.md").read_text()
    content = content + "\n\n" + (script_dir / "doc" / "message_durability_best_practice.md").read_text()
    content = content + "\n\n" + (script_dir / "doc" / "network_resilience_and_monitoring_best_practice.md").read_text()

    return content

################################################
######      RabbitMQ AMQP handlers        ######
################################################

def handle_enqueue(rabbitmq: RabbitMQConnection, queue: str, message: str):
    """Send a message to a RabbitMQ queue."""
    connection, channel = rabbitmq.get_channel()
    channel.queue_declare(queue)
    channel.basic_publish(exchange="", routing_key=queue, body=message)
    connection.close()


def handle_fanout(rabbitmq: RabbitMQConnection, exchange: str, message: str):
    """Publish a message to a fanout exchange."""
    connection, channel = rabbitmq.get_channel()
    channel.exchange_declare(exchange=exchange, exchange_type="fanout")
    channel.basic_publish(exchange=exchange, routing_key="", body=message)
    connection.close()

################################################
######      RabbitMQ admin handlers       ######
################################################

## Queues

def handle_list_queues(rabbitmq_admin: RabbitMQAdmin) -> List[str]:
    """List all queue names in the RabbitMQ server."""
    result = rabbitmq_admin.list_queues()
    return [queue["name"] for queue in result]


def handle_list_queues_by_vhost(rabbitmq_admin: RabbitMQAdmin, vhost: str = "/") -> List[str]:
    """List all queue names in a specific vhost."""
    result = rabbitmq_admin.list_queues_by_vhost(vhost)
    return [queue["name"] for queue in result]


def handle_get_queue_info(rabbitmq_admin: RabbitMQAdmin, queue: str, vhost: str = "/") -> dict:
    """Get detailed information about a specific queue."""
    return rabbitmq_admin.get_queue_info(queue, vhost)


def handle_delete_queue(rabbitmq_admin: RabbitMQAdmin, queue: str, vhost: str = "/") -> None:
    """Delete a queue from the RabbitMQ server."""
    rabbitmq_admin.delete_queue(queue, vhost)


def handle_purge_queue(rabbitmq_admin: RabbitMQAdmin, queue: str, vhost: str = "/") -> None:
    """Remove all messages from a queue."""
    rabbitmq_admin.purge_queue(queue, vhost)

## Exchanges

def handle_list_exchanges(rabbitmq_admin: RabbitMQAdmin) -> List[str]:
    """List all exchange names in the RabbitMQ server."""
    result = rabbitmq_admin.list_exchanges()
    return [exchange["name"] for exchange in result]


def handle_list_exchanges_by_vhost(rabbitmq_admin: RabbitMQAdmin, vhost: str = "/") -> List[str]:
    """List all exchange names in a specific vhost."""
    result = rabbitmq_admin.list_exchanges_by_vhost(vhost)
    return [queue["name"] for queue in result]


def handle_delete_exchange(rabbitmq_admin: RabbitMQAdmin, exchange: str, vhost: str = "/") -> None:
    """Delete an exchange from the RabbitMQ server."""
    rabbitmq_admin.delete_exchange(exchange, vhost)


def handle_get_exchange_info(
    rabbitmq_admin: RabbitMQAdmin, exchange: str, vhost: str = "/"
) -> dict:
    """Get detailed information about a specific exchange."""
    return rabbitmq_admin.get_exchange_info(exchange, vhost)

## Vhosts

def handle_list_vhosts(rabbitmq_admin: RabbitMQAdmin) -> List[str]:
    """List all vhost names in the RabbitMQ server."""
    result = rabbitmq_admin.list_vhosts()
    return [vhost["name"] for vhost in result]


## Shovels

def handle_list_shovels(rabbitmq_admin: RabbitMQAdmin) -> List[dict]:
    """List all shovels in the RabbitMQ server."""
    return rabbitmq_admin.list_shovels()


def handle_shovel(rabbitmq_admin: RabbitMQAdmin, shovel_name: str, vhost: str = "/") -> dict:
    """Get detailed information about a specific shovel."""
    return rabbitmq_admin.get_shovel_info(shovel_name, vhost)
