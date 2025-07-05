def point_wkt(x, y):
    if x and y:
        return f"POINT({x} {y})"
    return None 