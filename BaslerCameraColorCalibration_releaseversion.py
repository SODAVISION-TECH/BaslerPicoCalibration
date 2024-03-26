# Import necessary libraries
import cv2  
import os  
import numpy as np  
import skimage
from skimage import io, color
import re
from pypylon import pylon  # Basler camera SDK

# Function used to convert RGB value to LAB value.
def rgb2lab(inputColor):
    """
    Convert RGB color to LAB color space.
    """
    num = 0
    RGB = [0, 0, 0]

    # Convert RGB values to the range 0-1 and apply gamma correction
    for value in inputColor:
        value = float(value) / 255

        if value > 0.04045:
            value = ((value + 0.055) / 1.055) ** 2.4
        else:
            value = value / 12.92

        RGB[num] = value * 100
        num = num + 1

    # Convert RGB to XYZ color space
    XYZ = [0, 0, 0]
    X = RGB[0] * 0.4124 + RGB[1] * 0.3576 + RGB[2] * 0.1805
    Y = RGB[0] * 0.2126 + RGB[1] * 0.7152 + RGB[2] * 0.0722
    Z = RGB[0] * 0.0193 + RGB[1] * 0.1192 + RGB[2] * 0.9505
    XYZ[0] = round(X, 4)
    XYZ[1] = round(Y, 4)
    XYZ[2] = round(Z, 4)

    # Normalize XYZ values
    XYZ[0] = float(XYZ[0]) / 95.047  # ref_X =  95.047   Observer= 2°, Illuminant= D65
    XYZ[1] = float(XYZ[1]) / 100.0   # ref_Y = 100.000
    XYZ[2] = float(XYZ[2]) / 108.883 # ref_Z = 108.883

    # Apply XYZ to LAB transformation
    num = 0
    for value in XYZ:
        if value > 0.008856:
            value = value ** (0.3333333333333333)
        else:
            value = (7.787 * value) + (16 / 116)
        XYZ[num] = value
        num = num + 1

    # Calculate LAB values
    Lab = [0, 0, 0]
    L = (116 * XYZ[1]) - 16
    a = 500 * (XYZ[0] - XYZ[1])
    b = 200 * (XYZ[1] - XYZ[2])
    Lab[0] = round(L, 4)
    Lab[1] = round(a, 4)
    Lab[2] = round(b, 4)

    return Lab

# Open Basler camera and feed the CCM result to the camera setting.
camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
camera.Open()

# Load Camera default setting
camera.UserSetSelector.SetValue("Default")
camera.UserSetLoad.Execute()
camera.Gamma.SetValue(0.4545)
camera.LightSourcePreset.SetValue("Off")

# Camera roi - 760 x 450
camera.Width.SetValue(760)
camera.Height.SetValue(450)
camera.CenterX.SetValue(True)
camera.CenterY.SetValue(True)
camera.ReverseX.SetValue(True)
camera.ReverseY.SetValue(True)
camera.AcquisitionFrameRateEnable.SetValue(True)
camera.AcquisitionFrameRate.SetValue(30)
converter = pylon.ImageFormatConverter()
converter.OutputPixelFormat = pylon.PixelType_BGR8packed

# Print the model name of the camera.
print("Using device ", camera.GetDeviceInfo().GetModelName())
print("Move to Patch-19 to adjust the image grey value, press 's' Key when ready ")

# Write raw image RGB value to file
file = open(r"C:\Users\\Desktop\ColorCalibration\CamerarawRGBValue.txt", "w+")

# Write calibrated RGB value to file
calibratedfile = open(r"C:\Users\\Desktop\ColorCalibration\NewCameracalibratedRGBValue.txt", "w+")

# Start grabbing images from the camera
camera.StartGrabbing(pylon.GrabStrategy_LatestImages)

# Declare an empty numpy array to store the image rgb value
CameraRawRGBValue = np.array([])
CameraCalibratedRGBValue = np.array([])
count = 1
count1 = 1

# Main loop to grab images
while camera.IsGrabbing():
    key = cv2.waitKey(1) & 0xFF
    grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
    image = converter.Convert(grabResult)
    img = image.GetArray()
    #Display results
    cv2.namedWindow('Image',cv2.WINDOW_NORMAL)    
    cv2.imshow("Image",img)
    #Calculate the mean of each channel
    meanvalue = cv2.mean(img)
    # Swap blue and red values (making it RGB, not BGR)
    MeanRGBValue = np.array([(meanvalue[2], meanvalue[1], meanvalue[0])])
    cv2.waitKey(1)
    #print (MeanRGBValue)

    if key == ord("s"):
       print ("Calculating Patch-19 Grey value, please wait...")
       while True:
          grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
          image = converter.Convert(grabResult)
          img = image.GetArray()
          meanvalue = cv2.mean(img)
          MeanRGBValue = np.array([(meanvalue[2], meanvalue[1], meanvalue[0])])
          #Display results
          cv2.namedWindow('Image',cv2.WINDOW_NORMAL)
          cv2.imshow("Image",img)
          cv2.waitKey(1)
          minimumExposuretime = camera.ExposureTime.GetMin()
          maximumExposuretime = camera.ExposureTime.GetMax()

          if meanvalue[1] < 240:
             Exposuretime = camera.ExposureTime.GetValue()
             print (MeanRGBValue)
             newExposuretime = Exposuretime*1.05
             if (newExposuretime < maximumExposuretime):
                 camera.ExposureTime.SetValue(newExposuretime)
                                      
          if meanvalue[1] > 244:
             Exposuretime = camera.ExposureTime.GetValue()
             print (MeanRGBValue)
             newExposuretime = Exposuretime*0.95
             if (newExposuretime > minimumExposuretime):
                 camera.ExposureTime.SetValue(newExposuretime)                  
             
          if (meanvalue[1] < 245 and meanvalue[1] > 242):
             print ("=====================Patch-19 RGB Values=====================")
             MeanRGBValue = np.array([(meanvalue[2], meanvalue[1], meanvalue[0])])
             print (MeanRGBValue)
             print ("=====Collecting raw images for CCM Calculation, press 't' to store the RGB value=====")
             break;
            
    if key == ord("t"):
          #Calculate the mean of each channel
          meanvalue = cv2.mean(img)
          # Swap blue and red values (making it RGB, not BGR)
          MeanRGBValue = np.array([(meanvalue[2], meanvalue[1], meanvalue[0])])
          newCameraRawRGBValue = np.append(CameraRawRGBValue, MeanRGBValue)
          file.write(str(newCameraRawRGBValue)[1 : -1]+'\n')
          print ("Write patch:",count, "=",newCameraRawRGBValue)
          print ("===Move to next patch and press 't' to store the next RGB value, press 'd' when the 24th patch RGB value is recorded===")
          count += 1
          
    if key == ord("d"):
        print ("file write done")
        print ("Press 'p' to compute CCM calculation")
        file.close()
            
    if key == ord("p"):
       #Read camera RGB value from file for the calibration
       CameraRGBValue = np.loadtxt("NewCamerarawRGBValue.txt", dtype=int)
       print(CameraRGBValue)

       #Read reference RGB value from file for the calibration
       ReferenceRGBValue = np.loadtxt("ReferenceRGBValue.txt", dtype=int)
       print(ReferenceRGBValue)

       #Calculate Color Correction Matrix
       #Return the least-squares solution to a linear matrix equation.
       CCM = np.transpose(np.linalg.lstsq(CameraRGBValue, ReferenceRGBValue,rcond=None)[0])
       CCMResults = np.round(CCM, 3)
       print("======================CCMResults==============================")
       print(CCMResults)
       print("==============================================================")
       # Upload the CCM Results to camera setting.
       camera.ColorTransformationValueSelector.SetValue("Gain00")
       camera.ColorTransformationValue.SetValue(CCMResults[0][0])
       Gain00 = camera.ColorTransformationValue.GetValue()
       camera.ColorTransformationValueSelector.SetValue("Gain01")
       camera.ColorTransformationValue.SetValue(CCMResults[0][1])
       Gain01 = camera.ColorTransformationValue.GetValue()
       camera.ColorTransformationValueSelector.SetValue("Gain02")
       camera.ColorTransformationValue.SetValue(CCMResults[0][2])
       Gain02 = camera.ColorTransformationValue.GetValue()
       camera.ColorTransformationValueSelector.SetValue("Gain10")
       camera.ColorTransformationValue.SetValue(CCMResults[1][0])
       Gain10 = camera.ColorTransformationValue.GetValue()
       camera.ColorTransformationValueSelector.SetValue("Gain11")
       camera.ColorTransformationValue.SetValue(CCMResults[1][1])
       Gain11 = camera.ColorTransformationValue.GetValue()
       camera.ColorTransformationValueSelector.SetValue("Gain12")
       camera.ColorTransformationValue.SetValue(CCMResults[1][2])
       Gain12 = camera.ColorTransformationValue.GetValue()
       camera.ColorTransformationValueSelector.SetValue("Gain20")
       camera.ColorTransformationValue.SetValue(CCMResults[2][0])
       Gain20 = camera.ColorTransformationValue.GetValue()
       camera.ColorTransformationValueSelector.SetValue("Gain21")
       camera.ColorTransformationValue.SetValue(CCMResults[2][1])
       Gain21 = camera.ColorTransformationValue.GetValue()
       camera.ColorTransformationValueSelector.SetValue("Gain22")
       camera.ColorTransformationValue.SetValue(CCMResults[2][2])                                     
       Gain22 = camera.ColorTransformationValue.GetValue()
       print("CCM Calculation is completed.")
       print("Move to Patch-19 for next step, press 'v' Key when ready ")

    if key == ord("v"):
       print ("Calculating RGB Gain value, please wait...")
       while True:
          grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
          image = converter.Convert(grabResult)
          img = image.GetArray()
          meanvalue = cv2.mean(img)
          #Display results
          cv2.namedWindow('Image',cv2.WINDOW_NORMAL)
          cv2.imshow("Image",img)
          cv2.waitKey(1)
       
          if meanvalue[1] < 235 :
             camera.BalanceRatioSelector.SetValue("Green")
             BalanceRatioVal = camera.BalanceRatio.GetValue()
             camera.BalanceRatio.SetValue(BalanceRatioVal + 0.00072)
             NewBalanceRatioVal = camera.BalanceRatio.GetValue()
             print ("G", NewBalanceRatioVal)
             print (meanvalue)
             
          if meanvalue[1] > 245:
             camera.BalanceRatioSelector.SetValue("Green")
             BalanceRatioVal = camera.BalanceRatio.GetValue()
             camera.BalanceRatio.SetValue(BalanceRatioVal - 0.00072)
             NewBalanceRatioVal = camera.BalanceRatio.GetValue()
             print ("G", NewBalanceRatioVal)
             print (meanvalue)
             
          if meanvalue[0] < 230 :
             camera.BalanceRatioSelector.SetValue("Blue")
             BalanceRatioVal = camera.BalanceRatio.GetValue()
             camera.BalanceRatio.SetValue(BalanceRatioVal + 0.00072)
             NewBalanceRatioVal = camera.BalanceRatio.GetValue()
             print ("B", NewBalanceRatioVal)
             print (meanvalue)
             
          if meanvalue[0] > 245:
             camera.BalanceRatioSelector.SetValue("Blue")
             BalanceRatioVal = camera.BalanceRatio.GetValue()
             camera.BalanceRatio.SetValue(BalanceRatioVal - 0.00072)
             NewBalanceRatioVal = camera.BalanceRatio.GetValue()
             print ("B", NewBalanceRatioVal)
             print (meanvalue)
             
          if meanvalue[2] < 230 :
             camera.BalanceRatioSelector.SetValue("Red")
             BalanceRatioVal = camera.BalanceRatio.GetValue()
             camera.BalanceRatio.SetValue(BalanceRatioVal + 0.00072)
             NewBalanceRatioVal = camera.BalanceRatio.GetValue()
             print ("R", NewBalanceRatioVal)
             print (meanvalue)
             
             
          if meanvalue[2] > 245:
             camera.BalanceRatioSelector.SetValue("Red")
             BalanceRatioVal = camera.BalanceRatio.GetValue()
             camera.BalanceRatio.SetValue(BalanceRatioVal - 0.00072)
             NewBalanceRatioVal = camera.BalanceRatio.GetValue()
             print ("R", NewBalanceRatioVal)
             print (meanvalue)
             
          if (meanvalue[0] > 230 and meanvalue[1] > 233 and meanvalue[2] > 230 and meanvalue[2] < 245 and meanvalue[1] < 245 and meanvalue[0] < 245):
             print ("=====================RGB Balance Ratio Values=====================")
             print ("Red Green Blue Gain Calculation Done")
             camera.BalanceRatioSelector.SetValue("Red")
             RedBalanceRatioVal = camera.BalanceRatio.GetValue()
             print ("Red_BalanceRatio=",RedBalanceRatioVal)
             camera.BalanceRatioSelector.SetValue("Green")
             GreenBalanceRatioVal = camera.BalanceRatio.GetValue()
             print ("Green_BalanceRatio=",GreenBalanceRatioVal)
             camera.BalanceRatioSelector.SetValue("Blue")
             BlueBalanceRatioVal = camera.BalanceRatio.GetValue()
             print ("Green_BalanceRatio=",BlueBalanceRatioVal)
             MeanRGBValue = np.array([(meanvalue[2], meanvalue[1], meanvalue[0])])
             print (MeanRGBValue)
             print ("=====================Proceed to 6-axis Operator Correction=====================")
             print ("Please move to patch-15 and press 'r' to start")
             break;

    if key == ord("r"):
       print("Calculating Red Gain value, please wait...")
       while True:
          grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
          image = converter.Convert(grabResult)
          img = image.GetArray()
          meanvalue = cv2.mean(img)
          #Display results
          cv2.namedWindow('Image',cv2.WINDOW_NORMAL)
          cv2.imshow("Image",img)
          # Swap blue and red values (making it RGB, not BGR)
          MeanRGBValue = np.array([(meanvalue[2], meanvalue[1], meanvalue[0])])
          cv2.waitKey(1)
          
          if ((meanvalue[0] - meanvalue[1]) <6):
             camera.ColorAdjustmentSelector.SetValue("Red")
             cameraHueVal = camera.ColorAdjustmentHue.GetValue()
             camera.ColorAdjustmentHue.SetValue(cameraHueVal + 0.03)
             
          if ((meanvalue[0] - meanvalue[1]) >8):
             camera.ColorAdjustmentSelector.SetValue("Red")
             cameraHueVal = camera.ColorAdjustmentHue.GetValue()
             camera.ColorAdjustmentHue.SetValue(cameraHueVal - 0.03)

          if (meanvalue[1] >55 or meanvalue[0] >60 ):
             camera.ColorAdjustmentSelector.SetValue("Red")
             cameraSaturationVal = camera.ColorAdjustmentSaturation.GetValue()
             camera.ColorAdjustmentSaturation.SetValue(cameraSaturationVal + 0.0078)

          if (meanvalue[1] <53 or meanvalue[0] <59 ):
             camera.ColorAdjustmentSelector.SetValue("Red")
             cameraSaturationVal = camera.ColorAdjustmentSaturation.GetValue()
             camera.ColorAdjustmentSaturation.SetValue(cameraSaturationVal - 0.0078)

          #if (meanvalue[1] >53 and meanvalue[1] <55 and meanvalue[0] >59 and meanvalue[0] <61  ):
          else:
              print ("Good, ok")
              print (MeanRGBValue)
              print ("Please move to patch-14 and press 'g' to start")
              break

    if key == ord("g"):
       print("Calculating Green Gain value, please wait...")
       while True:
          grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
          image = converter.Convert(grabResult)
          img = image.GetArray()
          meanvalue = cv2.mean(img)
          #Display results
          cv2.namedWindow('Image',cv2.WINDOW_NORMAL)
          cv2.imshow("Image",img)
          # Swap blue and red values (making it RGB, not BGR)
          MeanRGBValue = np.array([(meanvalue[2], meanvalue[1], meanvalue[0])])
          cv2.waitKey(1)
          
          if (((meanvalue[0] - meanvalue[2]) <3)):
             camera.ColorAdjustmentSelector.SetValue("Green")
             cameraHueVal = camera.ColorAdjustmentHue.GetValue()
             camera.ColorAdjustmentHue.SetValue(cameraHueVal + 0.01)
             print ("1")
             print (MeanRGBValue)
             
          if (((meanvalue[0] - meanvalue[2]) >5)):
             camera.ColorAdjustmentSelector.SetValue("Green")
             cameraHueVal = camera.ColorAdjustmentHue.GetValue()
             camera.ColorAdjustmentHue.SetValue(cameraHueVal - 0.01)
             print ("2")
             print (MeanRGBValue)

          if (meanvalue[0] >73 or meanvalue[2] >71):
             camera.ColorAdjustmentSelector.SetValue("Green")
             cameraSaturationVal = camera.ColorAdjustmentSaturation.GetValue()
             camera.ColorAdjustmentSaturation.SetValue(cameraSaturationVal + 0.007)
             print ("3")
             print (MeanRGBValue)

          if (meanvalue[0] <72 or meanvalue[2] <70 ):
             camera.ColorAdjustmentSelector.SetValue("Green")
             cameraSaturationVal = camera.ColorAdjustmentSaturation.GetValue()
             camera.ColorAdjustmentSaturation.SetValue(cameraSaturationVal - 0.007)
             print ("4")
             print (MeanRGBValue)

          if (meanvalue[2] >65 and meanvalue[2] <80 and meanvalue[0] >50 and meanvalue[0] <85  ):
              print ("Good, ok")
              print (MeanRGBValue)
              print ("Please move to patch-13 and press 'b' to start")             
              break
            
    if key == ord("b"):
       print("Calculating Blue Gain value, please wait...")
       while True:
          grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
          image = converter.Convert(grabResult)
          img = image.GetArray()
          meanvalue = cv2.mean(img)
          #Display results
          cv2.namedWindow('Image',cv2.WINDOW_NORMAL)
          cv2.imshow("Image",img)
          # Swap blue and red values (making it RGB, not BGR)
          MeanRGBValue = np.array([(meanvalue[2], meanvalue[1], meanvalue[0])])
          cv2.waitKey(1)
          
          if ((meanvalue[1] - meanvalue[2]) <4):
             camera.ColorAdjustmentSelector.SetValue("Blue")
             cameraHueVal = camera.ColorAdjustmentHue.GetValue()
             camera.ColorAdjustmentHue.SetValue(cameraHueVal + 0.03)
             
          if ((meanvalue[1] - meanvalue[2]) >6):
             camera.ColorAdjustmentSelector.SetValue("Blue")
             cameraHueVal = camera.ColorAdjustmentHue.GetValue()
             camera.ColorAdjustmentHue.SetValue(cameraHueVal - 0.03)

          if (meanvalue[1] >62 or meanvalue[2] >58 ):
             camera.ColorAdjustmentSelector.SetValue("Blue")
             cameraSaturationVal = camera.ColorAdjustmentSaturation.GetValue()
             camera.ColorAdjustmentSaturation.SetValue(cameraSaturationVal + 0.007)

          if (meanvalue[1] <60 or meanvalue[2] <56 ):
             camera.ColorAdjustmentSelector.SetValue("Blue")
             cameraSaturationVal = camera.ColorAdjustmentSaturation.GetValue()
             camera.ColorAdjustmentSaturation.SetValue(cameraSaturationVal - 0.007)

          #if (meanvalue[2] >56 and meanvalue[2] <58 and meanvalue[1] >60 and meanvalue[1] <62  ):
          else:
             print ("Good, ok")
             print (MeanRGBValue)
             print ("Please move to patch-16 and press 'y' to start")
             break
            
    if key == ord("y"):
       print("Calculating Yellow Gain value, please wait...")
       while True:
          grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
          image = converter.Convert(grabResult)
          img = image.GetArray()
          meanvalue = cv2.mean(img)
          #Display results
          cv2.namedWindow('Image',cv2.WINDOW_NORMAL)
          cv2.imshow("Image",img)
          # Swap blue and red values (making it RGB, not BGR)
          MeanRGBValue = np.array([(meanvalue[2], meanvalue[1], meanvalue[0])])
          print (MeanRGBValue)
          cv2.waitKey(1)
          
          if ((meanvalue[2] - meanvalue[1]) <25):
             camera.ColorAdjustmentSelector.SetValue("Yellow")
             cameraHueVal = camera.ColorAdjustmentHue.GetValue()
             camera.ColorAdjustmentHue.SetValue(cameraHueVal + 0.03)
             cameraHueVal = camera.ColorAdjustmentHue.GetValue()
             print (cameraHueVal)
             
          if ((meanvalue[2] - meanvalue[1]) >45):
             camera.ColorAdjustmentSelector.SetValue("Yellow")
             cameraHueVal = camera.ColorAdjustmentHue.GetValue()
             camera.ColorAdjustmentHue.SetValue(cameraHueVal - 0.03)
             cameraHueVal = camera.ColorAdjustmentHue.GetValue()
             print (cameraHueVal)

          if (meanvalue[0] >35 ):
             camera.ColorAdjustmentSelector.SetValue("Yellow")
             cameraSaturationVal = camera.ColorAdjustmentSaturation.GetValue()
             camera.ColorAdjustmentSaturation.SetValue(cameraSaturationVal + 0.0078)
             cameraSaturationVal = camera.ColorAdjustmentSaturation.GetValue()
             print (cameraSaturationVal)

          if (meanvalue[0] <30):
             camera.ColorAdjustmentSelector.SetValue("Yellow")
             cameraSaturationVal = camera.ColorAdjustmentSaturation.GetValue()
             camera.ColorAdjustmentSaturation.SetValue(cameraSaturationVal - 0.0078)
             cameraSaturationVal = camera.ColorAdjustmentSaturation.GetValue()
             print (cameraSaturationVal)

          #if (meanvalue[2] >200 and meanvalue[2] <240 and meanvalue[0] >25 and meanvalue[0] <35  ):
          else:
             print ("Good, ok")
             print (MeanRGBValue)
             print ("Please move to patch-17 and press 'm' to start")
             break

    if key == ord("m"):
       print("Calculating Magenta Gain value, please wait...")
       while True:
          grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
          image = converter.Convert(grabResult)
          img = image.GetArray()
          meanvalue = cv2.mean(img)
          #Display results
          cv2.namedWindow('Image',cv2.WINDOW_NORMAL)
          cv2.imshow("Image",img)
          # Swap blue and red values (making it RGB, not BGR)
          MeanRGBValue = np.array([(meanvalue[2], meanvalue[1], meanvalue[0])])
          print (MeanRGBValue)
          cv2.waitKey(1)
          
          if ((meanvalue[2] - meanvalue[0]) <25):
             camera.ColorAdjustmentSelector.SetValue("Magenta")
             cameraHueVal = camera.ColorAdjustmentHue.GetValue()
             camera.ColorAdjustmentHue.SetValue(cameraHueVal + 0.03)
             cameraHueVal = camera.ColorAdjustmentHue.GetValue()
             print (cameraHueVal)
             
          if ((meanvalue[2] - meanvalue[0]) >45):
             camera.ColorAdjustmentSelector.SetValue("Magenta")
             cameraHueVal = camera.ColorAdjustmentHue.GetValue()
             camera.ColorAdjustmentHue.SetValue(cameraHueVal - 0.03)
             cameraHueVal = camera.ColorAdjustmentHue.GetValue()
             print (cameraHueVal)

          if (meanvalue[1] >88 ):
             camera.ColorAdjustmentSelector.SetValue("Magenta")
             cameraSaturationVal = camera.ColorAdjustmentSaturation.GetValue()
             camera.ColorAdjustmentSaturation.SetValue(cameraSaturationVal + 0.0078)
             cameraSaturationVal = camera.ColorAdjustmentSaturation.GetValue()
             print (cameraSaturationVal)

          if (meanvalue[1] <85):
             camera.ColorAdjustmentSelector.SetValue("Magenta")
             cameraSaturationVal = camera.ColorAdjustmentSaturation.GetValue()
             camera.ColorAdjustmentSaturation.SetValue(cameraSaturationVal - 0.0078)
             cameraSaturationVal = camera.ColorAdjustmentSaturation.GetValue()
             print (cameraSaturationVal)

          #if (meanvalue[2] >185 and meanvalue[0] <155 and meanvalue[1] >84 and meanvalue[1] <88  ):
          else:
             print ("Good, ok")
             print (MeanRGBValue)
             print ("Please move to patch-18 and press 'c' to start")
             break

    if key == ord("c"):
       print("Calculating Cyan Gain value, please wait...")
       while True:
          grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
          image = converter.Convert(grabResult)
          img = image.GetArray()
          meanvalue = cv2.mean(img)
          #Display results
          cv2.namedWindow('Image',cv2.WINDOW_NORMAL)
          cv2.imshow("Image",img)
          # Swap blue and red values (making it RGB, not BGR)
          MeanRGBValue = np.array([(meanvalue[2], meanvalue[1], meanvalue[0])])
          print (MeanRGBValue)
          cv2.waitKey(1)
          
          if ((meanvalue[0] - meanvalue[1]) <45):
             camera.ColorAdjustmentSelector.SetValue("Cyan")
             cameraHueVal = camera.ColorAdjustmentHue.GetValue()
             camera.ColorAdjustmentHue.SetValue(cameraHueVal + 0.03)
             cameraHueVal = camera.ColorAdjustmentHue.GetValue()
             print ((meanvalue[0] - meanvalue[1]))
             
          if ((meanvalue[0] - meanvalue[1]) >65):
             camera.ColorAdjustmentSelector.SetValue("Cyan")
             cameraHueVal = camera.ColorAdjustmentHue.GetValue()
             camera.ColorAdjustmentHue.SetValue(cameraHueVal - 0.03)
             cameraHueVal = camera.ColorAdjustmentHue.GetValue()
             print ((meanvalue[0] - meanvalue[1]))

          if (meanvalue[2] >9 ):
             camera.ColorAdjustmentSelector.SetValue("Cyan")
             cameraSaturationVal = camera.ColorAdjustmentSaturation.GetValue()
             camera.ColorAdjustmentSaturation.SetValue(cameraSaturationVal + 0.0078)
             cameraSaturationVal = camera.ColorAdjustmentSaturation.GetValue()
             print (cameraSaturationVal)

          if (meanvalue[2] <7):
             camera.ColorAdjustmentSelector.SetValue("Cyan")
             cameraSaturationVal = camera.ColorAdjustmentSaturation.GetValue()
             camera.ColorAdjustmentSaturation.SetValue(cameraSaturationVal - 0.0078)
             cameraSaturationVal = camera.ColorAdjustmentSaturation.GetValue()
             print (cameraSaturationVal)

          else:
             print (MeanRGBValue)
             print ("=====================6-Axis Operator Hue&Saturation Values=====================")
             camera.ColorAdjustmentSelector.SetValue("Red")
             cameraSaturationVal = camera.ColorAdjustmentSaturation.GetValue()
             cameraHueVal = camera.ColorAdjustmentHue.GetValue()
             print("Red Selector: Hue=",cameraHueVal," Saturation=",cameraSaturationVal)
             camera.ColorAdjustmentSelector.SetValue("Green")
             cameraSaturationVal = camera.ColorAdjustmentSaturation.GetValue()
             cameraHueVal = camera.ColorAdjustmentHue.GetValue()
             print("Green Selector: Hue=",cameraHueVal," Saturation=",cameraSaturationVal)
             camera.ColorAdjustmentSelector.SetValue("Blue")
             cameraSaturationVal = camera.ColorAdjustmentSaturation.GetValue()
             cameraHueVal = camera.ColorAdjustmentHue.GetValue()
             print("Blue Selector: Hue=",cameraHueVal," Saturation=",cameraSaturationVal)
             camera.ColorAdjustmentSelector.SetValue("Yellow")
             cameraSaturationVal = camera.ColorAdjustmentSaturation.GetValue()
             cameraHueVal = camera.ColorAdjustmentHue.GetValue()
             print("Yellow Selector: Hue=",cameraHueVal," Saturation=",cameraSaturationVal)
             camera.ColorAdjustmentSelector.SetValue("Magenta")
             cameraSaturationVal = camera.ColorAdjustmentSaturation.GetValue()
             cameraHueVal = camera.ColorAdjustmentHue.GetValue()
             print("Magenta Selector: Hue=",cameraHueVal," Saturation=",cameraSaturationVal)
             camera.ColorAdjustmentSelector.SetValue("Cyan")
             cameraSaturationVal = camera.ColorAdjustmentSaturation.GetValue()
             cameraHueVal = camera.ColorAdjustmentHue.GetValue()
             print("Cyan Selector: Hue=",cameraHueVal," Saturation=",cameraSaturationVal)
             print ("====Color Calibration process is completed, Well done, Press 'e' to save the calibrated RGB value for DeltaE calculation====")          
             break

    if key == ord("e"):
          #Calculate the mean of each channel
          meanvalue = cv2.mean(img)
          # Swap blue and red values (making it RGB, not BGR)
          MeanRGBValue2 = np.array([(meanvalue[2], meanvalue[1], meanvalue[0])])
          newCameraCalibratedRGBValue = np.append(CameraCalibratedRGBValue, MeanRGBValue2)
          calibratedfile.write(str(newCameraCalibratedRGBValue)[1 : -1]+'\n')
          print ("Write patch:",count1, "=",newCameraCalibratedRGBValue)
          print ("===Move to next patch and press 'e' to store the next RGB value, press 'f' when the 24th patch RGB value is recorded===")
          count1 += 1

    if key == ord("f"):
        print ("Calibrated RGB Values recorded")
        print ("Press 'q' to calculate DeltaE values")
        calibratedfile.close()
        
    # if the `q` key was pressed, break from the loop.   
    if key == ord("q"):
       break
camera.Close()


print ("=========================================DeltaE Calculation========================================")
#print ("======================================Convert RGB Value to LAB Value========================================")
#Read Calibrated RGB value from file for the calibration
CalibratedRGBValue = np.loadtxt("NewCameracalibratedRGBValue.txt", dtype=int)
file1 = open(r"C:\Users\\Desktop\ColorCalibration\NewCameracalibratedLABValue.txt","w+")
for i in range (24):
    CalibratedRGBValue1 = np.round(CalibratedRGBValue, 3)
    CalibratedLABValue = rgb2lab(CalibratedRGBValue1[i]) #Covert RGB to LAB value for DeltaE Calculation
    CalibratedLABValue2 = np.char.replace(str(CalibratedLABValue),",","")  ##replace "," with ""
    file1.write(str(CalibratedLABValue2)[1 : -1]+'\n')
file1.close()

#Read reference LAB value and Calibrated LAB value for DeltaE Calculation
#print ("=================Results================")
ReferenceLABValue = np.loadtxt("ReferenceLABValue.txt", dtype=str)
CalibratedLABValue = np.loadtxt("CalibratedLABValue.txt", dtype=str)

aveDeltaE = np.array([])
for i in range (24):
    ReferenceLABValuefloat = ReferenceLABValue[i].astype(np.float)
    CalibratedLABValuefloat = CalibratedLABValue[i].astype(np.float)
    DeltaE = skimage.color.deltaE_ciede2000(ReferenceLABValuefloat,CalibratedLABValuefloat , kL=1, kC=1, kH=1)
    aveDeltaE =np.append(aveDeltaE,DeltaE)
    print ("Patch",i+1," DeltaE=", DeltaE)
print ("Average Delta E= ", np.mean(aveDeltaE))