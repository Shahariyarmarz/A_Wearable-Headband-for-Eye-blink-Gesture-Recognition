
void set_SD_card(void){

  pinMode(14, INPUT_PULLUP);	                      //manuell switch to enable SD CARD
  SPI.begin(SPI_SCK, SPI_MISO, SPI_MOSI, chipSelect);
  // ---------------------Initialize at the highest speed supported by the board that is not over 50 MHz. We have to try a lower speed if SPI errors occur---------------------
  if (!sd.begin(chipSelect, SD_SCK_MHZ(50))) {
    sd.initErrorHalt();
  }
  // ----------------------------------------------Find an unused file name-------------------------------------------------------------
  if (BASE_NAME_SIZE > 10) {
    error("FILE_BASE_NAME too long");
  }
  while (sd.exists(fileName)) {
    if (fileName[BASE_NAME_SIZE + 1] != '9') {       // check for the unity position of the file number
      fileName[BASE_NAME_SIZE + 1]++;
    } else if (fileName[BASE_NAME_SIZE] != '9') {    // check for the decimal position of the file number
      fileName[BASE_NAME_SIZE + 1] = '0';
      fileName[BASE_NAME_SIZE]++;
    } else {
      error("Can't create file name");
    }
  }
}

void set_pinMode(void){
  pinMode(A0, INPUT); //Pin 01
  pinMode(A1, INPUT); //Pin 02
  pinMode(A2, INPUT);
  pinMode(A3, INPUT);
  pinMode(A4, INPUT);
  pinMode(A5, INPUT);
  pinMode(A6, INPUT);
  pinMode(A7, INPUT);
  pinMode(A14, INPUT);
  pinMode(A15, INPUT); //Pin 16
  pinMode(buttonPin, INPUT_PULLUP);
  pinMode(led_red, OUTPUT);
  pinMode(PIN_VBAT, INPUT);
  pinMode(led_yellow, OUTPUT);
  pinMode(Green_led,OUTPUT);
}


void blink_LED_RED(void) {
  for(uint8_t i = 1; i < 4; i++){
    digitalWrite(led_red, HIGH);
    delay(250);
    digitalWrite(led_red, LOW);
    delay(250);
  }
}


void set_IMU(void){
  Wire.begin(SDApin_IMU, SCLpin_IMU);   //(41=SDApin, 40=SCLpin)
  Serial.println("Initializing the LSM9DS1");
  //--------------------------------------------Gyro Settings--------------------------------------------------
  // [scale] sets the full-scale range of the gyroscope.
  // scale can be set to either 245, 500, or 2000
  imu.settings.gyro.scale = 2000; // Set scale to +/-245dps

  // [sampleRate] sets the output data rate (ODR) of the gyro
  // sampleRate can be set between 1-6
  // 1 = 14.9 LPF1 cut off 5Hz    4 = 238 LPF1 cut off 76Hz      (LPF1=Low Pass Filter 1)
  // 2 = 59.5 LPF1 cut off 19Hz   5 = 476 LPF1 cut off 100Hz
  // 3 = 119 LPF1 cut off 38Hz    6 = 952 LPF1 cut off 100Hz
  imu.settings.gyro.sampleRate = 5; // 476Hz sample rate with 100Hz cutoff low pass filter 

  // [bandwidth] sets the anti-aliasing filter bandwidth.
  // Allowed values: 0-3. Actual value of cutoff frequency of LPF depends on the sample rate. (Datasheet section 7.12)
  imu.settings.gyro.bandwidth = 0;  // BW = 100Hz also try with 2

  // [HPFEnable] enables or disables the high-pass filter
  imu.settings.gyro.HPFEnable = true; // HPF enable
  // [HPFCutoff] sets the HPF cutoff frequency (if enabled)
  // Allowable values are 0-9. Value depends on ODR.(Datasheet section 7.14)
  // High Pass Filter cut off frequency vary with respect to the sample rate of LPF1 (ODR)
  // 0 = 30Hz Cut off at ODR = 476Hz, 15Hz Cut off at ODR = 238Hz                      5 = 1Hz Cut off at ODR = 476Hz, 0.5Hz Cut off at ODR = 238Hz            
  // 1 = 15Hz Cut off at ODR = 476Hz, 8Hz Cut off at ODR = 238Hz                       6 = 0.5Hz Cut off at ODR = 476Hz, 0.2Hz Cut off at ODR = 238Hz 
  // 2 = 8Hz Cut off at ODR = 476Hz, 4Hz Cut off at ODR = 238Hz                        7 = 0.2Hz Cut off at ODR = 476Hz, 0.1Hz Cut off at ODR = 238Hz 
  // 3 = 4Hz Cut off at ODR = 476Hz, 2Hz Cut off at ODR = 238Hz                        8 = 0.1Hz Cut off at ODR = 476Hz, 0.05Hz Cut off at ODR = 238Hz
  // 4 = 2Hz Cut off at ODR = 476Hz, 1Hz Cut off at ODR = 238Hz                        9 = 0.05Hz Cut off at ODR = 476Hz, 0.02Hz Cut off at ODR = 238Hz
  imu.settings.gyro.HPFCutoff = 6; // HPF cutoff = 0.5Hz at ODR 476

  // [flipX], [flipY], and [flipZ] are booleans that can
  // automatically switch the positive/negative orientation
  // of the three gyro axes.
  imu.settings.gyro.flipX = false; // Don't flip X
  imu.settings.gyro.flipY = false; // Don't flip Y
  imu.settings.gyro.flipZ = false; // Don't flip Z

  //-------------------------------------------Acceler Settings-------------------------------------------------
  // [scale] sets the full-scale range of the accelerometer.
  // accel scale can be 2, 4, 8, or 16
  imu.settings.accel.scale = 16; // Set accel scale to +/-16g.

  // [sampleRate] sets the output data rate (ODR) of the accelerometer. ONLY APPLICABLE WHEN THE GYROSCOPE IS DISABLED! 
  // Otherwise accel sample rate = gyro sample rate.
  // accel sample rate can be 1-6
  // 1 = 10 Hz    4 = 238 Hz
  // 2 = 50 Hz    5 = 476 Hz
  // 3 = 119 Hz   6 = 952 Hz
  imu.settings.accel.sampleRate = 5; // Set accel to 10Hz.

  // [bandwidth] sets the anti-aliasing filter bandwidth.
  // Accel cutoff freqeuncy can be any value between -1 - 3. 
  // -1 = bandwidth determined by sample rate
  // 0 = 408 Hz   2 = 105 Hz
  // 1 = 211 Hz   3 = 50 Hz
  imu.settings.accel.bandwidth = 2; // BW = 105Hz

  // [highResEnable] enables or disables high resolution mode for the acclerometer.
  imu.settings.accel.highResEnable = false; // Disable HR
  // [highResBandwidth] sets the LP cutoff frequency of
  // the accelerometer if it's in high-res mode.
  // can be any value between 0-3
  // LP cutoff is set to a factor of sample rate
  // 0 = ODR/50    2 = ODR/9
  // 1 = ODR/100   3 = ODR/400
  // imu.settings.accel.highResBandwidth = 2; 

  //---------------------------------------Magneto Settings---------------------------------------------------------
  // [scale] sets the full-scale range of the magnetometer
  // mag scale can be 4, 8, 12, or 16
  imu.settings.mag.scale = 16; // Set mag scale to +/-16 Gs
  
  // [sampleRate] sets the output data rate (ODR) of the
  // magnetometer.
  // mag data rate can be 0-7:
  // 0 = 0.625 Hz  4 = 10 Hz
  // 1 = 1.25 Hz   5 = 20 Hz
  // 2 = 2.5 Hz    6 = 40 Hz
  // 3 = 5 Hz      7 = 80 Hz
  imu.settings.mag.sampleRate = 7; // Set OD rate to 80Hz

  // [tempCompensationEnable] enables or disables 
  // temperature compensation of the magnetometer.
  imu.settings.mag.tempCompensationEnable = false;

  // [XYPerformance] sets the x and y-axis performance of the
  // magnetometer to either:
  // 0 = Low power mode      2 = high performance
  // 1 = medium performance  3 = ultra-high performance
  imu.settings.mag.XYPerformance = 3; // Ultra-high perform.
  // [ZPerformance] does the same thing, but only for the z
  imu.settings.mag.ZPerformance = 3; // Ultra-high perform.

  // [lowPowerEnable] enables or disables low power mode in
  // the magnetometer.
  imu.settings.mag.lowPowerEnable = false;
  
  // [operatingMode] sets the operating mode of the
  // magnetometer. operatingMode can be 0-2:
  // 0 = continuous conversion
  // 1 = single-conversion
  // 2 = power down
  imu.settings.mag.operatingMode = 0; // Continuous mode

  if (imu.begin(LSM9DS1_AG, LSM9DS1_M, Wire) == false)  // with no arguments, this uses default addresses (AG:0x6B, M:0x1E) and i2c port (Wire).
  {
    Serial.println("Failed to communicate with LSM9DS1.");
    Serial.println("Double-check wiring.");
    Serial.println("Default settings in this sketch will "
                   "work for an out of the box LSM9DS1 "
                   "Breakout, but may need to be modified "
                   "if the board jumpers are.");
    while (1)
      ;
  }
}

void set_external_I2C_ADC(void){
  Wire1.begin (SDApin, SCLpin);

  Serial.println("Read single-ended readings from AIN0..3");
  Serial.println("ADC Range: +/- 6.144V (1 bit = 0.1875mV");
  //ADDR = Board has pull-down to ground (sets I2C address of 0x48)
  if (!ads.begin(0x48,&Wire1)) {
    Serial.println("Failed to initialize ADS.");
    while (1);
  }
  ads.setDataRate(RATE_ADS1115_128SPS);
}
