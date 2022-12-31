import utime
import netman
from neopixel import Neopixel

#var
wlanSSID = 'WlanSSID'
wlanPW = 'WlanPassword'
country = 'DE'
mqttBroker = 'MQTT Broker IP'
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
    client = netman.mqttConnect(mqttClient, mqttBroker, mqttUser, mqttPW)
    if client == None:
        machine.reset()
    client.set_callback(sub_cb)
    client.subscribe(color_topic)
    client.subscribe(bright_topic)
    client.wait_msg()
    utime.sleep(1)
    client.publish(con_topic, wifi_connection[0],True)
    led.low()
    utime.sleep(10)
    client.disconnect()