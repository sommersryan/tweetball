import pika
from run import execute_from_json
from config import AMQP_URL

connection = pika.BlockingConnection(
	parameters=pika.URLParameters(AMQP_URL)
)

sub_channel = connection.channel()
sub_channel.exchange_declare(exchange='games', exchange_type='topic')
result = sub_channel.queue_declare('', exclusive=True)
queue_name = result.method.queue
sub_channel.queue_bind(exchange='games', queue=queue_name, routing_key='games.execution.start')

pub_channel = connection.channel()
pub_channel.exchange_declare(exchange='games', exchange_type='topic')


def callback(ch, method, properties, body):
	game_result_json = execute_from_json(body)
	pub_channel.basic_publish(exchange='games', routing_key='games.execution.complete', body=game_result_json)


sub_channel.basic_consume(
	queue=queue_name, on_message_callback=callback, auto_ack=True
)

print('now listening for game start events')
sub_channel.start_consuming()
