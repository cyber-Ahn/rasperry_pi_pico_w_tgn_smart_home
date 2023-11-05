from machine import Pin, I2C
import netman
import mcp23017
import time
import utime
import uasyncio


wlanSSID = 'WlanSSID'
wlanPW = 'WlanPassword'
country = 'DE'
mqttBroker = 'MQTT Broker IP'
mqttClient = 'pico_4'
mqttUser = ''
mqttPW = ''
con_topic = "tgn/pico_4/connection/ip";
but_1 = "tgn/buttons/status/1"
but_2 = "tgn/buttons/status/2"
but_3 = "tgn/buttons/status/3"
but_4 = "tgn/buttons/status/4"
but_5 = "tgn/buttons/status/5"
but_6 = "tgn/buttons/status/6"
but_7 = "tgn/buttons/status/7"
but_8 = "tgn/buttons/status/8"

led = machine.Pin('LED', machine.Pin.OUT, value=0)
led.low()

sdaPIN=machine.Pin(20)
sclPIN=machine.Pin(21)
scl_freq = 400000
addr = 0x20
mcp_out = [0, 7]
mcp_in = [8, 15]

port_cach = ""
but_1_s = 0
but_2_s = 0
but_3_s = 0
but_4_s = 0
but_5_s = 0
but_6_s = 0
but_7_s = 0
but_8_s = 0

client = ""

i2c=machine.I2C(0,sda=sdaPIN, scl=sclPIN, freq=scl_freq)
mcp = mcp23017.MCP23017(i2c, addr)

p = mcp_out[0]
while p <= mcp_out[1]:
    mcp[p].output(1)
    time.sleep(.10)
    p += 1
p = mcp_out[0]
while p <= mcp_out[1]:
    mcp[p].output(0)
    time.sleep(.10)
    p += 1
pi = mcp_in[0]
while pi <= mcp_in[1]:
    mcp[pi].input()
    mcp[pi].input(pull=1)
    pi += 1

def set_mcp(start_bit, stop_bit):
    p = start_bit
    mcp[p].output(but_1_s); p += 1
    mcp[p].output(but_2_s); p += 1
    mcp[p].output(but_3_s); p += 1
    mcp[p].output(but_4_s); p += 1
    mcp[p].output(but_5_s); p += 1
    mcp[p].output(but_6_s); p += 1
    mcp[p].output(but_7_s); p += 1
    mcp[p].output(but_8_s)

def read_mcp(start_bit, end_bit):
    pi = start_bit; port_s = ""; global port_cach
    while pi <= end_bit:
        if mcp[pi].value() == 1:
            p = pi - start_bit
            mcp[p].output(1)
            port_s = port_s + "1"
        elif mcp[pi].value() == 0:
            p = pi - start_bit
            mcp[p].output(0)
            port_s = port_s + "0"  
        pi += 1
    if port_cach != port_s:
        if port_s != "00000000": dec_but_n(port_s)
        port_cach = port_s
        
def dec_but_n(data):
    but_n = data.find('1')+1
    stat = "0"
    if but_n == 1: stat = str(but_1_s)
    if but_n == 2: stat = str(but_2_s)
    if but_n == 3: stat = str(but_3_s)
    if but_n == 4: stat = str(but_4_s)
    if but_n == 5: stat = str(but_5_s)
    if but_n == 6: stat = str(but_6_s)
    if but_n == 7: stat = str(but_7_s)
    if but_n == 8: stat = str(but_8_s)
    if stat == "0": stat = "1"
    else: stat = "0"
    topic = "tgn/buttons/status/"+str(but_n)
    print(topic + ": "+stat)
    client.publish(topic, stat,True)
    
def connect_to_wifi():
    global connected; global wifi
    connected = False
    wifi = netman.connectWiFi(wlanSSID,wlanPW,country)
    connected = True
    return wifi

def sub_cb(topic, msg):
    global but_1_s; global but_2_s; global but_3_s; global but_4_s
    global but_5_s; global but_6_s; global but_7_s; global but_8_s
    msg = msg.decode('utf-8')
    if topic.decode('utf-8') == but_1: but_1_s = int(msg)
    if topic.decode('utf-8') == but_2: but_2_s = int(msg)
    if topic.decode('utf-8') == but_3: but_3_s = int(msg)
    if topic.decode('utf-8') == but_4: but_4_s = int(msg)
    if topic.decode('utf-8') == but_5: but_5_s = int(msg)
    if topic.decode('utf-8') == but_6: but_6_s = int(msg)
    if topic.decode('utf-8') == but_7: but_7_s = int(msg)
    if topic.decode('utf-8') == but_8: but_8_s = int(msg)

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
            global client
            client = netman.mqttConnect(mqttClient, mqttBroker, mqttUser, mqttPW)
            if client == None:
                machine.reset()
            client.set_callback(sub_cb)
            client.subscribe(but_1); client.subscribe(but_2); client.subscribe(but_3); client.subscribe(but_4)
            client.subscribe(but_5); client.subscribe(but_6); client.subscribe(but_7); client.subscribe(but_8)
            client.wait_msg()
            utime.sleep(1)
            if not wifi == None:
                    client.publish(con_topic, wifi.ifconfig()[0],True)
            led.low()
            await uasyncio.sleep(10)
            read_mcp(mcp_in[0], mcp_in[1])
            await uasyncio.sleep(1)
            set_mcp(mcp_out[0], mcp_out[1])
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