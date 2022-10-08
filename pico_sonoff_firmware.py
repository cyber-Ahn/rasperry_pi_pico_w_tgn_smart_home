from machine import Pin
import utime
import network
import netman
from umqttsimple import MQTTClient

#var
wlanSSID = 'WlanSSID'
wlanPW = 'WlanPassword'
country = 'DE'
mqttBroker = 'MQTT Broker IP'
mqttClient = 'pico_9'
mqttUser = ''
mqttPW = ''
con_topic = "tgn/pico_9/connection/ip";
data_topic = "tgn/sonoff/data";

homecode = "10101"
modul = "6.0"

#functions
def sub_cb(topic, msg):
    msg = msg.decode('utf-8')
    if topic.decode('utf-8') == data_topic:
        print(msg)
        #10101-6.0-0
        cach = msg.split("-")
        if homecode == cach[0] and modul == cach[1]:
            if cach[2] == "1":
                print('Sonoff on')
                led.high()
                relay.high()
            if cach[2] == "0":
                print('Sonoff off')
                led.low()
                relay.low()
        
        

def mqttConnect():
    if mqttUser != '' and mqttPW != '':
        print("MQTT-Verbindung herstellen: %s mit %s als %s" % (mqttClient, mqttBroker, mqttUser))
        client = MQTTClient(mqttClient, mqttBroker, user=mqttUser, password=mqttPW)
    else:
        print("MQTT-Verbindung herstellen: %s mit %s" % (mqttClient, mqttBroker))
        client = MQTTClient(mqttClient, mqttBroker)
    client.connect()
    client.set_callback(sub_cb)
    return client

#set pins
led = machine.Pin('LED', machine.Pin.OUT, value=0)
btn = machine.Pin(3, machine.Pin.IN, machine.Pin.PULL_UP) #btn with ground
relay = machine.Pin(6, machine.Pin.OUT, value=0)

#ini
led.low()
relay.low()
wifi_connection = netman.connectWiFi(wlanSSID,wlanPW,country)

# program
while True:
    if btn.value() == 0:
        led.high()
        relay.high()
    else:
        led.low()
        relay.low()
    try:
        client = mqttConnect()
        client.subscribe(data_topic)
        client.wait_msg()
    except OSError:
        print('Fehler: Keine MQTT-Verbindung')
    utime.sleep(1)
    client.publish(con_topic, wifi_connection[0],True)
    utime.sleep(10)
    client.disconnect()
    