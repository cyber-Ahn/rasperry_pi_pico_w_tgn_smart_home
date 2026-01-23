from machine import Pin
import utime
import dht
import netman
import uasyncio

wlanSSID = 'WlanSSID'
wlanPW = 'WlanPassword'
country = 'DE'
mqttBroker = 'MQTT Broker IP'
mqttClient = 'Blind 1 WZ'
mqttUser = ''
mqttPW = ''
con_topic = "tgn/blind_1/connection/ip"
name_topic = "tgn/blind_1/name"
state_topic = "tgn/blind_1/state"
set_topic = "tgn/blind_1/set"
steps_topic = "tgn/blind_1/steps"
delay_topic = "tgn/blind_1/delay"
is_topic = "tgn/blind_1/is_pos"
boot = 0
moved_steps = 0
move = 0
steps = 0
delay = 0.01
set_in = "-"
is_pos = "x"

step_sequence = [
    [1, 0, 0, 0],
    [1, 1, 0, 0],
    [0, 1, 0, 0],
    [0, 1, 1, 0],
    [0, 0, 1, 0],
    [0, 0, 1, 1],
    [0, 0, 0, 1],
    [1, 0, 0, 1]
]

led = machine.Pin('LED', machine.Pin.OUT, value=0)
btn_stop = machine.Pin(11, machine.Pin.IN, machine.Pin.PULL_UP) #btn with ground
btn_rv = machine.Pin(12, machine.Pin.IN, machine.Pin.PULL_UP)
btn_fw = machine.Pin(13, machine.Pin.IN, machine.Pin.PULL_UP)

IN1 = Pin(15,Pin.OUT)
IN2 = Pin(14,Pin.OUT)
IN3 = Pin(16,Pin.OUT)
IN4 = Pin(17,Pin.OUT)

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

def sub_cb(topic, msg):
    global steps
    global delay
    global set_in
    global is_pos
    msg = msg.decode('utf-8')
    if topic.decode('utf-8') == steps_topic:
        steps = int(msg)
    if topic.decode('utf-8') == delay_topic:
        delay = round(float(msg),2)
    if topic.decode('utf-8') == is_topic:
        is_pos = msg
    if topic.decode('utf-8') == set_topic:
        set_in = msg
        if set_in == "up" and is_pos != "up":
            print("Move UP")
            client.publish(set_topic, "done",True)
            if is_pos == "50":
                step_motor(steps/2, 1, delay)
            else:
                step_motor(steps, 1, delay)
            client.publish(is_topic, "up",True)
        if set_in == "down" and is_pos != "down":
            print("Move DOWN")
            client.publish(set_topic, "done",True)
            if is_pos == "50":
                step_motor(steps/2, -1, delay)
            else:
                step_motor(steps, -1, delay)
            client.publish(is_topic, "down",True)
        if set_in == "50" and is_pos != "50":
            print("Move 50")
            client.publish(set_topic, "done",True)
            if is_pos == "up":
                step_motor(steps/2, -1, delay)
            if is_pos == "down":
                step_motor(steps/2, 1, delay)
            client.publish(is_topic, "50",True)
            
def set_step(w1, w2, w3, w4):
    IN1.value(w1)
    IN2.value(w2)
    IN3.value(w3)
    IN4.value(w4)

def step_motor(steps, direction=1, delay=0.01):
    global moved_steps
    for x in range(steps):
        for step in (step_sequence if direction > 0 else reversed(step_sequence)):
            set_step(*step)
            utime.sleep(delay)
        if direction == 1:
            moved_steps = moved_steps - 1
        elif direction == -1:
            moved_steps = moved_steps + 1
        print(moved_steps)
    set_step(0, 0, 0, 0)

def set_pos(dy,dc,move):
    global moved_steps
    global steps
    client.publish(state_topic, "set_pos:"+str(dc),True)
    while move == 1:
        moved_steps = moved_steps + 1
        print(moved_steps)
        for step in (step_sequence if dc > 0 else reversed(step_sequence)):
            set_step(*step)
            utime.sleep(dy)
        if btn_stop.value() == 0:
            move = 0
            client.publish(is_topic, "up",True)
            if dc == -1:
                steps = moved_steps
                client.publish(is_topic, "down",True)
            moved_steps = 0
            set_step(0, 0, 0, 0)
            client.publish(state_topic, "IDL",True)
            client.publish(steps_topic, str(steps),True)
    
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
    #steps 512 for one full revolution
    #direction 1 for forward, -1 for backward
    global client
    global boot
    while True:
        if connected:
            led.high()
            
            client = netman.mqttConnect(mqttClient, mqttBroker, mqttUser, mqttPW)
            if client == None:
                machine.reset()
            client.publish(name_topic, str(mqttClient),True)
            if not wifi == None:
                if boot == 0:
                    print("Test Motor")
                    client.publish(state_topic, "Test",True)
                    step_motor(128, 1, 0.01)
                    step_motor(128, -1, 0.01)
                    client.publish(con_topic, wifi.ifconfig()[0],True)
                    client.publish(state_topic, "IDL",True)
                    client.publish(set_topic, "done",True)
                    #client.publish(delay_topic, "0.01",True)
                    #client.publish(steps_topic, "0",True)
                    boot = 1
            print("send to mqtt")
            print()
            if btn_fw.value() == 0:
                set_pos(delay, 1, 1)
            if btn_rv.value() == 0:
                set_pos(delay, -1, 1)
            client.set_callback(sub_cb)
            client.subscribe(delay_topic)
            client.subscribe(steps_topic)
            client.subscribe(set_topic)
            client.subscribe(is_topic)
            client.wait_msg()
            await uasyncio.sleep(2)
            client.disconnect()
            led.low()
        await uasyncio.sleep(1)

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