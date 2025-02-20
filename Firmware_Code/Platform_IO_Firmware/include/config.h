#ifndef __CONFIG__H__
#define __CONFIG__H__
#include <Arduino.h>
#include <SPI.h>
#include "SdFat.h"
// //---------------------------------ADC PIN initialization------------------------------
// # define SDApin 38
// # define SCLpin 39
// Adafruit_ADS1115 ads; 
//---------------------------------IMU PIN initialization------------------------------
// #define ICM20948_ADDR 0x69
// ICM20948_WE myIMU = ICM20948_WE(&Wire, ICM20948_ADDR);
//---------------------------------Battery PIN------------------------------------------------------------------------------------------------------
#define PIN_VBAT 35                       // If this is not work roperly then we can use VBAT pin to Analog pin such as A8 for calculating battery voltage.


//---------------------------------Define Analog Pin-------------------------------------------------------------------------------------------
// static const uint8_t A6 = 7;
// static const uint8_t A7 = 8;

//---------------------------------SD CARD Pin Configuration---------------------------------------------------------------------------------------
#define chipSelect 10
#define SPI_MOSI 11
#define SPI_MISO 13
#define SPI_SCK 12
//---------------------------------Button PIN Initialization----------------------------------------------------------
#define buttonPin   42 
//---------------------------------Defining BASE NAME for the DAT File of SD Card-----------------------------------------------------------------
#define FILE_BASE_NAME "S1_DAQ2_Data"
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
volatile uint16_t data_count = 0;
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
volatile uint8_t button_value;
// uint16_t button_count = 0;
const uint8_t button_press_ON_threshold = 2;
const uint8_t button_press_OFF_threshold = 4;

//-----------------------------------FLAG related variable--------------------------------------------------------------------------------------------
volatile uint8_t start_flag = 0;
volatile uint8_t led_flag = 0; 
volatile uint8_t ADC_BUFFER_Uncopied_flag = 0;       // Used to check data that remain Uncopied in ADC BUFFER and Enable Storing that data to SD Card. 
volatile bool DATA_READ_ENABLE;                      // Enable data reading according to Button press and Others Flag information.
volatile bool game_start_flag;

//-----------------------------------LED Pin Configuration--------------------------------------------------------------------------------------------
const uint8_t led_yellow = 00;              // To Indicate Battery Life or Voltage Level
const int Green_led = 21;                   // To control the built in GREEN LED
const int led_red = 45;                     // To Indicate the Data Reading of DAQ -- START or STOP--Blink 3 times
// //-----------------------------------I2C, IMU & ADC value asigning global variables--------------------------------------------------------------------
// uint16_t adc0; //I2C ADC pin 0
// uint16_t adc1; //I2C ADC pin 1
// int32_t accx;  //I2C IMU Accelerometer X axis
// int32_t accy;  //I2C IMU Accelerometer Y axis
// int32_t accz;  //I2C IMU Accelerometer Z axis
// int32_t gyx;   //I2C IMU Gyroscope X axis
// int32_t gyy;   //I2C IMU Gyroscope Y axis
// int32_t gyz;   //I2C IMU Gyroscope Z axis
// int32_t mgx;   //I2C IMU Magnetometer X axis
// int32_t mgy;   //I2C IMU Magnetometer Y axis
// int32_t mgz;   //I2C IMU Magnetometer Z axis

//-----------------------------------SD CARD Related Variables----------------------------------------------------------------------------------------
SdFat sd;
SdFile file;
#endif  //!__CONFIG__H__