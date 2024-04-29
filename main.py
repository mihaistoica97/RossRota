import cv2
import easyocr
import matplotlib.pyplot as plt 

def draw_bounding_boxes(image, detections, threshold=0.25):

    for bbox, text in detections:
        cv2.rectangle(image, tuple(map(int, bbox[0])), tuple(map(int, bbox[2])), (0, 255, 0), 5)

        cv2.putText(image, text, tuple(map(int, bbox[0])), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.65, (255, 0, 0), 2)

reader = easyocr.Reader(['en'])

value = ""
first_thresh = 109
second_thresh = 56

img = cv2.imread('cropped_test_rota.jpg')
gry = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


thr = cv2.adaptiveThreshold(gry, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                   cv2.THRESH_BINARY, 127, 57)
cv2.imwrite('cropped_thresh.png', thr)
# detail = 0,
result = reader.readtext(thr,  paragraph=True, y_ths = 0.2, width_ths=1.5, height_ths=1.2, decoder ='beamsearch', beamWidth=200, min_size=7, mag_ratio=1.5)
print("------RESULTS-----")
print(result)

draw_bounding_boxes(thr, result)

plt.imshow(thr)

plt.show()