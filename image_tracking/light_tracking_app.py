import cv2
import numpy as np
import serial
import time
import tkinter as tk
from tkinter import Label, Button
from PIL import Image, ImageTk

class VideoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Light Tracker 1000")
        
        # Create a label for displaying the video
        self.label = Label(self.root)
        self.label.pack()
        
        # OpenCV Video Capture. Change this to 1 for USB camera
        self.cap = cv2.VideoCapture(0)
        
        # Buttons
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack()
        
        self.btn1 = Button(self.button_frame, text="Left")
        self.btn1.pack(side=tk.LEFT)
        self.btn1.bind('<ButtonPress>', lambda event: self.func1(True))
        self.btn1.bind('<ButtonRelease>', lambda event: self.func1(False))
        
        self.btn2 = Button(self.button_frame, text="Up")
        self.btn2.pack(side=tk.TOP)
        self.btn2.bind('<ButtonPress>', lambda event: self.func2(True))
        self.btn2.bind('<ButtonRelease>', lambda event: self.func2(False))
        
        self.btn3 = Button(self.button_frame, text="Down")
        self.btn3.pack(side=tk.BOTTOM)
        self.btn3.bind('<ButtonPress>', lambda event: self.func3(True))
        self.btn3.bind('<ButtonRelease>', lambda event: self.func3(False))
        
        self.btn4 = Button(self.button_frame, text="Right")
        self.btn4.pack(side=tk.LEFT)
        self.btn4.bind('<ButtonPress>', lambda event: self.func4(True))
        self.btn4.bind('<ButtonRelease>', lambda event: self.func4(False))
        
        self.toggle_state = False
        self.btn5 = Button(self.button_frame, text="Track", command=self.toggle_func)
        self.btn5.pack(side=tk.LEFT)

        self.toggled = False #This is for only doing things if it was just toggled.
        
        # Update the frame
        self.update()
        
        # Close the application properly
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def update(self):
        if self.toggle_state:
            frame = light_tracker(self)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            self.label.imgtk = imgtk
            self.label.configure(image=imgtk)
            pass

        else:
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame)
                imgtk = ImageTk.PhotoImage(image=img)
                self.label.imgtk = imgtk
                self.label.configure(image=imgtk)
        
        # Call update every 30ms
        self.root.after(30, self.update)
    
    def on_closing(self):
        self.cap.release()
        self.root.destroy()
    
    def func1(self, pressed):
        if pressed:
            print("Button 1 Held Down")
        else:
            print("Button 1 Released")
    
    def func2(self, pressed):
        if pressed:
            print("Button 2 Held Down")
        else:
            print("Button 2 Released")
    
    def func3(self, pressed):
        if pressed:
            print("Button 3 Held Down")
        else:
            print("Button 3 Released")
    
    def func4(self, pressed):
        if pressed:
            print("Button 4 Held Down")
        else:
            print("Button 4 Released")
    
    def toggle_func(self):
        self.toggle_state = not self.toggle_state
        print(f"Toggle Button State: {'ON' if self.toggle_state else 'OFF'}")
        

def light_tracker(self):

    # Parameters
    threshold_bright = 220  # Brightness threshold for bright regions
    threshold_dark = 80     # Threshold for dark regions
    max_bright_area = 20   # Maximum area for small bright contours
    min_dark_area = 10000    # Minimum area for dark contours to be considered

    #if not cap.isOpened():
    #    print("Error: Could not open webcam.")
    #    return
    cap = self.cap
    # Capture frame-by-frame
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame.")
    
    # Get frame dimensions for center calculation
    frame_height, frame_width = frame.shape[:2]
    frame_center = (frame_width // 2, frame_height // 2)

    # Convert frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)

    # Threshold the image to isolate bright areas
    _, thresholded = cv2.threshold(blurred, threshold_bright, 255, cv2.THRESH_BINARY)

    # Find contours of the bright areas
    bright_contours, _ = cv2.findContours(thresholded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # Detect dark regions (invert the grayscale for thresholding dark regions)
    _, dark_mask = cv2.threshold(blurred, threshold_dark, 255, cv2.THRESH_BINARY_INV)
    dark_contours, _ = cv2.findContours(dark_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for bright_contour in bright_contours:
        # Filter small bright contours
        bright_area = cv2.contourArea(bright_contour)
        if bright_area > max_bright_area:
            continue

        # Get bright contour center and bounding box
        bx, by, bw, bh = cv2.boundingRect(bright_contour)
        bright_center = (bx + bw // 2, by + bh // 2)

        # Check for nearby larger dark contours
        valid_dark_contour = False
        for dark_contour in dark_contours:
            dark_area = cv2.contourArea(dark_contour)
            if dark_area < min_dark_area: #minimum dark area
                continue

            # Compute distance between bright center and dark bounding box center
            dx, dy, dw, dh = cv2.boundingRect(dark_contour)
            dark_center = (dx + dw // 2, dy + dh // 2)
                
            # Distance calculation (Euclidean distance)
            distance = np.sqrt((bright_center[0] - dark_center[0]) ** 2 + 
                            (bright_center[1] - dark_center[1]) ** 2)
                
            # Validate if the dark contour is close enough
            if distance < 300:  # Example distance threshold
                valid_dark_contour = True
                break
            
        if valid_dark_contour:
            # Draw bright contour (green box)
            cv2.rectangle(frame, (bx, by), (bx + bw, by + bh), (0, 255, 0), 2)
            cv2.circle(frame, bright_center, 5, (0, 255, 0), -1)
            cv2.rectangle(frame, (dx, dy), (dx + dw, dy + dh), (0, 0, 255), 2)

            #calculate distance and display the text
            distance_x = bright_center[0] - frame_center[0]
            distance_y = bright_center[1] - frame_center[1]
            distance_text = f"dx: {distance_x}, dy: {distance_y}, area: {bright_area}"
            cv2.putText(frame, distance_text, (bx, by - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

            #Send the coordinates to the arduino
            #send_coord(distance_x, distance_y)  

        # Draw a rectangle around the bright area
        #cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        #cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)

        # Display distance information
        #distance_text = f"dx: {distance_x}, dy: {distance_y}"
        #cv2.putText(frame, distance_text, (cx + 10, cy - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    return frame
    '''
    # Display the processed frame
    cv2.imshow("Bright Light Tracking", frame)

    # Break the loop on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break'''

# Release resources
#cap.release()
#cv2.destroyAllWindows()

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoApp(root)
    root.mainloop()
