import machine

sensor_temp = machine.ADC(4)
conversion_factor = 3.3 / (65535)
temp_adjust = 12

def intern_temp():
    temp = 0
    reading = sensor_temp.read_u16() * conversion_factor
    temp = temp_adjust - (reading - 0.706)/0.001721
    temp = int(temp*10 +0.5)/10
    return str(temp)