#import shit we need
import time
import numpy as np
import pandas as pd
from gpiozero import InputDevice
import smbus2
import sys

from ADXL345_utils import ADXL345

bus = smbus2.SMBus(1)

#variables (user-configurable)
debugmode = False #set true to monitor FIFO overrun interrupt on GPIO27
block_size = 15 #samples read from FIFO once watermark interrupt occurs, max 31 or (0b11111)
devices = [0x53, 0x1d]

#variables (sys args)
aika = int(sys.argv[1]) #desired measurement time in seconds from command line argument

#DEBUG
if debugmode:
    int_overrun = InputDevice(27, pull_up=False) #INT2 wired to GPIO27
    print('DEBUG MODE: GPIO27 set to receive FIFO overrun interrupt from sensor 1')

sample_data_1 = []
sample_data_2 = []
samples = 0
block_size = 15
flag = True

#sensor configuration
sensor_1 = ADXL345(1, devices[0], 'x', block_size)
sensor_2 = ADXL345(2, devices[1], 'y', block_size)
sensor_1.configureDevice()
sensor_2.configureDevice()

#GPIO configuration
interrupt_1 = InputDevice(17, pull_up=False) #INT1 of sensor 1 wired to GPIO17; pulled low by default
interrupt_2 = InputDevice(14, pull_up=False) #INT1 of sensor 2 wired to GPIO14
print('GPIO17 set to receive FIFO watermark interrupt from sensor 1')
print('GPIO14 set to receive FIFO watermark interrupt from sensor 2')

print('---------------')
alku = time.time()

while samples < (aika*200): #run for set time

    #THIS IS FOR DEBUG PURPOSES ONLY: read FIFO buffer duty from sensor 1
    #if ((samples*0.01) % 10) == 0 and flag and samples > 1:
    #    n = bus.read_byte_data(devices[0], 0x39)
    #    n = n & 0b111111
    #    print('DEBUG INFO from sensor 1:')
    #    print('%d samples done, %d in FIFO buffer' % (samples, n))
    #    print('%.2f seconds elapsed' % (time.time()-alku))
    #    flag = False

    #sensor 1
    if interrupt_1.is_active: #run when an interrupt occurs
        if debugmode and int_overrun.is_active and samples > 1:
            print('FIFO overrun!!')
        sensor_1.readFIFO() #when interrupt occurs, read predetermined qty of samples from FIFO
        flag = True
        samples += block_size
    
    #sensor 2
    if interrupt_2.is_active: #run when an interrupt occurs
        sensor_2.readFIFO() #when interrupt occurs, read predetermined qty of samples from FIFO

elapsed_time = (time.time()-alku)
title = ['1: resultantti m/s2', '2: resultantti m/s2']
filename = 'result_' + time.strftime('%Y%m%d-%H%M%S') + '.csv'

#pandas magic
f = pd.DataFrame(columns=title, data=zip(sensor_1.sample_data, sensor_2.sample_data))
f.to_csv(filename, mode='a', float_format='%.3f', header=False, index=0)
    
print('Written %d samples to %s in %.2f seconds' % (samples, filename[11:], (elapsed_time)))




