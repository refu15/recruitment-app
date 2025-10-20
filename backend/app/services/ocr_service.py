from google.cloud import vision
from typing import Dict, Any
import io
from PIL import Image
import PyPDF2
from pdf2image import convert_from_path
from app.utils.config import settings
import os

class OCRService:
    def __init__(self):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = settings.google_application_credentials
        self.client = vision.ImageAnnotatorClient()

    async def extract_text_from_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """PDFからテキストを抽出"""
        try:
            # PDFを画像に変換
            images = convert_from_path(pdf_path)

            all_text = []
            total_confidence = 0.0

            for i, image in enumerate(images):
                # 画像をバイト配列に変換
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format='PNG')
                img_byte_arr = img_byte_arr.getvalue()

                # Vision APIで画像解析
                vision_image = vision.Image(content=img_byte_arr)
                response = self.client.text_detection(image=vision_image)
                texts = response.text_annotations

                if texts:
                    all_text.append(texts[0].description)
                    # 信頼度の計算（簡易版）
                    total_confidence += response.text_annotations[0].score if hasattr(response.text_annotations[0], 'score') else 0.9

            avg_confidence = total_confidence / len(images) if images else 0.0

            return {
                "text": "\n\n".join(all_text),
                "confidence": avg_confidence,
                "page_count": len(images),
                "success": True
            }

        except Exception as e:
            return {
                "text": "",
                "confidence": 0.0,
                "page_count": 0,
                "success": False,
                "error": str(e)
            }

    async def extract_text_from_image(self, image_path: str) -> Dict[str, Any]:
        """画像からテキストを抽出"""
        try:
            with io.open(image_path, 'rb') as image_file:
                content = image_file.read()

            image = vision.Image(content=content)
            response = self.client.text_detection(image=image)
            texts = response.text_annotations

            if response.error.message:
                raise Exception(response.error.message)

            extracted_text = texts[0].description if texts else ""
            confidence = texts[0].score if texts and hasattr(texts[0], 'score') else 0.9

            return {
                "text": extracted_text,
                "confidence": confidence,
                "success": True
            }

        except Exception as e:
            return {
                "text": "",
                "confidence": 0.0,
                "success": False,
                "error": str(e)
            }
