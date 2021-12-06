#library functions for Analog Devices ADXL345 sensor
import time
import numpy as np
import pandas as pd
from gpiozero import InputDevice
import smbus2

bus = smbus2.SMBus(1)

class ADXL345:
    def __init__(self, id, address):
        self.id = id
        self.address = address

def configureDevice(device):
        
    print('Configuring device at address %s' % device.address)
    #set bandwidth
    bus.write_byte_data(device_address, 0x2c, 0b1011) #write to bw_rate register: normal mode, 200 Hz
    read = bus.read_byte_data(device_address, 0x2c)
    if read == 0b1011:
        print('{0:b}'.format(read) + ' read from 0x2c (OK!)') #read reset status of data format register
    else: 
        print('{0:b}'.format(read) + ' read from 0x2c (FAIL!)') #read reset status of data format register

    #configure data format register
    bus.write_byte_data(device_address, 0x31, 0b0)
    read = bus.read_byte_data(device_address, 0x31)
    if read == 0b0:
        print('{0:b}'.format(read) + ' read from 0x31 (OK!)') #read reset status of data format register
    else: 
        print('{0:b}'.format(read) + ' read from 0x31 (FAIL!)') #read reset status of data format register

    #map interrupts
    bus.write_byte_data(device_address, 0x2f, 0x1) #map all interrupts to pin INT1
    read = bus.read_byte_data(device_address, 0x2f)
    if read == 0x1:
        print('{0:b}'.format(read) + ' read from 0x2f (OK!)') #read reset status of data format register
    else: 
        print('{0:b}'.format(read) + ' read from 0x2f (FAIL!)') #read reset status of data format register

    #configure FIFO
    bus.write_byte_data(device_address, 0x38, (64 + block_size)) #write 0b01001111: FIFO mode, 10 samples until interrupt  
    read = bus.read_byte_data(device_address, 0x38)
    if read == (0b1000000 + block_size):
        print('{0:b}'.format(read) + ' read from 0x38 (OK!)') #read reset status of data format register
    else: 
        print('{0:b}'.format(read) + ' read from 0x38 (FAIL!)') #read reset status of data format register

    #enable interrupts
    bus.write_byte_data(device_address, 0x2e, 0x3) #enable watermark interrupt only
    read = bus.read_byte_data(device_address, 0x2e)
    if read == 0b11:
        print('{0:b}'.format(read) + ' read from 0x2e (OK!)') #read reset status of data format register
    else: 
        print('{0:b}'.format(read) + ' read from 0x2e (FAIL!)') #read reset status of data format register

    #set measurement mode in POWER_CTL
    bus.write_byte_data(device_address, 0x2d, 0x08) #write 0b1000: default measurement mode