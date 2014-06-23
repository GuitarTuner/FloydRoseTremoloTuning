# -*- coding: utf-8 -*-
"""
Created on Fri Jun 06 16:25:48 2014

@author: Arnaud
"""

import sys
from PyQt4 import QtGui, uic
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
import matplotlib.pyplot as plt
import os
import numpy as np
import scipy.io.wavfile as wavfile
from scipy import fft
import pyaudio
import wave

from pylab import diff, sign, arange

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
WAVE_OUTPUT_FILENAME = "output.wav"

freq_th = np.array([82.4,110,146.8,196,246.9,329.5])

class MplFigure(object):
    def __init__(self, parent):
        self.figure = plt.figure(facecolor='white')
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, parent)

class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        
        # load the UI from the disk
        self.ui = uic.loadUi("Accordeur.ui", self)

        # customize the UI
        self.initUI()
        
        # init class data
        self.initData()       
        
        # connect slots
        self.connectSlots()
        
    def initUI(self):
         # prep tab
        self.prep_ui = MplFigure(self)
        layout = self.ui.tab_1.layout()
        layout.addWidget(self.prep_ui.toolbar)
        layout.addWidget(self.prep_ui.canvas)
        
        # accor tab
        self.accor_ui = MplFigure(self)
        layout = self.ui.tab_2.layout()
        layout.addWidget(self.accor_ui.toolbar)
        layout.addWidget(self.accor_ui.canvas)
        
        
    def initData(self):
        pass
        
    def connectSlots(self):
        # Bouton pour première acquisition
        self.ui.pushButton.clicked.connect(self.prem_acquisition)
        # Bouton pour deuxième acquisition
        self.ui.pushButton_2.clicked.connect(self.sec_acquisition)
        # Bouton pour troisième acquisition
        self.ui.pushButton_3.clicked.connect(self.ter_acquisition)
        # Bouton pour accordage mi grave
        self.ui.pushButton_4.clicked.connect(self.migrave)
        # Bouton pour accordage la
        self.ui.pushButton_4.clicked.connect(self.la)
        # Bouton pour accordage re
        self.ui.pushButton_4.clicked.connect(self.re)
        # Bouton pour accordage sol
        self.ui.pushButton_4.clicked.connect(self.sol)
        # Bouton pour accordage si
        self.ui.pushButton_4.clicked.connect(self.si)
        # Bouton pour accordage mi aigu
        self.ui.pushButton_4.clicked.connect(self.miaigu)
        
    def recordSound(self):
        """ records a sound
        code is taken from http://people.csail.mit.edu/hubert/pyaudio/
        """
                
        p = pyaudio.PyAudio()
        
        TIME = self.ui.spinBox_8.value()

        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)
        
        print("* recording")
        
        frames = []
        
        for i in range(0, int(RATE / CHUNK * TIME)):
            data = stream.read(CHUNK)
            frames.append(data)
        
        print("* done recording")
        
        stream.stop_stream()
        stream.close()
        p.terminate()
        

        wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
    
        (sample_freq, data) = wavfile.read(WAVE_OUTPUT_FILENAME)
        
        # temps
        plt.figure(self.main_figure.figure.number)
        plt.clf()
        ax = self.main_figure.figure.add_subplot(211)
        ax.plot(arange(data[:, 0].shape[0]) / float(sample_freq), data[:, 0], label='channel 1')
        ax.plot(arange(data[:, 1].shape[0]) / float(sample_freq), data[:, 1], label='channel 2')
        ax.set_ylim(-32768, 32768)
        ax.legend()
        ax.set_xlabel(u'temps (s)')
        
        # fréquence
        ax = self.main_figure.figure.add_subplot(212)
        from scipy.fftpack import fftfreq
        freq_vect = fftfreq(data[:, 0].size) * sample_freq
        ax.plot(freq_vect, abs(fft(data[:, 0])), label='channel 1')
        ax.plot(freq_vect, abs(fft(data[:, 1])), label='channel 2')
        ax.set_xlim(0, sample_freq/2.)
        ax.legend()
        ax.set_xlabel(u'fréquence (Hz)')
        
        # mise à jour du graphique        
        plt.tight_layout()
        self.ui.main_figure.canvas.draw()
        
        # on garde les données
        self.sample_freq = sample_freq
        self.data = data
        
    def analyzeSound(self):
        """ highlights N first peaks in frequency diagram
        """
        # on recharge les données 
        data = self.data
        sample_freq = self.sample_freq
        from scipy.fftpack import fftfreq
        freq_vect = fftfreq(data.size) * sample_freq
        
        # on trouve les maxima
        y0 = abs(fft(data))
#        y1 = abs(fft(data[:, 1]))
        maxi0 = ((diff(sign(diff(y0))) < 0) & (y0[1:-1] > y0.max()/10.)).nonzero()[0] + 1 # local max
        # maxi1 = ((diff(sign(diff(y1))) < 0) & (y1[1:-1] > y1.max()/10.)).nonzero()[0] + 1 # local max
        
        # fréquence
#        ax = self.main_figure.figure.add_subplot(212)
#        ax.plot(freq_vect[maxi0], y0[maxi0], "o")
#        # ax.plot(freq_vect[maxi1], y1[maxi1], "o")
        
        # annotations au dessus d'une fréquence de coupure
        fc = 100.
        max_freq = []
        freq_vect_2 = freq_vect[maxi0]
        maxy0 = y0[maxi0]
        maxy0_list = maxy0.tolist()
        while np.size(max_freq) < 12 :
            F = np.argmax(maxy0_list)
            maxy0_list[F] = 0
            if np.abs(freq_vect_2[F]) > fc :
                max_freq.append(F)
            for i in range(0,4) :
                if (F+2-i) in range (1,len(maxy0_list)) and np.abs(freq_vect_2[F+2-i]-freq_vect_2[F]) < 4 :
                    maxy0_list[F+2-i] = 0
                    
        for point in max_freq:
            plt.annotate("%.2f" % freq_vect_2[point], (freq_vect_2[point], maxy0[point]))
        ax = self.main_figure.figure.add_subplot(212)
        ax.plot(freq_vect_2[max_freq], maxy0[max_freq], "o")
        
#        for point in maxi1[(freq_vect[maxi0] > fc).nonzero()][:self.ui.spinBox.value()]:
#            plt.annotate("%.2f" % freq_vect[point], (freq_vect[point], y1[point]))
#        
        self.ui.main_figure.canvas.draw()
        return(freq_vect_2[max_freq])
        
    def prem_acquisition(self) :
        self.recordSound()
        freq_vect = self.analyzeSound()
        f1 = []
        for point in freq_vect:
            for f in range(int(point/2)-1,int(point/2)+2):
                if f not in freq_vect and len(f1) < 6:
                    np.append(f1,point)
                    
        self.label_5.setText("Désaccorder sensiblement la corde de mi grave et \
        procéder à la deuxième acquisition")
        return(f1)

    def sec_acquisition(self) :
        self.recordSound()
        freq_vect = self.analyzeSound()
        f2 = []
        for point in freq_vect:
            for f in range(int(point/2)-1,int(point/2)+2):
                if f not in freq_vect and len(f2) < 6:
                    np.append(f2,point)
                    
        self.label_5.setText("Désaccorder sensiblement la corde de la et \
        procéder à la troisième acquisition.")
        return(f2)
        
    def ter_acquisition(self) :
        self.recordSound()
        freq_vect = self.analyzeSound()
        f3 = []
        for point in freq_vect:
            for f in range(int(point/2)-1,int(point/2)+2):
                if f not in freq_vect and len(f3) < 6:
                    np.append(f3,point)
        (f1,f2) = (self.prem_acquisition(self),self.sec_acquisition(self))
        P = self.prep()
        (T1,T2,T3) = (P*f1,P*f2,P*f3)
        (DT1,DT2) = (T2-T1,T3-T2)
        DT = np.sum(DT1)
        rho = - np.array([(DT1[3]*DT2[1])/(DT*DT2[3]),DT1[2]/DT,DT1[3]/DT,\
        DT1[4]/DT,DT1[5]/DT,DT1[6]/DT])
        
        self.label_5.setText("L'acquisition des données est maintenant terminée\
        Procéder à l'accordage dans l'onglet suivant.")
        return (f3,rho)
         
        
    def prep(self) :
        Long_cons = self.ui.spinBox.value()
        Long_r = self.ui.spinBox_10.value()
        Tension = np.array([self.ui.spinBox_2.value(), self.ui.spinBox_3.value(),self.ui.spinBox_4.value(),\
        self.ui.spinBox_5.value(),self.ui.spinBox_6.value(),self.ui.spinBox_7.value()])
        masse_l = Tension/(4*Long_cons**2*np.square(freq_th))
        psi = 4*masse_l*Long_r**2
        return(psi)
        
    def chemin(self):
        (f3,rho) = self.ter_acquisition()
        P = self.prep()
        DF_voulu = np.square(freq_th)-np.square(f3)
        M = np.eye(6,6)
        for i in range(1,6):
            for j in range (1,6):
                if j != i:
                    M[i,j] = -(P[i]/P[j])*rho[i]/(1+np.sum(rho)-rho[j])
        DF_app = np.dot(np.linalg.inv(M),DF_voulu)
        return(DF_app,M)
        
    def migrave(self):
        (DF_app,M) = self.chemin()
        DF_app_1 = np.array([DF_app[1],0,0,0,0,0])
        f0 = self.ter_acquisition()[1]
        f1 = np.sqrt(np.square(f0)+np.dot(M,DF_app_1))
        self.recordSound()
        data=self.data
        sample_freq = self.sample_freq
        from scipy.fftpack import fftfreq
        freq_vect = fftfreq(data.size) * sample_freq
        y0 = abs(fft(data))
        f_mes = freq_vect[np.argmax(y0)]
        if abs(f_mes-f1[1]) < 1 :
            return (f1)
            self.label_7.setText("La corde de mi grave est à la bonne fréquence. Passer à la \
            corde de la")
        elif f1[1] > f_mes:
            self.label_7.setText("Plus haut")
        else:
            self.label_7.setText("Plus bas")
            
    def la(self):
        (DF_app,M) = self.chemin()
        DF_app_2 = np.array([0,DF_app[2],0,0,0,0])
        f0 = self.migrave()
        f1 = np.sqrt(np.square(f0)+np.dot(M,DF_app_2))
        self.recordSound()
        data=self.data
        sample_freq = self.sample_freq
        from scipy.fftpack import fftfreq
        freq_vect = fftfreq(data.size) * sample_freq
        y0 = abs(fft(data))
        f_mes = freq_vect[np.argmax(y0)]
        if abs(f_mes-f1[2]) < 1 :
            return (f1)
            self.label_7.setText("La corde de la est à la bonne fréquence. Passer à la \
            corde de ré")
        elif f1[2] > f_mes:
            self.label_7.setText("Plus haut")
        else:
            self.label_7.setText("Plus bas")
    
    def re(self):
        (DF_app,M) = self.chemin()
        DF_app_3 = np.array([0,0,DF_app[3],0,0,0])
        f0 = self.la()
        f1 = np.sqrt(np.square(f0)+np.dot(M,DF_app_3))
        self.recordSound()
        data=self.data
        sample_freq = self.sample_freq
        from scipy.fftpack import fftfreq
        freq_vect = fftfreq(data.size) * sample_freq
        y0 = abs(fft(data))
        f_mes = freq_vect[np.argmax(y0)]
        if abs(f_mes-f1[3]) < 1 :
            return (f1) 
            self.label_7.setText("La corde de ré est à la bonne fréquence. Passer à la \
            corde de sol")
        elif f1[3] > f_mes:
            self.label_7.setText("Plus haut")
        else:
            self.label_7.setText("Plus bas")
        
    def sol(self):
        (DF_app,M) = self.chemin()
        DF_app_4 = np.array([0,0,0,DF_app[4],0,0])
        f0 = self.re()
        f1 = np.sqrt(np.square(f0)+np.dot(M,DF_app_4))
        self.recordSound()
        data=self.data
        sample_freq = self.sample_freq
        from scipy.fftpack import fftfreq
        freq_vect = fftfreq(data.size) * sample_freq
        y0 = abs(fft(data))
        f_mes = freq_vect[np.argmax(y0)]
        if abs(f_mes-f1[4]) < 1 :
            return (f1)
            self.label_7.setText("La corde de sol est à la bonne fréquence. Passer à la \
            corde de si")
        elif f1[4] > f_mes:
            self.label_7.setText("Plus haut")
        else :
            self.label_7.setText("Plus bas")
            
    def si(self):
        (DF_app,M) = self.chemin()
        DF_app_5 = np.array([0,0,0,0,DF_app[5],0])
        f0 = self.sol()
        f1 = np.sqrt(np.square(f0)+np.dot(M,DF_app_5))
        self.recordSound()
        data=self.data
        sample_freq = self.sample_freq
        from scipy.fftpack import fftfreq
        freq_vect = fftfreq(data.size) * sample_freq
        y0 = abs(fft(data))
        f_mes = freq_vect[np.argmax(y0)]
        if abs(f_mes-f1[5]) < 1 :
            return (f1)
            self.label_7.setText("La corde de si est à la bonne fréquence. Passer à la \
            corde de mi aigu")
        elif f1[5] > f_mes:
            self.label_7.setText("Plus haut")
        else :
            self.label_7.setText("Plus bas")
            
    def miaigu(self):
        (DF_app,M) = self.chemin()
        DF_app_6 = np.array([0,0,0,0,0,DF_app[6]])
        f0 = self.si()
        f1 = np.sqrt(np.square(f0)+np.dot(M,DF_app_6))
        self.recordSound()
        data=self.data
        sample_freq = self.sample_freq
        from scipy.fftpack import fftfreq
        freq_vect = fftfreq(data.size) * sample_freq
        y0 = abs(fft(data))
        f_mes = freq_vect[np.argmax(y0)]
        if abs(f_mes-f1[6]) < 1 :
            return (f1)
            self.label_7.setText("Votre guitare est parfaitement accordée! Félicitations!")
        elif f1[6] > f_mes:
            self.label_7.setText("Plus haut")
        else :
            self.label_7.setText("Plus bas")
            
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())