#
# Based on MicroPython LIS2HH12 driver
# Copyright (c) 2017-2018 Mika Tuupola
#
# Licensed under the MIT license:
#   http://www.opensource.org/licenses/mit-license.php
#
# Project home:
#   https://github.com/tuupola/micropython-lis2hh12
#

"""
.. module:: lis2hh12

***************
LIS2HH12 Module
***************

This module contains the driver for STMicroelectronics LIS2HH12 3-axis accelerometer.
    """

import struct
import spi

_TEMP_L = 0x0b
_TEMP_H = 0x0c
_WHO_AM_I = 0x0f # 0b01000001 = 0x41
_CTRL1 = 0x20
_CTRL2 = 0x21
_CTRL3 = 0x22
_CTRL4 = 0x23
_CTRL5 = 0x24
_CTRL6 = 0x25
_CTRL7 = 0x26
_OUT_X_L = 0x28
_OUT_X_H = 0x29
_OUT_Y_L = 0x2a
_OUT_Y_H = 0x2b
_OUT_Z_L = 0x2c
_OUT_Z_H = 0x2d

# CTRL1
_ODR_MASK = 0b01110000
ODR_OFF = 0b00000000
ODR_10HZ  = 0b00010000
ODR_50HZ  = 0b00100000
ODR_100HZ = 0b00110000
ODR_200HZ = 0b01000000
ODR_400HZ = 0b01010000
ODR_800HZ = 0b01100000

# CTRL4
_FS_MASK = 0b00110000
FS_2G = 0b00000000
FS_4G = 0b00100000
FS_8G = 0b00110000

_SO_2G = 0.061 # 0.061 mg / digit
_SO_4G = 0.122 # 0.122 mg / digit
_SO_8G = 0.244 # 0.244 mg / digit

SF_G = 0.001 # 1 mg = 0.001 g
SF_SI = 0.00980665 # 1 mg = 0.00980665 m/s2


@c_native("_lis2hh12_read_reg8",["csrc/lis2hh12.c"])
def _lis2hh12_read_reg8(spi,reg):
    pass

@c_native("_lis2hh12_read_reg16",["csrc/lis2hh12.c"])
def _lis2hh12_read_reg16(spi,reg):
    pass

@c_native("_lis2hh12_read_reg16x3",["csrc/lis2hh12.c"])
def _lis2hh12_read_reg16x3(spi,reg):
    pass

@c_native("_lis2hh12_write_reg8",["csrc/lis2hh12.c"])
def _lis2hh12_write_reg8(spi,reg,value):
    pass

@c_native("_lis2hh12_write_reg16",["csrc/lis2hh12.c"])
def _lis2hh12_write_reg16(spi,reg,value):
    pass

class LIS2HH12(spi.Spi):
    """
.. class:: LIS2HH12

    Class which provides a simple interface to LIS2HH12 features.
    """

    def __init__(self, spidrv, pin_cs, clk=5000000, odr=ODR_100HZ, fs=FS_2G, sf=SF_SI):
        """
.. method:: __init__(spidrv, pin_cs, clk=5000000, odr=ODR_100HZ, fs=FS_2G, sf=SF_SI)

        Creates an instance of LIS2HH12 class, using the specified SPI settings
        and initial device configuration.

        :param spidrv: the *SPI* driver to use (SPI0, ...)
        :param pin_cs: Chip select pin to access the NCV7240 chip
        :param clk: Clock speed, default 5 MHz
        :param odr: Device output data rate, default 100 Hz
        :param fs: Device full-scale setting, default +/-2g
        :param sf: Scaling factor, one of ``SF_G`` (unit=g) or ``SF_SI`` (unit=m/s^2 default)
        """
        spi.Spi.__init__(self,pin_cs,spidrv,clock=clk)
        # for native functions
        self.spi = spidrv & 0xFF

        #print(self.whoami())
        if 0x41 != self.whoami():
            raise RuntimeError #("LIS2HH12 not detected")

        self._register_char(_CTRL5, 0x43)
        sleep(100)
        self._register_char(_CTRL4, 0x06)
        self._register_char(_CTRL2, 0x40)
        self._register_char(_CTRL1, 0xBF)
        
        self._sf = sf
        self._odr(odr)
        self._fs(fs)

    def acceleration(self):
        """
.. method:: acceleration()

        Acceleration measured by the sensor.

        :returns: By default will return a 3-tuple of X, Y, Z axis acceleration \
        values in **m/s^2**. Will return values in **g** if constructor was provided \
        :samp:`sf=SF_G` parameter.
        """
        f = self._so * self._sf

        # x = self._register_word(_OUT_X_L) * f
        # y = self._register_word(_OUT_Y_L) * f
        # z = self._register_word(_OUT_Z_L) * f
        # return (x,y,z)

        self.lock()
        self.select()
        ex = None
        ret = None
        try:
            ret = _lis2hh12_read_reg16x3(self.spi, _OUT_X_L)
            ret = (ret[0] * f, ret[1] * f, ret[2] * f)
            # (x,y,z) = _lis2hh12_read_reg16x3(self.spi, _OUT_X_L)
            # ret = (x * f, y * f, z * f)
        except Exception as e:
            ex = e
        self.unselect()
        self.unlock()
        if ex is not None:
            raise ex
        return ret

    def temperature(self):
        """
.. method:: temperature()

        Temperature measured by the sensor.
        
        :returns: Die temperature in Celsius degrees.
        """
        t = self._register_word(_TEMP_L) / 256.0 + 25.0
        return t

    def whoami(self):
        """
.. method:: whoami()

        Value of the *WHO_AM_I* register (0x41).
        """
        return self._register_char(_WHO_AM_I)

    def _register_word(self, register, value=None):
        self.lock()
        self.select()
        ex = None
        ret = None
        try:
            if value is None:
                ret = _lis2hh12_read_reg16(self.spi, register)
            else:
                ret = _lis2hh12_write_reg16(self.spi, register, value)
        except Exception as e:
            ex = e
        self.unselect()
        self.unlock()
        if ex is not None:
            raise ex
        return ret

    def _register_char(self, register, value=None):
        self.lock()
        self.select()
        ex = None
        ret = None
        try:
            if value is None:
                ret = _lis2hh12_read_reg8(self.spi, register)
            else:
                ret = _lis2hh12_write_reg8(self.spi, register, value)
        except Exception as e:
            ex = e
        self.unselect()
        self.unlock()
        if ex is not None:
            raise ex
        return ret

    def _fs(self, value):
        char = self._register_char(_CTRL4)
        char &= ~_FS_MASK # clear FS bits
        char |= value
        self._register_char(_CTRL4, char)

        # Store the sensitivity multiplier
        if FS_2G == value:
            self._so = _SO_2G
        elif FS_4G == value:
            self._so = _SO_4G
        elif FS_8G == value:
            self._so = _SO_8G

    def _odr(self, value):
        char = self._register_char(_CTRL1)
        char &= ~_ODR_MASK # clear ODR bits
        char |= value
        self._register_char(_CTRL1, char)
