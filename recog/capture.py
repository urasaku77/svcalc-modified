import asyncio
import base64
import glob
import json
import os

import cv2
import numpy as np
import pyocr
from PIL import Image

from pokedata.exception import unrecognizable_pokemon
from pokedata.pokemon import Pokemon
from recog.coodinate import ConfCoordinate
from recog.obs import Obs


class Capture:
    def __init__(self):
        self.coords = ConfCoordinate()
        self.path_tesseract = r"E:\Tesseract-OCR"

        # party(相手パーティ待ち)→chosen(自分選出待ち)→start(対戦開始待ち)→finish(対戦終了待ち)
        self.phase = "party"
        # OBSの設定値を読み込む
        with open("recog/capture.json", "r") as json_file:
            self.account = json.load(json_file)

    # Websocket接続
    def connect_websocket(self):
        try:
            self.loop = asyncio.get_event_loop()
            self.obs = Obs(self.loop, self.account["port"], self.account["password"])
            return True
        except:
            return False

    # Websocket切断
    def disconnect_websocket(self):
        try:
            self.loop.run_until_complete(self.obs.breakRequest())
            return True
        except:
            return False

    # キャプチャ画像取得
    def getScreenshot(self):
        responseData = self.loop.run_until_complete(
            self.obs.getScreenshot(self.account["source_name"])
        )
        screenshotBase64 = responseData.responseData["imageData"].split(",")[1]
        img_binary = base64.b64decode(screenshotBase64)
        jpg = np.frombuffer(img_binary, dtype=np.uint8)
        self.img = cv2.imdecode(jpg, cv2.IMREAD_COLOR)

    # フェーズに応じて画像認識処理
    def image_recognize(self):
        match self.phase:
            case "party":
                return self.recognize_chosen_capture()
            case "chosen":
                chosen = self.sturted_battle()
                if not chosen:
                    return tuple(
                        [self.recognize_chosen_num(banme) for banme in range(3)]
                    )
                else:
                    self.phase = "party"
                    return chosen
        return -1

    # 選出画面解析
    def recognize_chosen_capture(self):
        self.getScreenshot()
        if self.is_exist_image(
            "recog/recogImg/situation/sensyutu.jpg", 0.8, "sensyutu"
        ) or self.is_exist_image(
            "recog/recogImg/situation/sensyutu2.jpg", 0.8, "sensyutu"
        ):
            self.phase = "chosen"
            self.recognize_oppo_tn()
            return self.recognize_oppo_party()

    # 相手パーティの解析
    def recognize_oppo_party(self):
        pokemonImages = glob.glob("recog/recogImg/pokemon/*")
        coordsList = [
            "opoPoke1",
            "opoPoke2",
            "opoPoke3",
            "opoPoke4",
            "opoPoke5",
            "opoPoke6",
        ]
        pokemonlist: list[Pokemon] = [Pokemon()] * 6

        for coord in range(len(coordsList)):
            oppo = self.is_exist_image_max(pokemonImages, 0.7, coordsList[coord])
            if oppo != "":
                oppo_shaped = self.shape_poke_num(oppo)
                oppo_pokemon = Pokemon.by_pid(oppo_shaped, True)
                if oppo_pokemon.base_name in unrecognizable_pokemon:
                    oppo_pokemon.form_selected = False
                pokemonlist[coord] = oppo_pokemon
        return pokemonlist

    # 相手のTN解析
    def recognize_oppo_tn(self):
        coord = self.coords.dicCoord["opoTn"]
        img = self.img[coord.top : coord.bottom, coord.left : coord.right]
        tn = self.ocr_full(img)
        return tn.replace(" ", "")

    # 自分の選出番号を取得
    def recognize_chosen_num(self, banme):
        for num in range(6):
            if self.is_exist_image(
                "recog\\recogImg\\sensyutu\\banme\\banme" + str(banme + 1) + ".jpg",
                0.85,
                "banme" + str(num + 1),
            ):
                return num
        return -1

    # 対戦開始画面を検知
    def sturted_battle(self):
        self.getScreenshot()
        return self.is_exist_image(
            "recog/recogImg/situation/aitewomiru.jpg", 0.8, "aitewomiru"
        )

    # テンプレートマッチング(最大のみ)
    def is_exist_image_max(self, temp_imgge_name, accuracy, coord_name):
        coord = self.coords.dicCoord[coord_name]
        img1 = self.img[coord.top : coord.bottom, coord.left : coord.right]
        gray = cv2.cvtColor(img1, cv2.COLOR_RGB2GRAY)
        max_val_list: list[float] = []
        for image in temp_imgge_name:
            tmp_max_val: list[float] = []
            for shrink_rate in (0.56, 0.69, 0.86):
                try:
                    temp = cv2.imread(image)
                    temp = cv2.cvtColor(temp, cv2.COLOR_RGB2GRAY)
                    temp = cv2.resize(temp, None, None, shrink_rate, shrink_rate)
                    match = cv2.matchTemplate(gray, temp, cv2.TM_CCOEFF_NORMED)
                    _, max_val, _, max_loc = cv2.minMaxLoc(match)
                    tmp_max_val.append(max_val)
                except:
                    pass

            max_val_list.append(max(tmp_max_val))

        if max(max_val_list) >= accuracy:
            return temp_imgge_name[max_val_list.index(max(max_val_list))]
        else:
            return ""

    # テンプレートマッチング
    def is_exist_image(self, temp_imgge_name, accuracy, coord_name):
        result = False
        coord = self.coords.dicCoord[coord_name]
        img1 = self.img[coord.top : coord.bottom, coord.left : coord.right]
        temp = cv2.imread(temp_imgge_name)
        if temp is None:
            print(temp_imgge_name + "が見つかりません")
            return False

        gray = cv2.cvtColor(img1, cv2.COLOR_RGB2GRAY)
        temp = cv2.cvtColor(temp, cv2.COLOR_RGB2GRAY)

        match = cv2.matchTemplate(gray, temp, cv2.TM_CCOEFF_NORMED)
        loc = np.where(match >= accuracy)
        for _pt in zip(*loc[::-1], strict=False):
            result = True
        return result

    # ポケモンの画像からPIDを取得
    def shape_poke_num(self, origin: str):
        try:
            except_folder = origin.rsplit("\\", 1)[1].rsplit(".", 1)[0]
            except_top_zero = (
                except_folder.lstrip("0") if except_folder[0] == "0" else except_folder
            )
            check_hyphen = (
                except_top_zero + "-0"
                if except_top_zero not in "-"
                else except_top_zero
            )
            return check_hyphen
        except:
            return ""

    # 全体OCR
    def ocr_full(self, img):
        try:
            if self.path_tesseract not in os.environ["PATH"].split(os.pathsep):
                os.environ["PATH"] += os.pathsep + self.path_tesseract
            tools = pyocr.get_available_tools()
            tool = tools[0]
            img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)  # グレースケールに変換
            # 閾値の設定
            threshold_value = 85
            # 配列の作成（output用）
            gray = img.copy()
            # 実装(numpy)
            img[gray < threshold_value] = 0
            img[gray >= threshold_value] = 255
            img = Image.fromarray(img)
            txt = tool.image_to_string(img, lang="jpn")
            return txt
        except Exception as e:
            print(e)
            return ""
