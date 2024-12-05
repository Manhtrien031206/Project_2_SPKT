import math
import time
import cv2
import numpy as np
import os
import Preprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Constants
ADAPTIVE_THRESH_BLOCK_SIZE = 19
ADAPTIVE_THRESH_WEIGHT = 9
Min_char = 0.01
Max_char = 0.09
RESIZED_IMAGE_WIDTH = 20
RESIZED_IMAGE_HEIGHT = 30

class ImageHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.src_path.endswith(('.jpg', '.png')):
            print(f"Phát hiện ảnh mới: {event.src_path}")
            time.sleep(1)
            process_license_plate(event.src_path)

def process_license_plate(image_path):
    if not (os.path.exists("classifications.txt") and os.path.exists("flattened_images.txt")):
        print("Model files are missing.")
        return
    
    img = cv2.imread(image_path)
    img = cv2.resize(img, dsize=(1920, 1080))
    
    try:
        npaClassifications = np.loadtxt("classifications.txt", np.float32)
        npaFlattenedImages = np.loadtxt("flattened_images.txt", np.float32)
        npaClassifications = npaClassifications.reshape((npaClassifications.size, 1))
        kNearest = cv2.ml.KNearest_create()
        kNearest.train(npaFlattenedImages, cv2.ml.ROW_SAMPLE, npaClassifications)
        
        imgGrayscaleplate, imgThreshplate = Preprocess.preprocess(img)
        canny_image = cv2.Canny(imgThreshplate, 250, 255)
        kernel = np.ones((3, 3), np.uint8)
        dilated_image = cv2.dilate(canny_image, kernel, iterations=1)
        
        contours, _ = cv2.findContours(dilated_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]

        screenCnt = []
        for c in contours:
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.06 * peri, True)
            if len(approx) == 4:
                screenCnt.append(approx)

        if not screenCnt:
            print("No plate detected")
            return

        for screenCnt in screenCnt:
            # License plate processing logic continues as in your code...
            pass

        cv2.imshow('License plate', img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    folder_to_track = r"C:\xampp\htdocs\doan2\uploads"
    event_handler = ImageHandler()
    observer = Observer()
    observer.schedule(event_handler, folder_to_track, recursive=False)
    
    observer.start()
    print(f"Theo dõi thư mục: {folder_to_track}")
    
    try: 
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
