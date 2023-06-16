import wave
import numpy as np
import matplotlib.pyplot as plt
import sys
from PyQt5.QtWidgets import QApplication,QWidget,QPushButton,QLineEdit,QFormLayout,QGridLayout,QLabel,QScrollArea,QHBoxLayout,QFileDialog,QSizePolicy,QVBoxLayout,QPlainTextEdit
from PyQt5.QtGui import QIcon, QPixmap,QPalette

class Logprompt:
    def __init__(self,nom_fichier,nb_freq,frame):
        self.initialisation_ihm(nb_freq)
        self.analyse_wave(nom_fichier,nb_freq,frame)

    def initialisation_ihm(self,nb_freq):
        self.app=QApplication([])
        self.window=QWidget()
        self.window.setGeometry(1,1,800,800)
        self.window.setWindowTitle("sound_prompt_generator")
        self.app.setStyle('Fusion')
        self.wglobprompt=QPlainTextEdit()
        self.wantiprompt=QPlainTextEdit()
        self.layi=QFormLayout()
        self.wprompt_freq=[]
        sp=""
        for i in range(nb_freq):
            self.wprompt_freq.append(QLineEdit())
        for i in range(len(self.wprompt_freq)):
            self.wprompt_freq[i].setFixedWidth(350)
            self.layi.addRow("Prompt Freq"+str(i)+" ( FQ"+str(i)+" )",self.wprompt_freq[i])
            sp=sp+" (FQ"+str(i)+")"
        self.wglobprompt.insertPlainText("what you want with "+sp)
        self.wantiprompt.insertPlainText("what you dont want with "+sp)
        self.wstep=QLineEdit()
        self.wscale=QLineEdit()
        self.wwidth=QLineEdit()
        self.wheight=QLineEdit()
        self.wstrength=QLineEdit()
        self.layi2=QFormLayout()
        self.layi2.addRow("Strength",self.wstrength)
        self.layi2.addRow("Steps",self.wstep)
        self.layi2.addRow("Guidance scale",self.wscale)
        self.layi2.addRow("Width",self.wwidth)
        self.layi2.addRow("Height",self.wheight)
        self.bprompts=QPushButton("Generate Prompts")
        self.bprompts.clicked.connect(self.gen_prompts)
        self.lay=QScrollArea()
        self.layd=QVBoxLayout()
        self.layd.addWidget(QLabel("General Prompt"))
        self.layd.addWidget(self.wglobprompt)
        self.layd.addWidget(QLabel("General Anti Prompt"))
        self.layd.addWidget(self.wantiprompt)
        self.layiw=QWidget()
        self.layiw.setLayout(self.layi)
        self.laydk=QScrollArea()
        self.laydk.setWidget(self.layiw)
        self.layd.addWidget(self.laydk)
        self.layi2w=QWidget()
        self.layi2w.setLayout(self.layi2)
        #self.layd.addWidget(self.layi2w)
        self.layd.addWidget(self.bprompts)
        self.lay.setLayout(self.layd)
        self.layo=QGridLayout()
        self.layo.addWidget(self.lay,0,0,1,1)
        self.window.setLayout(self.layo)

    def gen_prompts(self):
        f = open("resultats/resultat_prompt.txt", "w")
        for i in range(len(self.lefourier[0])):
            sprompt=self.wglobprompt.toPlainText()
            for j in range(len(self.wprompt_freq)):
                nel=""
                if self.lefourier[j][i]<1.0/7.0:
                    nel=""
                elif self.lefourier[j][i]<3.0/7.0:
                    nel="("+self.wprompt_freq[j].text()+")+"
                else:
                    nel="("+self.wprompt_freq[j].text()+")+++"
                if self.wprompt_freq[j].text()!="":
                    sprompt = sprompt.replace("(FQ"+str(j)+")",nel)
                else:
                    sprompt = sprompt.replace("(FQ"+str(j)+")","")
            f.write(sprompt+"\n")
        f.close()
        f = open("resultats/resultat_antiprompt.txt", "w")
        for i in range(len(self.lefourier[0])):
            sprompt=self.wantiprompt.toPlainText()
            for j in range(len(self.wprompt_freq)):
                nel=""
                if self.lefourier[j][i]<1.0/7.0:
                    nel=""
                elif self.lefourier[j][i]<3.0/7.0:
                    nel="("+self.wprompt_freq[j].text()+")+"
                else:
                    nel="("+self.wprompt_freq[j].text()+")+++"
                if self.wprompt_freq[j].text()!="":
                    sprompt = sprompt.replace("(FQ"+str(j)+")",nel)
                else:
                    sprompt = sprompt.replace("(FQ"+str(j)+")","")
            f.write(sprompt+"\n")
        f.close()

    def schemas_freq(self,fourier,nbfreqs):
        nbmoy=int(len(fourier[1])/nbfreqs)
        trans=[]
        for i in range(nbfreqs):
            trans2=fourier[0][i*nbmoy].copy()
            for j in range(1,nbmoy):
                for k in range(len(trans2)):
                    trans2[k]=trans2[k]+fourier[0][i*nbmoy+j][k]
            trans.append(trans2)
        return(trans)

    def schema_resolution_temps(self,dfg,tabt,frame):
        dt=1.0/frame
        result=[]
        for valsfreq in dfg:
            ntabfreq=[]
            k=1
            ntabfreq.append(0.0)
            for i in range(len(valsfreq)):
                if tabt[i]<k*dt:
                    ntabfreq[k-1]=ntabfreq[k-1]+valsfreq[i]
                else:
                    k=k+1
                    ntabfreq.append(0.0)
            result.append(ntabfreq)
        return(result)

    def normalisation_spectre(self,spc):
        resultat=[]
        for g in spc:
            maxi=0.0
            resf=[]
            for v in g:
                if v>maxi:
                    maxi=v
            for v in g:
                resf.append(v/maxi)
            resultat.append(resf)
        return(resultat)

    def analyse_wave(self,nom_fichier,nb_freq,frame):
        self.nb_freq=nb_freq
        self.frame=frame
        wav_obj = wave.open(nom_fichier, 'rb')
        sample_freq = wav_obj.getframerate()
        n_samples = wav_obj.getnframes()
        t_audio = n_samples/sample_freq
        signal_wave = wav_obj.readframes(n_samples)
        signal_array = np.frombuffer(signal_wave, dtype=np.int16)
        l_channel = signal_array[0::2]
        times = np.linspace(0, n_samples/sample_freq, num=n_samples)
        fourier=plt.specgram(l_channel, Fs=sample_freq, vmin=-20, vmax=50)
        dfg=self.schemas_freq(fourier,nb_freq)
        dfgf=self.schema_resolution_temps(dfg,fourier[2],frame)
        self.lefourier=self.normalisation_spectre(dfgf)
        plt.figure()
        for i in self.lefourier:
            plt.plot(i)
        plt.show()



gg=Logprompt('cap.wav',int(sys.argv[1]),int(sys.argv[2])) #nb frequences, #frames
gg.window.show()
sys.exit(gg.app.exec_())
