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

#include "InterruptRoutines.h"
#include "project.h"
#include "I2C_Interface.h"

int status=WAITING; 

int32 count;
uint8 ch_received;


CY_ISR(Custom_ISR_RX)
{
    //read the input character
    ch_received = UART_GetChar();
    
    switch(ch_received)
    {
        //Start the sampling when receive the start signal
        case 'a':
        case 'A':
            LED_Status_Write(1);
            status=SAMPLING;
            ch_received = 0;
            break;

        default:
            break;
    }
    
}

