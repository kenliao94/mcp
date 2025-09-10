from .admin import RabbitMQAdmin
from .connection import RabbitMQConnection
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
