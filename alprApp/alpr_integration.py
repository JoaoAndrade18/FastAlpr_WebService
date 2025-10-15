from fast_alpr import ALPR
from ultralytics import YOLO
from django.core.files.uploadedfile import InMemoryUploadedFile
from typing import List, Union
import cv2
import numpy as np
import os

class FastALPR:
    def __init__(self):
        self.alpr = ALPR(
            detector_model="yolo-v9-t-384-license-plate-end2end",
            ocr_model="cct-xs-v1-global-model",
        )
        self.auxLabelPlateDetector = YOLO('best_placa.pt')

    def fix_plate(self, text):
        def L(ch): return ch.isalpha()
        def N(ch): return ch.isdigit()

        default = [L, L, L, N, None, N, N] 
        
        corr = []
        for i, ch in enumerate(text[:7]): 
            f = default[i] 
            
            if f is None: 
                corr.append(ch)
            elif f == L:  
                if L(ch): 
                    corr.append(ch)
                else:  
                    mapa = {'0':'O', '1':'I', '2':'Z', '3':'E', '4':'A', '5':'S', '6':'G', '7':'T', '8':'B', '9':'B'}
                    corr.append(mapa.get(ch, ch))
            else:  
                if N(ch):  
                    corr.append(ch)
                else: 
                    mapa = {'O':'0', 'Q':'0', 'D':'0', 'I':'1', 'Z':'2', 'A':'4', 'S':'5', 'G':'6', 'T':'7', 'B':'8', 
                            'E':'3', 'C':'6', 'Y':'4', 'L':'1', 'F':'5', 'H':'4', 'X':'8', 'J':'1', 'K':'6', 
                            'M':'1', 'N':'1', 'P':'9', 'R':'2', 'U':'0', 'V':'8', 'W':'3'}
                    corr.append(mapa.get(ch, ch))
        
        return "".join(corr)

    def process_images(self, images: List[Union[str, InMemoryUploadedFile]]) -> List[dict]:
        """
        Accepts a list of image paths or uploaded files and returns a list of dictionaries with:
        - 'input': original image name or path
        - 'text': detected text
        - 'raw': raw ALPR response
        """
        results = []

        for img_input in images:
            if isinstance(img_input, str):
                image = cv2.imread(img_input)
                name = os.path.basename(img_input)
            else:  
                img_bytes = np.frombuffer(img_input.read(), np.uint8)
                image = cv2.imdecode(img_bytes, cv2.IMREAD_COLOR)
                name = getattr(img_input, 'name', 'uploaded_image')

            alpr_results = self.alpr.predict(image)

            if not alpr_results:
                yolo_results = self.auxLabelPlateDetector(image)
                if yolo_results and len(yolo_results[0].boxes) > 0:
                    box = yolo_results[0].boxes[0]
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    imageRoi = image[y1:y2, x1:x2]
                    alpr_results = self.alpr.predict(imageRoi)

            text = None
            if alpr_results and len(alpr_results) and hasattr(alpr_results[0], "ocr"):
                text = alpr_results[0].ocr.text
                raw = alpr_results[0].to_dict() if hasattr(alpr_results[0], "to_dict") else str(alpr_results[0])
            else:
                raw = str(alpr_results)
            
            # --- Fixes inclusion of invalid characters ---
            text = self.fix_plate(text)
            results.append({
                "input": name,
                "text": text,
                "raw": raw,
            })

        return results

alpr_service = FastALPR()
