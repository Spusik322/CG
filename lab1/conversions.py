from utils import clamp


def _hue_from_rgb(r, g, b, max_c, diff):
    if diff == 0:
        return 0.0

    if max_c == r:
        h = 60.0 * (((g - b) / diff) % 6)
    elif max_c == g:
        h = 60.0 * (((b - r) / diff) + 2)
    else:
        h = 60.0 * (((r - g) / diff) + 4)

    if h < 0:
        h += 360.0

    if h >= 360.0:
        h -= 360.0

    return h


def rgb_to_cmyk(r, g, b):
    r1 = clamp(r, 0, 255) / 255.0
    g1 = clamp(g, 0, 255) / 255.0
    b1 = clamp(b, 0, 255) / 255.0

    k = 1.0 - max(r1, g1, b1)

    if k >= 1.0:
        return 0.0, 0.0, 0.0, 100.0

    c = (1.0 - r1 - k) / (1.0 - k)
    m = (1.0 - g1 - k) / (1.0 - k)
    y = (1.0 - b1 - k) / (1.0 - k)

    c = clamp(c, 0.0, 1.0) * 100.0
    m = clamp(m, 0.0, 1.0) * 100.0
    y = clamp(y, 0.0, 1.0) * 100.0
    k = clamp(k, 0.0, 1.0) * 100.0

    return c, m, y, k


def cmyk_to_rgb(c, m, y, k):
    c = clamp(c, 0, 100) / 100.0
    m = clamp(m, 0, 100) / 100.0
    y = clamp(y, 0, 100) / 100.0
    k = clamp(k, 0, 100) / 100.0

    r = 255.0 * (1.0 - c) * (1.0 - k)
    g = 255.0 * (1.0 - m) * (1.0 - k)
    b = 255.0 * (1.0 - y) * (1.0 - k)

    r = int(round(clamp(r, 0, 255)))
    g = int(round(clamp(g, 0, 255)))
    b = int(round(clamp(b, 0, 255)))

    return r, g, b


def rgb_to_hsv(r, g, b):
    r1 = clamp(r, 0, 255) / 255.0
    g1 = clamp(g, 0, 255) / 255.0
    b1 = clamp(b, 0, 255) / 255.0

    max_c = max(r1, g1, b1)
    min_c = min(r1, g1, b1)
    diff = max_c - min_c

    v = max_c

    if diff == 0:
        h = 0.0
        s = 0.0
    else:
        s = diff / max_c
        h = _hue_from_rgb(r1, g1, b1, max_c, diff)

    return h, s * 100.0, v * 100.0


def hsv_to_rgb(h, s, v):
    h = clamp(h, 0, 360) % 360
    s = clamp(s, 0, 100) / 100.0
    v = clamp(v, 0, 100) / 100.0

    c = v * s
    x = c * (1.0 - abs((h / 60.0) % 2 - 1.0))
    m = v - c

    if 0 <= h < 60:
        r1, g1, b1 = c, x, 0
    elif 60 <= h < 120:
        r1, g1, b1 = x, c, 0
    elif 120 <= h < 180:
        r1, g1, b1 = 0, c, x
    elif 180 <= h < 240:
        r1, g1, b1 = 0, x, c
    elif 240 <= h < 300:
        r1, g1, b1 = x, 0, c
    else:
        r1, g1, b1 = c, 0, x

    r = int(round(clamp((r1 + m) * 255.0, 0, 255)))
    g = int(round(clamp((g1 + m) * 255.0, 0, 255)))
    b = int(round(clamp((b1 + m) * 255.0, 0, 255)))

    return r, g, b


def rgb_to_hls(r, g, b):
    r1 = clamp(r, 0, 255) / 255.0
    g1 = clamp(g, 0, 255) / 255.0
    b1 = clamp(b, 0, 255) / 255.0

    max_c = max(r1, g1, b1)
    min_c = min(r1, g1, b1)
    diff = max_c - min_c

    l = (max_c + min_c) / 2.0

    if diff == 0:
        h = 0.0
        s = 0.0
    else:
        denominator = 1.0 - abs(2.0 * l - 1.0)

        if denominator == 0:
            s = 0.0
        else:
            s = diff / denominator

        h = _hue_from_rgb(r1, g1, b1, max_c, diff)

    return h, l * 100.0, s * 100.0


def hls_to_rgb(h, l, s):
    h = clamp(h, 0, 360) % 360
    l = clamp(l, 0, 100) / 100.0
    s = clamp(s, 0, 100) / 100.0

    c = (1.0 - abs(2.0 * l - 1.0)) * s
    x = c * (1.0 - abs((h / 60.0) % 2 - 1.0))
    m = l - c / 2.0

    if 0 <= h < 60:
        r1, g1, b1 = c, x, 0
    elif 60 <= h < 120:
        r1, g1, b1 = x, c, 0
    elif 120 <= h < 180:
        r1, g1, b1 = 0, c, x
    elif 180 <= h < 240:
        r1, g1, b1 = 0, x, c
    elif 240 <= h < 300:
        r1, g1, b1 = x, 0, c
    else:
        r1, g1, b1 = c, 0, x

    r = int(round(clamp((r1 + m) * 255.0, 0, 255)))
    g = int(round(clamp((g1 + m) * 255.0, 0, 255)))
    b = int(round(clamp((b1 + m) * 255.0, 0, 255)))

    return r, g, b