"""Message queue infrastructure for the Slot Game Analyzer."""

from typing import Any, Callable, Dict, Optional
from kombu import Connection, Exchange, Queue, Producer, Consumer
from slot_analyzer.config import settings
from slot_analyzer.log_utils import get_logger
from slot_analyzer.errors import MessageQueueError

logger = get_logger(__name__)

# Define default exchanges
default_exchange = Exchange('slot_analyzer', type='direct')
event_exchange = Exchange('slot_analyzer.events', type='topic')

# Define default queues
analysis_queue = Queue('analysis', exchange=default_exchange, routing_key='analysis')
event_queue = Queue('events', exchange=event_exchange, routing_key='events.#')

class MessageQueue:
    """Message queue manager for the application."""
    
    def __init__(self) -> None:
        self.url = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
        self._connection: Optional[Connection] = None
    
    @property
    def connection(self) -> Connection:
        """Get or create a connection to the message queue."""
        if self._connection is None or not self._connection.connected:
            try:
                self._connection = Connection(self.url)
                self._connection.connect()
                logger.info("Connected to message queue", url=self.url)
            except Exception as e:
                raise MessageQueueError(f"Failed to connect to message queue: {str(e)}")
        return self._connection

    def publish(
        self,
        payload: Dict[str, Any],
        routing_key: str,
        exchange: Exchange = default_exchange
    ) -> None:
        """Publish a message to the queue."""
        try:
            with Producer(self.connection) as producer:
                producer.publish(
                    payload,
                    exchange=exchange,
                    routing_key=routing_key,
                    serializer='json',
                    retry=True,
                    retry_policy={
                        'interval_start': 0,
                        'interval_step': 2,
                        'interval_max': 30,
                        'max_retries': 3,
                    }
                )
                logger.debug(
                    "Message published",
                    routing_key=routing_key,
                    exchange=exchange.name
                )
        except Exception as e:
            raise MessageQueueError(f"Failed to publish message: {str(e)}")

    def consume(
        self,
        queue: Queue,
        callback: Callable,
        name: Optional[str] = None
    ) -> None:
        """Setup a consumer for the specified queue."""
        try:
            with Consumer(
                self.connection,
                queues=[queue],
                callbacks=[callback],
                accept=['json']
            ) as consumer:
                logger.info(
                    "Started consuming messages",
                    queue=queue.name,
                    consumer=name or 'default'
                )
                consumer.consume()
                
                while True:
                    try:
                        self.connection.drain_events(timeout=1)
                    except Exception as e:
                        logger.warning(
                            "Consumer connection reset",
                            error=str(e),
                            consumer=name
                        )
                        break
                        
        except Exception as e:
            raise MessageQueueError(f"Consumer error: {str(e)}")

    def close(self) -> None:
        """Close the message queue connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
            logger.info("Closed message queue connection")

# Global message queue instance
message_queue = MessageQueue()