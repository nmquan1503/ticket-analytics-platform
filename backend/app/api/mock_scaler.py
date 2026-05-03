import hashlib
from functools import wraps

def mock_scale(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        filter_obj = kwargs.get('filter')
        if not filter_obj:
            return res
        
        filter_str = f"{filter_obj.date_range}_{filter_obj.locations}_{filter_obj.branches}_{filter_obj.priorities}"
        h = int(hashlib.md5(filter_str.encode()).hexdigest(), 16)
        m = 0.2 + (h % 800) / 1000.0  # multiplier between 0.2 and 1.0
        
        def scale(d, key=""):
            if isinstance(d, dict):
                return {k: scale(v, k) for k, v in d.items()}
            elif isinstance(d, list):
                return [scale(x, key) for x in d]
            elif isinstance(d, int):
                if d <= 10 or "id" in key.lower() or "rnk" in key.lower() or "pct" in key.lower(): return d
                return int(d * m)
            elif isinstance(d, float):
                if "pct" in key.lower() or "rate" in key.lower(): return d
                return round(d * m, 2)
            return d
            
        return scale(res)
    return wrapper
