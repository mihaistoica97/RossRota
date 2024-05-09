import cv2
import easyocr
import matplotlib.pyplot as plt
import datetime

# def draw_bounding_boxes(image, detections, threshold=0.25):
#     #Helper function in case anything goes wrong
#     for bbox, text in detections:
#         cv2.rectangle(image, tuple(map(int, bbox[0])), tuple(map(int, bbox[2])), (0, 255, 0), 5)

#         cv2.putText(image, text, tuple(map(int, bbox[0])), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.65, (255, 0, 0), 2)

def verifyData(sorted_result):
    if('W/C' not in sorted_result[0][0].upper() or 'DATE' not in sorted_result[0][0].upper()):
        print('Somethings wrong with this image, try again')
        return False
    sorted_result.pop(0)
    last_date = 0
    verified_data = []
    for row in sorted_result:
        date = datetime.datetime.strptime(row[0], "%d/%m/%Y")
        if(last_date):
            if(last_date == (date - datetime.timedelta(days=7))):
                verified_data.append([row[0]])
            else:
                # This could spit out the wrong date, double check by going backwards. This is fine for now though
                date = last_date + datetime.timedelta(days=7)
                verified_data.append(date.strftime('%d/%m/%Y'))
        else:
            verified_data.append([row[0]])
        last_date = date

    for idx, row in enumerate(sorted_result):
        for value in row[1:]:
            if any(char.isdigit() for char in value):
                # Usual mistakes
                value = value.replace('o', '0')
                value = value.replace('O', '0')
                value = value.replace('c', '0')
                value = value.replace('0000', '2400')
                value = list(value)
                value[4] = '-'
                value = ''.join(value)
            if 'DAY' in value.upper() or 'OFF' in value.upper():
                # INCREASE GRANULARITY OF THIS CHECK
                value = 'Day Off'

            verified_data[idx].append(value)
    #print(verified_data)
    return verified_data

def getPossibleDays(verified_data, start_time):
    possible_days = []
    for row in verified_data:
        for idx, value in enumerate(row):
            if('Day Off' in value):
                day_off_date = datetime.datetime.strptime(row[0], "%d/%m/%Y") + datetime.timedelta(days=idx - 1)
                if(day_off_date >= datetime.datetime.today()):
                    possible_days.append(day_off_date.strftime('%A %d/%m/%Y'))
            elif('-' in value and int(value.split('-')[0]) + 400 < start_time and int(value.split('-')[1]) <= (start_time - 200)): # THINK OF A BETTER WAY OF DOING THIS, BROTHER THIS STINKS.
            #Probably should check if value is in range between the start time and end time also if the value is over 0000 then it's in the next day
                day_off_date = datetime.datetime.strptime(row[0], "%d/%m/%Y") + datetime.timedelta(days=idx - 1)
                if(day_off_date >= datetime.datetime.today()):
                    possible_days.append(day_off_date.strftime(value + ' %A %d/%m/%Y'))
    return possible_days

def sortDays(result):
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
    just_characters = []
    for row in sorted_result:
        just_characters.append([word[1] for word in sorted(row, key=lambda element: element[0][0][0])])

    return just_characters

if __name__ == '__main__':
    print("Please give me a FULL file path to a picture of Ross' rota")
    rota_picture = input()
    print("Please give me a start time (in 24 hour time with no special characters)")
    start_time = int(input())
    reader = easyocr.Reader(['en'])

    img = cv2.imread(rota_picture)
    gry = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


    thr = cv2.adaptiveThreshold(gry, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                    cv2.THRESH_BINARY, 127, 57)
    cv2.imwrite('cropped_thresh.png', thr)

    result = reader.readtext(thr,  paragraph=True, y_ths = 0.2, slope_ths = 1,width_ths=1.5, height_ths=1.2, decoder ='beamsearch', beamWidth=50, min_size=7, mag_ratio=1.5)
    print("------RESULTS-----")

    # draw_bounding_boxes(thr, result)

    # plt.imshow(thr)

    # plt.show()

    sorted_result = sortDays(result)

    verified_data = verifyData(sorted_result)
    if(verified_data):
        days_off = []
        blocked_by_tuesday_or_thursday_days = [] # This should change to be decided by user
        finishes_early_enough_days = []
        #Also the start time value here needs to be an input or something
        for value in getPossibleDays(verified_data, start_time):
            if('Tuesday' in value or 'Thursday' in value):
                blocked_by_tuesday_or_thursday_days.append(value)
            elif('-' in value):
                finishes_early_enough_days.append(value)
            else:
                days_off.append(value)

        print('The following are days that are available for sure')
        for day in days_off:
            print(day)
        print('The following are days that are blocked by other events')
        for day in blocked_by_tuesday_or_thursday_days:
            print(day)
        print('The following are days where Ross finishes early enough to play')
        for day in finishes_early_enough_days:
            print(day)