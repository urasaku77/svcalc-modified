import cv2
import os
import pyocr
from PIL import Image
from numpy.random._generator import np

from recog.coodinate import ConfCoordinate

class ImageRecognition(object):
    '''
    画像認識について取り扱うクラス
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.coords=ConfCoordinate()
        self.path_tesseract = r"E:\Tesseract-OCR"
        self.img_flag=False

    def set_image(self,img):
        self.img=img
        self.img_flag=True

    def is_exist_image(self,temp_imgge_name,accuracy,coord_name):
        result=False
        coord=self.coords.dicCoord[coord_name]
        if not self.img_flag:
            return 
        img1 = self.img[coord.top : coord.bottom, coord.left: coord.right]
        temp=cv2.imread(temp_imgge_name)
        if temp is None:
            print(temp_imgge_name+"が見つかりません")
            return False

        gray= cv2.cvtColor(img1,cv2.COLOR_RGB2GRAY)
        temp= cv2.cvtColor(temp,cv2.COLOR_RGB2GRAY)

        match=cv2.matchTemplate(gray,temp,cv2.TM_CCOEFF_NORMED)
        loc = np.where( match >=accuracy)
        for pt in zip(*loc[::-1]):
            result=True
        return result

    def is_exist_image_max(self,temp_imgge_name,accuracy,coord_name):
        coord=self.coords.dicCoord[coord_name]
        img1 = self.img[coord.top : coord.bottom, coord.left: coord.right]
        gray= cv2.cvtColor(img1,cv2.COLOR_RGB2GRAY)
        max_val_list: list[float] = []
        for image in temp_imgge_name:
            tmp_max_val: list[float] = []
            for shrink_rate in (0.56, 0.69, 0.86):
                try:
                    temp=cv2.imread(image)
                    temp= cv2.cvtColor(temp,cv2.COLOR_RGB2GRAY)
                    temp= cv2.resize(temp, None, None, shrink_rate, shrink_rate)
                    match=cv2.matchTemplate(gray,temp,cv2.TM_CCOEFF_NORMED)
                    _, max_val, _, max_loc = cv2.minMaxLoc(match)
                    tmp_max_val.append(max_val)
                except:
                    pass
                
            max_val_list.append(max(tmp_max_val))

        if max(max_val_list) >= accuracy:
            return temp_imgge_name[max_val_list.index(max(max_val_list))]
        else:
            return ""

    def is_banme(self):
        for num in range(6):
            img=self.img[165+num*115:175+num*115,1144:1153]
            lower=np.array([240,240,240],dtype=np.uint8)
            upper=np.array([255,255,255],dtype=np.uint8)
            mask=cv2.inRange(img,lower,upper)
            recognition_image=cv2.bitwise_and(img,img,mask=mask)
            per=np.count_nonzero(recognition_image)
            if per>70:
                return True
        return False

    def recognize_chosen_num(self,banme):
        for num in range(6):
            if self.is_exist_image("recog\\recogImg\\sensyutu\\banme\\banme" + str(banme+1) +".jpg",0.85,"banme"+str(num+1)):
                return num
        return -1

    def recognize_oppo_tn(self):
        coord=self.coords.dicCoord["opoTn"]
        img=self.img[coord.top : coord.bottom, coord.left: coord.right]
        tn = self.ocr_full(img)
        return tn.replace(' ', '')

    def shape_poke_num(self, origin: str):
        try:
            except_folder = origin.rsplit('\\', 1)[1].rsplit('.', 1)[0]
            except_top_zero = except_folder.lstrip('0') if except_folder[0] == "0" else except_folder
            check_hyphen = except_top_zero + "-0" if not except_top_zero in "-" else except_top_zero
            return check_hyphen
        except:
            return ""

    def ocr_full(self, img):
        try:
            if self.path_tesseract not in os.environ["PATH"].split(os.pathsep):
                os.environ["PATH"] += os.pathsep + self.path_tesseract
            tools = pyocr.get_available_tools()
            tool = tools[0]
            img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)#グレースケールに変換
            #閾値の設定
            threshold_value = 85
            #配列の作成（output用）
            gray = img.copy()
            #実装(numpy)
            img[gray < threshold_value] = 0
            img[gray >= threshold_value] = 255
            img = Image.fromarray(img)
            txt = tool.image_to_string(img, lang="jpn")
            return txt
        except Exception as e:
            print(e)
            return ""