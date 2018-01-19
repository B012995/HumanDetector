import cv2


fps = 1
video_input = cv2.VideoCapture('http://admin:3476C559C42E@192.168.11.2:10226/snapshot.cgi?.mjpeg')

if (video_input.isOpened() == False):
    print("ビデオカメラが見つかりません")
    exit()

count = 0
while(True):
    count += 1
    count_padded = '%05d' % count

    ret, frame = video_input.read()

    cv2.imshow('frame', frame)
    c = cv2.waitKey(int(1000/fps)) & 0xFF

    write_file_name = '/Users/nttcom/Desktop/FrameSave/' + count_padded + ".jpg"
    cv2.imwrite(write_file_name, frame)

    if c==27: # ESC
        break

video_input.release()
cv2.destroyAllWindows()