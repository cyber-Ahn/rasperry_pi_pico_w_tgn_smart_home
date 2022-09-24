from machine import Pin, ADC
import utime
import dht
import network
import netman
from umqttsimple import MQTTClient

#var
wlanSSID = 'WlanSSID'
wlanPW = 'WlanPassword'
country = 'DE'
mqttBroker = 'MQTT Broker IP'
mqttClient = 'pico_1'
mqttUser = ''
mqttPW = ''
btn_state="0"
temp_topic = b"tgn/pico_1/temp/sensor_1"
hum_topic = b"tgn/pico_1/temp/sensor_2"
b1_topic = "tgn/pico_1/button/b1"
light_topic = "tgn/pico_1/analog/sensor_1"
con_topic = "tgn/pico_1/connection/ip";

#set pins
led = machine.Pin('LED', machine.Pin.OUT, value=0)
btn = machine.Pin(15, machine.Pin.IN, machine.Pin.PULL_UP) #btn with ground
sensor = dht.DHT22(Pin(2))
ldr = ADC(0)

#functions
def mqttConnect():
    if mqttUser != '' and mqttPW != '':
        print("MQTT-Verbindung herstellen: %s mit %s als %s" % (mqttClient, mqttBroker, mqttUser))
        client = MQTTClient(mqttClient, mqttBroker, user=mqttUser, password=mqttPW)
    else:
        print("MQTT-Verbindung herstellen: %s mit %s" % (mqttClient, mqttBroker))
        client = MQTTClient(mqttClient, mqttBroker)
    client.connect()
    print()
    print('MQTT-Verbindung hergestellt')
    print()
    return client

#ini
led.low()
wifi_connection = netman.connectWiFi(wlanSSID,wlanPW,country)

# program
while True:
    led.high()
    if btn.value() == 0:
        btn_state = "1"
    else:
        btn_state = "0"
    sensor.measure()
    temp = sensor.temperature()
    hum = sensor.humidity()
    read = ldr.read_u16()
    print("ADC: ", read)
    print("Temperature: {}°C   Humidity: {:.0f}% ".format(temp, hum))
    print("Button: " + btn_state)
    try:
        client = mqttConnect()
        client.publish(temp_topic, str(temp))
        client.publish(hum_topic, str(hum))
        client.publish(b1_topic, btn_state)
        client.publish(light_topic, str(read))
        client.publish(con_topic, wifi_connection[0])
        print("send to mqtt")
        print()
        client.disconnect()
    except OSError:
        print('Fehler: Keine MQTT-Verbindung')
    utime.sleep(1)
    led.low()
    utime.sleep(10)