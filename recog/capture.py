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

        # party(相手パーティ待ち)→chosen(対戦画面待ち)→一旦終了
        self.phase = "party"
        self.banme = 0
        # OBSの設定値を読み込む
        with open("recog/capture.json", "r") as json_file:
            self.account = json.load(json_file)
        try:
            with open("recog/setting.json", "r") as json_file:
                self.setting_data = json.load(json_file)
        except FileNotFoundError:
            self.setting_data = {"panipani_auto": False}

        self.is_panipani = self.setting_data["panipani_auto"]

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
            self.loop.run_until_complete(self.obs.break_request())
            return True
        except:
            return False

    # キャプチャ画像取得
    def get_screenshot(self):
        responseData = self.loop.run_until_complete(
            self.obs.get_screenshot(self.account["source_name"])
        )
        screenshotBase64 = responseData.responseData["imageData"].split(",")[1]
        img_binary = base64.b64decode(screenshotBase64)
        jpg = np.frombuffer(img_binary, dtype=np.uint8)
        self.img = cv2.imdecode(jpg, cv2.IMREAD_COLOR)

    # キャプチャ画像保存
    def save_screenshot(self, coordName, savePath):
        coord = self.coords.dicCoord[coordName]
        img1 = self.img[coord.top : coord.bottom, coord.left : coord.right]
        cv2.imwrite(savePath, img1)

    # フェーズに応じて画像認識処理
    def image_recognize(self):
        match self.phase:
            case "party":
                return self.recognize_chosen_capture()
            case "chosen":
                chosen = self.started_battle()
                if chosen:
                    self.phase = "party"
                    return chosen
                elif self.chose_pokemon():
                    banme_list = [
                        self.recognize_chosen_num(banme) for banme in range(3)
                    ]
                    if self.is_panipani and banme_list != [-1, -1, -1]:
                        self.create_my_chosen_image(
                            banme_list, len(banme_list) - banme_list.count(-1)
                        )
                    return banme_list
        return -1

    # 選出画面検知
    def chose_pokemon(self):
        return self.is_exist_image(
            "recog/recogImg/situation/sensyutu.jpg", 0.8, "sensyutu"
        ) or self.is_exist_image(
            "recog/recogImg/situation/sensyutu2.jpg", 0.8, "sensyutu"
        )

    # 選出画面解析
    def recognize_chosen_capture(self) -> tuple[list[Pokemon], str]:
        self.get_screenshot()
        if self.chose_pokemon():
            self.phase = "chosen"
            oppo_tn = self.recognize_oppo_tn()
            return (self.recognize_oppo_party(), oppo_tn)

    # 相手パーティの解析
    def recognize_oppo_party(self):
        if self.is_panipani:
            # OBS表示用のキャプチャ取得
            self.save_screenshot("myPokemon", "recog/outputImg/myPokemon.jpg")
            self.save_screenshot("opoPokemon", "recog/outputImg/opoPokemon.jpg")
            self.set_my_party_img()

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

    # OBS表示用の自分パーティ画像取得
    def set_my_party_img(self):
        coord = self.coords.dicCoord["mySensyutu"]
        self.myPartyImg = self.img[coord.top : coord.bottom, coord.left : coord.right]

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

    # OBS表示用の自分選出画像作成
    def create_my_chosen_image(self, sensyutuPoke, count):
        img = Image.fromarray(cv2.cvtColor(self.myPartyImg, cv2.COLOR_BGR2RGB))
        if self.banme == count:
            return
        self.banme = count
        i = 0
        dst = Image.new("RGB", (575 * (count) + 1, 106))
        for num in sensyutuPoke:
            if num == -1:
                dst.save("recog/outputImg/outputSensyutu.jpg", quality=95)
                return
            outputImg = img.crop((0, 0 + 115 * num, 570, 105 + 115 * num))
            dst.paste(outputImg, (0 + 570 * i, 0))
            i = i + 1
        dst.save("recog/outputImg/outputSensyutu.jpg", quality=95)

    # 対戦開始画面を検知
    def started_battle(self):
        self.get_screenshot()
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
    def ocr_full(self, base_img):
        try:
            if self.path_tesseract not in os.environ["PATH"].split(os.pathsep):
                os.environ["PATH"] += os.pathsep + self.path_tesseract
            tools = pyocr.get_available_tools()
            tool = tools[0]
            img = cv2.cvtColor(base_img, cv2.COLOR_BGR2RGB)
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
