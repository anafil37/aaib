import random
import numpy as np
import paho.mqtt.subscribe as subscribe
import paho.mqtt.publish as publish
import json 
import pandas as pd
import time
import streamlit as st
from streamlit_page import streamlit_app

def process_data(data):
    #amplitude do sonograma
    s_amp = data[0]
    s_amp = np.array(s_amp)
    #vetor tempo sonograma
    s_time = data[1]
    s_time = np.array(s_time)
    #amplitude espetro
    e_amp = data[2]
    e_amp =np.array(e_amp)
    #amplitude espetro
    e_freq = data[3]
    e_freq = np.array(e_freq)

    #criar dataframe
    d1 = {'time': s_time, 'amplitude': s_amp}
    df1 = pd.DataFrame(data=d1)

    d2 = {'frequency':  e_freq, 'amplitude': e_amp}
    df2 = pd.DataFrame(data=d2)

    return [df1, df2]


def run():
    st.set_page_config(page_icon="📥", page_title="Cloud Logger de Instrumentação ")
    st.title("Real-Time Audio Recorder using Paho MQTT")
    st.write("Project developed under the AAIB subject at NOVA SHCOOL")

    if st.button('Start Recording', key='down'):
        st.write("Recording in progress, please wait")
        publish.single("data/aaib/start_recording", payload="start",  hostname="mqtt.eclipseprojects.io")


        print("waiting for data for sonograme")
        msg1 = subscribe.simple( "data/aaib/sonograme", hostname="mqtt.eclipseprojects.io") 
        raw_data_sonograme = json.loads(msg1.payload.decode())
        print("data from sonogram received")


        print("waiting for data for power spectrum")
        msg2 = subscribe.simple( "data/aaib/power", hostname="mqtt.eclipseprojects.io")
        raw_data_power = json.loads(msg2.payload.decode())
        print("data from power spectrum received")
        

        for elm in raw_data_power:
            raw_data_sonograme.append(elm)
        
        data = process_data(raw_data_sonograme)
        df1 = data[0]
        df2 = data[1]
        streamlit_app(data[0], data[1])
    
 
if __name__ == '__main__':
    run()
    
   
