import time
import math

def step_by_step(x1, y1, x2, y2):
    start_time = time.perf_counter()
    points = []
    
    dx = x2 - x1
    dy = y2 - y1
    
    if abs(dx) > abs(dy):
        if x1 > x2:
            x1, x2 = x2, x1
            y1, y2 = y2, y1
            dx, dy = -dx, -dy
        k = dy / dx
        b = y1 - k * x1
        for x in range(x1, x2 + 1):
            y = round(k * x + b)
            points.append((x, y))
    else:
        if y1 > y2:
            x1, x2 = x2, x1
            y1, y2 = y2, y1
            dx, dy = -dx, -dy
        k = dx / dy
        b = x1 - k * y1
        for y in range(y1, y2 + 1):
            x = round(k * y + b)
            points.append((x, y))
            
    end_time = time.perf_counter()
    return points, (end_time - start_time) * 1000

def dda(x1, y1, x2, y2):
    start_time = time.perf_counter()
    points = []
    
    dx = x2 - x1
    dy = y2 - y1
    steps = max(abs(dx), abs(dy))
    
    if steps == 0:
        return [(x1, y1)], 0
        
    x_inc = dx / steps
    y_inc = dy / steps
    
    x, y = x1, y1
    for _ in range(steps + 1):
        points.append((round(x), round(y)))
        x += x_inc
        y += y_inc
        
    end_time = time.perf_counter()
    return points, (end_time - start_time) * 1000

def bresenham_line(x1, y1, x2, y2):
    start_time = time.perf_counter()
    points = []
    
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    error = dx - dy
    
    while True:
        points.append((x1, y1))
        if x1 == x2 and y1 == y2:
            break
        e2 = 2 * error
        if e2 > -dy:
            error -= dy
            x1 += sx
        if e2 < dx:
            error += dx
            y1 += sy
            
    end_time = time.perf_counter()
    return points, (end_time - start_time) * 1000

def bresenham_circle(xc, yc, r):
    start_time = time.perf_counter()
    points = []
    
    x = 0
    y = r
    d = 3 - 2 * r
    
    while y >= x:
        points.extend([
            (xc + x, yc + y), (xc - x, yc + y), (xc + x, yc - y), (xc - x, yc - y),
            (xc + y, yc + x), (xc - y, yc + x), (xc + y, yc - x), (xc - y, yc - x)
        ])
        x += 1
        if d > 0:
            y -= 1
            d = d + 4 * (x - y) + 10
        else:
            d = d + 4 * x + 6
            
    end_time = time.perf_counter()
    points = list(set(points)) 
    return points, (end_time - start_time) * 1000