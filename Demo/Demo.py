#!/usr/bin/env python
# coding: utf-8



import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn import svm
from sklearn.linear_model import LogisticRegression
from keras.layers import Dense, Dropout
from keras.models import Sequential
#imports
from nltk.tokenize import word_tokenize
import pandas  as pd
pd.options.display.max_colwidth = 120
import numpy as np
import re



#Code
def ultimate_processing(sentence):
    return basic_string_processing(" "+sentence+" ")
    
def process_apotrophies():
    txt_file = open('apotrophies.txt')
    lst = txt_file.read().split('\n')
    res=[]
    for i in lst:
        sr = i.strip().split('\t')
        if len(sr)>1:
            res.append((sr[0].lower(),sr[1].lower()))
        
    return res


def basic_string_processing(s):
        line  = s[1:-1]
        badwordlst = [i.strip() for i in open('compiled_badword_list.txt').readlines()]
        
        #regex_expressions = [r'\\x..',r'\\n',r'^(http:\/\/www\.|https:\/\/www\.|http:\/\/|https:\/\/)?[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}(:[0-9]{1,5})?(\/.*)?$',r'\\x...',r'\\n',r'<.*?>']
        #regex_expressions = [r'\\x..',r'\\n',r'\\x...',r'\\n',r'<.*?>']
        regex_expressions = [r'\\x..',r'\\n',r'\\u..',r'(http:\/\/|https:\/\/|https:\/\/|www|http:\/\/).*(\s)*',r'\\x...',r'\\n',r'<.*?>']
        
        
        words_replacement = process_apotrophies()
        for i in words_replacement:
            line = line.replace(i[0],i[1])
            line = line.replace(i[0].capitalize(),i[1].capitalize())
        
        for i in regex_expressions:
            line = re.sub(i," ",line)

        for j in line:
            if j.lower() not in "abcdefghijklmnopqrstuvwxyx1234567890!@#$%^&*$.\\/:?=',"+"'":
                line = line.replace(j,' ')
                
        
        final_str = line.strip() 
        
        new_str = ""
        i=0
        try:
            while(i<len(final_str.split())-1):
                
                word = final_str.split()[i] + final_str.split()[i+1]
                #print (i,new_str,word)
                if word in badwordlst:
                    #print ("loop1")
                    new_str+= " " + final_str.split()[i] + final_str.split()[i+1]
                    i+=2
                else:
                    #print ("loop2")
                    new_str+=" "+ final_str.split()[i]
                    i+=1
                    
            new_str+= " "+ final_str.split()[i]

            return new_str
        except:
            return final_str
        
def hasBadWords(sentence):
    badWordFile = open("compiled_badword_list.txt","r")
    badWordList = badWordFile.readlines()
    for badWord in badWordList:
        if badWord.strip() in sentence.lower().split():
            return 1
    return 0

def percent_insult(sentence):
    sentence =  ultimate_processing(sentence)
    fv1 = open('vect1.joblib','rb')
    fv2 = open('vect2.joblib','rb')
    f2 = open('model2.joblib', 'rb')
    f4 = open('model4.joblib', 'rb')
    f5 = open('model5.joblib', 'rb')
    
    sent = [sentence]
    vect1 = pickle.load(fv1)
    vect2 = pickle.load(fv2)
    model2 = pickle.load(f2)
    model4 = pickle.load(f4)
    model5 = pickle.load(f5)
    
    
    vec1 = vect1.transform(sent)
    vec2 = vect2.transform(sent)
    
    p2 = model2.predict_proba(vec1)[0][1]
    p4 = model4.predict_proba(vec2)[0][1]
    p5 = model5.predict_proba(vec2)[0][1]
    
    model = Sequential()
    

    model.add(Dense(100,input_shape=(vec1.T.shape[0],)))
    model.add(Dropout(0.2))
    model.add(Dense(10))
    model.add(Dropout(0.1))
    model.add(Dense(1,activation='sigmoid'))
    
    model.load_weights("model1.pth")
    
    p = model.predict(vec1)[0][0]
    
    b = hasBadWords(sentence)
    
    a = (p2* 0.1+ p4*0.45+ p*0.15 + p5*0.25)
    
    prob = 0.9*a + 0.1*b
    
    
    
    return round(prob,5) * 100
 
class App(QMainWindow):
 
    def __init__(self):
        super().__init__()
        self.title = 'Insult Detection demo | Credits - pythonspot.com'
        self.left = 400
        self.top = 400
        self.width = 1050
        self.height = 220
        self.initUI()
 
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        
        # Height
        a = 80
        wi = 1000
        font = QFont("Times", 20, QFont.Bold) 

        # Create a Parent Label
        self.label = QLabel(self)
        self.label.setText("Insult Detection of Social Comentary")
        self.label.resize(wi,40)
        self.label.setFont(font)
        self.label.move(20, 20)

        # Create a main Label
        self.label_names = QLabel(self)
        self.label_names.setText("Team Members: Abhavya | Apoorv"
                                 " | Atishay | Ritik | Varun | Rithwik")
        font = QFont("Times", 14) 
        self.label_names.setFont(font)
        self.label_names.resize(wi,40)
        self.label_names.move(20, 55)

        # Create textbox
        self.textbox = QLineEdit(self)
        self.textbox.move(20, a + 20)
        self.textbox.resize(wi,40)
 
        # Create a button in the window
        self.button = QPushButton('Calc. Probability', self)
        self.button.move(wi-100, a + 80)
 
        # connect button to function on_click
        self.textbox.returnPressed.connect(self.button.click)
        self.button.clicked.connect(self.on_click)
        self.show()
 
    @pyqtSlot()
    def on_click(self):
        textboxValue = self.textbox.text()
        percent_value = percent_insult(textboxValue)
        QMessageBox.question(self, 'Insult ' +'%' +' detected', "Probability of Insult: "                              + str(percent_value) + '%', QMessageBox.Ok, QMessageBox.Ok)
        self.textbox.setText("")
 
if __name__ == '__main__':
    app = QApplication(sys.argv)
    # print(app)
    # print(type(app))
    ex = App()
    sys.exit(app.exec_())






