from django.shortcuts import render,redirect
import os,io,requests
import cloudinary
from PIL import Image
import cv2
from pytesseract import pytesseract
import numpy as np
from django.conf import settings
from imageclass.forms import ImageClassForm
from imageclass.models import ImageClass
from datetime import datetime
from io import BytesIO


def upload_image(request):
      
    if request.method=="POST":
        
        form = ImageClassForm(request.POST or None, request.FILES)

        
        if form.is_valid() :
            
            obj=form.save()
            return redirect('result',pk= obj.id)
    else:
        form =ImageClassForm()
    return render(request,'upload.html',{"form":form})   



def get_text(img):
    #path_to_tesseract ='/app/.apt/usr/bin/tesseract'
    #print(os.path.join(settings.BASE_DIR,'Tesseract-OCR','tesseract.exe'))
   # pytesseract.tesseract_cmd =os.path.join(settings.BASE_DIR,'Tesseract-OCR','tesseract.exe')
    text = pytesseract.image_to_string(img)
  
    line=text[:-1]
    texts=''
    line = line.strip()
    # If line is small, ignore it
    if len(line.split(" ")) < 10 and len(line.split(" "))>0:
        texts= texts + " " + str(line) + "\n"

    elif len(line.split(" "))<2:
        pass
    else:
        if line[-1]!=".":
            texts = texts + " " + str(line)
        else:
            texts = texts + " " + line + "\n"
    if len(line)==0:
        return "No text found in image"
    # Displaying the extracted text
    return texts


def detect_object(img):
    #Labels of network.
    classNames = { 0: 'background',
        1: 'aeroplane', 2: 'bicycle', 3: 'bird', 4: 'boat',
        5: 'bottle', 6: 'bus', 7: 'car', 8: 'cat', 9: 'chair',
        10: 'cow', 11: 'diningtable', 12: 'dog', 13: 'horse',
        14: 'motorbike', 15: 'person', 16: 'pottedplant',
        17: 'sheep', 18: 'sofa', 19: 'train', 20: 'tvmonitor' }

    l=[]
    net = cv2.dnn.readNetFromCaffe(os.path.join(settings.BASE_DIR,"MobileNetSSD_deploy.prototxt"),os.path.join(settings.BASE_DIR,"MobileNetSSD_deploy.caffemodel"))
    frame=np.asarray(img)
    
    frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2RGB)
    frame_resized = cv2.resize(frame,(300,300)) # resize frame for prediction
    blob = cv2.dnn.blobFromImage(frame_resized, 0.007843, (300, 300), (127.5, 127.5, 127.5), False)
    #Set to network the input blob 
    net.setInput(blob)
    #Prediction of network
    detections = net.forward()
    #Size of frame resize (300x300)
    cols = frame_resized.shape[1] 
    rows = frame_resized.shape[0]
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2] #Confidence of prediction 
        if confidence > 0.2: # Filter prediction 
            class_id = int(detections[0, 0, i, 1]) # Class label

            # Object location 
            xLeftBottom = int(detections[0, 0, i, 3] * cols) 
            yLeftBottom = int(detections[0, 0, i, 4] * rows)
            xRightTop   = int(detections[0, 0, i, 5] * cols)
            yRightTop   = int(detections[0, 0, i, 6] * rows)
            # Factor for scale to original size of frame
            heightFactor = frame.shape[0]/300.0  
            widthFactor = frame.shape[1]/300.0 
            # Scale object detection to frame
            xLeftBottom = int(widthFactor * xLeftBottom) 
            yLeftBottom = int(heightFactor * yLeftBottom)
            xRightTop   = int(widthFactor * xRightTop)
            yRightTop   = int(heightFactor * yRightTop)
            # Draw location of object  
            cv2.rectangle(frame, (xLeftBottom, yLeftBottom), (xRightTop, yRightTop),
                        (0, 255, 0))

            # Draw label and confidence of prediction in frame resized
            if class_id in classNames:
                label = classNames[class_id] + ": " + str(confidence)
                labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)

                yLeftBottom = max(yLeftBottom, labelSize[1])
                cv2.rectangle(frame, (xLeftBottom, yLeftBottom - labelSize[1]),
                                    (xLeftBottom + labelSize[0], yLeftBottom + baseLine),
                                    (255, 255, 255), cv2.FILLED)
                cv2.putText(frame, label, (xLeftBottom, yLeftBottom),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0))
                l.append(label)
    img = Image.fromarray(frame, 'RGB')
    return img,l

import base64
from io import BytesIO
def to_data_uri(pil_img):
    data = BytesIO()
    pil_img.save(data, "JPEG") # pick your format
    data64 = base64.b64encode(data.getvalue())
    return u'data:pil_img/jpeg;base64,'+data64.decode('utf-8') 
    
def view_result(request,pk):
    try:
        book=ImageClass.objects.get(pk=pk)
        print(book.Image.url)
        ll=000
        URL=cloudinary.utils.cloudinary_url(book.Image.url)
        url=URL[0]
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        text=get_text(img)
        #text="fuck"
        direct,labels=detect_object(img)
        print(labels)
        if len(labels)==0:
            labels.append("No object detected")
        img= to_data_uri(direct)
       
        return render(request,'result.html',{"text":text,'img':img,'label':labels})
    except Exception as e :
        print(e)
        return redirect('home')


