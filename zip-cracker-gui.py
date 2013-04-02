# Python Version 2.7.3
# File: zip-cracker-gui.py

import zipfile
import sys, os
import tkMessageBox
from Tkinter import *
from tkFileDialog import askopenfilename
from threading import Thread

class Cracker:

    def __init__(self, master):

        #set up frame
        frame = Frame(master)
        frame.pack()

        #show title
        self.title = Label(frame, text = "ZIP Password Cracker")
        self.title.grid(row = 0, column = 0, columnspan = 4)

        #set up variables
        self.archFileMade = False
        self.dictFilename = ""
        self.finished = False
        
        #set up all widgets and their layout
        self.openZipLabel = Label(frame, text = "Select ZIP file:")
        self.openZipLabel.grid(row = 1, column = 0, columnspan = 3)
        self.openZipField = Text(frame, state = DISABLED, height = 1)
        self.openZipField.grid(row = 2, column = 0, columnspan = 3)
        self.openZipButton = Button(frame, text = "...", command = lambda: self.getFileName("zip"))
        self.openZipButton.grid(row = 2, column = 3)

        self.openDictLabel = Label(frame, text = "Select dictionary file:")
        self.openDictLabel.grid(row = 4, column = 0, columnspan = 3)
        self.openDictField = Text(frame, state = DISABLED, height = 1)
        self.openDictField.grid(row = 5, column = 0, columnspan = 3)
        self.openDictButton = Button(frame, text = "...", command = lambda: self.getFileName("dict"))
        self.openDictButton.grid(row = 5, column = 3)

        self.crackButton = Button(frame, text = "Crack", command = lambda: self.crackPass())
        self.crackButton.grid(row = 7, column = 0, columnspan = 4)
        self.outputLabel = Label(frame, text = "Status:")
        self.outputLabel.grid(row = 9, column = 0, columnspan = 4)
        self.outputText = Text(frame, state = NORMAL, height = 1)
        self.outputText.insert(1.0, "Waiting for ZIP and Dictionary files.")
        self.outputText.config(state = DISABLED)
        self.outputText.grid(row = 10, column = 0, columnspan = 4)

        self.exitButton = Button(frame, text = "Exit", command = lambda: self.closeProgram())
        self.exitButton.grid(row = 11, column = 0, columnspan = 4)

    def getFileName(self, filetype):
        error = False
        if filetype == "zip":
            archFilename = askopenfilename()
            #check if user actually picked a file
            if archFilename != "":
                #check if file exists and access is allowed
                if not os.path.isfile(archFilename):
                    tkMessageBox.showinfo("File Error", archFilename + " does not exist.")
                    error = True
                if not os.access(archFilename, os.R_OK):
                    tkMessageBox.showinfo("File Error", archFilename + " access denied.")
                    error = True
                error = self.checkIfZip(archFilename)
                #update data if no errors found
                if error == False:
                    self.archFileMade = True
                    self.openZipField.config(state = NORMAL)
                    self.openZipField.delete(1.0, END)
                    self.openZipField.insert(END, archFilename)
                    self.openZipField.config(state = DISABLED)

        if filetype == "dict":
            dictFilename = askopenfilename()
            #check if user actually picked a file
            if dictFilename != "":
                #check if file exists and access is allowed
                if not os.path.isfile(dictFilename):
                    tkMessageBox.showinfo("File Error", dictFilename + " does not exist.")
                    error = True
                if not os.access(dictFilename, os.R_OK):
                    tkMessageBox.showinfo("File Error", dictFilename + " access denied.")
                    error = True
                #updata data if no errors found
                if error == False:
                    self.dictFilename = dictFilename
                    self.openDictField.config(state = NORMAL)
                    self.openDictField.delete(1.0, END)
                    self.openDictField.insert(END, dictFilename)
                    self.openDictField.config(state = DISABLED)

    def checkIfZip(self, filename):
        #create file if zip, otherwise return error
        try:
            self.archFile = zipfile.ZipFile(filename)
            return False
        except zipfile.BadZipfile:
            tkMessageBox.showinfo("File Error", filename + " is corrupt or not a ZIP file.")
            return True
        except zipfile.LargeZipFile:
            tkMessageBox.showing("File Error", filename + " requires ZIP64, which is not enabled")
            return True
        except:
            tkMessageBox.showinfo("File Error", "An error occurred, please try again.")
            return True
            

    def crackPass(self):
        if self.archFileMade == False:
            tkMessageBox.showinfo("Error", "Please select a ZIP file.")
        elif self.dictFilename == "":
            tkMessageBox.showinfo("Error", "Please select a dictionary file.")
        else:
            #output status message
            self.outputText.config(state = NORMAL)
            self.outputText.delete(1.0, END)
            self.outputText.insert(END, "Cracking...")
            self.outputText.config(state = DISABLED)

            #open dict file
            dictFile = open(self.dictFilename, 'r')
            
            #start threads
            for line in dictFile.readlines():
                #if finished, don't start new threads
                if self.finished == False:
                    password = line.strip("\n")
                    password = password.strip()
                    t = Thread(target = self.extractFile, args = (self.archFile, password))
                    t.start()

            #if failed, change status message
            if self.finished == False:
                self.outputText.config(state = NORMAL)
                self.outputText.delete(1.0, END)
                self.outputText.insert(END, "Password not in dictionary.")
                self.outputText.config(state = DISABLED)

    def extractFile(self, archFile, password):
        #try extract file, if successful - print password that worked
        if self.finished == False:
            try:
                archFile.extractall(pwd = password)
                self.passwordFound(password)
            except:
                pass

    def passwordFound(self, password):
        self.finished = True
        self.outputText.config(state = NORMAL)
        self.outputText.delete(1.0, END)
        self.outputText.insert(END, "Password found: " + password)
        self.outputText.config(state = DISABLED)

    def closeProgram(self):
        global root
        root.destroy()

#create Tk widget
root = Tk()
#set title
root.title("ZIP Password Cracker")

#create instance
cracker = Cracker(root)
#make sure root is killed on close
root.protocol('WM_DELETE_WINDOW', cracker.closeProgram)

#run event loop
root.mainloop()
