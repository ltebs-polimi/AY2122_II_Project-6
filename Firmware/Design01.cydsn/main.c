/* ========================================
 *
 * Copyright YOUR COMPANY, THE YEAR
 * All Rights Reserved
 * UNPUBLISHED, LICENSED SOFTWARE.
 *
 * CONFIDENTIAL AND PROPRIETARY INFORMATION
 * WHICH IS THE PROPERTY OF your company.
 *
 * ========================================
*/
#include "project.h"
#include <stdio.h>
#include "I2C_Interface.h"
#include "LIS3DH.h"
#include "InterruptRoutines.h"
#include "Device_driver.h"
#define f_sample 50

int count, tempo; 
extern int status; 
float X_acc = 0, Y_acc = 0, Z_acc = 0;
float X_f, Y_f, Z_f;
uint8_t control_reg; 
ErrorCode error;
char message[50] = {'\0'};

extern _Bool flag_stop;

int main(void)

{
    
    CyGlobalIntEnable;
    isr_RX_StartEx(Custom_ISR_RX);
    Device_start(); //LIS3DH initialization is performed in Device_driver.c
    status=WAITING; 

    //Create data buffer
    uint8_t XData[2]; 
    uint8_t YData[2]; 
    uint8_t ZData[2]; 
    
    //Create output data
    int16 outZ;
    int16 outY;
    int16 outX;
    _Bool ovr=0; 
    
    for(;;){
        
        //Control if there is an error in register reading and turn on a red LED to alert us
        if (error==ERROR){
            Pin_ROSSO_Write(1);
            status = WAITING;
            count = 0;
            LED_Status_Write(0);}
        else {
            Pin_ROSSO_Write(0); }    
        
        
        if(status==WAITING){
            ovr=0; 
            //Turn off the sampling
            control_reg= 0x00; 
            error = I2C_Peripheral_WriteRegister(LIS3DH_DEVICE_ADDRESS,LIS3DH_CTRL_REG1,control_reg);
            //Initialization of the variables
            count=0; 
            tempo=0; 
            LED_Status_Write(0);
            Pin_ROSSO_Write(0);
            //Reset FIFO
            control_reg = 0x00;
            error = I2C_Peripheral_WriteRegister(LIS3DH_DEVICE_ADDRESS,LIS3DH_FIFO,control_reg);
            control_reg = 0x40;
            error = I2C_Peripheral_WriteRegister(LIS3DH_DEVICE_ADDRESS,LIS3DH_FIFO,control_reg);}
            
            
        
        if (status==SAMPLING){
            
            LED_Status_Write(1);
            
            //Turn on the sampling at 50Hz
            control_reg= 0x47; 
            error = I2C_Peripheral_WriteRegister(LIS3DH_DEVICE_ADDRESS,LIS3DH_CTRL_REG1,control_reg);
            
            //We check if the FIFO register is full
            
            u_int8_t fifo_status;
            error=I2C_Peripheral_ReadRegister(LIS3DH_DEVICE_ADDRESS, LIS3DH_FIFO_SRC, &fifo_status);

            //If this condition is fulfilled the FIFO register is full
            if(((fifo_status&0x40)>>6)==1&&(ovr==0)){
                ovr=1; 
            }
            
            //Once the FIFO register is full we send the collected data
            if(ovr){
                
                //Read and print the data
                error=I2C_Peripheral_ReadRegister(LIS3DH_DEVICE_ADDRESS, LIS3DH_X_L, &XData[0]); 
                error=I2C_Peripheral_ReadRegister(LIS3DH_DEVICE_ADDRESS, LIS3DH_X_H, &XData[1]); 

                error=I2C_Peripheral_ReadRegister(LIS3DH_DEVICE_ADDRESS, LIS3DH_Y_L, &YData[0]); 
                error=I2C_Peripheral_ReadRegister(LIS3DH_DEVICE_ADDRESS, LIS3DH_Y_H, &YData[1]);

                error=I2C_Peripheral_ReadRegister(LIS3DH_DEVICE_ADDRESS, LIS3DH_Z_L, &ZData[0]); 
                error=I2C_Peripheral_ReadRegister(LIS3DH_DEVICE_ADDRESS, LIS3DH_Z_H, &ZData[1]);
                
                //If there are no error in the reading we place the collected data in the variables
                if (error==NO_ERROR){
                    outX= (int16) (XData[0] | (XData[1] <<8)) >> 6;
                    outY= (int16) (YData[0] | (YData[1] <<8)) >> 6;
                    outZ= (int16) (ZData[0] | (ZData[1] <<8)) >> 6; 
                    
                    sprintf(message, "%d, %d, %d\n", outX, outY, outZ);  
                    UART_PutString(message);
                    
                    count++; }
                
                //When all the data are read
                if(fifo_status==128){
                    //Reset the FIFO register
                    //Put the LIS3DH in bypass mode
                    control_reg = 0x00;
                    error = I2C_Peripheral_WriteRegister(LIS3DH_DEVICE_ADDRESS,LIS3DH_FIFO,control_reg);
                    //Put the LIS3DH in FIFO mode
                    control_reg = 0x40;
                    error = I2C_Peripheral_WriteRegister(LIS3DH_DEVICE_ADDRESS,LIS3DH_FIFO,control_reg);
                    
                    ovr=0; 
                }
                
            }
            //When we have collected all the data, return in waiting condition
            if (count==180*f_sample){
                status=WAITING; 
                count=0; 
                LED_Status_Write(0);
            }
        }
    }
}        
