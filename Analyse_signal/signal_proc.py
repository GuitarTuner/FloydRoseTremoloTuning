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

import Tkinter

import numpy as np
Guitare = ["mi(grave)","la","ré","sol","si","mi(aigu)"]
Freq_notes = [82.4,110,146.8,196,246.9,329.5]

""" Première partie : enregistrement d'un signal au micro"""

def record(CHANNELS,TIME,OUTPUT):
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
   
#Création d'un fichier .wav intermédiaire qui permet une analyse plus facile par la suite (tableau de complexes)
    wf = wave.open(OUTPUT, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

""" Deuxième partie : analyse spectrale pour récupérer la note jouée"""

### Construction of the cepstrum of the signal ###
def cepstrum(signal):
    Fsig = np.fft.fft(signal)   #transformée de Fourier du signal
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
    Corde = "Fausse"
    for i in [0,1,2,3,4,5]:
        if fond >= (Freq_notes[i]-0.1) and fond <= (Freq_notes[i]+0.1): #on vérifie que la fréquence mesurée est une fondamentale de guitare à 0.1Hz près
            Corde = Guitare[i]
    return Corde
 
 
""" Fonction globale """

def Accordeur(CHANNELS,TIME,OUTPUT):
    record(CHANNELS,TIME,OUTPUT)        #enregistre le signal du micro et crée le fichier .wav
    signal = np.fromfile(open(OUTPUT),np.int8)[24:]     #récupére le signal sous formes d'une liste de complexes
    fondamentale = pitch(cepstrum(signal),RATE)     #calcule la fréquence fondamentale de ce signal
    Results=[note(fondamentale),"La note jouee a pour frequence fondamentale\
    : "+str(fondamentale)+"Hz"]
    return(Results)
    
""" Interface graphique """

class Accor_graph(Tkinter.Tk):              #Classe de notre interface
    def __init__(self,parent):              #Initialisation de l'interface
        Tkinter.Tk.__init__(self,parent)
        self.parent=parent                  #Référence sur le répertoire parent
        self.initialize()
        
        
    def initialize(self):       #Création de la fenêtre
        self.grid()             #Grille pour le placement des widgets
        
#Champ de texte fixe qui indique la consigne à suivre pour le canal       
        label_channel = Tkinter.Label(self,text="CHANNELS (1:Mono, 2:Stereo)",\
        anchor='w',bg='white',fg='black')   
        label_channel.grid(row=0,column=0,sticky='EW')

#Champ de texte que l'on peut modifier pour indiquer le nombre de canaux sur lequel on travaille
        self.entryVariable_channel = Tkinter.IntVar()           
        self.entry_channel = Tkinter.Entry(self,textvariable=\
        self.entryVariable_channel)
        self.entry_channel.grid(row=0,column=1)
        
#Champ de texte fixe qui indique la consigne à suivre pour le temps d'enregistrement        
        label_time = Tkinter.Label(self,text="Durée de l'enregistrement\
        (secondes)",anchor='w',bg='white',fg='black')
        label_time.grid(row=1,column=0,sticky='EW')
#Champ de texte que l'on peut modifier pour indiquer la durée pendant laquelle le micro va enregistrer
        self.entryVariable_time = Tkinter.IntVar()
        self.entry_time = Tkinter.Entry(self,textvariable=\
        self.entryVariable_time)
        self.entry_time.grid(row=1,column=1)
        
#Champ de texte fixe qui indique la consigne à suivre pour le fichier intermédiaire
        label_output = Tkinter.Label(self,text="Fichier de sortie (.wav)",\
        anchor='w',bg='white',fg='black')
        label_output.grid(row=2,column=0,sticky='EW')

#Champ de texte que l'on peut modifier pour indiquer le nom du fichier intermédiaire dans lequel on socke l'enregistrement        
        self.entryVariable_output = Tkinter.StringVar()
        self.entry_output = Tkinter.Entry(self,textvariable=\
        self.entryVariable_output)
        self.entry_output.grid(row=2,column=1)
        
#Création du bouton de lancemen de la procédure d'enregistrement et d'accordage        
        button_Accord = Tkinter.Button(self,text="Démarrer l'accordage",\
        command=self.Start)
        button_Accord.grid(row=3,column=0)
        
#Champ de texte variable où l'on vient inscrire si l'accord est correct ou pas     
        self.labelVariable_note = Tkinter.StringVar()
        label_note = Tkinter.Label(self,textvariable=\
        self.labelVariable_note,anchor="w",fg="black",bg="green")
        label_note.grid(row=3,column=1,sticky='EW')
        
#Champ de texte variable où l'on vient indiquer la fréquence fondamentale de la note jouée        
        self.labelVariable_results = Tkinter.StringVar()
        label_results = Tkinter.Label(self,textvariable=\
        self.labelVariable_results,anchor="w",fg="black",bg="yellow")
        label_results.grid(row=4,column=0,columnspan=2,sticky='EW')
        
        
        self.columnconfigure(0,weight=1)    #indique que l'on étire la première colonne quand on modifie la taille de la fenêtre
        self.resizable(True,False)      #on peut modifier la taille de la fenêtre horizontalement mais pas verticalement
        self.update()       #actualise la géométrie
        self.geometry(self.geometry())  #fixe la géométrie de la fenêtre pour éviter qu'elle s'agrandisse quand on rentre un texte trop long par exemple
        
# Action qui lance la procédure d'accordage                
    def Start(self):
        self.CHANNELS = self.entryVariable_channel.get() #on récupére le nombre de canaux du champ texte
        self.TIME = self.entryVariable_time.get()   #on récupére le temps d'enregistrement
        self.OUTPUT = self.entryVariable_output.get()+".wav" #et le nom du fichier
        self.entry_channel.focus_set()      #sélectionne le champ texte pour relancer plus facilement la procédure
        self.entry_channel.selection_range(0, Tkinter.END)
        self.entry_time.focus_set()
        self.entry_time.selection_range(0, Tkinter.END)
        self.entry_output.focus_set()
        self.entry_output.selection_range(0, Tkinter.END)
        self.RESULTS = Accordeur(self.CHANNELS,self.TIME,self.OUTPUT)
        self.labelVariable_note.set(self.RESULTS[0])
        self.labelVariable_results.set(self.RESULTS[1])
        
#Boucle qui affiche l'interface graphique Accorgraph        
if __name__ == "__main__":
    app=Accor_graph(None)
    app.title('Accorgraph')
    app.mainloop()      #Boucle infinie qui maintient la fenêtre tant qu'on ne la ferme pas et ne réagit qu'aux actions des widgets définis plus haut
