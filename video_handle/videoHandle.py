import os
import glob
import cv2

class videoInfo:
    def __init__(self,fps,totalFrame):
        self.fps = fps
        self.totFrame = totalFrame
class vidCollector:
    def __init__(self):
        self.vidCap = []
        self.vidList = []
        self.vidIndex = 0
        self.curFrame = []
        self.vidInfo = videoInfo(0,0)
        self.isRunning = False
        
class videoHandle:
    def __init__(self, verbose=True):
        self.vid_in = vidCollector()
        self.vid_out = vidCollector()
        if verbose:
            print('initiate empyt video handle with index at ' + str(self.vid_in.vidIndex))
        
    def getVideoList(self, filePath, fileExtension=['avi'], verbose=True):
        vidNum = 0
        if not filePath.endswith('/'):
            filePath = filePath + '/'
        for ext in fileExtension:
            regString = filePath + '*' + ext
            videos = glob.glob(regString)
            self.vid_in.vidList += videos
            vidNum = vidNum + len(videos)
        if verbose:
            print('from file path :{0}, we obtain {1} videos'.format(filePath,vidNum))
    
    # get video name from the current index of video_in (for dir=0) or video_out (for dir=1)  
    def getVideoName(self, dir=0, verbose=True):
        if dir==0:
            vidHd = self.vid_in
        else:
            vidHd = self.vid_out
         
        # assign it to internal variable just to make the code more readable
        videos = vidHd.vidList
        index = vidHd.vidIndex
        filename_ext = os.path.basename(videos[index])
        filename, file_extension  = os.path.splitext(filename_ext)
        if verbose:
            print('fileName:{0}.'.format(filename))
        return filename
    
    # increase the video index get the next video in video list
    # video_in (for dir=0) or video_out (for dir=1) 
    def nextVideo(self, dir=0, verbose=True):
        if dir==0:
            vidHd = self.vid_in
        else:
            vidHd = self.vid_out
        if (vidHd.vidIndex +1) >= len(vidHd.vidList):
            vidHd.index = 0
        else:
            vidHd.index = vidHd.index + 1
        if verbose:
            print('Next index:{0}'.format(vidHd.index))
        return self.getVideoName(dir=dir, verbose=verbose)
    
    def openVideo(self, dir=0, verbose=True):
        if dir==0:
            vidHd = self.vid_in
        else:
            vidHd = self.vid_out
        videos = vidHd.vidList
        index = vidHd.vidIndex
        if vidHd.isRunning:
            if verbose:
                print('releasing the current video capture')
                vidHd.vidCap.release()
        vidHd.vidCap = cv2.VideoCapture(videos[index])
        try:
            # Find OpenCV version
            (major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')
            if int(major_ver)  < 3 :
                fps =  vidHd.vidCap.get(cv2.cv.CV_CAP_PROP_FPS)
                total = int( vidHd.vidCap.get(cv2.cv.CAP_PROP_FRAME_COUNT))
                if verbose:
                    print("Frames per second using video.get(cv2.cv.CV_CAP_PROP_FPS): {0}".format(fps))
            else :
                fps =  vidHd.vidCap.get(cv2.CAP_PROP_FPS)
                total = int(vidHd.vidCap.get(cv2.CAP_PROP_FRAME_COUNT))
                if verbose:
                    print("Frames per second using video.get(cv2.CAP_PROP_FPS) : {0}".format(fps))
            
            vidHd.vidInfo = videoInfo(fps,total)
            vidHd.isRunning = True
        except:
            vidHd.vidCap.release()
            vidHd.isRunning = False
        return vidHd.isRunning

    def initVideoOut(self, frameSize=[], verbose=True):
        if not self.vid_in.isRunning:
            print('no input video, please openVid first')
            return False

        if len(frameSize) == 0:
            if verbose:
                print('no framesize is specify, try to use the input video framesize')
            if len(self.vid_in.curFrame) == 0:
                print('Cannot obtain current frame info, please readFrame first')
                return False
            frameSize = self.curFrame.shape[1], self.curFrame[0]

        inpath = self.vid_in.vidList[self.vid_in.vidIndex]
        # get out two step
        vidInName = self.getVideoName()
        tempPath = os.path.dirname(inpath)
        tempPath = os.path.dirname(tempPath)
        video_output = tempPath + '/video_out/' + vidInName + '_out.mp4'
        fourcc = cv2.VideoWriter_fourcc(*'MP4V')
        fps = self.vid_in.vidInfo.fps
        self.vid_out.vidCap = cv2.VideoWriter(video_output,fourcc,float(fps),frameSize)
    def readFrame(self, verbose=True):
        if not self.vid_in.isRunning:
            print('no video is capturing right now')
            return False, []

        ret, self.curFrame =  self.vid_in.vidCap.read()
        if not ret:
            if verbose:
                print('the capturing video is reaching the end, the video will now release')
            self.vid_in.vidCap.release()
            self.isRunning = ret

        return ret, self.vid_in.curFrame
    def closeVideo(self, dir =0, verbose=True):
        if dir==0:
            vidHd = self.vid_in
        else:
            vidHd = self.vid_out
        
        vidHd.vidCap.release()
        vidHd.isRunning = False
        vidHd.curFrame = []
