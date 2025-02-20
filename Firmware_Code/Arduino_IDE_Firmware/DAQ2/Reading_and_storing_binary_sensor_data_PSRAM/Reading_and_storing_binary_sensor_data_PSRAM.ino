#include <SPI.h>
#include "SdFat.h"
#include <Arduino.h>
#include <Wire.h>
#include <SparkFunLSM9DS1.h>
#include <Adafruit_ADS1X15.h>

// //---------------------------------ADC PIN initialization----------------------------------------------------------------------------------------
# define SDApin 38
# define SCLpin 39
Adafruit_ADS1115 ads; 
//------------------------------------IMU PIN initialization----------------------------------------------------------------------------------------
# define SDApin_IMU 41
# define SCLpin_IMU 40
LSM9DS1 imu;  // Use the LSM9DS1 class to create an object. [imu] can be
// SDO_XM and SDO_G are both pulled high, so our addresses are:
#define LSM9DS1_M  0x1E // Would be 0x1C if SDO_M is LOW
#define LSM9DS1_AG 0x6B // Would be 0x6A if SDO_AG is LOW
//---------------------------------Battery PIN------------------------------------------------------------------------------------------------------
#define PIN_VBAT 35                       // If this is not work roperly then we can use VBAT pin to Analog pin such as A8 for calculating battery voltage.

//---------------------------------SD CARD Pin Configuration---------------------------------------------------------------------------------------
#define chipSelect 10
#define SPI_MOSI 11
#define SPI_MISO 13
#define SPI_SCK 12
//---------------------------------Button PIN Initialization----------------------------------------------------------
#define buttonPin   42 
//---------------------------------Defining BASE NAME for the DAT File of SD Card-----------------------------------------------------------------
#define FILE_BASE_NAME "DAQ2_Data"
#define error(msg) sd.errorHalt(F(msg)) // Give SD card initialization related error

//----------------------------------Miscellaneous Variables---------------------------------------------------------------------------------------
int Battery_voltage;                        // Battery Related Variable
const uint16_t ADC_FREQ = 1024;             // Samping frequency of the ADC data in Hz. This is also the sampling frequency of button press
uint8_t sensor_read_count = 1;

//----------------------------------ADC BUFFER and COPY BUFFER Related Variables------------------------------------------------------------------
int32_t** ADC_BUFFER;                       // Variable for buffering the ADC data in the PSRAM
volatile uint32_t ADC_BUF_START_INDX = 0;   // Start index of ADC Buffer
volatile uint32_t ADC_BUF_END_INDX = 1;     // END index of ADC Buffer
volatile uint32_t ADC_COUNT = 0;            // variable to track the number of sampling has happened
const uint8_t Sensor_size=17;               // Number of Analog SENSORS that is also used for BUFFER SIZE
const uint16_t ADC_BUF_SIZE = 20480;        // BUFFER array Size=======Max size try 9216*************In case of PSRAM Max size can be more than 20 lac for integer data type.
const uint16_t ADC_COPY_SIZE = 32;          // BUFFER COPY array size =======Max size try 3072
uint16_t data_count = 0;
// volatile uint32_t ADC_BUFFER[2][ADC_BUF_SIZE] = { 0 };  // variable for buffering the data in the ISR

// ----------------------------------Set a new file name with respect to saving sequence but the base name remain same---------------------------------
const uint8_t BASE_NAME_SIZE = sizeof(FILE_BASE_NAME) - 1;
char fileName[25] = FILE_BASE_NAME "00.dat";

// ----------------------------------Timerinterrupt related Variables for Sensor Reading (Timer 1)-----------------------------------------------------------------------------------------
const uint16_t TIMER_PRESCALER = 50;        // CPU APB CLock Frequency*(1/prescaler)
const uint16_t TIMER_TICK = 6250;           // TimerTick = CPU_CLK_FREQ / (TIMER_PRESCALER * ADC_FREQ) Hard coded because u_16_integer size limit
// According to ADC sampling rate it can sample 12-13 sample per millisecond(ms) thus it's sampling frequency is 14KHz(approx).
// Timer Tick = 1000 and Prescaler =80 so sampling frequency is 1000 Hz. So you can sample data for approx 1ms uninterruptedly and that's why you can read 11/12 sample for max 11/12 different sensor(one sample data for each sensor) at timerinterrupt ISR function.
// Timer Tick = 1953 and Prescaler =80 so sampling frequency is 512 Hz(approx). So you can sample data for 2ms(approx) uninterruptedly and that's why you can read 21/22(11sample*2ms=22sample) sample for max 21/22 different sensor(one sample data for each sensor) at timerinterrupt ISR function.
// Timer Tick = 3125 and Prescaler =50 so sampling frequency is 512 Hz. So you can sample data for 2ms uninterruptedly and that's why you can read 21/22(11sample*2ms=22sample) sample for max 21/22 different sensor(one sample data for each sensor) at timerinterrupt ISR function.
// Timer Tick = 1250 and Prescaler =125 so sampling frequency is 512 Hz. So you can sample data for 2ms uninterruptedly and that's why you can read 21/22(11sample*2ms=22sample) sample for max 21/22 different sensor(one sample data for each sensor) at timerinterrupt ISR function.
// Timer Tick = 6250 and Prescaler =50 so sampling frequency is 256 Hz. So you can sample data for 4ms uninterruptedly and that's why you can read 43/44(11sample*4ms=44sample) sample for max 43/44 different sensor(one sample data for each sensor) at timerinterrupt ISR function.
// We can notice different combinations of prescaler and timer tick for 512 Hz sampling rate where prescalers 50, 80 & 125 are only significant for sampling rate and also change the clock frequency of APB clock. 
// Reducing APB clock frequency(Increasing Prescaler) causes small number of timertick for constant sampling frequency and alternatively Increasing APB clock frequency(Reducing Prescaler) causes large number of timertick for constant sampling frequency.
hw_timer_t* Timer0_Cfg = NULL;

// ----------------------------------Timerinterrupt related Variables for Button Counting (Timer 0)-----------------------------------------------------------------------------------------
const uint16_t TIMER_PRESCALER_1 = 80;        // CPU CLock Frequency
const uint16_t TIMER_TICK_1 = 1000;           // TimerTick = CPU_CLK_FREQ / (TIMER_PRESCALER * ADC_FREQ) Hard coded because u_16_integer size limit
// Timer Tick = 1000 and Prescaler =80 so sampling frequency is 1000 Hz.
hw_timer_t* Timer1_Cfg = NULL;
//------------------------------------Semaphore variable----------------------------------------------------------------------------------
volatile SemaphoreHandle_t timerSemaphore;
//A semaphore is a non-negative integer variable, shared among multiple processes/threads, 
//a special kind of synchronization data that can be used only through specific synchronization primitives.
//transmit messages between distant points.
//Two types of semaphore available incliuding Binary Semaphore and Counting Semaphore.
portMUX_TYPE timerMux = portMUX_INITIALIZER_UNLOCKED;
//------------------------------------Push Button counting in ISR (Interrupt Service Routine)----------------------------------------------------------
volatile uint32_t isrCounter = 0;

//------------------------------------Push Button Related Variables----------------------------------------------------------------------------------- 
uint8_t button_value;
// uint16_t button_count = 0;
const uint8_t button_press_ON_threshold = 2;
const uint8_t button_press_OFF_threshold = 4;

//-----------------------------------FLAG related variable--------------------------------------------------------------------------------------------
uint8_t start_flag = 0;
uint8_t led_flag = 0; 
uint8_t ADC_BUFFER_Uncopied_flag = 0;       // Used to check data that remain Uncopied in ADC BUFFER and Enable Storing that data to SD Card. 
bool DATA_READ_ENABLE;                      // Enable data reading according to Button press and Others Flag information.
bool game_start_flag;                       // Flag used in Synchronizing the eyeblink game starting time with button

//-----------------------------------LED Pin Configuration--------------------------------------------------------------------------------------------
const uint8_t led_yellow = 00;              // To Indicate Battery Life or Voltage Level
const int Green_led = 21;                   // To control the built in GREEN LED
const int led_red = 45;                     // To Indicate the Data Reading of DAQ -- START or STOP--Blink 3 times
// //-----------------------------------I2C, IMU & ADC value asigning global variables--------------------------------------------------------------------
// uint16_t adc0; //I2C ADC pin 0
// uint16_t adc1; //I2C ADC pin 1
int32_t accx;  //I2C IMU Accelerometer X axis
int32_t accy;  //I2C IMU Accelerometer Y axis
int32_t accz;  //I2C IMU Accelerometer Z axis
int32_t gyx;   //I2C IMU Gyroscope X axis
int32_t gyy;   //I2C IMU Gyroscope Y axis
int32_t gyz;   //I2C IMU Gyroscope Z axis
int32_t mgx;   //I2C IMU Magnetometer X axis
int32_t mgy;   //I2C IMU Magnetometer Y axis
int32_t mgz;   //I2C IMU Magnetometer Z axis

//-----------------------------------SD CARD Related Variables----------------------------------------------------------------------------------------
SdFat sd;
SdFile file;

//-----------------------------------Timerinterrupt Function for Push Button counting (Timer 0)------------------------------------------------------------------------------------------
void IRAM_ATTR Timer1_ISR() {
  portENTER_CRITICAL_ISR(&timerMux);
  if (button_value = 1-digitalRead(buttonPin)) {
  isrCounter++;
  }
  portEXIT_CRITICAL_ISR(&timerMux);
  // Give a semaphore that we can check in the loop
  xSemaphoreGiveFromISR(timerSemaphore, NULL);
  //For the semaphore to be used, it must be released with xSemaphoreGive(sem)
}
//-----------------------------------Timerinterrupt Function declaration for Sensor Reading (Timer 1)------------------------------------------------------------------
void IRAM_ATTR Timer0_ISR();

//-----------------------------------VOID SETUP, PUT the part of CODE here which need to RUN ONCE------------------------------------------------------------------
void setup() {
  Serial.begin(115200);
  // //------------------------------------------------"I2C"---IMU SETUP ----------------------------------------------------------------------------------------
  set_IMU();
  // Wire.begin(41,40); //(SDApin, SCLpin)
  // Wire.setClock(100000);
  // myIMU.init();
  // myIMU.initMagnetometer();
  // // myIMU.enableI2CMaster();
  // myIMU.reset_ICM20948();  //To use this function we need to edit the Library function and made this function private to public and save the header file using VScode.
  // myIMU.init();
  // myIMU.initMagnetometer();
  // myIMU.setAccRange(ICM20948_ACC_RANGE_2G);
  // myIMU.setAccDLPF(ICM20948_DLPF_3);   // Digital Low Pass Filter for Accelerometer
  // myIMU.setAccSampleRateDivider(14);   // Output data rate is = 1125/(1 + setAccSampleRateDivider) Hz------>control sampling frequency from setAccSampleRateDivider------>setAccSampleRateDivider value must be integer.
  
  //---------------------------------------------------"I2C"-----ADC SETUP (External)----------------------------------------------------------------------------
  // set_external_I2C_ADC();
  
  //--------------------------------------------------------ADC Resolution SETUP (Built in)---------------------------------------------------------------
  analogReadResolution(13);
  set_pinMode();
  set_SD_card();
  // float Sketch_size = ESP.getSketchSize();
  // float Free_sketch_space = ESP.getFreeSketchSpace();
  // float Total_heap_size = ESP.getHeapSize();
  // float Free_heap_size = ESP.getFreeHeap();
  // float Min_free_heap_size = ESP.getMinFreeHeap();
  // float Allocated_heap_size = ESP.getMaxAllocHeap();
  // Serial.println((String)"Sketch Size = " + Sketch_size + (String)" bytes");  // Approx 1.5 MB
  // Serial.println((String)"Free Sketch Space = " + Free_sketch_space + (String)" bytes");
  // Serial.println((String)"Total Heap Size = " + Total_heap_size + (String)" bytes");
  // Serial.println((String)"Free Heap Size = " + Free_heap_size + (String)" bytes");
  // Serial.println((String)"Min Free Heap Size = " + Min_free_heap_size + (String)" bytes");
  // Serial.println((String)"Allocated Heap Size = " + Allocated_heap_size + (String)" bytes");
  Serial.println("Press PUSH Button to START data Reading from SENSORS & writing to SD CARD");
  // Battery_voltage = analogRead(A6);
  // Serial.println((String)"Battery Voltage: "+Battery_voltage);
  // digitalWrite(Green_led, HIGH);

//------------------------------------PSRAM Initialization Check, BUFFER Memory Allocation in PSRAM & PSRAM Free Space Check-------------------------------
  if (psramInit()) {
    Serial.println("\nPSRAM is correctly initialized");

    //--------------------------------Memory size printing-------------------------------------------------------------------------------------------------
    int available_PSRAM_size = ESP.getPsramSize();
    Serial.println((String) "Available PSRAM size in bytes:" + available_PSRAM_size);

    //--------------------------------BUFFER Memory Allocation in PSRAM with Zero initilization BUFFER-----------------------------------------------------
    ADC_BUFFER = (int32_t**)ps_calloc(Sensor_size, sizeof(int32_t*));
    for (int sensor = 0; sensor < Sensor_size; sensor++) {
      ADC_BUFFER[sensor] = (int32_t*)ps_calloc(ADC_BUF_SIZE, sizeof(int32_t));
    }

    //--------------------------------PSRAM, Free & Buffer Allocated Space Check--------------------------------------------------------------------------
    int available_PSRAM_size_after = ESP.getFreePsram();
    Serial.println((String) "PSRAM Size available (bytes): " + available_PSRAM_size_after);  // Free memory space has decreased
    int array_size = available_PSRAM_size - available_PSRAM_size_after;
    Serial.println((String) "Array size in PSRAM in bytes: " + array_size);
  } else {
    Serial.println("PSRAM not available");
  }


  // //------------------------------------SETUP Multi-threading function for while loop to update IMU values in global variables------------------------------------------
  xTaskCreate(
    i2c_data,      // Function name of the task
    "I2C_DATA",   // Name of the task (e.g. for debugging)
    3072,        // Stack size (bytes)
    NULL,        // Parameter to pass
    1,           // Task priority
    NULL         // Task handle
  );


  //----------------------------------Timerinterrupt Related SETUP for Push Button counting (Timer 0)----------------------------------------------------------------------------------------
  timerSemaphore = xSemaphoreCreateBinary(); // Create semaphore to inform at void loop when the timer 0 has fired
  Timer1_Cfg = timerBegin(0, TIMER_PRESCALER_1, true);  // timerBegin(timer, prescaler, counUp)
  timerAttachInterrupt(Timer1_Cfg, &Timer1_ISR, true);// True = Edge Triggered Timer & False = Level Triggered Timer
  timerAlarmWrite(Timer1_Cfg, TIMER_TICK_1, true);  // timerAlarmWrite(timer, TimerTick, autoReload)
  timerAlarmEnable(Timer1_Cfg);

  //----------------------------------Timerinterrupt Related SETUP for Sensor Reading (Timer 1)----------------------------------------------------------------------------------------
  Timer0_Cfg = timerBegin(1, TIMER_PRESCALER, true);  // timerBegin(timer, prescaler, counUp)
  timerAttachInterrupt(Timer0_Cfg, &Timer0_ISR, true);// True = Edge Triggered Timer & False = Level Triggered Timer
  timerAlarmWrite(Timer0_Cfg, TIMER_TICK, true);  // timerAlarmWrite(timer, TimerTick, autoReload)
  timerAlarmEnable(Timer0_Cfg);

}
//-----------------------------------Timerinterrupt Function for Sensor Reading (Timer 1)------------------------------------------------------------------------------------------
void IRAM_ATTR Timer0_ISR() {
  read_analog_sensors();
}
//-----------------------------------Executing Multi-threading function to update the data of I2C in global variables using while infinite loop (FreeRTOS)-----------------------
void i2c_data(void *parameter) {
    while(1){
      if (imu.gyroAvailable()) {
        // To read from the gyroscope,  first call the
        // readGyro() function. When it exits, it'll update the
        // gx, gy, and gz variables with the most current data.
        imu.readGyro();
      }
      if (imu.accelAvailable()) {
        // To read from the accelerometer, first call the
        // readAccel() function. When it exits, it'll update the
        // ax, ay, and az variables with the most current data.
        imu.readAccel();
      }
      if (imu.magAvailable()) {
        // To read from the magnetometer, first call the
        // readMag() function. When it exits, it'll update the
        // mx, my, and mz variables with the most current data.
        imu.readMag();
      }
      gyx = imu.gx;
      gyy = imu.gy;
      gyz = imu.gz;
      accx = imu.ax;
      accy = imu.ay;
      accz = imu.az;
      mgx = imu.mx;
      mgy = imu.my;
      mgz = imu.mz;
      // adc0=ads.readADC_SingleEnded(0);
      // adc1=ads.readADC_SingleEnded(1);
    }
}

//----------------------------VOID LOOP---------------------------------VOID LOOP---------------------------------VOID LOOP--------------------------------------
void loop() {
  uint32_t isrCount = 0;
  if (xSemaphoreTake(timerSemaphore, 0) == pdTRUE){
    //For the semaphore to be used, it must be released with xSemaphoreGive(sem). To receive the semaphore, 
    //there is the function xSemaphoreTake(sem, xTicksToWait) with xTicksToWait as the maximum waiting time in ticks. 
    //If the semaphore was accepted within the waiting time, the function return value is pdTRUE, otherwise pdFALSE.
    // Read the interrupt count and time
    portENTER_CRITICAL(&timerMux);
    isrCount = isrCounter;
    portEXIT_CRITICAL(&timerMux);
    // Print it
    // Serial.println(button_count);
  }
  if (isrCount == button_press_ON_threshold * 1000) {
      Serial.println((String)"ISR count 2000---> at:" + isrCount);
      led_flag = 1;
      data_count = 0;
      // Serial.print(led_flag);
      // Serial.println(data_count);
    }
    
  
  // if (isrCount==2000) {
  //   Serial.print("ISR count 2000--->");
  //   Serial.print(isrCount);
  //   Serial.println(" at ");
  //   // Serial.print(isrTime);
  //   // Serial.println(" ms");
  //   isrCounter=0;
  //   }

  if (isrCount == button_press_ON_threshold * 1000) {
    if (led_flag == 1) {
      blink_LED_RED();
      led_flag = 0;
      Serial.println("Data Reading from SENSORS & Writing to SD has been STARTED,Press PUSH BUTTON to STOP");
      //----------------------------------If we set SD card here,it will just open a single file and append 512 samples repeatedly and write on it-------------------------------------------
      set_SD_card();
      if (!file.open(fileName, O_WRONLY | O_CREAT | O_APPEND)) {
        error("file.open");
      }
    }
    //------------------------------------If we set SD card here,it will open multiple file with 512 samples in a single file and write on it--------------------------------------------------
    // set_SD_card();
    // if (!file.open(fileName, O_WRONLY | O_CREAT | O_APPEND)) {
    //   error("file.open");
    // }
    start_flag = 1;
    game_start_flag=true;
  }

  if (start_flag == 1) {
    //------------------------------------Writing Data to SD CARD--------------------------------------------------------------------------------------------
    DATA_READ_ENABLE = true;
    if (game_start_flag==true) {
      Serial.println("StartEyeblinkGame");
      game_start_flag=false;
    }
    int32_t ADC_buf_copy[Sensor_size][ADC_COPY_SIZE];             // variable to contain (ADC_copy_size x Sensor_size x 2(uint16_t)) bytes copy of the buffer
    if ((ADC_BUF_END_INDX - ADC_BUF_START_INDX + ADC_BUF_SIZE) % ADC_BUF_SIZE >= ADC_COPY_SIZE) {
      for (uint32_t i = 0; i < ADC_COPY_SIZE; i++) {
        ADC_buf_copy[0][i] = ADC_BUFFER[0][ADC_BUF_START_INDX];
        ADC_buf_copy[1][i] = ADC_BUFFER[1][ADC_BUF_START_INDX];
        ADC_buf_copy[2][i] = ADC_BUFFER[2][ADC_BUF_START_INDX];
        ADC_buf_copy[3][i] = ADC_BUFFER[3][ADC_BUF_START_INDX];
        ADC_buf_copy[4][i] = ADC_BUFFER[4][ADC_BUF_START_INDX];
        ADC_buf_copy[5][i] = ADC_BUFFER[5][ADC_BUF_START_INDX];
        ADC_buf_copy[6][i] = ADC_BUFFER[6][ADC_BUF_START_INDX];
        ADC_buf_copy[7][i] = ADC_BUFFER[7][ADC_BUF_START_INDX];
        ADC_buf_copy[8][i] = ADC_BUFFER[8][ADC_BUF_START_INDX];
        ADC_buf_copy[9][i] = ADC_BUFFER[9][ADC_BUF_START_INDX];
        ADC_buf_copy[10][i] = ADC_BUFFER[10][ADC_BUF_START_INDX];
        ADC_buf_copy[11][i] = ADC_BUFFER[11][ADC_BUF_START_INDX];
        ADC_buf_copy[12][i] = ADC_BUFFER[12][ADC_BUF_START_INDX];
        ADC_buf_copy[13][i] = ADC_BUFFER[13][ADC_BUF_START_INDX];
        ADC_buf_copy[14][i] = ADC_BUFFER[14][ADC_BUF_START_INDX];
        ADC_buf_copy[15][i] = ADC_BUFFER[15][ADC_BUF_START_INDX];
        ADC_buf_copy[16][i] = ADC_BUFFER[16][ADC_BUF_START_INDX];
        // ADC_buf_copy[17][i] = ADC_BUFFER[17][ADC_BUF_START_INDX];
        // ADC_buf_copy[18][i] = ADC_BUFFER[18][ADC_BUF_START_INDX];
        // ADC_buf_copy[19][i] = ADC_BUFFER[19][ADC_BUF_START_INDX];
        // ADC_buf_copy[20][i] = ADC_BUFFER[20][ADC_BUF_START_INDX];
        // ADC_buf_copy[21][i] = ADC_BUFFER[21][ADC_BUF_START_INDX];
        // ADC_buf_copy[22][i] = ADC_BUFFER[22][ADC_BUF_START_INDX];
        // ADC_buf_copy[23][i] = ADC_BUFFER[23][ADC_BUF_START_INDX];
        // ADC_buf_copy[24][i] = ADC_BUFFER[24][ADC_BUF_START_INDX];
        ADC_BUF_START_INDX = (ADC_BUF_START_INDX + 1) % ADC_BUF_SIZE;
      }
      //-----------------------------------------Opening a Specific File at SD Card to Store Data---------------------------------------------------------------
      if (!file.open(fileName, O_WRONLY | O_CREAT | O_APPEND)) {
        error("file.open");
      }
      //-----------------------------------------Sending Data from COPY BUFFER  to SD Card and Store in a Specific file-----------------------------------------
      logData(ADC_buf_copy, ADC_COPY_SIZE);                

      // set_SD_card();
      // if (!file.open(fileName, O_WRONLY | O_CREAT | O_APPEND)) {
      //   error("file.open");
      //   }
    }
  }

  if (isrCount == button_press_OFF_threshold*1000) {
    Serial.println((String)"ISR count 4000---> at:" + isrCount);
    start_flag = 0;
    // button_count = 0;
    isrCounter=0;   // this is new button count used in ISR Timer 0
    DATA_READ_ENABLE = false;
    ADC_BUFFER_Uncopied_flag = 1;
    // Serial.println("Data Reading from SENSORS & writing to SD has been STOPPED,Press PUSH Button to START");
    blink_LED_RED();
  }
  if (ADC_BUFFER_Uncopied_flag == 1) {
    //----------------------------------Store the data on SD CARD that is less than ADC COPY BUFFER Size (less than ADC_COPY_SIZE=32 samples Chunk)--------------------------
    int32_t ADC_buf_copy[Sensor_size][ADC_COPY_SIZE];
    for (uint32_t i = 0; i < ((ADC_BUF_END_INDX - ADC_BUF_START_INDX + ADC_BUF_SIZE) % ADC_BUF_SIZE); i++) {
      ADC_buf_copy[0][i] = ADC_BUFFER[0][ADC_BUF_START_INDX];
      ADC_buf_copy[1][i] = ADC_BUFFER[1][ADC_BUF_START_INDX];
      ADC_buf_copy[2][i] = ADC_BUFFER[2][ADC_BUF_START_INDX];
      ADC_buf_copy[3][i] = ADC_BUFFER[3][ADC_BUF_START_INDX];
      ADC_buf_copy[4][i] = ADC_BUFFER[4][ADC_BUF_START_INDX];
      ADC_buf_copy[5][i] = ADC_BUFFER[5][ADC_BUF_START_INDX];
      ADC_buf_copy[6][i] = ADC_BUFFER[6][ADC_BUF_START_INDX];
      ADC_buf_copy[7][i] = ADC_BUFFER[7][ADC_BUF_START_INDX];
      ADC_buf_copy[8][i] = ADC_BUFFER[8][ADC_BUF_START_INDX];
      ADC_buf_copy[9][i] = ADC_BUFFER[9][ADC_BUF_START_INDX];
      ADC_buf_copy[10][i] = ADC_BUFFER[10][ADC_BUF_START_INDX];
      ADC_buf_copy[11][i] = ADC_BUFFER[11][ADC_BUF_START_INDX];
      ADC_buf_copy[12][i] = ADC_BUFFER[12][ADC_BUF_START_INDX];
      ADC_buf_copy[13][i] = ADC_BUFFER[13][ADC_BUF_START_INDX];
      ADC_buf_copy[14][i] = ADC_BUFFER[14][ADC_BUF_START_INDX];
      ADC_buf_copy[15][i] = ADC_BUFFER[15][ADC_BUF_START_INDX];
      ADC_buf_copy[16][i] = ADC_BUFFER[16][ADC_BUF_START_INDX];
      // ADC_buf_copy[17][i] = ADC_BUFFER[17][ADC_BUF_START_INDX];
      // ADC_buf_copy[18][i] = ADC_BUFFER[18][ADC_BUF_START_INDX];
      // ADC_buf_copy[19][i] = ADC_BUFFER[19][ADC_BUF_START_INDX];
      // ADC_buf_copy[20][i] = ADC_BUFFER[20][ADC_BUF_START_INDX];
      // ADC_buf_copy[21][i] = ADC_BUFFER[21][ADC_BUF_START_INDX];
      // ADC_buf_copy[22][i] = ADC_BUFFER[22][ADC_BUF_START_INDX];
      // ADC_buf_copy[23][i] = ADC_BUFFER[23][ADC_BUF_START_INDX];
      // ADC_buf_copy[24][i] = ADC_BUFFER[24][ADC_BUF_START_INDX];
      Serial.print(ADC_buf_copy[0][i]);
      Serial.print("--");
      Serial.print(ADC_buf_copy[1][i]);
      Serial.print("--");
      Serial.print(ADC_buf_copy[10][i]);
      Serial.print("--");
      Serial.print(ADC_buf_copy[13][i]);
      Serial.print("--");
      Serial.print(ADC_buf_copy[16][i]);
      Serial.print("***");
      data_count++;
      ADC_BUF_START_INDX = (ADC_BUF_START_INDX + 1) % ADC_BUF_SIZE;
    }
    Serial.println("");
    Serial.println((String)"ADC Buffer Remaining Data Count: "+ (data_count*Sensor_size));

    //-----------------------------------------Opening a Specific File at SD Card to Store Data---------------------------------------------------------------
    if (!file.open(fileName, O_WRONLY | O_CREAT | O_APPEND)) {
      error("file.open");
    }

    //-----------------------------------------Sending Data from COPY BUFFER  to SD Card and Store in a Specific file-----------------------------------------
    logData(ADC_buf_copy, data_count);

    Serial.println("Data Reading from SENSORS & writing to SD has been STOPPED,Press PUSH Button to START");
    ADC_BUFFER_Uncopied_flag = 0;
    Serial.println("");
  }
}