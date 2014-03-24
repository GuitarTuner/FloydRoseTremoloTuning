# -*- coding: utf-8 -*-
"""
Created on Wed Mar 19 23:32:06 2014

@author: ordi
"""
### Introduction des données du programme###

import pyaudio
import wave

CHUNK = 1024
FORMAT = pyaudio.paInt16
RATE = 44100 #Hertz

import numpy as np
Guitare = ["mi(grave)","la","ré","sol","si","mi(aigu)"]

""" Première partie : enregistrement d'un signal au micro"""

def record(CHANNELS,TIME):
    p = pyaudio.PyAudio()

    stream = p.open(format = FORMAT, rate=RATE, channels=CHANNELS, input=True,\
    frames_per_buffer=CHUNK) #ouverture du canal micro

    print("recording")

    frames = [] #signal reçu par le micro

    for i in range(0,int(RATE/CHUNK*TIME)):
        data=stream.read(CHUNK) #lecture du signal micro
        frames.append(data)     #écriture du signal dans frames

    print("done recording")

    stream.stop_stream()        #arrêt de la lecture
    stream.close()              #fermeture du canal
    p.terminate()
    
    return(frames)
    
def audio_file(frames,CHANNELS,OUTPUT):
    p=pyaudio.PyAudio()

    wf = wave.open(OUTPUT, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

""" Deuxième partie : analyse spectrale pour récupérer la note jouée"""

### Construction of the cepstrum of the signal ###
def cepstrum(signal):
    #sig = signal[:,1]
    Fsig = np.fft.ftt(signal)   #transformée de Fourier du signal
    c = np.fft.ifft(np.log(np.abs(Fsig))) #cepstrum
    return c

### Détection de la fréquence fondamentale ###
def pitch(cepstrum,sample_freq) :
    mint = sample_freq*0.0025   #borne inf pour la recherche 2.5ms(400Hz)
    maxt = sample_freq*0.02     #borne sup pour la recherche 20ms(50Hz)
    index_max = np.argmax(np.abs(cepstrum[mint:maxt]))
    f0 = sample_freq/(mint+index_max)
    return f0

### Vérification de la note ###
def note(fond):
    guitare = np.genfromtxt('Notes_fondamentales_guitare.txt')
    freq_notes = guitare[1:,0]
    Corde = "Fausse"
    for i in [0,1,2,3,4,5]:
        if fond >= (freq_notes[i]-0.1) and fond <= (freq_notes[i]+0.1):
            Corde = Guitare[i]
    return Corde
 
""" Test """
note_guit = 329.43
print(note(note_guit)) 

""" Fonction globale """

def Accordeur(CHANNELS,TIME):
    frames = record(CHANNELS,TIME)
    fondamentale = pitch(cepstrum(frames),RATE)
    print (note(fondamentale))
    print("La note jouée a pour fréquence fondamentale : "+fondamentale+"Hz")
    
Accordeur(2,10)