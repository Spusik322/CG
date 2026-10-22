import numpy as np
import cv2
from utils import ensure_rgb, to_gray, clip_uint8, stats_text

def linear_stretch_channel(ch, low_pct=1.0, high_pct=99.0):
    ch = np.asarray(ch, dtype=np.float64)
    fmin = np.percentile(ch, low_pct)
    fmax = np.percentile(ch, high_pct)
    if fmax - fmin < 1e-6: return clip_uint8(ch)
    out = (ch - fmin) * 255.0 / (fmax - fmin)
    return clip_uint8(out)

def equalize_channel(ch):
    ch = np.asarray(ch, dtype=np.uint8)
    hist = cv2.calcHist([ch], [0], None, [256], [0, 256]).ravel()
    cdf = hist.cumsum()
    cdf_nonzero = cdf[cdf > 0]
    if cdf_nonzero.size == 0: return ch.copy()
    cdf_min = cdf_nonzero[0]
    total = ch.size
    if total == cdf_min: return ch.copy()
    lut = ((cdf - cdf_min) * 255.0) / (total - cdf_min)
    lut = np.clip(lut, 0, 255).astype(np.uint8)
    return lut[ch]

def process_contrast(img, method, low_pct, high_pct):
    if img is None: return None, "Загрузите изображение."
    
    rgb = ensure_rgb(img)
    gray_before = to_gray(rgb)
    out_rgb = rgb.copy()

    if method == "Линейное (серый)":
        out_gray = linear_stretch_channel(gray_before, low_pct, high_pct)
        out_rgb = cv2.cvtColor(out_gray, cv2.COLOR_GRAY2RGB)
    elif method == "Эквализация (серый)":
        out_gray = equalize_channel(gray_before)
        out_rgb = cv2.cvtColor(out_gray, cv2.COLOR_GRAY2RGB)
    elif method == "Линейное RGB (цвет)":
        for c in range(3): out_rgb[:, :, c] = linear_stretch_channel(out_rgb[:, :, c], low_pct, high_pct)
    elif method == "Линейное HSV (цвет)":
        hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
        hsv[:, :, 2] = linear_stretch_channel(hsv[:, :, 2], low_pct, high_pct)
        out_rgb = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
    elif method == "Эквализация RGB (цвет)":
        for c in range(3): out_rgb[:, :, c] = equalize_channel(out_rgb[:, :, c])
    elif method == "Эквализация HSV (цвет)":
        hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
        hsv[:, :, 2] = equalize_channel(hsv[:, :, 2])
        out_rgb = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)

    gray_after = to_gray(out_rgb)
    return out_rgb, stats_text(gray_before, gray_after)