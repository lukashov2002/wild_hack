import cv2
import time
import glob
#model = yolov5.load('best.pt').cpu()

def check_animals():
    return True

def get_video_with_animal(name):
    vid_capture = cv2.VideoCapture(name)
    if (vid_capture.isOpened() == False):  # возвращает логическое значение, которое указывает, действителен ли видеопоток
        print("Ошибка открытия видеофайла")
        exit(-1)
    file_count = 0
    frame_width = int(vid_capture.get(3))
    frame_height = int(vid_capture.get(4))
    frameSize = (frame_width, frame_height)
    j = 1
    out = cv2.VideoWriter('dataset/aim{0:04}.avi'.format(j), cv2.VideoWriter_fourcc(*'XVID'), 25, frameSize)
    print("Для преждевремнного завершения нажмите q или Esc")  # закомментить в будущем
    while (vid_capture.isOpened()):
        ret, frame = vid_capture.read()  # делим на фреймы
        if ret == True:
            #cv2.imshow('Look', frame) #закомментить в будущем
            file_count += 1
            #print('Кадр{0:04d}'.format(file_count)) #закомментить в будущем
            if file_count < 40 or file_count > 245:
                img = frame
                out.write(img)
                if check_animals()==True:
                    out.release()
                    j += 1
                    out = cv2.VideoWriter('dataset/aim{0:04}.avi'.format(j), cv2.VideoWriter_fourcc(*'XVID'), 25, frameSize)

            key = cv2.waitKey(100)
            if (key == ord('q')) or key == 27:
                out.release()
                break
        else:
            break
    vid_capture.release()
    cv2.destroyAllWindows()

name = 'captured.avi' #или путь к файлу. Но надо тестировать внимательно
get_video_with_animal(name)