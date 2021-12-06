Utilities to handle communication between Analog Devices ADXL345 sensor and RaspBerry Pi (4 in this case). 

Since Raspbian is a non-real-time OS, it can't really handle sensors accurately or reliably in significant frequencies (say, over 100 Hz). This is true especially when the timing of the samples is cricital, such as when doing Fourier transform or other time derivative operations on the data. This code utilizes the built-in FIFO register of the sensor, to try to more accurately gather data (only limiting factor being I2C bus saturation).
