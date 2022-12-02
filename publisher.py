# -*- coding: utf-8 -*-
"""
Created on Thu Dec  1 18:25:22 2022

@author: peter
"""

# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""


import pyaudio
import numpy as np
import wave
from scipy.io.wavfile import read
import random
import time
import paho.mqtt.subscribe as subscribe
import paho.mqtt.publish as publish
import json




   
def recorder():
    
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    
    print("start recording")
    
    frames = []
    seconds = 5
    
    for i in range (0 , int(RATE/CHUNK*seconds)):
        data = stream.read(CHUNK)
        frames.append(data)
        
    print("recording stopped")
    
    stream.stop_stream()
    stream.close()
    p.terminate()
    
    print("saving wav file")
    
    wf = wave.open("output.wav",'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
        
    print("file saved with success")

def sonograme():
    fs=44100
    input_data = read("output.wav")
    audio = input_data[1]
    time = np.linspace(0, len(audio) / fs, num=len(audio))
    return [audio, time] 

def power_spectrum():
    input_data = read("output.wav")
    audio = input_data[1]
    ps = np.abs(np.fft.fft(audio))**2
    time_step = 1 / 30
    freqs = np.fft.fftfreq(audio.size, time_step)
    idx = np.argsort(freqs)
    return [freqs[idx], ps[idx]] 

    
def prepare_data_sonograme(df):
    
    print("preparing sonograme data to send")
    
    #sonograma
    array_amplitude= df[0]
    list_amplitude = array_amplitude.tolist()
    array_time = df[1]
    list_time = array_time.tolist()
    
    #convert to 
    final_list = [list_amplitude, list_time]
    data = json.dumps(final_list)
    
    print("data ready to send")
    return data
    
def prepare_data_power(df):  
    
    print("preparing power spectrum data to send")
    
    #espetograma
    array_freq = df[0]
    list_freq= array_freq.tolist()
    array_amp = df[1]
    list_amp = array_amp.tolist()
    
    #criar lista
    final_list = [ list_amp, list_freq ]
    
    #converter para json
    data = json.dumps(final_list)
    print("data ready to send")
    return data
    
    
def run():
    
    print("waiting for start message")
    start_msg = subscribe.simple("data/aaib/start_recording", hostname="mqtt.eclipseprojects.io")
    
    if start_msg.payload.decode() == "start":
    
    #record audio
        recorder()
        
        
        l1 = sonograme()
        data1 = prepare_data_sonograme(l1) 
        publish.single("data/aaib/sonograme", payload=data1,  hostname="mqtt.eclipseprojects.io")
        print("Data from sonograme send to broker with sucess")
        
        
        time.sleep(5)
        
        l2 = power_spectrum()
        data2 = prepare_data_power(l2) 
        time.sleep(10)
        
        publish.single("data/aaib/power", payload=data2,  hostname="mqtt.eclipseprojects.io")
        print("Data from power spectrum send to broker with sucess")
        
    else:
        print("Recording impossible to start")


if __name__ == '__main__':
    run()
         
