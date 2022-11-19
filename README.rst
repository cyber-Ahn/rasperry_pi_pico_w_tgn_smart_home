# rasperry_pi_pico_w_tgn_smart_home

pico_1:

send Sensor data to Mqtt Brocker

Read DHT22,light sensor(analog), publish data to MQTT-Brocker


pico_2:

red data from mqtt for RGB Light WS2812b

pico_sonoff_firmware:

simulated a sonoff modul

pico_rfid_SmartHome-On-Off-KasaHS100:

switch SmartHome ON-OFF with Kasa HS100 and RFID-Card by cheking MQTT Status from Smart Home

---------------------

usde MicroPython Libs:

base64.py

mfrc522.py

neopixel.py

netman.py

temp_intern.py

umqttsimple.py
