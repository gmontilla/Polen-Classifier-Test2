#!/usr/bin/env python
# coding: utf-8

# # Importing libraries which we are going to use

from tensorflow.keras.preprocessing import image
from keras.models import load_model

import pandas as pd
import matplotlib.pyplot as plt
import time
import cv2
import numpy as np
import os
import shutil
import zipfile
from datetime import datetime 

    
class PollenClassifierServices:

    CLASS_NAMES = ['Brassica', 'Cardus', 'Cistus sp', 'Citrus sp', 'Erica.m', 'Eucalyptus sp',
        'Helianthus annuus', 'Lavandula', 'Pinus', 'Rosmarinus officinalis', 'Taraxacum',  'Tilia']

    def predictFromDisk(self, img_path, model):
        """
        img_path: path of the test image.
        model: resnet model
        classes: name of the classes according this list
            Class' index 0: Brassica
            Class' index 1: Cardus
            Class' index 2: Cistus sp
            Class' index 3: Citrus sp
            Class' index 4: Erica.m
            Class' index 5: Eucalyptus sp
            Class' index 6: Helianthus annuus
            Class' index 7: Lavandula
            Class' index 8: Pinus
            Class' index 9: Rosmarinus officinalis
            Class' index 10: Taraxacum
            Class' index 11: Tilia
        
        This method return the name of the class predicted,
        and the vector of probabilities of each class.
        Output: preditedClassName, probabilities
    """
        #from tensorflow.keras.preprocessing import image
        test_image = image.load_img(img_path, target_size=(224, 224))
        test_image = image.img_to_array(test_image)
        test_image = np.expand_dims(test_image, axis=0)
        start_time = datetime.now() 
        probs = model.predict(test_image, batch_size=1)
        time_elapsed = datetime.now() - start_time
        print("Time1:", time_elapsed)
        # self.elapse_time_all = self.elapse_time_all + time_elapsed
        classIndex = np.argmax(probs)

        return PollenClassifierServices.CLASS_NAMES[classIndex], probs

    def readZippedImageBatch(self, zip_path, temp_path):
        self.temp_path = temp_path
        self.zip_name = os.path.split(zip_path)[1][:-4]
        with zipfile.ZipFile(zip_path,"r") as zip_ref:
            zip_ref.extractall(temp_path)

    def requestUplodad(self):
        pass

    def requestDownlodad(self):
        pass

    def startService(self, startService_folderpath=""):
        startServiceFilename = "start.txt"
        startServiceFilePath = os.path.join(startService_folderpath, startServiceFilename)
        with open(startServiceFilePath, mode='w'): pass

    def endService(self, endService_folderpath=""):
        endServiceFilename = "end.txt"
        endServiceFilePath = os.path.join(endService_folderpath, endServiceFilename)
        with open(endServiceFilePath, mode='w'): pass

    @staticmethod
    def TestServices(zip_path, temp_path):
        root = os.getcwd()
        pollen = PollenClassifierServices()
        pollen.readZippedImageBatch(zip_path, temp_path)
        predictions, imagePathList = pollen.batchInference(temp_path)
        pollen.convert2CSV(predictions, imagePathList)
        print(predictions)

    @staticmethod
    def __readTempFolder(tempFolder):
        content = os.listdir(tempFolder)
        if len(content) == 1:
            path = os.path.join(tempFolder, content[0])
            if os.path.isdir(path):
                testImageList = [os.path.join(path, fname) for fname in os.listdir(path)]
            elif os.path.isfile(path):
                testImageList = path
            else: testImageList = []
        elif len(content) > 1:
            testImageList = [os.path.join(tempFolder, fname) for fname in content]
        else: testImageList = []

        return testImageList

    def batchInference(self, tempFolder):
        model = load_model("./models/resnet50.h5")
        testImageList = PollenClassifierServices.__readTempFolder(tempFolder)
        predictions = []
        

        start_time = datetime.now() 
        if len(testImageList) > 0:
            for img_path in testImageList:
                className, probs = self.predictFromDisk(img_path, model)
                predictions.append(className)
        time_elapsed = datetime.now() - start_time
        print("Time:", time_elapsed)
        print("Total:", PollenClassifierServices.elapse_time_all)
        return predictions, testImageList

    def convert2CSV(self, predictions, testImagePathList):

        if len(predictions) != len(testImagePathList):
            return None
        
        Names = []
        for path in testImagePathList:
            Names.append(os.path.split(path)[1])
        colunms = ["Nombre de la imagen", "Tipo de Polen"]

        #print(type(predictions))
        #print(type(Names))
        csv_path = os.path.join(self.temp_path, self.zip_name + ".csv")
        xl_path = os.path.join(self.temp_path, self.zip_name + ".xlsx")
        df = pd.DataFrame()
        df["Nombre de la imagen"] = Names
        df["Tipo de Polen"] = predictions
        df.to_csv(csv_path,index = False)
        df.to_excel(xl_path,index = False)
        path_data = os.path.join(self.temp_path, self.zip_name)
        shutil.rmtree(path_data, ignore_errors=True)


def Test():
    zip_path = r"G:\Proyectos\Polen\datasets\Lote120.zip"
    temp_path = r"G:\Proyectos\Polen\datasets\Temp"
    PollenClassifierServices.TestServices(zip_path, temp_path)

Test()

