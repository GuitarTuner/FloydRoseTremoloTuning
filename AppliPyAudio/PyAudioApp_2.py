# -*- coding: utf-8 -*-
"""
Created on May 23 2014

@author: florian
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

class MplFigure(object):
    def __init__(self, parent):
        self.figure = plt.figure(facecolor='white')
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, parent)

class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        
        # load the UI from the disk
        self.ui = uic.loadUi("PyAudioApp.ui", self)

        # customize the UI
        self.initUI()
        
        # init class data
        self.initData()       
        
        # connect slots
        self.connectSlots()
        
    def initUI(self):
        # main figure
        self.main_figure = MplFigure(self)
        layout = self.ui.centralwidget.layout()
        layout.addWidget(self.main_figure.toolbar)
        layout.addWidget(self.main_figure.canvas)
        self.ui.centralwidget.setLayout(layout)
     
    def initData(self):
        pass
        
    def connectSlots(self):
        # button for recording
        self.ui.pushButton_2.clicked.connect(self.recordSound)
        # button for analyzing current data
        self.ui.pushButton.clicked.connect(self.analyzeSound)

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
            print(freq_vect_2[F])
            if np.abs(freq_vect_2[F]) > fc :
                max_freq.append(F)
            for i in range(0,4) :
                if (F+2-i) in range (1,len(maxy0_list)) and np.abs(freq_vect_2[F+2-i]-freq_vect_2[F]) < 4 :
                    maxy0_list[F+2-i] = 0
                    
        print(freq_vect_2[max_freq])
        for point in max_freq:
            plt.annotate("%.2f" % freq_vect_2[point], (freq_vect_2[point], maxy0[point]))
        ax = self.main_figure.figure.add_subplot(212)
        ax.plot(freq_vect_2[max_freq], maxy0[max_freq], "o")
        
#        for point in maxi1[(freq_vect[maxi0] > fc).nonzero()][:self.ui.spinBox.value()]:
#            plt.annotate("%.2f" % freq_vect[point], (freq_vect[point], y1[point]))
#        
        self.ui.main_figure.canvas.draw()
        
        
    def recordSound(self):
        """ records a sound
        code is taken from http://people.csail.mit.edu/hubert/pyaudio/
        """
        RECORD_SECONDS = self.ui.spinBox_2.value()        
        
        p = pyaudio.PyAudio()

        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)
        
        print("* recording")
        
        frames = []
        
        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
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
        ax.plot(arange(data.shape[0]) / float(sample_freq), data, label='channel 1')
        # ax.plot(arange(data.shape[0]) / float(sample_freq), data, label='channel 2')
        ax.set_ylim(-32768, 32768)
        ax.legend()
        ax.set_xlabel(u'temps (s)')
        
        # fréquence
        ax = self.main_figure.figure.add_subplot(212)
        from scipy.fftpack import fftfreq
        freq_vect = fftfreq(data.size) * sample_freq
        ax.plot(freq_vect, abs(fft(data)), label='channel 1')
        # ax.plot(freq_vect, abs(fft(data[:, 1])), label='channel 2')
        ax.set_xlim(0, sample_freq/2.)
        ax.legend()
        ax.set_xlabel(u'fréquence (Hz)')
        
        # mise à jour du graphique        
        plt.tight_layout()
        self.ui.main_figure.canvas.draw()
        
        # on garde les données
        self.sample_freq = sample_freq
        self.data = data
    
                                        
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())