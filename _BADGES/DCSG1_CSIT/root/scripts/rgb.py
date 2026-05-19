import serial, colorsys, time, os

# WS2812B setup magic numbers
uart_lookup = [0x5b, 0x1b, 0x53, 0x13, 0x5a, 0x1a, 0x52, 0x12]
def get_rgb_payload(rgb_int):
    rgb_oct = f"{rgb_int:08o}"
    rgb_uart = [uart_lookup[int(ch)] for ch in rgb_oct]
    rgb_uart = bytes(rgb_uart)
    return rgb_uart

def hue_to_hex(hue_degrees, saturation=1.0, lightness=0.05):
    # 1. Normalize hue to the 0.0 to 1.0 range expected by colorsys
    h = hue_degrees / 360.0
    
    # 2. Convert HLS to RGB (floats between 0.0 and 1.0)
    # The 'colorsys' module uses HLS (Luminance), which is slightly different 
    # from HSL (Lightness), but suitable for this purpose.
    r_f, g_f, b_f = colorsys.hls_to_rgb(h, lightness, saturation)
    
    # 3. Convert RGB floats to 8-bit integers (0-255)
    r = round(r_f * 255)
    g = round(g_f * 255)
    b = round(b_f * 255)
    
    # 4. Format the RGB integers into a 24-bit hex string
    return (r << 16 | g << 8 | b)

try:
    ser = serial.Serial(
        port='/dev/ttyS3',
        baudrate=2400000,
        bytesize=serial.SEVENBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=1
    )

    if ser.is_open:
        print(f"--- Connection established on {ser.portstr} ---")
        #print("--- Press Ctrl+C to stop sending ---")

        # Writing data
        # Note: When using 7-bit, ensure your characters fit within the 0-127 range
        hue = 0
        hue_offset = 360//18
        # payload = get_rgb_payload(0xffffff) # GRB
        # payload += get_rgb_payload(0x00ff00)
        # payload += get_rgb_payload(0xff0000)
        # payload += get_rgb_payload(0x0000ff)

        lightness = 0.05
        while True:
            hue += 30
            hue %= 360
            payload = get_rgb_payload(hue_to_hex(hue, lightness=lightness))
            payload += get_rgb_payload(hue_to_hex(hue+hue_offset, lightness=lightness))
            payload += get_rgb_payload(hue_to_hex(hue+hue_offset*2, lightness=lightness))
            payload += get_rgb_payload(hue_to_hex(hue+hue_offset*3, lightness=lightness))
            ser.write(payload)
            time.sleep(0.2)
            
            # Update less frequently
            if hue == 0 or hue == 180:
                if os.path.exists("/tmp/rgb_flag"):
                    lightness = 0.00
                else:
                    lightness = 0.03 # DO NOT INCREASE AS NOT ENOUGH CURRENT

except serial.SerialException as e:
    print(f"Error opening serial port: {e}")

except KeyboardInterrupt:
    print("\n[Exiting] Stop command received.")

finally:
    # Close the connection gracefully
    if 'ser' in locals() and ser.is_open:
        ser.close()
        print("--- Serial port closed. ---")
    quit()
    
