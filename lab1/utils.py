def clamp(value, low, high):
    return max(low, min(high, value))


def format_number(value):
    value = float(value)

    if abs(value - round(value)) < 1e-6:
        return str(int(round(value)))

    text = f"{value:.2f}".rstrip("0").rstrip(".")
    return text if text else "0"