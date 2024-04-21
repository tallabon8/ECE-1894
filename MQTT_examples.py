import sys

import paho.mqtt.client as paho

client = paho.Client()

def add_device(name,number):#for noah to connect devices

    client = paho.Client()

    if client.connect("localhost", 1883, 60) != 0:
        print("Couldn't connect to the mqtt broker")
        sys.exit(1)

    client.publish(name, "Device Connected!", 0)
    client.disconnect()

def message_handling(client, userdata, msg):
    print(f"{msg.topic}: {msg.payload.decode()}")

def set_broker(name):#for app to detect noahs devices | must do before adding any devices, at beginnning of setup, runs continuously
    client = paho.Client()
    client.on_message = message_handling

    if client.connect("localhost", 1883, 60) != 0:
        print("Couldn't connect to the MQTT broker")
        sys.exit(1)

    client.subscribe(name)

    try:
        print("Press CTRL+C to exit...")
        client.loop_forever()
    except Exception:
        print("Caught an Exception, something went wrong...")
    finally:
        print("Disconnecting from the MQTT broker")
        client.disconnect()
