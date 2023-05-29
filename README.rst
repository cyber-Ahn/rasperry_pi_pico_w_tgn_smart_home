rasperry_pi_pico_w_tgn_smart_home
---------------------

|Build Status|  |Python versions|

pico_1:

send Sensor data to Mqtt Brocker

Read DHT22,light sensor(analog), publish data to MQTT-Brocker


pico_2:

red data from mqtt for RGB Light WS2812b


pico_3:

red data from mqtt and set to E-Paper Display


pico_sonoff_firmware:

simulated a sonoff modul


pico_rfid_SmartHome-On-Off-KasaHS100:

switch SmartHome ON-OFF with Kasa HS100 and RFID-Card by cheking MQTT Status from Smart Home

Update:
add web request for reset machine
(example: 192.166.0.5/reset)

---------------------

used MicroPython Libs:

base64.py

mfrc522.py

neopixel.py

netman.py

EPD_2in9.py

umqttsimple.py


.. ..

.. |Build Status| image:: https://caworks-sl.de/images/build.png
   :target: https://caworks-sl.de
.. |Python versions| image:: https://caworks-sl.de/images/mpython.png
   :target: https://caworks-sl.de
