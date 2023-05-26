from machine import Pin
import utime
import netman
import uasyncio

wlanSSID = 'WlanSSID'
wlanPW = 'WlanPassword'
country = 'DE'
mqttBroker = 'MQTT Broker IP'
mqttClient = 'pico_9'
mqttUser = ''
mqttPW = ''
con_topic = "tgn/pico_9/connection/ip"
data_topic = "tgn/sonoff/data"
homecode = "10101"
modul = "6.0"

led = machine.Pin('LED', machine.Pin.OUT, value=0)
btn = machine.Pin(3, machine.Pin.IN, machine.Pin.PULL_UP) #btn with ground
relay = machine.Pin(6, machine.Pin.OUT, value=0)
led.low()
relay.low()
connected = False
wifi = None

def sub_cb(topic, msg):
    msg = msg.decode('utf-8')
    if topic.decode('utf-8') == data_topic:
        print(msg)
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

async def web():
    while True:
        if connected:
            print("Server")
        await uasyncio.sleep(15)
        
async def prog():
    while True:
        if connected:
            client = netman.mqttConnect(mqttClient, mqttBroker, mqttUser, mqttPW)
            if client == None:
                machine.reset()
            client.set_callback(sub_cb)
            client.subscribe(data_topic)
            client.wait_msg()
            await uasyncio.sleep(1)
            if not wifi == None:
                client.publish(con_topic, wifi.ifconfig()[0],True)
            await uasyncio.sleep(10)
            client.disconnect()
        await uasyncio.sleep(0)

async def main():
    while True:
        try:
            tasks = (uasyncio.create_task(lan()),uasyncio.create_task(prog()),uasyncio.create_task(web()))
            await uasyncio.gather(*tasks)
        except Exception as e:
            print(e)
            uasyncio.new_event_loop()
            await uasyncio.sleep(20)
uasyncio.run(main())