import threading,queue,cv2


class VideoCapture:

        def __init__(self, name):
            self.cap = cv2.VideoCapture(name)
            self.q = queue.Queue()
            self.t = threading.Thread(target=self._reader)
            self.t.daemon = True
            self.t.start()

        # read frames as soon as they are available, keeping only most recent one
        def _reader(self):
            try:
                while True:
                    ret, frame = self.cap.read()
                    if not ret:
                        break
                    if not self.q.empty():
                        try:
                            self.q.get_nowait()   # discard previous (unprocessed) frame
                        except queue.Empty:
                            pass
                    self.q.put(frame)
            except:
                print("sin camara")

        def read(self):
            #if self.q.empty():
            #  return 0
            return 1,self.q.get()
        
        def release(self):
            self.cap.release()
            self.t.join()
        
        def isOpened(self):
            return self.cap.isOpened()
            

cap = VideoCapture('http://192.168.100.25:8080/video')
print(cap.isOpened())
while(True):
# if 1:
    # time.sleep(1)
    ret,frame = cap.read()
    cv2.imshow('Detected Markers', frame)
    # cv2.waitKey(0)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        cap.release()
        cv2.destroyAllWindows()
        break