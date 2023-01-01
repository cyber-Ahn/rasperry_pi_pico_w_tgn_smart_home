import base64
import netman
import socket
import utime
from mfrc522 import MFRC522

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

def sub_cb(topic, msg):
    global brightness
    global col
    global cach
    msg = msg.decode('utf-8')
    if topic.decode('utf-8') == con_topic:
        if msg == "connected":
            print("shutdown")
            client.publish(down_topic, "1",True)
            utime.sleep(20)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((PLUG_IP, 9999))
            s.send(base64.standard_b64decode(OFF))
            s.close()

reader = MFRC522(spi_id=0,sck=2,miso=4,mosi=3,cs=1,rst=0)
led = machine.Pin('LED', machine.Pin.OUT, value=0)
led.low()
wifi_connection = netman.connectWiFi(wlanSSID,wlanPW,country)
print("Bring TAG closer...")
print("")
while True:
    utime.sleep_ms(500)
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
                    client.subscribe(con_topic)
                    client.wait_msg()
                print("")
            else:
                led.low()
                print("card not allowed")
                print("")
            utime.sleep(5)
    led.low()
utime.sleep_ms(500)