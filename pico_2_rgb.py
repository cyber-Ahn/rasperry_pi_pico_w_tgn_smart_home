import utime
import netman
from neopixel import Neopixel
import uasyncio

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

pixels = Neopixel(numpix, 0, gpio, "GRB")
led = machine.Pin('LED', machine.Pin.OUT, value=0)
led.low()
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
connected = False
wifi = None

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

def connect_to_wifi():
    global connected
    global wifi
    connected = False
    wifi = netman.connectWiFi(wlanSSID,wlanPW,country)
    connected = True
    return wifi

async def lan():
    wifi = connect_to_wifi()
    while True:
        if not wifi.isconnected():
            wifi = connect_to_wifi()
        await uasyncio.sleep_ms(0)

async def web_handler(reader, writer):
    request_line = str(await reader.readline())
    while await reader.readline() != b"\r\n":
        pass
    writer.write('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
    await writer.drain()
    await writer.wait_closed()
    should_reset = request_line.find('/reset') != -1
    if should_reset:
        machine.reset()
        
async def prog():
    while True:
        if connected:
            led.high()
            client = netman.mqttConnect(mqttClient, mqttBroker, mqttUser, mqttPW)
            if client == None:
                machine.reset()
            client.set_callback(sub_cb)
            client.subscribe(color_topic)
            client.subscribe(bright_topic)
            client.wait_msg()
            utime.sleep(1)
            if not wifi == None:
                    client.publish(con_topic, wifi.ifconfig()[0],True)
            led.low()
            await uasyncio.sleep(10)
            client.disconnect()
        await uasyncio.sleep(0)
        
async def main():
    while True:
        try:
            tasks = (uasyncio.create_task(lan()),uasyncio.create_task(prog()),uasyncio.create_task(uasyncio.start_server(web_handler, "0.0.0.0", 80)))
            await uasyncio.gather(*tasks)
        except Exception as e:
            print(e)
            uasyncio.new_event_loop()
            await uasyncio.sleep(20)
uasyncio.run(main())