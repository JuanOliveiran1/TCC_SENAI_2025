# utils.py
def safe_float(x, default=0.0):
    try:
        return float(x)
    except Exception:
        return default

def rele_to_bool(s):
    if isinstance(s, bool):
        return s
    if isinstance(s, str):
        return s.strip().upper() in ("ON", "1", "TRUE", "HIGH")
    return bool(s)
