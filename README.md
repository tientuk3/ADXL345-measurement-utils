Utilities to handle communication between Analog Devices ADXL345 sensor and RaspBerry Pi (4 in this case). 

Contains functions to utilize the ADXL345's built-in 32-level FIFO register. This way the measurement sampling can be done on the sensor chip itself (based on the bus clock signal), and only read in bulk eg. for every 20 samples. This reduces the host processor load and allows sampling rates to only be limited by the I2C bus speed.
