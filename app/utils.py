def get_prev_month(month_key: str) -> str:
    y, m = map(int, month_key.split('-'))
    if m == 1: return f"{y-1}-12"
    return f"{y}-{m-1:02d}"

def get_next_month(month_key: str) -> str:
    y, m = map(int, month_key.split('-'))
    if m == 12: return f"{y+1}-01"
    return f"{y}-{m+1:02d}"