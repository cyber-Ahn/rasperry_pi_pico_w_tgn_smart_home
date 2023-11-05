__version__ = '0.1.4'
_MCP_IODIR        = const(0x00)
_MCP_IPOL         = const(0x01)
_MCP_GPINTEN      = const(0x02)
_MCP_DEFVAL       = const(0x03)
_MCP_INTCON       = const(0x04)
_MCP_IOCON        = const(0x05)
_MCP_GPPU         = const(0x06)
_MCP_INTF         = const(0x07)
_MCP_INTCAP       = const(0x08)
_MCP_GPIO         = const(0x09)
_MCP_OLAT         = const(0x0a)

_MCP_IOCON_INTPOL = const(2)
_MCP_IOCON_ODR    = const(4)

_MCP_IOCON_DISSLW = const(16)
_MCP_IOCON_SEQOP  = const(32)
_MCP_IOCON_MIRROR = const(64)
_MCP_IOCON_BANK   = const(128)


class Port():
    def __init__(self, port, mcp):
        self._port = port & 1
        self._mcp = mcp

    def _which_reg(self, reg):
        if self._mcp._config & 0x80 == 0x80:
            return reg | (self._port << 4)
        else:
            return (reg << 1) + self._port

    def _flip_property_bit(self, reg, condition, bit):
        if condition:
            setattr(self, reg, getattr(self, reg) | bit)
        else:
            setattr(self, reg, getattr(self, reg) & ~bit)

    def _read(self, reg):
        return self._mcp._i2c.readfrom_mem(self._mcp._address, self._which_reg(reg), 1)[0]

    def _write(self, reg, val):
        val &= 0xff
        self._mcp._i2c.writeto_mem(self._mcp._address, self._which_reg(reg), bytearray([val]))
        if reg == _MCP_IOCON:
            self._mcp._config = val

    @property
    def mode(self):
        return self._read(_MCP_IODIR)
    @mode.setter
    def mode(self, val):
        self._write(_MCP_IODIR, val)

    @property
    def input_polarity(self):
        return self._read(_MCP_IPOL)
    @input_polarity.setter
    def input_polarity(self, val):
        self._write(_MCP_IPOL, val)

    @property
    def interrupt_enable(self):
        return self._read(_MCP_GPINTEN)
    @interrupt_enable.setter
    def interrupt_enable(self, val):
        self._write(_MCP_GPINTEN, val)

    @property
    def default_value(self):
        return self._read(_MCP_DEFVAL)
    @default_value.setter
    def default_value(self, val):
        self._write(_MCP_DEFVAL, val)

    @property
    def interrupt_compare_default(self):
        return self._read(_MCP_INTCON)
    @interrupt_compare_default.setter
    def interrupt_compare_default(self, val):
        self._write(_MCP_INTCON, val)

    @property
    def io_config(self):
        return self._read(_MCP_IOCON)
    @io_config.setter
    def io_config(self, val):
        self._write(_MCP_IOCON, val)

    @property
    def pullup(self):
        return self._read(_MCP_GPPU)
    @pullup.setter
    def pullup(self, val):
        self._write(_MCP_GPPU, val)

    @property
    def interrupt_flag(self):
        return self._read(_MCP_INTF)

    @property
    def interrupt_captured(self):
        return self._read(_MCP_INTCAP)

    @property
    def gpio(self):
        return self._read(_MCP_GPIO)
    @gpio.setter
    def gpio(self, val):
        self._write(_MCP_GPIO, val)

    @property
    def output_latch(self):
        return self._read(_MCP_OLAT)
    @output_latch.setter
    def output_latch(self, val):
        self._write(_MCP_OLAT, val)

class MCP23017():
    def __init__(self, i2c, address=0x20):
        self._i2c = i2c
        self._address = address
        self._config = 0x00
        self._virtual_pins = {}
        self.init()

    def init(self):
        if self._i2c.scan().count(self._address) == 0:
            raise OSError('MCP23017 not found at I2C address {:#x}'.format(self._address))
        self.porta = Port(0, self)
        self.portb = Port(1, self)
        self.io_config = 0x00
        self.mode = 0xFFFF
        self.input_polarity = 0x0000
        self.interrupt_enable = 0x0000
        self.default_value = 0x0000
        self.interrupt_compare_default = 0x0000
        self.pullup = 0x0000
        self.gpio = 0x0000

    def config(self, interrupt_polarity=None, interrupt_open_drain=None, sda_slew=None, sequential_operation=None, interrupt_mirror=None, bank=None):
        io_config = self.porta.io_config
        if interrupt_polarity is not None:
            io_config = self._flip_bit(io_config, interrupt_polarity, _MCP_IOCON_INTPOL)
            if interrupt_polarity:
                interrupt_open_drain = False
        if interrupt_open_drain is not None:
            io_config = self._flip_bit(io_config, interrupt_open_drain, _MCP_IOCON_ODR)
        if sda_slew is not None:
            io_config = self._flip_bit(io_config, sda_slew, _MCP_IOCON_DISSLW)
        if sequential_operation is not None:
            io_config = self._flip_bit(io_config, sequential_operation, _MCP_IOCON_SEQOP)
        if interrupt_mirror is not None:
            io_config = self._flip_bit(io_config, interrupt_mirror, _MCP_IOCON_MIRROR)
        if bank is not None:
            io_config = self._flip_bit(io_config, bank, _MCP_IOCON_BANK)
        self.porta.io_config = io_config
        self._config = io_config

    def _flip_bit(self, value, condition, bit):
        if condition:
            value |= bit
        else:
            value &= ~bit
        return value

    def pin(self, pin, mode=None, value=None, pullup=None, polarity=None, interrupt_enable=None, interrupt_compare_default=None, default_value=None):
        assert 0 <= pin <= 15
        port = self.portb if pin // 8 else self.porta
        bit = (1 << (pin % 8))
        if mode is not None:
            port._flip_property_bit('mode', mode & 1, bit)
        if value is not None:
            port._flip_property_bit('gpio', value & 1, bit)
        if pullup is not None:
            port._flip_property_bit('pullup', pullup & 1, bit)
        if polarity is not None:
            port._flip_property_bit('input_polarity', polarity & 1, bit)
        if interrupt_enable is not None:
            port._flip_property_bit('interrupt_enable', interrupt_enable & 1, bit)
        if interrupt_compare_default is not None:
            port._flip_property_bit('interrupt_compare_default', interrupt_compare_default & 1, bit)
        if default_value is not None:
            port._flip_property_bit('default_value', default_value & 1, bit)
        if value is None:
            return port.gpio & bit == bit

    def interrupt_triggered_gpio(self, port):
        port = self.portb if port else self.porta
        return port.interrupt_flag

    def interrupt_captured_gpio(self, port):
        port = self.portb if port else self.porta
        return port.interrupt_captured
    @property
    def mode(self):
        return self.porta.mode | (self.portb.mode << 8)
    @mode.setter
    def mode(self, val):
        self.porta.mode = val
        self.portb.mode = (val >> 8)
    @property
    def input_polarity(self):
        return self.porta.input_polarity | (self.portb.input_polarity << 8)
    @input_polarity.setter
    def input_polarity(self, val):
        self.porta.input_polarity = val
        self.portb.input_polarity = (val >> 8)
    @property
    def interrupt_enable(self):
        return self.porta.interrupt_enable | (self.portb.interrupt_enable << 8)
    @interrupt_enable.setter
    def interrupt_enable(self, val):
        self.porta.interrupt_enable = val
        self.portb.interrupt_enable = (val >> 8)
    @property
    def default_value(self):
        return self.porta.default_value | (self.portb.default_value << 8)
    @default_value.setter
    def default_value(self, val):
        self.porta.default_value = val
        self.portb.default_value = (val >> 8)
    @property
    def interrupt_compare_default(self):
        return self.porta.interrupt_compare_default | (self.portb.interrupt_compare_default << 8)
    @interrupt_compare_default.setter
    def interrupt_compare_default(self, val):
        self.porta.interrupt_compare_default = val
        self.portb.interrupt_compare_default = (val >> 8)
    @property
    def io_config(self):
        return self.porta.io_config
    @io_config.setter
    def io_config(self, val):
        self.porta.io_config = val
    @property
    def pullup(self):
        return self.porta.pullup | (self.portb.pullup << 8)
    @pullup.setter
    def pullup(self, val):
        self.porta.pullup = val
        self.portb.pullup = (val >> 8)
    @property
    def interrupt_flag(self):
        return self.porta.interrupt_flag | (self.portb.interrupt_flag << 8)
    @property
    def interrupt_captured(self):
        return self.porta.interrupt_captured | (self.portb.interrupt_captured << 8)
    @property
    def gpio(self):
        return self.porta.gpio | (self.portb.gpio << 8)
    @gpio.setter
    def gpio(self, val):
        self.porta.gpio = val
        self.portb.gpio = (val >> 8)
    @property
    def output_latch(self):
        return self.porta.output_latch | (self.portb.output_latch << 8)
    @output_latch.setter
    def output_latch(self, val):
        self.porta.output_latch = val
        self.portb.output_latch = (val >> 8)
    def __getitem__(self, pin):
        assert 0 <= pin <= 15
        if not pin in self._virtual_pins:
            self._virtual_pins[pin] = VirtualPin(pin, self.portb if pin // 8 else self.porta)
        return self._virtual_pins[pin]

class VirtualPin():
    def __init__(self, pin, port):
        self._pin = pin % 8
        self._bit = 1 << self._pin
        self._port = port
    def __call__(self):
        return self.value()

    def _flip_bit(self, value, condition):
        return value | self._bit if condition else value & ~self._bit

    def _get_bit(self, value):
        return (value & self._bit) >> self._pin

    def value(self, val=None):
        if val is not None:
            self._port.gpio = self._flip_bit(self._port.gpio, val & 1)
        else:
            return self._get_bit(self._port.gpio)

    def input(self, pull=None):
        self._port.mode = self._flip_bit(self._port.mode, 1)
        if pull is not None:
            self._port.pullup = self._flip_bit(self._port.pullup, pull & 1)

    def output(self, val=None):
        self._port.mode = self._flip_bit(self._port.mode, 0)
        if val is not None:
            self._port.gpio = self._flip_bit(self._port.gpio, val & 1)
