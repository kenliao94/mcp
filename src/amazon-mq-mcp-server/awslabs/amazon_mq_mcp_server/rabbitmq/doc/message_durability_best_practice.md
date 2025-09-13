# Best practices for message durability and reliability in Amazon MQ for RabbitMQ

Before moving your application to production, complete the following best practices for preventing message loss and resource overutilization.

## Step 1: Use persistent messages and durable queues

Persistent messages can help prevent data loss in situations where a broker crashes or restarts. Persistent messages are written to disk as soon as they arrive. Unlike lazy queues, however, persistent messages are cached both in memory and in disk unless more memory is needed by the broker. In cases where more memory is needed, messages are removed from memory by the RabbitMQ broker mechanism that manages storing messages to disk, commonly referred to as the _persistence layer_.

To enable message persistence, you can declare your queues as `durable` and set message delivery mode to `persistent`. The following example demonstrates using the [RabbitMQ Java client library](https://www.rabbitmq.com/java-client.html) to declare a durable queue. When working with AMQP 0-9-1, you can mark messages as persistent by setting delivery mode "2".

```
boolean durable = true;
channel.queueDeclare("my_queue", durable, false, false, null);
```

Once you have configured your queue as durable, you can send a persistent message to your queue by setting `MessageProperties` to `PERSISTENT_TEXT_PLAIN` as shown in the following example.

```
import com.rabbitmq.client.MessageProperties;

channel.basicPublish("", "my_queue",
            MessageProperties.PERSISTENT_TEXT_PLAIN,
            message.getBytes());
```

## Step 2: Configure publisher confirms and consumer delivery acknowledgement

The process of confirming a message has been sent to the broker is known as _publisher confirmation_. Publisher confirms let your application know when messages have been reliably stored. Publisher confirms can also help control the rate of messages stored to the broker. Without publisher confirms, there is no confirmation that a message is processed successfully, and your broker may drop messages it cannot process.

Similarly, when a client application sends confirmation of delivery and consumption of messages back to the broker, it is known as _consumer delivery acknowledgment_. Both confirmation and acknowledgement are essential to ensuring data safety when working with RabbitMQ brokers.

Consumer delivery acknowledgement is typically configured on the client application. When working with AMQP 0-9-1, acknowledgement can be enabled by configuring the `basic.consume` method. AMQP 0-9-1 clients can also configure publisher confirms by sending the `confirm.select` method.

Typically, delivery acknowledgement is enabled in a channel. For example, when working with the RabbitMQ Java client library, you can use the `Channel#basicAck` to set up a simple `basic.ack` positive acknowledgement as shown in the following example.

```
// this example assumes an existing channel instance

boolean autoAck = false;
channel.basicConsume(queueName, autoAck, "a-consumer-tag",
     new DefaultConsumer(channel) {
         @Override
         public void handleDelivery(String consumerTag,
                                    Envelope envelope,
                                    AMQP.BasicProperties properties,
                                    byte[] body)
             throws IOException
         {
             long deliveryTag = envelope.getDeliveryTag();
             // positively acknowledge a single delivery, the message will
             // be discarded
             channel.basicAck(deliveryTag, false);
         }
     });
```

###### Note

Unacknowledged messages must be cached in memory. You can limit the number of messages that a consumer pre-fetches by configuring [pre-fetch](https://docs.aws.amazon.com/amazon-mq/latest/developer-guide/best-practices-performance.html#configure-prefetching) settings for a client application.

You can configure `consumer_timeout` to detect when consumers do not acknowledge deliveries. If the consumer does not send an acknowledgment within the timeout value, the channel will be closed, and you will recieve a `PRECONDITION_FAILED`. To diagnose the error, use the [UpdateConfiguration](https://docs.aws.amazon.com/amazon-mq/latest/api-reference/configurations-configuration-id.html) API to increase the `consumer_timeout` value.

## Step 3: Keep queues short

In cluster deployments, queues with a large number of messages can lead to resource overutilization. When a broker is overutilized, rebooting an Amazon MQ for RabbitMQ broker can cause further degradation of performance. If rebooted, overutilized brokers might become unresponsive in the `REBOOT_IN_PROGRESS` state.

During [maintenance windows](https://docs.aws.amazon.com/amazon-mq/latest/developer-guide/amazon-mq-rabbitmq-editing-broker-preferences.html#rabbitmq-edit-current-configuration-console), Amazon MQ performs all maintenance work one node at a time to ensure that the broker remains operational. As a result, queues might need to synchronize as each node resumes operation. During synchronization, messages that need to be replicated to mirrors are loaded into memory from the corresponding Amazon Elastic Block Store (Amazon EBS) volume to be processed in batches. Processing messages in batches lets queues synchronize faster.

If queues are kept short and messages are small, the queues successfully synchronize and resume operation as expected. However, if the amount of data in a batch approaches the node's memory limit, the node raises a high memory alarm, pausing the queue sync. You can confirm memory usage by comparing the `RabbitMemUsed` and `RabbitMqMemLimit`[broker node metrics in CloudWatch](https://docs.aws.amazon.com/amazon-mq/latest/developer-guide/amazon-mq-accessing-metrics.html). Synchronization can't complete until messages are consumed or deleted, or the number of messages in the batch is reduced.

If queue synchronization is paused for a cluster deployment, we recommend consuming or deleting messages to lower the number of messages in queues. Once queue depth is reduced and queue sync completes, the broker status will change to `RUNNING`. To resolve a paused queue sync, you can also apply a policy to [reduce the queue synchronization batch-size](https://docs.aws.amazon.com/amazon-mq/latest/developer-guide/rabbitmq-queue-sync.html).

You can also define auto-delete and TTL policies to proactively reduce resource usage, as well as keep NACKs from consumers to a minimum. Requeueing messages on the broker is CPU-intensive so a high number of NACKs can affect broker performance.
