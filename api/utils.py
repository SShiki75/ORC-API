from PIL import Image

def resize_image(img, max_size=1200):
    img.thumbnail((max_size, max_size))
    return img

def save_log(entry, path="logs.txt"):
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except:
        lines = []

    lines.append(entry + "\n")
    lines = lines[-2:]  # 直近2件だけ

    with open(path, "w", encoding="utf-8") as f:
        f.writelines(lines)
