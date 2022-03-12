"""
Copy the haarcascade_frontalface_alt file in the directory to the training dir specified in the code
"""

import cv2
import os

ROOT = "~/Desktop/pictures"
FACES = "~/Desktop/faces"
TRAIN = "~/Desktop/training"

def detect(srcdir=ROOT, tgtdir=FACES, train_dir=TRAIN):
    for fname in os.listdir(srcdir):
        # Looking for faces, most likely jpgs
        if not fname.upper().endswith('.JPG'):
            continue
        fullname = os.path.join(srcdir, fname)
        newname = os.path.join(tgtdir, fname)
        img = cv2.imread(fullname)
        if img is None:
            continue

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        training = os.path.join(train_dir, 'haarcascade_frontalface_alt.xml')
        cascade = cv2.CascadeClassifier(training)
        rects = cascade.detectMultiScale(gray, 1.3, 5)
        try:
            if rects.any():
                print('Got a face!')
                rects[:, 2:] += rects[:, 2:]
        except AttributeError:
            print(f"No faces found in {fname}")
            continue

        for x1, y1, x2, y2 in rects:
            cv2.rectangle(img, (xy, y1), (x2, y2), (127, 255, 0), 2)
        cv2.imwrite(newname, img)

if __name__ == "__main__":
    detect()
