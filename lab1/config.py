MODEL_DEFS = {
    "RGB": [
        ("R", 0, 255),
        ("G", 0, 255),
        ("B", 0, 255),
    ],

    "CMYK": [
        ("C", 0, 100),
        ("M", 0, 100),
        ("Y", 0, 100),
        ("K", 0, 100),
    ],

    "HSV": [
        ("H", 0, 360),
        ("S", 0, 100),
        ("V", 0, 100),
    ],

    "HLS": [
        ("H", 0, 360),
        ("L", 0, 100),
        ("S", 0, 100),
    ],
}


def create_empty_state():
    return {
        model: {
            comp: 0.0
            for comp, _, _ in components
        }
        for model, components in MODEL_DEFS.items()
    }