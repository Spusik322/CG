import numpy as np
import cv2
from utils import ensure_rgb, to_gray, clip_uint8, stats_text

def highpass_laplacian(gray, amount=1.0):
    gray_f = gray.astype(np.float64)
    lap = cv2.Laplacian(gray_f, cv2.CV_64F, ksize=3)
    return clip_uint8(gray_f - amount * lap)

def unsharp_masking(gray, amount=1.0, sigma=1.0):
    gray_f = gray.astype(np.float64)
    blurred = cv2.GaussianBlur(gray_f, (0, 0), sigma)
    return clip_uint8(gray_f + amount * (gray_f - blurred))

def highpass_log(gray, amount=1.0, sigma=1.0):
    gray_f = gray.astype(np.float64)
    blurred = cv2.GaussianBlur(gray_f, (0, 0), sigma)
    log = cv2.Laplacian(blurred, cv2.CV_64F)
    return clip_uint8(gray_f - amount * log)

def process_highpass(img, method, amount, sigma):
    if img is None: return None, "Загрузите изображение."
    
    rgb = ensure_rgb(img)
    gray_before = to_gray(rgb)

    if method == "Лапласиан":
        out_gray = highpass_laplacian(gray_before, amount)
    elif method == "Unsharp Masking":
        out_gray = unsharp_masking(gray_before, amount, max(0.1, sigma))
    else:
        out_gray = highpass_log(gray_before, amount, max(0.1, sigma))

    out_rgb = cv2.cvtColor(out_gray, cv2.COLOR_GRAY2RGB)
    return out_rgb, stats_text(gray_before, out_gray)