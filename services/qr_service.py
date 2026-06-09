import qrcode
import json
import cv2
import numpy as np
from PIL import Image
import io


def gerar_qr_code(aluno_id: int, matricula: str, prova_id: int) -> Image.Image:
    """Gera um QR Code com os dados do aluno e da prova."""
    dados = json.dumps({
        "aluno_id": aluno_id,
        "matricula": matricula,
        "prova_id": prova_id
    })
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=6,
        border=2,
    )
    qr.add_data(dados)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white")


def ler_qr_code(imagem_pil: Image.Image) -> dict | None:
    img_array = np.array(imagem_pil.convert("RGB"))
    img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
    detector = cv2.QRCodeDetector()

    # Tentativa 1: imagem original
    data, _, _ = detector.detectAndDecode(img_bgr)
    if data:
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            pass

    # Tentativa 2: escala de cinza
    img_gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    data, _, _ = detector.detectAndDecode(img_gray)
    if data:
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            pass

    # Tentativa 3: aumenta resolução (QR Code pequeno na foto)
    scale = 2.0
    h, w = img_gray.shape
    img_upscaled = cv2.resize(img_gray, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_CUBIC)
    data, _, _ = detector.detectAndDecode(img_upscaled)
    if data:
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            pass

    # Tentativa 4: binarização para melhorar contraste
    _, img_thresh = cv2.threshold(img_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    data, _, _ = detector.detectAndDecode(img_thresh)
    if data:
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            pass

    # Tentativa 5: recorta só o canto inferior direito onde o QR Code está
    h, w = img_gray.shape
    canto = img_gray[int(h * 0.6):, int(w * 0.6):]
    canto_upscaled = cv2.resize(canto, None, fx=3.0, fy=3.0, interpolation=cv2.INTER_CUBIC)
    data, _, _ = detector.detectAndDecode(canto_upscaled)
    if data:
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            pass

    return None