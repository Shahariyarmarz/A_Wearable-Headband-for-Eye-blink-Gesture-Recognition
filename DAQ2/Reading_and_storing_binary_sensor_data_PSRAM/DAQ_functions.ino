void read_analog_sensors(void){
  // if (DATA_READ_ENABLE) {
    if(DATA_READ_ENABLE && sensor_read_count<4){
      ADC_BUFFER[0][ADC_BUF_END_INDX] = analogRead(A0);  
      ADC_BUFFER[1][ADC_BUF_END_INDX] = analogRead(A1);
      ADC_BUFFER[2][ADC_BUF_END_INDX] = analogRead(A2);
      ADC_BUFFER[3][ADC_BUF_END_INDX] = analogRead(A3);
      ADC_BUFFER[4][ADC_BUF_END_INDX] = analogRead(A4);
      ADC_BUFFER[5][ADC_BUF_END_INDX] = analogRead(A5);  
      ADC_BUFFER[6][ADC_BUF_END_INDX] = analogRead(A6);
      ADC_BUFFER[7][ADC_BUF_END_INDX] = analogRead(A7); 
      // ADC_BUFFER[14][ADC_BUF_END_INDX] = adc0; 
      // ADC_BUFFER[15][ADC_BUF_END_INDX] = adc1;
      ADC_BUF_END_INDX = (ADC_BUF_END_INDX + 1) % ADC_BUF_SIZE;
      if (ADC_BUF_END_INDX == ADC_BUF_START_INDX) {
        Serial.println("Buffer Overflow!!!!!");
        }
    }
    if(DATA_READ_ENABLE && sensor_read_count==4){
      sensor_read_count=0;
      ADC_BUFFER[0][ADC_BUF_END_INDX] = analogRead(A0);  
      ADC_BUFFER[1][ADC_BUF_END_INDX] = analogRead(A1);
      ADC_BUFFER[2][ADC_BUF_END_INDX] = analogRead(A2);
      ADC_BUFFER[3][ADC_BUF_END_INDX] = analogRead(A3);
      ADC_BUFFER[4][ADC_BUF_END_INDX] = analogRead(A4);
      ADC_BUFFER[5][ADC_BUF_END_INDX] = analogRead(A5);  
      ADC_BUFFER[6][ADC_BUF_END_INDX] = analogRead(A6);
      ADC_BUFFER[7][ADC_BUF_END_INDX] = analogRead(A7);
      ADC_BUFFER[8][ADC_BUF_END_INDX] = gyx;
      ADC_BUFFER[9][ADC_BUF_END_INDX] = gyy;  
      ADC_BUFFER[10][ADC_BUF_END_INDX] = gyz;
      ADC_BUFFER[11][ADC_BUF_END_INDX] = accx;
      ADC_BUFFER[12][ADC_BUF_END_INDX] = accy;  
      ADC_BUFFER[13][ADC_BUF_END_INDX] = accz;
      ADC_BUFFER[14][ADC_BUF_END_INDX] = mgx;
      ADC_BUFFER[15][ADC_BUF_END_INDX] = mgy;
      ADC_BUFFER[16][ADC_BUF_END_INDX] = mgz;
      ADC_BUF_END_INDX = (ADC_BUF_END_INDX + 1) % ADC_BUF_SIZE;
      if (ADC_BUF_END_INDX == ADC_BUF_START_INDX) {
        Serial.println("Buffer Overflow!!!!!");
        }
    }
    sensor_read_count++;
	// }
}



// void read_analog_sensors(void){
//   if (DATA_READ_ENABLE) {
// 		ADC_BUFFER[0][ADC_BUF_END_INDX] = (analogRead(A0) + analogRead(A0)+ analogRead(A0)+ analogRead(A0)+ analogRead(A0)+ analogRead(A0)) / 6;
// 		ADC_BUFFER[1][ADC_BUF_END_INDX] = (analogRead(A1) + analogRead(A1)+ analogRead(A1)+analogRead(A1) + analogRead(A1)+ analogRead(A1)) / 6;
// 		ADC_BUFFER[2][ADC_BUF_END_INDX] = (analogRead(A2) + analogRead(A2)+ analogRead(A2)+analogRead(A2) + analogRead(A2)+ analogRead(A2)) / 6;
//     ADC_BUFFER[3][ADC_BUF_END_INDX] = (analogRead(A3) + analogRead(A3)+ analogRead(A3)+analogRead(A3) + analogRead(A3)+ analogRead(A3)) / 6;
//     ADC_BUFFER[4][ADC_BUF_END_INDX] = (analogRead(A4) + analogRead(A4)+ analogRead(A4)+analogRead(A4) + analogRead(A4)+ analogRead(A4)) / 6;
// 		ADC_BUF_END_INDX = (ADC_BUF_END_INDX + 1) % ADC_BUF_SIZE;
// 		if (ADC_BUF_END_INDX == ADC_BUF_START_INDX) {
// 			Serial.println("Buffer Overflow!!!!!");
// 		}
// 	}
// }

void logData(int32_t ADC_buf_copy[Sensor_size][ADC_COPY_SIZE], uint16_t size) {
  if (file) {
        for (size_t i = 0; i < size; i++) {
            
            // -------------------------Check this portion by trial and error with type casting of int8_t, uint8_t and int32_t-------------------------------
            // -------------------------file.write can write data to SD card byte(8 bit) by byte(8 bit)-----------------------------
            // file.write((const uint8_t *)&ADC_buf_copy[0][i], sizeof(ADC_buf_copy[0][i])); // type casting the buf_copy to uint8_t type and writing to the SD card
            // file.write((const int8_t *)&ADC_buf_copy[0][i], sizeof(ADC_buf_copy[0][i]));
            
            file.write((const int32_t *)&ADC_buf_copy[0][i], sizeof(ADC_buf_copy[0][i]));    
            file.write((const int32_t *)&ADC_buf_copy[1][i], sizeof(ADC_buf_copy[1][i]));
            file.write((const int32_t *)&ADC_buf_copy[2][i], sizeof(ADC_buf_copy[2][i]));
            file.write((const int32_t *)&ADC_buf_copy[3][i], sizeof(ADC_buf_copy[3][i]));
            file.write((const int32_t *)&ADC_buf_copy[4][i], sizeof(ADC_buf_copy[4][i]));
            file.write((const int32_t *)&ADC_buf_copy[5][i], sizeof(ADC_buf_copy[5][i]));
            file.write((const int32_t *)&ADC_buf_copy[6][i], sizeof(ADC_buf_copy[6][i]));
            file.write((const int32_t *)&ADC_buf_copy[7][i], sizeof(ADC_buf_copy[7][i]));
            file.write((const int32_t *)&ADC_buf_copy[8][i], sizeof(ADC_buf_copy[8][i]));
            file.write((const int32_t *)&ADC_buf_copy[9][i], sizeof(ADC_buf_copy[9][i]));
            file.write((const int32_t *)&ADC_buf_copy[10][i], sizeof(ADC_buf_copy[10][i]));
            file.write((const int32_t *)&ADC_buf_copy[11][i], sizeof(ADC_buf_copy[11][i]));
            file.write((const int32_t *)&ADC_buf_copy[12][i], sizeof(ADC_buf_copy[12][i]));
            file.write((const int32_t *)&ADC_buf_copy[13][i], sizeof(ADC_buf_copy[13][i]));
            file.write((const int32_t *)&ADC_buf_copy[14][i], sizeof(ADC_buf_copy[14][i]));
            file.write((const int32_t *)&ADC_buf_copy[15][i], sizeof(ADC_buf_copy[15][i]));
            file.write((const int32_t *)&ADC_buf_copy[16][i], sizeof(ADC_buf_copy[16][i]));
            
            // file.write((const int32_t *)&ADC_buf_copy[17][i], sizeof(ADC_buf_copy[17][i]));
            // file.write((const int32_t *)&ADC_buf_copy[18][i], sizeof(ADC_buf_copy[18][i]));
            // file.write((const int32_t *)&ADC_buf_copy[19][i], sizeof(ADC_buf_copy[19][i]));
            // file.write((const int32_t *)&ADC_buf_copy[20][i], sizeof(ADC_buf_copy[20][i]));
            // file.write((const int32_t *)&ADC_buf_copy[21][i], sizeof(ADC_buf_copy[21][i]));
            // file.write((const int32_t *)&ADC_buf_copy[22][i], sizeof(ADC_buf_copy[22][i]));
            // file.write((const int32_t *)&ADC_buf_copy[23][i], sizeof(ADC_buf_copy[23][i]));
            // file.write((const int32_t *)&ADC_buf_copy[24][i], sizeof(ADC_buf_copy[24][i]));
            

            // file.write((const uint8_t *)&ADC_buf_copy, sizeof(ADC_buf_copy));
            // file.print(ADC_buf_copy[0][i]);
            // file.print(",");
            // file.print(ADC_buf_copy[1][i]);
            // file.print(",");
            // file.print(ADC_buf_copy[2][i]);
            // file.print(",");
            // file.print(ADC_buf_copy[3][i]);
            // file.print(",");
            // file.print(ADC_buf_copy[4][i]);
            // file.print(",");
            // file.print(ADC_buf_copy[5][i]);
            // file.print(",");
            // file.print(ADC_buf_copy[6][i]);
            // file.print(",");
            // file.print(ADC_buf_copy[7][i]);
            // file.print(",");
            // file.print(ADC_buf_copy[8][i]);
            // file.print(",");
            // file.print(ADC_buf_copy[9][i]);
            // file.print(",");
            // file.print(ADC_buf_copy[10][i]);
            // file.print(",");
            // file.print(ADC_buf_copy[11][i]);
            // file.print(",");
            // file.print(ADC_buf_copy[12][i]);
            // file.print(",");
            // file.print(ADC_buf_copy[13][i]);
            // file.print(",");
            // file.print(ADC_buf_copy[14][i]);
            // file.print(",");
            // file.print(ADC_buf_copy[15][i]);
            // file.print(",");
            // file.print(ADC_buf_copy[16][i]);
            // file.print(",");
            // file.print(ADC_buf_copy[17][i]);
            // file.print(",");
            // file.print(ADC_buf_copy[18][i]);
            // file.print(",");
            // file.print(ADC_buf_copy[19][i]);
            // file.print(",");
            // file.print(ADC_buf_copy[20][i]);
            // file.print(",");
            // file.print(ADC_buf_copy[21][i]);
            // file.print(",");
            // file.print(ADC_buf_copy[22][i]);
            // file.print(",");
            // file.print(ADC_buf_copy[23][i]);
            // file.print(",");
            // file.print(ADC_buf_copy[24][i]);
            // file.println();
        }
        file.close();
    } else {
        Serial.println("error opening datalog.dat");
    }

}