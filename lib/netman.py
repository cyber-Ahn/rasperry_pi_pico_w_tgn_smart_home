import network, rp2
import time
import machine
from umqttsimple import MQTTClient

sensor_temp = machine.ADC(4)
conversion_factor = 3.3 / (65535)
temp_adjust = 12

def intern_temp():
    temp = 0
    reading = sensor_temp.read_u16() * conversion_factor
    temp = temp_adjust - (reading - 0.706)/0.001721
    temp = int(temp*10 +0.5)/10
    return str(temp)

def connectWiFi(ssid,password,country):
   rp2.country(country)
   wlan = network.WLAN(network.STA_IF)
   wlan.config(pm = 0xa11140)
   wlan.active(True)
   wlan.connect(ssid, password)
   max_wait = 30
   while max_wait > 0:
      if wlan.status() < 0 or wlan.status() >= 3:
        break
      max_wait -= 1
      print('waiting for connection...')
      time.sleep(1)
   if wlan.status() != 3:
      raise RuntimeError('network connection failed')
   else:
      print('WIFI connected')
      status = wlan.ifconfig()
      print( 'ip = ' + status[0] )
   return status

def mqttConnect(mqttClient_s, mqttBroker_s, mqttUser_s, mqttPW_s):
    max_wait = 10
    while max_wait > 0:
        try:
            if mqttUser_s != '' and mqttPW_s != '':
                print("Establish MQTT connection: %s with %s as %s" % (mqttClient_s, mqttBroker_s, mqttUser_s))
                client = MQTTClient(mqttClient_s, mqttBroker_s, user=mqttUser_s, password=mqttPW_s)
            else:
                print("Establish MQTT connection: %s with %s" % (mqttClient_s, mqttBroker_s))
                client = MQTTClient(mqttClient_s, mqttBroker_s)
            client.connect()
            return client
        except OSError:
            max_wait -= 1
            print('Error: No MQTT connection')
            time.sleep(1)
    else:
        print("Reboot")
        time.sleep(60)