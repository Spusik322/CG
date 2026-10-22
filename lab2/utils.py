import numpy as np
import cv2

def normalize_img_dtype(img):
    img = np.asarray(img)
    if img.dtype == np.uint8:
        return img
    if np.issubdtype(img.dtype, np.floating):
        if img.size > 0 and img.max() <= 1.0:
            img = img * 255.0
        img = np.clip(img, 0, 255).astype(np.uint8)
    else:
        img = np.clip(img, 0, 255).astype(np.uint8)
    return img

def ensure_rgb(img):
    if img is None: return None
    img = normalize_img_dtype(img)
    if img.ndim == 2: return cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    if img.shape[2] == 1: return cv2.cvtColor(img[:, :, 0], cv2.COLOR_GRAY2RGB)
    if img.shape[2] == 4: return cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
    return img

def to_gray(rgb):
    return cv2.cvtColor(ensure_rgb(rgb), cv2.COLOR_RGB2GRAY)

def clip_uint8(img):
    return np.clip(img, 0, 255).astype(np.uint8)

def cv2_imread_unicode(path):
    try:
        stream = open(path, "rb")
        bytes_arr = bytearray(stream.read())
        numpy_arr = np.asarray(bytes_arr, dtype=np.uint8)
        img = cv2.imdecode(numpy_arr, cv2.IMREAD_COLOR)
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    except Exception:
        return None

def image_stats(gray):
    gray = np.asarray(gray, dtype=np.uint8)
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256]).ravel()
    p = hist / max(hist.sum(), 1)
    p = p[p > 0]
    entropy = float(-np.sum(p * np.log2(p)))

    gray_f = gray.astype(np.float64)
    gx = cv2.Sobel(gray_f, cv2.CV_64F, 1, 0, ksize=3)
    gy = cv2.Sobel(gray_f, cv2.CV_64F, 0, 1, ksize=3)
    sharpness = float(np.mean(gx ** 2 + gy ** 2))

    return {
        "min": int(gray.min()), "max": int(gray.max()),
        "mean": float(gray.mean()), "std": float(gray.std()),
        "contrast": int(gray.max() - gray.min()),
        "entropy": entropy, "sharpness": sharpness,
    }

def stats_text(gray_before, gray_after):
    s1, s2 = image_stats(gray_before), image_stats(gray_after)
    return (
        f"ДО\n"
        f"min={s1['min']}, max={s1['max']}, mean={s1['mean']:.2f}, std={s1['std']:.2f}\n"
        f"contrast={s1['contrast']}, entropy={s1['entropy']:.3f}, sharpness={s1['sharpness']:.2f}\n\n"
        f"ПОСЛЕ\n"
        f"min={s2['min']}, max={s2['max']}, mean={s2['mean']:.2f}, std={s2['std']:.2f}\n"
        f"contrast={s2['contrast']}, entropy={s2['entropy']:.3f}, sharpness={s2['sharpness']:.2f}"
    )