import cv2
import os

os.environ["OPENCV_LOG_LEVEL"] = "debug" 

# Try different indices if the camera index 0 doesn't work
for index in range(5):
    cap = cv2.VideoCapture(index)
    if cap.isOpened():
        print(f"Camera opened with index {index}")
        break
else:
    print("Could not open any camera.")
    exit()

i = 0

while cap.isOpened():
    ret, frame = cap.read()
    
    # This condition prevents from infinite looping  
    # in case video ends.
    if ret == False:
        break
    
    # Save Frame by Frame into disk using imwrite method 
    cv2.imwrite('Frame'+str(i)+'.jpg', frame)
    i += 1

cap.release()
cv2.destroyAllWindows()
