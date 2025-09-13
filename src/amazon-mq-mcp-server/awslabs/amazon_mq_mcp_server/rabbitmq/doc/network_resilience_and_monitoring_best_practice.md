# Best practices for network resilience and monitoring in Amazon MQ for RabbitMQ

Network resilience and monitoring broker metrics are essential for maintaining reliable messaging applications. Complete the following best practices to implement automatic recovery mechanisms and resource monitoring strategies.

## Step 1: Automatically recover from network failures

We recommend always enabling automatic network recovery to prevent significant downtime in cases where client connections to RabbitMQ nodes fail. The RabbitMQ Java client library supports automatic network recovery by default, beginning with version `4.0.0`.

Automatic connection recovery is triggered if an unhandled exception is thrown in the connection's I/O loop, if a socket read operation timeout is detected, or if the server misses a [heartbeat](https://www.rabbitmq.com/heartbeats.html).

In cases where the initial connection between a client and a RabbitMQ node fails, automatic recovery will not be triggered. We recommend writing your application code to account for initial connection failures by retrying the connection. The following example demonstrates retrying initial network failures using the RabbitMQ Java client library.

```
ConnectionFactory factory = new ConnectionFactory();
// enable automatic recovery if using RabbitMQ Java client library prior to version 4.0.0.
factory.setAutomaticRecoveryEnabled(true);
// configure various connection settings

try {
  Connection conn = factory.newConnection();
} catch (java.net.ConnectException e) {
  Thread.sleep(5000);
  // apply retry logic
}
```

###### Note

If an application closes a connection by using the `Connection.Close` method, automatic network recovery will not be enabled or triggered.

## Step 2: Monitor broker metrics and alarms

We recommend regularly monitoring [CloudWatch metrics](https://docs.aws.amazon.com/amazon-mq/latest/developer-guide/amazon-mq-accessing-metrics.html) and alarms for your Amazon MQ for RabbitMQ broker to identify and address potential issues before they impact your messaging application. Proactive monitoring is essential for maintaining a resilient messaging application and ensuring optimal performance.

Amazon MQ for RabbitMQ publishes metrics to CloudWatch that provide insights into broker performance, resource utilization, and message flow. Key metrics to monitor include memory usage and disk usage. You can set up [CloudWatch alarms](https://docs.aws.amazon.com/Ihttps://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/Alarm-On-Metrics.html) for when your broker approaches resource limits or experiences performance degradation.

Monitor the following essential metrics:

**`RabbitMQMemUsed` and `RabbitMQMemLimit`** Monitor memory usage to prevent memory alarms that can block message publishing.

**`RabbitMQDiskFree` and `RabbitMQDiskFreeLimit`** Monitor disk usage to avoid disk space issues that can cause broker failures.

For cluster deployments, also monitor [node-specific metrics](https://docs.aws.amazon.com/amazon-mq/latest/developer-guide/rabbitmq-logging-monitoring.html#security-logging-monitoring-cloudwatch-destination-metrics-rabbitmq) to identify node-specific issues.

###### Note

For more information about how to prevent high memory alarm, see [Address and prevent high memory alarm](https://docs.aws.amazon.com/amazon-mq/latest/developer-guide/troubleshooting-action-required-codes-rabbitmq-memory-alarm.html#address-prevent-high-memory-alarm).
