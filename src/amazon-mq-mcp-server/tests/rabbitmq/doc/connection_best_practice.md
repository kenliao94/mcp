# Best practices for broker setup and connection management in Amazon MQ for RabbitMQ - Amazon MQ

###### Important

Amazon MQ for RabbitMQ does not support the username "guest", and will delete the default guest account when you create a new broker. Amazon MQ will also periodically delete any customer created account called "guest".

## Step 1: Use cluster deployments

For production workloads, we recommend using cluster deployments instead of single-instance brokers to ensure high availability and message resiliency. Cluster deployments remove single points of failure and provide better fault tolerance.

Cluster deployments consist of three RabbitMQ broker nodes distributed across three Availability Zones, providing automatic failover and ensuring operations continue even if an entire Availability Zone becomes unavailable. Amazon MQ automatically replicates messages across all nodes to ensure availability during node failures or maintenance.

Cluster deployments are essential for production environments and are supported by the [Amazon MQ Service Level Agreement](https://aws.amazon.com/https://aws.amazon.com/amazon-mq/sla/).

For more information, see [Cluster deployment in Amazon MQ for RabbitMQ](https://docs.aws.amazon.com/amazon-mq/latest/developer-guide/rabbitmq-broker-architecture.html#rabbitmq-broker-architecture-cluster).

## Step 2: Choose the correct broker instance type

The message throughput of a broker instance type depends on your application use case. `M7g.medium` should only be used for testing application performance. Using this smaller instance before using larger instances in production can improve application performance. On instance types `m7g.large` and above, you can use cluster deployments for high availability and message durability. Larger broker instance types can handle production levels of clients and queues, high throughput, messages in memory, and redundant messages.

For more information on choosing the correct instance type, see [Sizing guidelines in Amazon MQ for RabbitMQ](https://docs.aws.amazon.com/amazon-mq/latest/developer-guide/rabbitmq-sizing-guidelines.html).

## Step 3: Use quorum queues

Quorum queues, with cluster deployment, should be the default choice for replicated queue types in production environments for RabbitMQ brokers on 3.13 and above. Quorum queues are a modern replicated queue type that provide high reliability, high throughput, and stable latency.

Quorum queues use the Raft consensus algorithm to provide better fault tolerance. When the leader node becomes unavailable, quorum queues automatically elect a new leader by majority vote, ensuring message delivery continues with minimal disruption. Since each node is in a different Availability Zone, your messaging system remains available even if an entire Availability Zone becomes temporarily unavailable.

To declare a quorum queue, set the header `x-queue-type` to `quorum` when creating your queues.

For more information on quorum queues, including migration strategies and best practices, see [Quorum queues in Amazon MQ for RabbitMQ](https://docs.aws.amazon.com/amazon-mq/latest/developer-guide/quorum-queues.html).

## Step 4: Use multiple channels

To avoid connection churn, use multiple channels over a single connection. Applications should avoid a 1:1 connection to channel ratio. We recommend using one connection for each process, and then one channel for each thread. Avoid excessive channel usage to prevent channel leaks.
