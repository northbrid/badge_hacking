#!/usr/bin/env python3
import argparse
import struct
from PIL import Image, ImageOps

def get_fb_info():
    """Detects screen resolution and bits-per-pixel from the system."""
    try:
        with open("/sys/class/graphics/fb0/virtual_size", "r") as f:
            res = f.read().strip().split(',')
            width, height = int(res[0]), int(res[1])
        with open("/sys/class/graphics/fb0/bits_per_pixel", "r") as f:
            bpp = int(f.read().strip())
        return width, height, bpp
    except Exception as e:
        # Default for many Luckfox Pico LCDs if sysfs read fails
        return 240, 240, 16

def display_png(image_path):
    #fb_w, fb_h, bpp = get_fb_info()
    fb_w, fb_h, bpp = 240, 320, 16
    print(f"Displaying on {fb_w}x{fb_h} ({bpp}bpp)...")

    try:
        img = Image.open(image_path).convert("RGB")
        
        # Resize to fill screen exactly 
        # Invert for this screen
        img = img.resize((fb_h, fb_w))
        img = img.transpose(Image.Transpose.ROTATE_90)
        img = ImageOps.invert(img)
        pixels = img.getdata()
        buffer = bytearray()

        if bpp == 16:
            # RGB565 conversion
            for r, g, b in pixels:
                # Pack: Red (5 bits), Green (6 bits), Blue (5 bits)
                rgb565 = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
                buffer += struct.pack("<H", rgb565) 
        elif bpp == 32:
            # ARGB/BGRA conversion (Typical for 32-bit FBs)
            for r, g, b in pixels:
                # Standard Linux FB often expects Blue, Green, Red, Alpha
                buffer += struct.pack("BBBB", b, g, r, 255)
        else:
            print(f"Unsupported bit depth: {bpp}")
            return

        with open("/dev/fb0", "wb") as fb:
            fb.write(buffer)
        print("Done.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Push a PNG to Luckfox /dev/fb0")
    parser.add_argument("image", help="Path to the PNG image file")
    args = parser.parse_args()

    display_png(args.image)

