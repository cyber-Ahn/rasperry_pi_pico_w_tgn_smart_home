import array, time
from machine import Pin
import rp2

@rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW, out_shiftdir=rp2.PIO.SHIFT_LEFT, autopull=True, pull_thresh=24)
def ws2812():
    T1 = 2
    T2 = 5
    T3 = 3
    wrap_target()
    label("bitloop")
    out(x, 1)               .side(0)    [T3 - 1]
    jmp(not_x, "do_zero")   .side(1)    [T1 - 1]
    jmp("bitloop")          .side(1)    [T2 - 1]
    label("do_zero")
    nop()                   .side(0)    [T2 - 1]
    wrap()

@rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW, out_shiftdir=rp2.PIO.SHIFT_LEFT, autopull=True, pull_thresh=32)
def sk6812():
    T1 = 2
    T2 = 5
    T3 = 3
    wrap_target()
    label("bitloop")
    out(x, 1)               .side(0)    [T3 - 1]
    jmp(not_x, "do_zero")   .side(1)    [T1 - 1]
    jmp("bitloop")          .side(1)    [T2 - 1]
    label("do_zero")
    nop()                   .side(0)    [T2 - 1]
    wrap()

class slice_maker_class:
    def __getitem__(self, slc):
        return slc

slice_maker = slice_maker_class()

class Neopixel:
    def __init__(self, num_leds, state_machine, pin, mode="RGB", delay=0.0001):
        self.pixels = array.array("I", [0] * num_leds)
        self.mode = mode
        self.W_in_mode = 'W' in mode
        if self.W_in_mode:
            self.sm = rp2.StateMachine(state_machine, sk6812, freq=8000000, sideset_base=Pin(pin))
            self.shift = ((mode.index('R') ^ 3) * 8, (mode.index('G') ^ 3) * 8,
                          (mode.index('B') ^ 3) * 8, (mode.index('W') ^ 3) * 8)
        else:
            self.sm = rp2.StateMachine(state_machine, ws2812, freq=8000000, sideset_base=Pin(pin))
            self.shift = (((mode.index('R') ^ 3) - 1) * 8, ((mode.index('G') ^ 3) - 1) * 8,
                          ((mode.index('B') ^ 3) - 1) * 8, 0)
        self.sm.active(1)
        self.num_leds = num_leds
        self.delay = delay
        self.brightnessvalue = 255

    def brightness(self, brightness=None):
        if brightness is None:
            return self.brightnessvalue
        else:
            if brightness < 1:
                brightness = 1
        if brightness > 255:
            brightness = 255
        self.brightnessvalue = brightness

    def set_pixel_line_gradient(self, pixel1, pixel2, left_rgb_w, right_rgb_w, how_bright=None):
        if pixel2 - pixel1 == 0:
            return
        right_pixel = max(pixel1, pixel2)
        left_pixel = min(pixel1, pixel2)
        with_W = len(left_rgb_w) == 4 and self.W_in_mode
        r_diff = right_rgb_w[0] - left_rgb_w[0]
        g_diff = right_rgb_w[1] - left_rgb_w[1]
        b_diff = right_rgb_w[2] - left_rgb_w[2]
        if with_W:
            w_diff = (right_rgb_w[3] - left_rgb_w[3])
        for i in range(right_pixel - left_pixel + 1):
            fraction = i / (right_pixel - left_pixel)
            red = round(r_diff * fraction + left_rgb_w[0])
            green = round(g_diff * fraction + left_rgb_w[1])
            blue = round(b_diff * fraction + left_rgb_w[2])
            if with_W:
                white = round(w_diff * fraction + left_rgb_w[3])
                self.set_pixel(left_pixel + i, (red, green, blue, white), how_bright)
            else:
                self.set_pixel(left_pixel + i, (red, green, blue), how_bright)

    def set_pixel_line(self, pixel1, pixel2, rgb_w, how_bright=None):
        if pixel2 >= pixel1:
            self.set_pixel(slice_maker[pixel1:pixel2 + 1], rgb_w, how_bright)

    def set_pixel(self, pixel_num, rgb_w, how_bright=None):
        if how_bright is None:
            how_bright = self.brightness()
        sh_R, sh_G, sh_B, sh_W = self.shift
        bratio = how_bright / 255.0

        red = round(rgb_w[0] * bratio)
        green = round(rgb_w[1] * bratio)
        blue = round(rgb_w[2] * bratio)
        white = 0
        if len(rgb_w) == 4 and self.W_in_mode:
            white = round(rgb_w[3] * bratio)

        pix_value = white << sh_W | blue << sh_B | red << sh_R | green << sh_G
        if type(pixel_num) is slice:
            for i in range(*pixel_num.indices(self.num_leds)):
                self.pixels[i] = pix_value
        else:
            self.pixels[pixel_num] = pix_value

    def __setitem__(self, idx, rgb_w):
        self.set_pixel(idx, rgb_w)

    def colorHSV(self, hue, sat, val):
        if hue >= 65536:
            hue %= 65536

        hue = (hue * 1530 + 32768) // 65536
        if hue < 510:
            b = 0
            if hue < 255:
                r = 255
                g = hue
            else:
                r = 510 - hue
                g = 255
        elif hue < 1020:
            r = 0
            if hue < 765:
                g = 255
                b = hue - 510
            else:
                g = 1020 - hue
                b = 255
        elif hue < 1530:
            g = 0
            if hue < 1275:
                r = hue - 1020
                b = 255
            else:
                r = 255
                b = 1530 - hue
        else:
            r = 255
            g = 0
            b = 0
        v1 = 1 + val
        s1 = 1 + sat
        s2 = 255 - sat
        r = ((((r * s1) >> 8) + s2) * v1) >> 8
        g = ((((g * s1) >> 8) + s2) * v1) >> 8
        b = ((((b * s1) >> 8) + s2) * v1) >> 8
        return r, g, b

    def rotate_left(self, num_of_pixels=None):
        if num_of_pixels is None:
            num_of_pixels = 1
        self.pixels = self.pixels[num_of_pixels:] + self.pixels[:num_of_pixels]

    def rotate_right(self, num_of_pixels=None):
        if num_of_pixels is None:
            num_of_pixels = 1
        num_of_pixels = -1 * num_of_pixels
        self.pixels = self.pixels[num_of_pixels:] + self.pixels[:num_of_pixels]

    def show(self):
        cut = 8
        if self.W_in_mode:
            cut = 0
        sm_put = self.sm.put
        for pixval in self.pixels:
            sm_put(pixval, cut)
        time.sleep(self.delay)

    def fill(self, rgb_w, how_bright=None):
        self.set_pixel(slice_maker[:], rgb_w, how_bright)

    def clear(self):
        self.pixels = array.array("I", [0] * self.num_leds)