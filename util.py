def try_parse_float(s):
    try:
        return float(s)
    except ValueError:
        return None
