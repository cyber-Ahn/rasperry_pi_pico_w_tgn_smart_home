import base64
import netman
import socket
import utime
from mfrc522 import MFRC522
import uasyncio

wlanSSID = 'WlanSSID'
wlanPW = 'WlanPassword'
country = 'DE'
mqttBroker = 'MQTT Broker IP'
mqttClient = 'pico_rfid'
mqttUser = ''
mqttPW = ''
con_topic = "tgn/info/status";
down_topic = "tgn/system/shutdown";
PLUG_IP = '192.168.0.57'
ON = 'AAAAKtDygfiL/5r31e+UtsWg1Iv5nPCR6LfEsNGlwOLYo4HyhueT9tTu36Lfog=='
OFF = 'AAAAKtDygfiL/5r31e+UtsWg1Iv5nPCR6LfEsNGlwOLYo4HyhueT9tTu3qPeow=='
user_allow = ["2452674083","36149765212152324"]
reader = MFRC522(spi_id=0,sck=2,miso=4,mosi=3,cs=1,rst=0)
led = machine.Pin('LED', machine.Pin.OUT, value=0)
led.low()
connected = False
wifi = None

def sub_cb(topic, msg):
    global brightness
    global col
    global cach
    msg = msg.decode('utf-8')
    if topic.decode('utf-8') == con_topic:
        if msg == "connected":
            print("shutdown")

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
            print("Bring TAG closer...")
            print("")
            await uasyncio.sleep_ms(500)
            led.high()
            reader.init()
            (stat, tag_type) = reader.request(reader.REQIDL)
            if stat == reader.OK:
                (stat, uid) = reader.SelectTagSN()
                if stat == reader.OK:
                    card = int.from_bytes(bytes(uid),"little",False)
                    print("CARD ID: "+str(card))
                    if str(card) in user_allow:
                        print("card approved")
                        client = netman.mqttConnect(mqttClient, mqttBroker, mqttUser, mqttPW)
                        if client == None:
                            print('Turn On')
                            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            s.connect((PLUG_IP, 9999))
                            s.send(base64.standard_b64decode(ON))
                            s.close()
                        else:
                            client.set_callback(sub_cb)
                            client.subscribe(con_topic)
                            client.wait_msg()
                            client.publish(down_topic, "1",True)
                            utime.sleep(20)
                            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            s.connect((PLUG_IP, 9999))
                            s.send(base64.standard_b64decode(OFF))
                            s.close()
                        print("")
                    else:
                        led.low()
                        print("card not allowed")
                        print("")
                    await uasyncio.sleep(5)
            led.low()
            await uasyncio.sleep_ms(500)
            
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