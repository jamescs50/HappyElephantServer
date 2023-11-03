from app import db
from app.models import WeatherData
import paho.mqtt.client as mqtt


def on_connect(client, userdata, flags, rc):
    print("Result from connect: {}".format(
            mqtt.connack_string(rc)))
# Subscribe to the senors/alitmeter/1 topic filter
    client.subscribe("weather/#")


def on_subscribe(client, userdata, mid, granted_qos):
    print("I've subscribed")


def on_message(client, userdata, msg):
    print("Message received. Topic: {}. Payload: {}".format(
            msg.topic, str(msg.payload)))
    newdata = {}
    newdata['source_topic'] = msg.topic
    newdata['data'] = msg.payload
    n = WeatherData(**newdata)
    db.session.add(n)
    db.session.commit()


if __name__ == "__main__":
    client = mqtt.Client(protocol=mqtt.MQTTv311)
    client.on_connect = on_connect
    client.on_subscribe = on_subscribe
    client.on_message = on_message
    client.connect(host="kodoo-svr02", port=1883)
    client.loop_forever()