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

#ifndef __LIS3DH_H
    #define __LIS3DH_H

    /**
    *   \brief 7-bit I2C address of the slave device.
    */
    #define LIS3DH_DEVICE_ADDRESS 0x18

    /**
    *   \brief Address of the WHO AM I register
    */
    #define LIS3DH_WHO_AM_I_REG_ADDR 0x0F
    
    /**
    *   \brief WHOAMI return value
    */
    #define LIS3DH_WHOAMI_RETVAL     0x33

    /**
    *   \brief Address of the Status register
    */
    #define LIS3DH_STATUS_REG 0x27

    /**
    *   \brief Address of the Control register 1
    */
    #define LIS3DH_CTRL_REG1 0x20

    /**
    *   \brief Hex value to set normal mode to the accelerator
    */
    #define LIS3DH_NORMAL_MODE_CTRL_REG1 0x47
    
    /**
    *   \brief Hex value to set normal mode (powered off)
    **/
    #define LIS3DH_NORMAL_MODE_OFF_CTRL_REG1 0x07

    /**
    *   \brief  Address of the Temperature Sensor Configuration register
    */
    #define LIS3DH_TEMP_CFG_REG 0x1F 

    #define LIS3DH_TEMP_CFG_REG_ACTIVE 0xC0
   
    /////////////////////////////////////////////////
    //EX.3
    
    // Brief Address of CTRL REG 4
    #define LIS3DH_CTRL_REG4 0x23
        
    // brief Block Data Update (BDU) Flag
    
    #define LIS3DH_CTRL_REG4_BDU_ACTIVE 0x80

    // Brief Address of the ADC output LSB register
    
    #define LIS3DH_OUT_ADC_3L 0x0C

    // Brief Address of the ADC output MSB register
    
    #define LIS3DH_OUT_ADC_3H 0x0D
    ////////////////////////////////////////////////
    #define LIS3DH_X_L 0x28
    #define LIS3DH_X_H 0x29
    #define LIS3DH_Y_L 0x2A
    #define LIS3DH_Y_H 0x2B
    #define LIS3DH_Z_L 0x2C
    #define LIS3DH_Z_H 0x2D
    #define LIS3DH_CNTRL_REG5 0x24
    #define LIS3DH_FIFO 0x2E
    #define LIS3DH_FIFO_SRC 0x2F
#endif


/* [] END OF FILE */
