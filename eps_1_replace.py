from machine import Pin, ADC
import utime
import dht
import netman
import uasyncio

wlanSSID = 'WlanSSID'
wlanPW = 'WlanPassword'
country = 'DE'
mqttBroker = 'MQTT Broker IP'
mqttClient = 'Living Room'
ocor_temp = -2.3
ocor_hum = -2.2
mqttUser = ''
mqttPW = ''
btn_state="0"
temp_topic = b"tgn/esp_1/temp/sensor_1"
hum_topic = b"tgn/esp_1/temp/sensor_2"
b1_topic = "tgn/esp_1/button/b1"
light_topic = "tgn/esp_1/analog/sensor_1"
con_topic = "tgn/esp_1/connection/ip"
name_topic = "tgn/esp_1/name"
color_topic = "tgn/esp_3/neopixel/color"
br_topic = "tgn/esp_3/neopixel/brightness"
neopixel = 1

led = machine.Pin('LED', machine.Pin.OUT, value=0)
btn = machine.Pin(15, machine.Pin.IN, machine.Pin.PULL_UP) #btn with ground
sensor = dht.DHT22(Pin(2))
ldr = ADC(0)
led.low()
connected = False
wifi = None

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
            global neopixel
            global btn_state
            led.high()
            if btn.value() == 0:
                btn_state = "1"
            else:
                btn_state = "0"
            sensor.measure()
            temp = sensor.temperature()
            hum = sensor.humidity()
            temp = temp + ocor_temp
            hum = hum + ocor_hum
            read = ldr.read_u16()
            print("ADC: ", read)
            print("Temperature: {}°C   Humidity: {}% ".format(temp, hum))
            print("Button: " + btn_state)
            client = netman.mqttConnect(mqttClient, mqttBroker, mqttUser, mqttPW)
            if client == None:
                machine.reset()
            client.publish(temp_topic, str(temp),True)
            client.publish(hum_topic, str(hum),True)
            client.publish(b1_topic, btn_state,True)
            client.publish(light_topic, str(read),True)
            client.publish(name_topic, str(mqttClient),True)
            if read <= 3000:
                if neopixel == 0:
                    client.publish(color_topic, "248.1.255.255", True)
                    client.publish(br_topic, "15", True)
                    neopixel = 1
                    print("Neo ON")
            if read>= 5000:
                if neopixel == 1:
                    client.publish(br_topic, "10", True)
                    client.publish(color_topic, "0.0.0.255", True)
                    neopixel = 0
                    print("Neo OFF")
            if not wifi == None:
                client.publish(con_topic, wifi.ifconfig()[0],True)
            print("send to mqtt")
            print()
            client.disconnect()
            await uasyncio.sleep(1)
            led.low()
        await uasyncio.sleep(10)
        
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
