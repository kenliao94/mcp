from .admin import RabbitMQAdmin
from .connection import RabbitMQConnection, validate_rabbitmq_name
from .handlers import (
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
from mcp.server.fastmcp import FastMCP


class RabbitMQModule:
    """A module that contains RabbitMQ API."""

    def __init__(self, mcp: FastMCP):
        """Initialize the RabbitMQ module."""
        self.mcp = mcp
        self.rmq: RabbitMQConnection | None = None
        self.rmq_admin: RabbitMQAdmin | None = None

    def register_rabbitmq_management_tools(self):
        """Install RabbitMQ tools to the MCP server."""

        @self.mcp.tool()
        def initialize_connection_to_rabbitmq_broker(
            rabbitmq_host: str,
            rabbitmq_port: str,
            rabbitmq_username: str,
            rabbitmq_password: str,
            rabbitmq_use_ttl: bool,
            rabbitmq_api_port: int = 15671,
        ) -> str:
            """Connect to a new RabbitMQ broker different from the initially configured one."""
            try:
                self.rmq = RabbitMQConnection(
                    host=rabbitmq_host,
                    port=rabbitmq_port,
                    username=rabbitmq_username,
                    password=rabbitmq_password,
                    use_tls=rabbitmq_use_ttl,
                )
                self.rmq_admin = RabbitMQAdmin(
                    host=rabbitmq_host,
                    port=rabbitmq_api_port,
                    username=rabbitmq_username,
                    password=rabbitmq_password,
                    use_tls=rabbitmq_use_ttl,
                )

                return "successfully connected"
            except Exception as e:
                raise e

        @self.mcp.tool()
        def enqueue(queue: str, message: str) -> str:
            """Enqueue a message to a queue hosted on RabbitMQ."""
            validate_rabbitmq_name(queue, "Queue name")
            try:
                handle_enqueue(self.rmq, queue, message)
                return "Message successfully enqueued"
            except Exception as e:
                self.logger.error(f"{e}")
                return f"Failed to enqueue message: {e}"

        @self.mcp.tool()
        def fanout(exchange: str, message: str) -> str:
            """Publish a message to an exchange with fanout type."""
            validate_rabbitmq_name(exchange, "Exchange name")
            try:
                handle_fanout(self.rmq, exchange, message)
                return "Message successfully published to exchange"
            except Exception as e:
                self.logger.error(f"{e}")
                return f"Failed to publish message: {e}"

        @self.mcp.tool()
        def publish(topic: str, message: str):
            raise NotImplementedError()

        @self.mcp.tool()
        def list_queues() -> str:
            """List all the queues in the broker."""
            try:
                result = handle_list_queues(self.rmq_admin)
                return str(result)
            except Exception as e:
                self.logger.error(f"{e}")
                return f"Failed to list queues: {e}"

        @self.mcp.tool()
        def list_queues_by_vhost(vhost: str = "/") -> str:
            """List all the queues for a specific virtual host (vhost) in the broker."""
            try:
                result = handle_list_queues_by_vhost(self.rmq_admin, vhost)
                return str(result)
            except Exception as e:
                self.logger.error(f"{e}")
                return f"Failed to get queue info: {e}"

        @self.mcp.tool()
        def list_exchanges() -> str:
            """List all the exchanges in the broker."""
            try:
                result = handle_list_exchanges(self.rmq_admin)
                return str(result)
            except Exception as e:
                self.logger.error(f"{e}")
                return f"Failed to list exchanges: {e}"

        @self.mcp.tool()
        def list_vhosts() -> str:
            """List all the virtual hosts (vhosts) in the broker."""
            try:
                result = handle_list_vhosts(self.rmq_admin)
                return str(result)
            except Exception as e:
                self.logger.error(f"{e}")
                return f"Failed to list virtual hosts: {e}"

        @self.mcp.tool()
        def list_exchanges_by_vhost(vhost: str = "/") -> str:
            """List all the exchanges for a specific virtual host in the broker."""
            try:
                result = handle_list_exchanges_by_vhost(self.rmq_admin, vhost)
                return str(result)
            except Exception as e:
                self.logger.error(f"{e}")
                return f"Failed to list exchanges: {e}"

        @self.mcp.tool()
        def get_queue_info(queue: str, vhost: str = "/") -> str:
            """Get detailed information about a specific queue."""
            try:
                validate_rabbitmq_name(queue, "Queue name")
                result = handle_get_queue_info(self.rmq_admin, queue, vhost)
                return str(result)
            except Exception as e:
                self.logger.error(f"{e}")
                return f"Failed to get queue info: {e}"

        @self.mcp.tool()
        def delete_queue(queue: str, vhost: str = "/") -> str:
            """Delete a specific queue."""
            try:
                validate_rabbitmq_name(queue, "Queue name")
                handle_delete_queue(self.rmq_admin, queue, vhost)
                return f"Queue {queue} successfully deleted"
            except Exception as e:
                self.logger.error(f"{e}")
                return f"Failed to delete queue: {e}"

        @self.mcp.tool()
        def purge_queue(queue: str, vhost: str = "/") -> str:
            """Remove all messages from a specific queue."""
            try:
                validate_rabbitmq_name(queue, "Queue name")
                handle_purge_queue(self.rmq_admin, queue, vhost)
                return f"Queue {queue} successfully purged"
            except Exception as e:
                self.logger.error(f"{e}")
                return f"Failed to purge queue: {e}"

        @self.mcp.tool()
        def delete_exchange(exchange: str, vhost: str = "/") -> str:
            """Delete a specific exchange."""
            try:
                validate_rabbitmq_name(exchange, "Exchange name")
                handle_delete_exchange(self.rmq_admin, exchange, vhost)
                return f"Exchange {exchange} successfully deleted"
            except Exception as e:
                self.logger.error(f"{e}")
                return f"Failed to delete exchange: {e}"

        @self.mcp.tool()
        def get_exchange_info(exchange: str, vhost: str = "/") -> str:
            """Get detailed information about a specific exchange."""
            try:
                validate_rabbitmq_name(exchange, "Exchange name")
                result = handle_get_exchange_info(self.rmq_admin, exchange, vhost)
                return str(result)
            except Exception as e:
                self.logger.error(f"{e}")
                return f"Failed to get exchange info: {e}"

        @self.mcp.tool()
        def list_shovels() -> str:
            """Get detailed information about shovels in the RabbitMQ broker."""
            try:
                result = handle_list_shovels(self.rmq_admin)
                return str(result)
            except Exception as e:
                self.logger.error(f"{e}")
                return f"Failed to get exchange info: {e}"

        @self.mcp.tool()
        def get_shovel_info(name: str, vhost: str = "/") -> str:
            """Get detailed information about specific shovel by name that is in a selected virtual host (vhost) in the RabbitMQ broker."""
            try:
                result = handle_shovel(self.rmq_admin, name, vhost)
                return str(result)
            except Exception as e:
                self.logger.error(f"{e}")
                return f"Failed to get exchange info: {e}"
