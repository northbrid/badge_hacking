from PIL import Image, ImageDraw, ImageFont

def make_menu(items=["HOME", "SETTINGS", "EXIT"]):

    # 1. Create a blank 320x240 image (RGBA for transparency support)
    width, height = 320, 240
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0)) # Transparent background
    draw = ImageDraw.Draw(img)

    # 3. Draw the Blue Menu Rectangle
    # Coordinates: (x0, y0, x1, y1)
    menu_color = (0, 0, 255, 255)  # Solid Blue (R, G, B, A)
    draw.rectangle([0, 0, width*0.30, height], fill=menu_color)

    # 4. Add Text (Optional)
    # If you have a .ttf font file, you can load it here. 
    # Otherwise, we'll use the default pixel font.
    try:
        # Attempt to use a system font
        font = ImageFont.truetype("DejaVuSans.ttf", 18)
    except:
        font = ImageFont.load_default()

    # List of menu items
    for i, item in enumerate(items):
        # Space items out by 30 pixels vertically
        draw.text((10, 20 + (i * 30)), item, fill="white", font=font)

    # 5. Save the result
    img.save("menu.png")
    print("Menu generated: menu.png")
    
