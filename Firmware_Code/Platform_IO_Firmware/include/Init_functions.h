// --------------------------------------DAQ2----------------------------------------
#ifndef __INIT_FUNCTIONS__H__
#define __INIT_FUNCTIONS__H__

#include <Arduino.h>
#include <config.h>
void set_SD_card(void){

  pinMode(14, INPUT_PULLUP);	                      //manuell switch to enable SD CARD
  SPI.begin(SPI_SCK, SPI_MISO, SPI_MOSI, chipSelect);
  // ---------------------Initialize at the highest speed supported by the board that is not over 50 MHz. We have to try a lower speed if SPI errors occur---------------------
  if (!sd.begin(chipSelect, SD_SCK_MHZ(50))) {
    sd.initErrorHalt();
  }
  // ----------------------------------------------Find an unused file name-------------------------------------------------------------
  if (BASE_NAME_SIZE > 14) {
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
  // pinMode(A14, INPUT);
  // pinMode(A15, INPUT); //Pin 16
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

#endif  //!__INIT_FUNCTIONS__H__

