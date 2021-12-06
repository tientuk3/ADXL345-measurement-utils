#library functions for Analog Devices ADXL345 sensor
import time
import numpy as np
import pandas as pd
from gpiozero import InputDevice
import smbus2

bus = smbus2.SMBus(1)

REG_BW_RATE = 0x2c
REG_INT_MAP = 0x2f
REG_INT_ENABLE = 0x2e
REG_DATA_FORMAT = 0x31
REG_DATA = 0x32 # 6 bytes
REG_FIFO_CTL = 0x38

FREQ = 0b1011 # hardcoded to 200 Hz for now



class ADXL345:

    def __init__(self, id, address, direction, block_size):
        self.id = id
        self.address = address
        self.sample_data = []
        self.direction = direction
        self.block_size = block_size

    def readAxes(self):
        bytes = bus.read_i2c_block_data(self.address, REG_DATA, 4) #read 4 bytes or (x, y)
        value = 0

        if self.direction == 'x':    
            value = bytes[0] | (bytes[1] << 8)
            if(value & (1 << 16 - 1)):
                value = value - (1<<16)
        if self.direction == 'y':
            value = bytes[2] | (bytes[3] << 8)
            if(value & (1 << 16 - 1)):
                value = value - (1<<16)

        value = value * 0.004 * 9.80665
        return round(value, 4)

    def readFIFO(self): #read FIFO register
        temp_data = []

        for i in range(self.block_size):
            temp_data.append(self.readAxes())

        self.sample_data.append(temp_data)


    def configureDevice(self):
            
        print('Configuring device at address %s' % self.address)
        #set bandwidth
        bus.write_byte_data(self.address, REG_BW_RATE, FREQ) #write to bw_rate register: normal mode, 200 Hz
        read = bus.read_byte_data(self.address, REG_BW_RATE)
        if read == 0b1011:
            print('{0:b}'.format(read) + ' read from 0x2c (OK!)') #read reset status of data format register
        else: 
            print('{0:b}'.format(read) + ' read from 0x2c (FAIL!)') #read reset status of data format register

        #configure data format register
        bus.write_byte_data(self.address, REG_DATA_FORMAT, 0b0)
        read = bus.read_byte_data(self.address, REG_DATA_FORMAT)
        if read == 0b0:
            print('{0:b}'.format(read) + ' read from 0x31 (OK!)') #read reset status of data format register
        else: 
            print('{0:b}'.format(read) + ' read from 0x31 (FAIL!)') #read reset status of data format register

        #map interrupts
        bus.write_byte_data(self.address, REG_INT_MAP, 0x1) #map all interrupts to pin INT1
        read = bus.read_byte_data(self.address, REG_INT_MAP)
        if read == 0x1:
            print('{0:b}'.format(read) + ' read from 0x2f (OK!)') #read reset status of data format register
        else: 
            print('{0:b}'.format(read) + ' read from 0x2f (FAIL!)') #read reset status of data format register

        #configure FIFO
        bus.write_byte_data(self.address, REG_FIFO_CTL, (64 + self.block_size)) #write 0b01001111: FIFO mode, 10 samples until interrupt  
        read = bus.read_byte_data(self.address, REG_FIFO_CTL)
        if read == (0b1000000 + self.block_size):
            print('{0:b}'.format(read) + ' read from 0x38 (OK!)') #read reset status of data format register
        else: 
            print('{0:b}'.format(read) + ' read from 0x38 (FAIL!)') #read reset status of data format register

        #enable interrupts
        bus.write_byte_data(self.address, REG_INT_ENABLE, 0x3) #enable watermark interrupt only
        read = bus.read_byte_data(self.address, REG_INT_ENABLE)
        if read == 0b11:
            print('{0:b}'.format(read) + ' read from 0x2e (OK!)') #read reset status of data format register
        else: 
            print('{0:b}'.format(read) + ' read from 0x2e (FAIL!)') #read reset status of data format register

        #set measurement mode in POWER_CTL
        bus.write_byte_data(self.address, 0x2d, 0x08) #write 0b1000: default measurement mode