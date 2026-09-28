import os
import numpy as np
from PIL import Image, ImageDraw

DATASET_DIR = os.path.join(os.path.dirname(__file__), 'dataset')
GENUINE_DIR = os.path.join(DATASET_DIR, 'genuine')
FORGED_DIR = os.path.join(DATASET_DIR, 'forged')

def draw_signature(person_id: int, is_forged: bool = False, variation: int = 0) -> Image.Image:
    """Generates synthetic handwritten signature image with realistic variation and tremor for forged ones."""
    width, height = 400, 200
    img = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Base control points per person
    np.random.seed(person_id * 100 + (99 if is_forged else 0))
    
    start_x = 50 + (np.random.randint(-15, 15) if is_forged else np.random.randint(-5, 5))
    start_y = 100 + (np.random.randint(-20, 20) if is_forged else np.random.randint(-5, 5))
    
    points = [
        (start_x, start_y),
        (start_x + 60, start_y - 40 + (30 if is_forged else 0)),
        (start_x + 120, start_y + 30 - (20 if is_forged else 0)),
        (start_x + 180, start_y - 50 + (40 if is_forged else 0)),
        (start_x + 240, start_y + 20),
        (start_x + 290, start_y - 10)
    ]
    
    # Add cursive loops & strokes
    num_points = 150
    t = np.linspace(0, 1, num_points)
    
    # Generate smooth curve
    x_coords = np.zeros(num_points)
    y_coords = np.zeros(num_points)
    
    for i, pt in enumerate(points[:-1]):
        next_pt = points[i+1]
        idx_start = int(i * (num_points / (len(points) - 1)))
        idx_end = int((i + 1) * (num_points / (len(points) - 1)))
        sub_t = np.linspace(0, 1, idx_end - idx_start)
        
        x_coords[idx_start:idx_end] = pt[0] + (next_pt[0] - pt[0]) * sub_t
        y_coords[idx_start:idx_end] = pt[1] + (next_pt[1] - pt[1]) * sub_t + np.sin(sub_t * np.pi * 3) * (15 if not is_forged else 35)

    if is_forged:
        # Add tremor noise and hesitation artifacts
        tremor_x = np.random.normal(0, 3.5, num_points)
        tremor_y = np.random.normal(0, 3.5, num_points)
        x_coords += tremor_x
        y_coords += tremor_y
    else:
        # Subtle organic variation for genuine signatures
        var_x = np.random.normal(0, 0.8, num_points) + (variation * 0.5)
        var_y = np.random.normal(0, 0.8, num_points) + (variation * 0.5)
        x_coords += var_x
        y_coords += var_y

    # Draw continuous stroke
    stroke_width = 3 if not is_forged else np.random.choice([2, 4, 5])
    for i in range(len(x_coords) - 1):
        p1 = (x_coords[i], y_coords[i])
        p2 = (x_coords[i+1], y_coords[i+1])
        draw.line([p1, p2], fill=(0, 0, 0), width=stroke_width)
        
    return img

def generate_dataset():
    os.makedirs(GENUINE_DIR, exist_ok=True)
    os.makedirs(FORGED_DIR, exist_ok=True)
    
    print("[+] Generating sample dataset...")
    count_g, count_f = 0, 0
    
    # 5 Person profiles, 5 genuine and 5 forged per person
    for person in range(1, 6):
        for var in range(1, 6):
            g_img = draw_signature(person_id=person, is_forged=False, variation=var)
            g_path = os.path.join(GENUINE_DIR, f"person_{person:02d}_genuine_{var:02d}.png")
            g_img.save(g_path)
            count_g += 1
            
            f_img = draw_signature(person_id=person, is_forged=True, variation=var)
            f_path = os.path.join(FORGED_DIR, f"person_{person:02d}_forged_{var:02d}.png")
            f_img.save(f_path)
            count_f += 1
            
    print(f"[+] Successfully generated {count_g} Genuine and {count_f} Forged sample signatures!")

if __name__ == '__main__':
    generate_dataset()
