import cv2
import subprocess as sp
FFMPEG_BIN = "ffmpeg"
import numpy as np

VIDEO_URL = "https://ewcdnsite02.nowe.com/session/09-0ff7c6f7d9eeac4ca142ce59146ff/Content/HLS/LIVE/Channel(HLS_CH332N)/index.m3u8?token=9f8eebf978ab172a3669c1f4a70f1635_1656408938"
saveTo = "/Users/hammerchu/Desktop/newsFrame.jpg"
nowLogo = '/Users/hammerchu/Desktop/DEV/computerVision/P_streaming/PSD/nowNewsLogo_01.jpg'

def detectLogo(small_image, large_image):

    method = cv2.TM_SQDIFF_NORMED

    result = cv2.matchTemplate(small_image, large_image, method)
    mn,_,mnLoc,_ = cv2.minMaxLoc(result)

    return mnLoc

def previewLogo():
    logo = cv2.imread(nowLogo)
    while True:
        cv2.imshow("news", logo)
        if cv2.waitKey(5) == 27:
            break
    cv2.destroyAllWindows()

def runStream():
    # cv2.namedWindow("GoPro",cv2.CV_WINDOW_AUTOSIZE)
    cv2.namedWindow("news")
    logoImg = cv2.imread(nowLogo)
    index = 0
    MPx,MPy = (0,0)
    pipe = sp.Popen([ FFMPEG_BIN, "-i", VIDEO_URL,
            "-loglevel", "quiet", # no text output
            "-an",   # disable audio
            "-f", "image2pipe",
            "-pix_fmt", "bgr24",
            "-vcodec", "rawvideo", "-"],
            stdin = sp.PIPE, stdout = sp.PIPE)
    
    while True:
        X = 1920
        Y = 1080

        timer = cv2.getTickCount() 

        raw_image = pipe.stdout.read(X*Y*3)
        image =  np.fromstring(raw_image, dtype='uint8').reshape((Y,X,3))
        smallerImage = image[0:int(Y/2), 0:int(X/2)]

        if (index % 25 == 0):
            mnLoc = detectLogo(logoImg, image)
            MPx,MPy = mnLoc
            trows,tcols = logoImg.shape[:2]
            cv2.rectangle(image, (MPx,MPy),(MPx+tcols,MPy+trows),(0,0,255),2)
            print (f'MPx: {MPx}  MPy: {MPy}')

        if MPx == 107 and MPy == 65:
            cv2.putText(image, "POSITIVE", (125, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,125, 255), 2)
        else:
            cv2.putText(image, "NEGATIVE", (125, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (125, 125, 255), 2)


        cv2.putText(image, "Fps:", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,0,255), 2)
        fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer) # calculate FPS
        if fps>20: UIColor = (230,20,20)
        else: UIColor = (20,20,230)
        cv2.putText(image,str(int(fps)), (75, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, UIColor, 2)

        dsize = (1280, 720) # resize
        image = cv2.resize(image, dsize, cv2.INTER_LINEAR) # resize
        cv2.imshow("news",image)
        if cv2.waitKey(5) == 27:
            break
        
        # elif cv2.waitKey(1) & 0xff == ord('q'): # save still frame
        #     cv2.imwrite(saveTo.replace('.jpg', '.'+str(index)+'.jpg'), image) 
        index +=1

    cv2.destroyAllWindows()


if __name__ == '__main__':
    runStream()
    # previewLogo()