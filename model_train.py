from ultralytics import YOLO
model=YOLO("yolo26m.pt")

import torch
import numpy as Numpy
import cv2 as cv


device=torch.device("cuda" if torch.cuda.is_available() else "cpu")



if __name__=="__main__":
    print("Device:", device)  

model.train(data='data/data.yaml',imgsz=640,batch=8,epochs=100,workers=0,device=torch.device('cuda'))


