# Project 6: Respiration Monitoring in Sleep Positions











# Contents
[Introduction](#_Toc107932681)

[Hardware](#_Toc107932682)

[Firmware](#_Toc107932683)

[Data acquisition](#_Toc107932684)

[Signal processing](#_Toc107932685)

[Machine learning model](#_Toc107932689)






















##

## Introduction
The aim of the project is to develop a system able to correctly classify four different sleep positions using an accelerometer. From the accelerometer we had to extract information about the respiration rate and, from these data, perform a classification with different machine learning algorithms.  

The steps of the project will be: 

- Development of a wearable device, where the accelerometer will be positioned on the chest of the subject;
- Data acquisition: following the specific protocol;
- Data processing (filtering and extraction of respiratory rate);
- Development of a Machine Learning algorithm to correctly classify the position of a subject from the signal. 

## Hardware
The components used to perform this project are: 

- PSoC
- 3-axis accelerometer (LIS3DH)
- Bluetooth module (HC-06)
- LEDs (red and blue)
- 9V battery
- Switch
- Voltage regulator (LM340T5)

To create the hardware of the system we first realized it on a breadboard and used the connections to design the printed circuit board (PCB). 

![](https://github.com/ltebs-polimi/AY2122_II_Project-6/blob/master/img/2.png)

![](https://github.com/ltebs-polimi/AY2122_II_Project-6/blob/master/img/3.png)

To do so, we realized the schematic and the board design on eagle, selecting the correct components to be used. Once the PCB design was done, we were able to produce the physical board with a process of acid etching, on which we soldered all the components. 

The switch allows to turn on and off the system without removing the battery. Initially there were a voltage divider to reduce the input voltage from 9V to 5V but was replaced with the voltage regulator due to the Bluetooth module not turning on.

![](https://github.com/ltebs-polimi/AY2122_II_Project-6/blob/master/img/4.png)

To contain the PCB we designed in Solidworks a case which was then 3D printed. The initial idea was to apply the case to the chest of the subject to acquire the data, but this idea was then discarded due to the high encumbrance of the case.
![](https://github.com/ltebs-polimi/AY2122_II_Project-6/blob/master/img/5.jpeg)![](https://github.com/ltebs-polimi/AY2122_II_Project-6/blob/master/img/6.jpeg)

The hardware is subdivided into two main parts: PCB and accelerometer. The PCB contain all the physical elements and their connections, while the accelerometer is stitched on a strap and is connected to the PCB through long cables. 

In this way, we apply the strap on the thorax of the subject, reducing the encumbrance and allowing a free movement of the accelerometer, and the case is kept near the acquisition site.
## Firmware
The accelerometer and the microprocessor communicate with a I2C Master/slave communication and the data are sent with a Bluetooth module. Then, there are two digital output to drive two LED. The first one (blue) turns ON when the accelerometer is sampling, the second one (red) turns ON if some error occurs in the communication with the accelerometer. 

When the device turns on, the microprocessor reads and writes the registers of the accelerometer.
We set the sampling frequency (CTRL\_REG1) at 50 Hz, the Full Scale Range (CTRL\_REG4) at +-2g and we enable the FIFO mode.   

The device is in the “waiting” status in which the accelerometer is not sampling and the FIFO register is empty. 

When the user sends a “start” signal, the device starts sampling for three minutes (according to the protocol for collecting the data), the blue light turns on and the data is saved in the FIFO register. 
When the register is full, we send the data with the Bluetooth module and reset the FIFO register. After three minutes the procedures stops and the device returns in the “waiting” status. 

If an error occurs during the sampling procedure, the sampling stops and the red LED turns on. It is possible to stop the sampling even with a “stop” signal. 

## Data acquisition
The protocol for the data acquisition consists in collecting data of 10 people in 4 different positions (supine, prone, lateral left, lateral right). Each subject must keep the position for 3 minutes. 

To make the procedure easier we implement a graphical interface in which the user can communicate with the device. 

![](https://github.com/ltebs-polimi/AY2122_II_Project-6/blob/master/img/7.png)

The user has to choose a port and connect to it. The application allows also to rescan the port or disconnect to the port if needed. 

![](https://github.com/ltebs-polimi/AY2122_II_Project-6/blob/master/img/8.png)

Then the user has to choose the position of the subject and starts the sampling. It is possible also to stop the sampling. 

![](https://github.com/ltebs-polimi/AY2122_II_Project-6/blob/master/img/9.png)

After three minutes the data is saved as ‘.csv’ in a specific folder. The data are automatically saved and labelled and every sampling has its own file. It is possible to change the position of the subjects and start another sampling. 

![](https://github.com/ltebs-polimi/AY2122_II_Project-6/blob/master/img/10.png)

The ‘.csv’ file contains all the data of the three axis and the position of the subject. These files will be then processed to obtain the information about the respiratory signal. 

## Signal processing

### Introduction
In order to process the data to extract the respiration signal and consequently the reparation rate, we have tried two different approaches, both based on data normalization and filtering data with Moving-average and Butterworth filters.

The main difference between these two methods regards the computation of the respiration rate:

- chest\_2.mat: compute the respiration rate based on pick coating function;
- F\_br.mat and PY\_file\_BR.py: compute the respiration rate based on fast Fourier transform.

` `We decided to adopt the second approach, basing on literature reviews.



### Explanation of the principal steps
` `The following are the main steps used in the algorithm:

\1.  Z-TRANSFORM AND WINDOWING

![](https://github.com/ltebs-polimi/AY2122_II_Project-6/blob/master/img/11.png)

In order to smooth and compare the data, a Z-normalization is applied. Based on a preliminary analysis of the raw-data plot, we choose only the horizontal component (X,Y axis) of the acceleration to extract the respiration signal, because the Z axis is most influenced by the tone sound vibration of the heart. (2)

` `Looking to the final aim of the ML analysis, we decide to divide any posture registration of 3 minutes in 3 windows of 60 seconds. In this way, from any registration of each posture, we obtain 3 signals of one minutes enlarging the dataset having 12 signals for each recorded volunteer (instead of 4).

The further analysis is applied to a 60 second window.

\2. FILTERING

We have filtered transformed raw-data in 60 seconds window applying a cascade of filter:

- Moving-Average Filtering: to reduce the noise, we have applied a Moving average filter on a window of length corresponding to a maximal breathing rate (40 breaths/min).

|Average window size |(40/60) x Sampling Frequencies |
| :- | :- |


![](https://github.com/ltebs-polimi/AY2122_II_Project-6/blob/master/img/12.png)







- Butterworth Filtering: the respiration frequencies in physiological condition can vary from 8 to 40 breaths for minutes (0.13-0.66 HZ). Therefore to extract the respiration signal we need to enhance this range of frequencies applying a Butterworth filter with parameters that are reported in the table. 

|FILTER ORDER|LOW F. (Hz)|HIGH F. (Hz)|
| :-: | :-: | :-: |
|4|0.05|0.66|



![](https://github.com/ltebs-polimi/AY2122_II_Project-6/blob/master/img/13.png)







- BR selection: from the filtered signal we compute the Fast Fourier transform in order to make a frequency analysis. Subsequently, computing its power spectrum it is possible to select the breathing rate looking at the range of frequencies corresponding to physiological one (8-40 breath/min). This corresponds to the maximal in that range.


![](https://github.com/ltebs-polimi/AY2122_II_Project-6/blob/master/img/14.png)






### Time and frequencies index extraction
In order to make further analysis on the signal, especially the classification purpose, we create a final dataset in which we report different time and frequencies domain index computed on the signal.  

After computed the principal index for ML analysis (4) reported in the table, we merge all the created dataset to proceed further.

## Machine learning model
For the classification we explored different ways. 

First, we tried to classify with the raw data coming from the accelerometer, we reached an accuracy of 100% mainly because of the orientation of the gravity acceleration that gives the major contribute to the signal.  

Then, we used the information about the respiration only to classify the position. 

We tried to classify the position from the respiration signal, but the classification didn’t perform very well, so we decided to use the information about the respiration signal (mean, variance...). 

1. Univariate analysis: we removed the outlier to the variables that had a Gaussian distribution and we tried to normalize the other distributions. 
1. Multivariate analysis: we removed from the dataset the variables with high linear correlation and the variables which show a pattern in the bivariate distribution. Then, we performed a PCA.
1. X and y dataset: after the standardization we split the dataset into y and x. The first one is the dataset containing the target (‘supine’, ‘prone’, ‘lateral R’, ‘lateral L’). The second one is the dataset containing the variables. We divided these datasets into train (70%) and test (30%). 
1. Machine Learning methods: we explore different ML methods. For each of them we select the best parameters with a function, in order to perform the best classification. We explore:
   1. KNN (k-Nearest Neighbour)
   1. Decisional Tree
   1. Naïve-Bayes classifier
   1. Logistic regression
   1. Multi-layer Perceptron Classifier
   1. Linear support vector classifier
   1. Random Forest

## Repository structure
