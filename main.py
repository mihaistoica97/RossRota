import cv2
import easyocr
import matplotlib.pyplot as plt

def draw_bounding_boxes(image, detections, threshold=0.25):

    for bbox, text in detections:
        cv2.rectangle(image, tuple(map(int, bbox[0])), tuple(map(int, bbox[2])), (0, 255, 0), 5)

        cv2.putText(image, text, tuple(map(int, bbox[0])), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.65, (255, 0, 0), 2)

def betterSort(result):
    sorted_result = []
    i = 0
    division = 0
    while(i < len(result)):
        value = result[i]
        if('/' in value[1] and value[1][0] != 'A' and value[1][-1] != 'L'):
            sorted_result.append([result.pop(i)])
            i -= 1 #THERE HAS TO BE A BETTER WAY
        i += 1

    division = int(sorted_result[-1][0][0][2][1] / len(sorted_result)) #get possible lowest known point and divide by the amount of weeks, hopefully gives a nice barrier for each week
    division = division + 5 # Give it some space
    for idx, row in enumerate(sorted_result):
        i = 0
        while(i < len(result)):
            value = result[i]
            if(value[0][0][1] <= division * (idx + 1)):
                if(len(row) < 8 and value not in sorted_result[idx]):
                    sorted_result[idx].append(result.pop(i))
                    i-=1 #Think of a nicer way to do this
            i+=1


    for row in sorted_result:
        print([word[1] for word in sorted(row, key=lambda element: element[0][0][0])])
        print('\n')
    return sorted_result

reader = easyocr.Reader(['en'])

img = cv2.imread('cropped_test_rota.jpg')
gry = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


thr = cv2.adaptiveThreshold(gry, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                   cv2.THRESH_BINARY, 127, 57)
cv2.imwrite('cropped_thresh.png', thr)

result = reader.readtext(thr,  paragraph=True, y_ths = 0.2, slope_ths = 1,width_ths=1.5, height_ths=1.2, decoder ='beamsearch', beamWidth=200, min_size=7, mag_ratio=1.5)
print("------RESULTS-----")

# draw_bounding_boxes(thr, result)

# plt.imshow(thr)

# plt.show()
result = sorted(result, key=lambda element: ([element[0][0][1], element[0][0][0], element[0][3][1], element[0][3][0]])) #Sort values by top left and bottom right corners of each box
#words = ([word[1] for word in result])

betterSort(result)

# [[[96, 6], [235, 6], [235, 46], [96, 46]], 'W/C Date'],              [[[659, 22], [779, 22],  [779, 70], [659, 70]], 'Tuesday']   [[[884, 27], [1040, 27], [1040, 79], [884, 79]], 'Wednesday']

# [[[1, 64], [167, 64], [167, 104], [1, 104]], '18/03/2024'],

#[[1831, 58], [1926, 58], [1926, 100], [1831, 100]], 'Sunday']


#[[34, 859], [193, 859], [193, 897], [34, 897]], '24/06/2024']
