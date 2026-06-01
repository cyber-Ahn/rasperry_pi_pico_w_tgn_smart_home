from machine import ADC

class TmpSensor:
    def __init__(self, pin):
        self.tmp = ADC(pin)
        
    def ReadTmp36(self):
        adc_value = self.tmp.read_u16()
        volt = (3.3/65535)*adc_value
        degC = (100*volt)-50
        return round(degC, 2)
    
    def ReadLM35(self):
        adc_value = self.tmp.read_u16()
        volt = (3.3/65535)*adc_value
        degC = (100*volt)
        return round(degC, 2)
