#import shit we need
import time
import numpy as np
import pandas as pd
from gpiozero import InputDevice
import smbus2

bus = smbus2.SMBus(1)

#variables (user-configurable)
aika = 100 #desired measurement time in seconds
debugmode = False #set true to monitor FIFO overrun interrupt on GPIO27
block_size = 15 #samples read from FIFO once watermark interrupt occurs, max 31 or (0b11111)
devices = [0x53, 0x1d]

#GPIO configuration
interrupt_1 = InputDevice(17, pull_up=False) #INT1 of sensor 1 wired to GPIO17; pulled low by default
interrupt_2 = InputDevice(14, pull_up=False) #INT1 of sensor 2 wired to GPIO14
print('GPIO17 set to receive FIFO watermark interrupt from sensor 1')
print('GPIO14 set to receive FIFO watermark interrupt from sensor 2')

#DEBUG
if debugmode:
    int_overrun = InputDevice(27, pull_up=False) #INT2 wired to GPIO27
    print('DEBUG MODE: GPIO27 set to receive FIFO overrun interrupt from sensor 1')

def configureDevice(devices):
    for device_address in devices: # device = i2c bus address
        
        print('Configuring device at address %s' % device_address)
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

def getAxes(address):
    bytes = bus.read_i2c_block_data(address, 0x32, 4) #read 4 bytes or (x, y)
        
    x = bytes[0] | (bytes[1] << 8)
    if(x & (1 << 16 - 1)):
        x = x - (1<<16)

    y = bytes[2] | (bytes[3] << 8)
    if(y & (1 << 16 - 1)):
        y = y - (1<<16)

    x = x * 0.004 
    y = y * 0.004

    x = x * 9.80665
    y = y * 9.80665

    x = round(x, 4)
    y = round(y, 4)

    return np.hypot(x, y)

def readFIFO(address): #read FIFO register
    temp_data = []

    for i in range(block_size):
        temp_data.append(getAxes(address))
        time.sleep(0.0005)

    return temp_data

    
sample_data_1 = []
sample_data_2 = []
samples = 0
flag = True

configureDevice(devices)

print('---------------')
alku = time.time()

while samples < (aika*200): #run for set time

    #THIS IS FOR DEBUG PURPOSES ONLY: read FIFO buffer duty from sensor 1
    if ((samples*0.01) % 10) == 0 and flag and samples > 1:
        n = bus.read_byte_data(devices[0], 0x39)
        n = n & 0b111111
        print('DEBUG INFO from sensor 1:')
        print('%d samples done, %d in FIFO buffer' % (samples, n))
        print('%.2f seconds elapsed' % (time.time()-alku))
        flag = False

    #sensor 1
    if interrupt_1.is_active: #run when an interrupt occurs
        if debugmode and int_overrun.is_active and samples > 1:
            print('FIFO overrun!!')
        data = readFIFO(0x53) #when interrupt occurs, read 10 samples from FIFO to a list
        sample_data_1.extend(data) #append to result list
        flag = True
        samples += block_size
    
    #sensor 2
    if interrupt_2.is_active: #run when an interrupt occurs
        data = readFIFO(0x1d) #when interrupt occurs, read 10 samples from FIFO to a list
        sample_data_2.extend(data) #append to result list

elapsed_time = (time.time()-alku)
title = ['1: resultantti m/s2', '2: resultantti m/s2']
filename = '/media/usb/result_' + time.strftime('%Y%m%d-%H%M%S') + '.csv'

#pandas magic
f = pd.DataFrame(columns=title, data=zip(sample_data_1, sample_data_2))
f.to_csv(filename, mode='a', float_format='%.3f', header=False, index=0)
    
print('Written %d samples to %s in %.2f seconds' % (samples, filename[11:], (elapsed_time)))




