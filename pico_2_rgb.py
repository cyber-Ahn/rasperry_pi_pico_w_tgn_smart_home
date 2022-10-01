from machine import Pin, ADC
import utime
import dht
import network
import netman
from umqttsimple import MQTTClient
from neopixel import Neopixel

#var
wlanSSID = 'Matrix'
wlanPW = 'rhjk0096#Matrix'
country = 'DE'
mqttBroker = '192.168.0.98'
mqttClient = 'pico_2'
mqttUser = ''
mqttPW = ''
con_topic = "tgn/pico_2/connection/ip";
color_topic = "tgn/esp_3/neopixel/color";
bright_topic = "tgn/esp_3/neopixel/brightness";
numpix = 60
gpio = 28
brightness = "0"
col = "0"
cach = []

#set pins
led = machine.Pin('LED', machine.Pin.OUT, value=0)
#functions
def sub_cb(topic, msg):
    global brightness
    global col
    global cach
    msg = msg.decode('utf-8')
    if topic.decode('utf-8') == bright_topic:
        brightness = msg
    if topic.decode('utf-8') == color_topic:
        col = msg
    if col != "0" and brightness != "0":
        cach = col.split(".")
        if len(cach) == 4:
            print("New Data")
            print(brightness)
            print(col)
            pixels.brightness(int(brightness))
            pixels.fill((int(cach[0]), int(cach[1]), int(cach[2])))
            pixels.show()

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

#ini
led.low()
wifi_connection = netman.connectWiFi(wlanSSID,wlanPW,country)
pixels = Neopixel(numpix, 0, gpio, "GRB")
print("Ini RGB Stripe")
pixels.brightness(50)
pixels.fill((255, 0, 0))
pixels.show()
utime.sleep(5)
pixels.fill((0, 255, 0))
pixels.show()
utime.sleep(5)
pixels.fill((0, 0, 255))
pixels.show()
utime.sleep(5)
pixels.fill((0, 0, 0))
pixels.show()

# program
while True:
    led.high()
    
    try:
        client = mqttConnect()
        client.subscribe(color_topic)
        client.subscribe(bright_topic)
        client.wait_msg()
    except OSError:
        print('Fehler: Keine MQTT-Verbindung')
    utime.sleep(1)
    client.publish(con_topic, wifi_connection[0],True)
    led.low()
    utime.sleep(10)
    client.disconnect()