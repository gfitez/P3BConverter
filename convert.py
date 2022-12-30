import struct 
import numpy as np
import cv2
import glob

def toInt(data,signed=True):
    return int.from_bytes(data,"little",signed=signed)

def decodeDataType(dataTypeCode):
    if dataTypeCode==1:
        dataType="uint8"
        dataLength=1
    elif dataTypeCode==2:
        dataType="int16"
        dataLength=2
    elif dataTypeCode==3:
        dataType="int32"
        dataLength=4
    elif dataTypeCode==4:
        dataType="single"
        dataLength=4
    elif dataTypeCode==5:
        dataType="double"
        dataLength=8
    elif dataTypeCode==7:
        dataType="*char"
        dataLength=1
    elif dataTypeCode==12:
        dataType="uint16"
        dataLength=2
    elif dataTypeCode==13:
        dataType="uint32"
        dataLength=4
    elif dataTypeCode==14:
        dataType="int64"
        dataLength=8
    elif dataTypeCode==15:
        dataType="uint64"
        dataLength=8
    else:
        raise Exception

    return dataType,dataLength

def decodeTag(start,data):
    nameLength=toInt(data[start:start+4])
    name=data[start+4:start+4+nameLength].decode("utf-8")
    dataTypeCode=toInt(data[start+nameLength+4:start+nameLength+8])
    itemLength=toInt(data[start+nameLength+8:start+nameLength+12])

    dataType,dataLength=decodeDataType(dataTypeCode)
    
    raw=data[start+nameLength+12:start+nameLength+12+itemLength*dataLength]
    pointer=start+nameLength+12+itemLength*dataLength

    rawValues=[raw[i:i+dataLength] for i in range(0, len(raw), dataLength)]
    
    
    if dataType=="int32" or dataType=="int16":
        item=[toInt(i) for i in rawValues]
    elif dataType=="uint16" or dataType=="uint32" or dataType=="uint8":
        item=[toInt(i,signed=False) for i in rawValues]
    elif dataType=="*char":
        item="".join([i.decode("utf-8") for i in rawValues])
    elif dataType=="single":
        item=[struct.unpack("f",i) for i in rawValues]
    elif dataType=="double":
        item=[struct.unpack("ff",i) for i in rawValues]
    else:
        raise Exception(f"unknown datatype: {dataType}")



    #print(name,dataType,itemLength,item)
    return (name,item), pointer


def readFileData(fileName):
    out={}
    with open(fileName, mode="rb") as f:
        data=f.read()

        ntags=toInt(data[0:4])
        pointer=4

        for _ in range(ntags):
            tag,pointer=decodeTag(pointer,data)
            out[tag[0]]=tag[1]
    return out


def getImg(data):
    dataType=decodeDataType(data["PIXTYPE"][0])[0]

    image=np.reshape(data["DATA"],(data["DIMY"][0],data["DIMX"][0]))
    image=image.astype(dataType)

    return image

def showFile(file):
    data=readFileData(file)
    dataType=decodeDataType(data["PIXTYPE"][0])[0]

    image=np.reshape(data["DATA"],(data["DIMY"][0],data["DIMX"][0]))
    image=image.astype(dataType)

    cv2.imwrite("image.png",image)
    cv2.imshow("window",image)
    cv2.waitKey(0)

if __name__=="__main__":



    files=glob.glob("220513/bl11__011/*.P3B")
    for file in files:
        data=readFileData(file)
        image=getImg(data)
        cv2.imwrite(file[:-4]+".png",image)
    

    