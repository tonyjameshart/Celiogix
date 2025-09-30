import os

from PIL import Image


def convert_png_to_ico(png_path, ico_path=None, sizes=None):
    if sizes is None:
        sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    if not os.path.isfile(png_path):
        raise FileNotFoundError(f"❌ PNG not found: {png_path}")

    if ico_path is None:
        ico_path = os.path.splitext(png_path)[0] + ".ico"

    img = Image.open(png_path).convert("RGBA")
    img.save(ico_path, format="ICO", sizes=sizes)
    print(f"✅ ICO saved to: {ico_path}")
