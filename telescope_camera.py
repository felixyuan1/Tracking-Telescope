import numpy as np
import cv2

cap = cv2.VideoCapture(0)

cv2.startWindowThread()

while True:
    ret, frame = cap.read()
    width = int(cap.get(3))
    height = int(cap.get(4))

    image = np.zeros(frame.shape, np.uint8)
    smaller_frame = cv2.resize(frame, (0,0), fx = 0.5, fy = 0.5)
    image[:height//2, :width//2] = smaller_frame
    image[height//2:, :width//2] = smaller_frame
    image[:height//2, width//2:] = smaller_frame
    image[height//2:, width//2:] = smaller_frame

    cv2.imshow('frame', image)

    if cv2.waitKey(100) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

'''
img = cv2.imread('assets/logo.png', 0)
img = cv2.resize(img, (0, 0), fx=0.5, fy=0.5)


cv2.imshow('Image', img)
cv2.waitKey(0)
cv2.destroyAllWindows()
print(img[230][215:220])
'''