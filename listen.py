import pika
from run import execute_from_json
from config import AMQP_URL

connection = pika.BlockingConnection(
    parameters=pika.URLParameters(AMQP_URL)
)

channel = connection.channel()

channel.exchange_declare(exchange='games', exchange_type='topic')

result = channel.queue_declare('', exclusive=True)

queue_name = result.method.queue

channel.queue_bind(exchange='games', queue=queue_name, routing_key='games.execution.start')


def callback(ch, method, properties, body):
    game_result_json = execute_from_json(body)
    print(game_result_json)


channel.basic_consume(
    queue=queue_name, on_message_callback=callback, auto_ack=True
)

channel.start_consuming()
