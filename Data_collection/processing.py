from re import X
import numpy as np
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt
import math
import statistics
from matplotlib import style
import matplotlib.pyplot as pt
import scipy.fftpack
import scipy as sp
from scipy.stats import zscore
import pandas as pd
from scipy.signal import butter, filtfilt
from scipy import signal
import warnings
warnings.filterwarnings(action="ignore", module="scipy", message="^internal gelsd")

from scipy.signal import butter, sosfilt, sosfreqz

def butter_bandpass(lowcut, highcut, fs, order=4):
        nyq = 0.5 * fs
        low = lowcut / nyq
        high = highcut / nyq
        sos = butter(order, [low, high], analog=False, btype='band', output='sos')
        return sos

def butter_bandpass_filter(data, lowcut, highcut, fs, order=4):
        sos = butter_bandpass(lowcut, highcut, fs, order=order)
        y = sosfilt(sos, data)
        return y

import csv
import os 
import natsort
from natsort import natsorted

mypath = os.getcwd() 
path1='.\\raw_data'
files = [f for f in os.listdir(path1) if not f.startswith('.')]
files = natsorted(files)
files_csv= [f for f in files if f[-3:] == 'csv']
num=1

for f in files_csv:
    data_i= pd.read_csv('.\\raw_data\\'+f)
    print(data_i)
    # signal parameters definition

    #reference axis
    x = abs(data_i['X'].mean())
    y = abs(data_i['Y'].mean())
    z = abs(data_i['Z'].mean())
    

    if x > y and x > z:
        r_axis = 'x'

    if y > x and y > z:
        r_axis = 'y'

    if z > y and z > x:
        r_axis = 'z'

    fs = 50                                              #samplinf frequency
    average_filter_window_duration_br = int((40/60)*fs)  #window avarage (max resp. f) for filtering
    T = 1/fs
    posizione=data_i.at[0,'pos']
    #dataset creation
    data2 = [
        {"BR": 0, "WL": 0, "MAV": 0, "MV": 0, "STD": 0, "RMSE": 0, "Max": 0, "Min": 0, "VAR": 0,
        "SEN": 0, "MDF": 0, "MNF": 0, "Max_p": 0, "Min_p": 0, 'r_axis':'', 'target': posizione }]
    final_dataset = pd.DataFrame(data2)
    print(final_dataset)
    #Z_score Normalization
    for i in range(0,3):
        data_i.iloc[:,i] = sp.stats.zscore(data_i.iloc[:,i])

    #windowing of 60 s
    start_point=0
    end_point=60*50
    window_size = 60*50
    num_windows=0

    j = 0
    while (end_point <= len(data_i)):
        data = data_i.iloc[start_point:end_point,1]
        print(data)
        start_point = start_point + (window_size)
        end_point = start_point + window_size - 1
        num_windows = num_windows + 1

    #avarage filter
        y_acc = np.array(pd.Series(data).rolling(average_filter_window_duration_br).mean())
        y_acc = np.nan_to_num(y_acc)
        t = np.linspace(0, len(y_acc) / fs, len(y_acc))
        print(y_acc)

        #pt.plot(y_acc)
        #pt.show()

        # butter parameters
        order = 4.  # filter order
        nyq = 0.5 * fs;  # Ny frequency
        low = 0.05  # frequencies band of the filter (0.66= 40/60)
        high = 0.66

        #butter filtering between the normal BR (8-40) resp/min
        y_filter = butter_bandpass_filter(y_acc, 0.05, 0.66, 50)

        #pt.plot(y_filter)
        #pt.show()

        # avarage filtering on the signal
        y_filter = np.array(pd.Series(y_filter).rolling(average_filter_window_duration_br).mean())
        y_filter = np.nan_to_num(y_filter)
        #pt.plot(y_filter)
        #pt.show()

        #Analisi in frequenza del segnale e selezione
        #della frequenza principale nel range (8-40)

        acc_data = y_filter[~np.isnan(y_filter)]
        acc_data = sp.signal.detrend(acc_data)
        N = len(acc_data)

        fft_data = sp.fftpack.fft(acc_data)
        f = np.linspace(0, N / fs, N)

        max_amp = 0
        max_index = 0
        index = 0
        for c in fft_data:
            if f[index] < low or f[index] > high:
                index = index + 1
                continue;
            real = np.real(c)
            img = np.imag(c)
            amp = np.sqrt(real * real + img * img)
            if max_amp < amp:
                max_amp = amp
                max_index = index
            index = index + 1

        #Breathing Rate
        BR = f[max_index]
        # calcolo la Wave length (WL) come la sommatoria degli elementi del segnale
        WL= np.sum(y_filter)

        # Mean Absolut Value
        MAV = abs(np.mean(y_filter))
        MV = np.mean(y_filter)

        # standard deviation
        STD = statistics.stdev(y_filter - np.mean(y_filter))

        # Root Mean Square Error
        MSE = mean_squared_error(y_filter[0:len(y_filter) - 1], y_filter[1:len(y_filter)])
        RMSE = math.sqrt(MSE)

        # variance
        VAR = (1 / (len(y_filter) - 1)) * sum(y_filter)

        # min and max signal value
        Max = max(y_filter)
        Min = min(y_filter)

        # Frequencies index

        # Spectral Energy
        a = sum(fft_data)
        real = np.real(a)
        imag = np.imag(a)
        amp = np.sqrt(real * real + imag * imag)
        SEN = pow(amp, 2)

        # Median Frequencies MDF
        MDF = (1 / 2) * amp

        # Mean Frequencies (Central) MNF
        for i in range(0, len(fft_data)):
            MNF = 0
            real = np.real(fft_data[i])
            imag = np.imag(fft_data[i])
            Amp = np.sqrt(real * real + imag * imag)
            MNF = MNF + (f[i] * Amp)

        MNF = MNF / amp

        for i in range(0, len(fft_data)):
            real = np.real(fft_data)
            imag = np.imag(fft_data)
            Amp = np.sqrt(real * real + imag * imag)
            Max_p = max(Amp)
            Min_p = min(Amp)

    # da=[
        #    {"BR": BR,  "WL": WL ,"MAV":  MAV,"MV":  MV, "STD": STD,"RMSE":  RMSE,"Max": Max,"Min":  Min,"Var":  VAR ,
        #    "SEN": SEN, "MDF": MDF,"MNF":  MNF, "Max_p": Max_p, "Min_p": Min_p }
        #]
        final_dataset.loc[j]=[ BR,WL,MAV,MV,STD,RMSE,Max,Min,VAR,SEN,MDF,MNF,Max_p,Min_p, r_axis, posizione]
        j=j+1



    print(final_dataset)
    final_dataset.to_csv('.\processed_data\exa'+str(num)+'.csv', header=True, index=False)
    num=num+1