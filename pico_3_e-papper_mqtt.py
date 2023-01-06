import utime
import netman
import json
import socket
from EPD_2in9 import EPD_2in9

wlanSSID = 'WlanSSID'
wlanPW = 'WlanPassword'
country = 'DE'
mqttBroker = 'MQTT Broker IP'
time_server = 'http://worldtimeapi.org/api/timezone/Europe/Berlin'
mqttClient = 'pico_3'
mqttUser = ''
mqttPW = ''
con_topic = "tgn/pico_3/connection/ip";
con_w_temp = "tgn/weather/temp"
con_w_hum = "tgn/weather/humidity"
con_e_temp = "tgn/esp_1/temp/sensor_1"
con_e_hum = "tgn/esp_1/temp/sensor_2"
con_p_temp = "tgn/pico_1/temp/sensor_1"
con_p_hum = "tgn/pico_1/temp/sensor_2"
con_o_temp = "tgn/esp_2/temp/sensor_1"
con_o_hum = "tgn/esp_2/temp/sensor_2"
con_power = "tgn/hs100/192.168.0.50/power"
con_voltage = "tgn/hs100/192.168.0.50/voltage"
con_total = "tgn/hs100/192.168.0.50/total"
con_p_1 = "tgn/pico_1/connection/ip"
con_p_2 = "tgn/pico_2/connection/ip"
con_p_3 = "tgn/pico_3/connection/ip"
con_e_1 = "tgn/esp_1/connection/ip"
con_e_2 = "tgn/esp_2/connection/ip"
con_e_3 = "tgn/esp_3/connection/ip"
con_r_1 = "tgn/ip"
pihole_block = "tgn/pihole/adBlock"
pihole_queries = "tgn/pihole/queries"
pihole_client = "tgn/pihole/clients"
pihole_dns = "tgn/pihole/dnslist"
con_a_ip = "tgn/android/ip"
con_a_name = "tgn/android/name"
con_a_ver = "tgn/android/version"
con_a_gps = "tgn/android/gps/status"
con_a_sat = "tgn/android/gps/sat_fix"
con_p_shutdown = "tgn/pico/shutdown"

p_shutdown = "0"
a_ip = "000.000.0.0"
a_name = "not Found"
a_ver = "00"
a_gps = "offline"
a_sat = "0"
block = "0"
queries = "0"
client_p = "0"
dns_p = "0"
p_1 = "000.000.0.00"
p_2 = "000.000.0.00"
p_3 = "000.000.0.00"
e_1 = "000.000.0.00"
e_2 = "000.000.0.00"
e_3 = "000.000.0.00"
r_1 = "000.000.0.00"
w_temp = "0.0"
w_hum = "0.0"
e_temp = "0.0"
e_hum = "0.0"
w_temp = "0.0"
w_hum = "0.0"
p_temp = "0.0"
p_hum = "0.0"
o_temp = "0.0"
o_hum = "0.0"
power = "0"
voltage = "0"
total = "0"

#set pins
led = machine.Pin('LED', machine.Pin.OUT, value=0)
#functions
def http_get(url):
    result = ''
    _, _, host, path = url.split('/', 3)
    addr = socket.getaddrinfo(host, 80)[0][-1]
    s = socket.socket()
    s.connect(addr)
    s.send(bytes('GET /%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (path, host), 'utf8'))
    while True:
        data = s.recv(100)
        if data:
            result = result + str(data, 'utf8')
        else:
            break
    s.close()
    return result

def findJson(response):
    txt = 'abbreviation'
    return response[response.find(txt)-2:]

def mqtt_subscribe(topic):
    num = len(topic)
    for i in range(num):
        client.subscribe(topic[i])

def sub_cb(topic, msg):
    global w_temp; global w_hum; global e_temp; global e_hum; global p_temp; global p_hum; global e_temp; global e_hum; global o_temp; global o_hum
    global power; global voltage; global total
    global p_1; global p_2; global p_3; global e_1; global e_2; global e_3; global r_1
    global block; global queries; global client_p; global dns_p
    global a_ip; global a_name; global a_ver; global a_gps; global a_sat; global p_shutdown
    msg = msg.decode('utf-8')
    if topic.decode('utf-8') == con_e_temp:
        e_temp = msg
    if topic.decode('utf-8') == con_e_hum:
        e_hum = msg
    if topic.decode('utf-8') == con_w_temp:
        w_temp = msg
    if topic.decode('utf-8') == con_w_hum:
        w_hum = msg
    if topic.decode('utf-8') == con_p_temp:
        p_temp = msg
    if topic.decode('utf-8') == con_p_hum:
        p_hum = msg
    if topic.decode('utf-8') == con_o_temp:
        o_temp = msg
    if topic.decode('utf-8') == con_o_hum:
        o_hum = msg
    if topic.decode('utf-8') == con_power:
        power = msg
    if topic.decode('utf-8') == con_voltage:
        voltage = msg
    if topic.decode('utf-8') == con_total:
        total = msg
    if topic.decode('utf-8') == con_p_1:
        p_1 = msg
    if topic.decode('utf-8') == con_p_2:
        p_2 = msg
    if topic.decode('utf-8') == con_p_3:
        p_3 = msg
    if topic.decode('utf-8') == con_e_1:
        e_1 = msg
    if topic.decode('utf-8') == con_e_2:
        e_2 = msg
    if topic.decode('utf-8') == con_e_3:
        e_3 = msg
    if topic.decode('utf-8') == con_r_1:
        r_1 = msg  
    if topic.decode('utf-8') == pihole_block:
        block = msg
    if topic.decode('utf-8') == pihole_queries:
        queries = msg
    if topic.decode('utf-8') == pihole_client:
        client_p = msg
    if topic.decode('utf-8') == pihole_dns:
        dns_p = msg  
    if topic.decode('utf-8') == con_a_ip:
        a_ip = msg
    if topic.decode('utf-8') == con_a_name:
        a_name = msg
    if topic.decode('utf-8') == con_a_ver:
        a_ver = msg
    if topic.decode('utf-8') == con_a_gps:
        a_gps = msg
    if topic.decode('utf-8') == con_a_sat:
        a_sat = msg
    if topic.decode('utf-8') == con_p_shutdown:
        p_shutdown = msg

def clear_page():
    epd.Clear(0xff)
    epd.delay_ms(2000)

def set_text(text, x, y):
    epd.fill(0xff)
    epd.text(text, x, y, 0x00)
    epd.display(epd.buffer)
    epd.delay_ms(9000)
    
def page_1():
    epd.fill(0xff)
    epd.text("Waveshare", 5, 5, 0x00)
    epd.text("Pico_ePaper-2.9", 5, 25, 0x00)
    epd.text("Raspberry Pico", 5, 45, 0x00)
    epd.text("Load Mqtt Data", 5, 65, 0x00)
    epd.text("Ip:"+mqttBroker, 5, 85, 0x00)
    epd.text("please wait ....", 5, 105, 0x00)
    epd.display(epd.buffer)
    epd.delay_ms(9000)
    
def page_2():
    epd.fill(0xff)
    epd.text("WIFI Connected", 5, 125, 0x00)
    epd.text("IP:"+wifi_connection[0], 5, 135, 0x00)
    epd.display(epd.buffer)
    epd.delay_ms(9000)

def page_3(date, time):
    epd.fill(0xff)
    epd.line(0, 0, 128, 0, 0x00)
    epd.line(0, 0, 0, 296, 0x00)
    epd.line(127, 0, 127, 296, 0x00)
    epd.line(0, 295, 128, 295, 0x00)
    epd.text("Temperatures", 15, 5, 0x00)
    epd.line(0, 15, 128, 15, 0x00)
    epd.text("Weather:", 5, 25, 0x00)
    epd.text("Temp.: "+w_temp+"C", 5, 35, 0x00)
    epd.text("Hum.: "+w_hum+"%", 5, 45, 0x00)
    epd.line(0, 55, 128, 55, 0x00)
    epd.text("ESP Livingroom:", 5, 65, 0x00)
    epd.text("Temp.: "+e_temp+"C", 5, 75, 0x00)
    epd.text("Hum.: "+e_hum+"%", 5, 85, 0x00)
    epd.line(0, 95, 128, 95, 0x00)
    epd.text("Pico Nursery:", 5, 105, 0x00)
    epd.text("Temp.: "+p_temp+"C", 5, 115, 0x00)
    epd.text("Hum.: "+p_hum+"%", 5, 125, 0x00)
    epd.line(0, 135, 128, 135, 0x00)
    epd.text("ESP Outside:", 5, 145, 0x00)
    epd.text("Temp.: "+o_temp+"C", 5, 155, 0x00)
    epd.text("Hum.: "+o_hum+"%", 5, 165, 0x00)
    epd.line(0, 175, 128, 175, 0x00)
    epd.text("Powermeter", 20, 195, 0x00)
    epd.text(voltage, 25, 215, 0x00)
    epd.text(power, 25, 225, 0x00)
    epd.text(total, 25, 235, 0x00)
    epd.line(0, 275, 128, 275, 0x00)
    epd.text(time+"-"+date, 10, 285, 0x00)
    epd.display(epd.buffer)
    epd.delay_ms(60000)
    
def page_4(date, time):
    epd.fill(0xff)
    epd.line(0, 0, 128, 0, 0x00)
    epd.line(0, 0, 0, 296, 0x00)
    epd.line(127, 0, 127, 296, 0x00)
    epd.line(0, 295, 128, 295, 0x00)#
    epd.text("IP List", 35, 5, 0x00)
    epd.line(0, 15, 128, 15, 0x00)
    epd.text("Raspberry Pi", 5, 25, 0x00)
    epd.text(r_1, 10, 35, 0x00)
    epd.line(0, 45, 128, 45, 0x00)
    epd.text("Pico 1", 5, 55, 0x00)
    epd.text(p_1, 10, 65, 0x00)
    epd.line(0, 75, 128, 75, 0x00)
    epd.text("Pico 2", 5, 85, 0x00)
    epd.text(p_2, 10, 95, 0x00)
    epd.line(0, 105, 128, 105, 0x00)
    epd.text("Pico 3", 5, 115, 0x00)
    epd.text(p_3, 10, 125, 0x00)
    epd.line(0, 135, 128, 135, 0x00)
    epd.text("ESP 1", 5, 145, 0x00)
    epd.text(e_1, 10, 155, 0x00)
    epd.line(0, 165, 128, 165, 0x00)
    epd.text("ESP 2", 5, 175, 0x00)
    epd.text(e_2, 10, 185, 0x00)
    epd.line(0, 195, 128, 195, 0x00)
    epd.text("ESP 3", 5, 205, 0x00)
    epd.text(e_3, 10, 215, 0x00)
    epd.line(0, 225, 128, 225, 0x00)
    epd.line(0, 275, 128, 275, 0x00)
    epd.text(time+"-"+date, 10, 285, 0x00)
    epd.display(epd.buffer)
    epd.delay_ms(10000)

def page_5(date, time):
    epd.fill(0xff)
    epd.line(0, 0, 128, 0, 0x00)
    epd.line(0, 0, 0, 296, 0x00)
    epd.line(127, 0, 127, 296, 0x00)
    epd.line(0, 295, 128, 295, 0x00)#
    epd.text("PI-Hole", 35, 5, 0x00)
    epd.line(0, 15, 128, 15, 0x00)
    epd.text("Blocked:"+block, 5, 25, 0x00)
    epd.text("Queries:"+queries, 5, 35, 0x00)
    epd.text("Clients:"+client_p, 5, 45, 0x00)
    epd.text("DNS-List:", 5, 55, 0x00)
    epd.text(dns_p, 35, 65, 0x00)
    epd.line(0, 75, 128, 75, 0x00)
    epd.text("Android", 35, 95, 0x00)
    epd.line(0, 105, 128, 105, 0x00)
    epd.text("IP:"+a_ip, 5, 115, 0x00)
    epd.text("Model:", 5, 125, 0x00)
    epd.text(a_name.split(" ")[0], 5, 135, 0x00)
    epd.text(a_name.split(" ")[1], 5, 145, 0x00)
    epd.text("Version:"+a_ver, 5, 155, 0x00)
    epd.text("GPS:"+a_gps, 5, 165, 0x00)
    epd.text("Sat-Fix:"+a_sat, 5, 175, 0x00)
    epd.line(0, 275, 128, 275, 0x00)
    epd.text(time+"-"+date, 10, 285, 0x00)
    epd.display(epd.buffer)
    epd.delay_ms(10000)

#ini
led.low()
epd = EPD_2in9()
epd.init()
clear_page()    
page_1()
wifi_connection = netman.connectWiFi(wlanSSID,wlanPW,country)
page_2()
    
# program
while True:
    led.high()
    aDict = json.loads(findJson(http_get(time_server)))
    date = aDict['datetime'].split("T")[0].split("20")[1].replace("-", ".")
    time = aDict['datetime'].split("T")[1].split(".")[0].split(":")[0]+":"+aDict['datetime'].split("T")[1].split(".")[0].split(":")[1]
    client = netman.mqttConnect(mqttClient, mqttBroker, mqttUser, mqttPW)
    if client == None:
        machine.reset()
    client.set_callback(sub_cb)
    mqtt_subscribe([con_w_temp, con_w_hum, con_e_temp, con_e_hum, con_p_temp, con_p_hum, con_o_temp, con_o_hum])
    mqtt_subscribe([con_power, con_voltage, con_total])
    mqtt_subscribe([con_p_1, con_p_2, con_p_3, con_e_1, con_e_2, con_e_3, con_r_1])
    mqtt_subscribe([pihole_block, pihole_queries, pihole_client, pihole_dns])
    mqtt_subscribe([con_a_ip, con_a_name, con_a_ver, con_a_gps, con_a_sat, con_p_shutdown])
    client.wait_msg()
    utime.sleep(1)
    client.publish(con_topic, wifi_connection[0],True)
    utime.sleep(1)
    led.low()
    if p_shutdown == "0":
        page_3(date, time)
        page_4(date, time)
        page_5(date, time)
    if p_shutdown == "1":
        print("shutdown")
        client.publish(con_p_shutdown, "0",True)
        utime.sleep(1)
        clear_page()
        break
    client.disconnect()