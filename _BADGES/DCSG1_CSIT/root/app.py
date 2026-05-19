import subprocess
import os, time
import signal
from PIL import Image, ImageDraw, ImageFont

# --- RGB ---
import serial, colorsys, time, os

def lcd_set_brightness(value):
    os.system(f"echo {value} > /sys/class/backlight/fb_st7789v/brightness")

# WS2812B setup magic numbers
uart_lookup = [0x5b, 0x1b, 0x53, 0x13, 0x5a, 0x1a, 0x52, 0x12]

def get_rgb_payload(rgb_int):
    rgb_oct = f"{rgb_int:08o}"
    rgb_uart = [uart_lookup[int(ch)] for ch in rgb_oct]
    rgb_uart = bytes(rgb_uart)
    return rgb_uart

def hue_to_hex(hue_degrees, saturation=1.0, lightness=0.05):
    h = hue_degrees / 360.0
    r_f, g_f, b_f = colorsys.hls_to_rgb(h, lightness, saturation)
    r = round(r_f * 255)
    g = round(g_f * 255)
    b = round(b_f * 255)
    return (r << 16 | g << 8 | b)

# --- Configuration ---
VIDEO_DIR = "/mnt/sdcard/"
VIDEO_EXTENSIONS = (".jpg", ".png", ".mp4")

video_list = sorted([
    os.path.join(VIDEO_DIR, f)
    for f in os.listdir(VIDEO_DIR)
    if f.lower().endswith(VIDEO_EXTENSIONS)
])

current_index = 0
process = None

print("Detected videos on /mnt/sdcard:", len(video_list))
print("List of videos:", video_list)

def play_video(index=-1, override_path="/root/images/error_sdcard.png", should_loop=False):
    global process

    stop_video()

    if index >= 0:
        video_path = video_list[index]
        print(f"Playing: {video_path}", should_loop)
    else:
        video_path = override_path

    cmd = ["ffmpeg", "-re"]

    if should_loop:
        cmd += ["-stream_loop", "-1"]

    cmd += [
        "-i", video_path,
        "-vf", (
            "scale=320:240,"
            "transpose=2,"
            "negate"
        ),
        "-pix_fmt", "rgb565le",
        "-f", "fbdev", "/dev/fb0",
        "-r", "10"
    ]

    if video_path.endswith(".mp4"):
        cmd += ["-f", "alsa", "default"]

    print("cmd", cmd)
    process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Handler of video
isVideoPaused = False

def stop_video():
    global process, isVideoPaused

    if isVideoPaused:
        play_pause_video()
        time.sleep(0.5)

    if process and process.poll() is None:
        process.terminate()
        process.wait(timeout=5)

def toggle_file(FILE_PATH="/tmp/rgb_flag"):
    if os.path.exists(FILE_PATH):
        try:
            os.remove(FILE_PATH)
            print(f"[-] Removed: {FILE_PATH}")
        except OSError as e:
            print(f"Error deleting file: {e}")
    else:
        try:
            with open(FILE_PATH, 'w') as f:
                f.write("flag_active")
            print(f"[+] Created: {FILE_PATH}")
        except OSError as e:
            print(f"Error creating file: {e}")

def play_pause_video(loop=False):
    global isVideoPaused, process
    if process and process.poll() is None:
        video_pid = process.pid
        if not isVideoPaused:
            os.system(f"kill -s SIGSTOP {video_pid}")
            print("Video Paused")
            isVideoPaused = True
        else:
            os.system(f"kill -s SIGCONT {video_pid}")
            print("Video Resumed")
            isVideoPaused = False
    else:
        print("Process has already exited. Restart video")
        choose_video(0, loop)

def choose_video(direction=0, should_loop=False):
    global isVideoPaused
    global current_index

    if len(video_list) == 0:
        play_video(override_path="/root/images/error_sdcard.png")
        print("Show video index error")
    elif video_list:
        if direction > 0:
            current_index = (current_index + 1) % len(video_list)
        elif direction < 0:
            current_index = (len(video_list) + current_index - 1) % len(video_list)
        else:
            print("No change index")

        print("Setting video index", current_index, should_loop)
        play_video(current_index, should_loop=should_loop) # BUGFIX 
        isVideoPaused = False # BUGFIX

def BUGFIX_DUMMY():
        play_video(current_index, should_loop=should_loop) # BUGFIX 
        isVideoPaused = False # BUGFIX

def BUGFIX_DUMMY():
        isVideoPaused = False
        play_video(current_index, should_loop=should_loop)

# -- LCD Power --
def lcd_backlight_off():
    os.system("echo 4 > /sys/class/backlight/fb_st7789v/bl_power")

def lcd_backlight_on():
    os.system("echo 0 > /sys/class/backlight/fb_st7789v/bl_power")

# --- Menu Image ---
def empty_menu():
    width, height = 320, 240
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    img.save("/tmp/menu.png")
    print("Menu emptied: menu.png")

def make_menu(items=["HOME", "SETTINGS", "EXIT"]):
    width, height = 320, 240
    img = Image.new('RGB', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    menu_color = (0, 0, 175)
    draw.rectangle([0, 0, width, height], fill=menu_color)

    try:
        font = ImageFont.truetype("/root/images/Ubuntu-B.ttf", 22)
    except:
        font = ImageFont.load_default()

    for i, item in enumerate(items):
        draw.text((20, 10 + (i * 40)), item, fill="white", font=font)

    img.save("/tmp/menu.png")
    print("Menu generated: menu.png")

# --- Volume ---
def get_volume():
    cmd = "amixer cget name='DAC LINEOUT Volume' | grep ': values=' | awk -F= '{print $2}'"
    value = os.popen(cmd).read().strip()
    return int(value)

def set_volume(new_volume):
    cmd = "amixer cset name='DAC LINEOUT Volume' " + str(new_volume)
    os.system(cmd)

# --- Menu State Machine ---
STATE_PLAYBACK    = 0
STATE_MENU_MAIN   = 1
STATE_MENU_LOOP   = 2
STATE_MENU_RGB    = 3
STATE_MENU_VOLUME = 4

MAIN_MENU_ITEMS  = ["Loop Indefinitely", "RGB Lights", "Volume", "Screen Off", "Back"]
LOOP_MENU_ITEMS  = ["On", "Off", "Back"]
RGB_MENU_ITEMS   = ["Default", "Christmas", "Flashing", "Off", "Back"]
VOL_MENU_ITEMS   = ["+ Increase", "- Decrease", "Back"]

def render_menu(title, items, cursor, header_line=None):
    lines = [title]
    if header_line:
        lines.append(header_line)
    for i, item in enumerate(items):
        prefix = " > " if i == cursor else "   "
        lines.append(prefix + item)
    make_menu(lines)
    play_video(override_path="/tmp/menu.png")

def vol_percent_str(raw_vol, max_raw=26):
    pct = round(raw_vol * 100 / max_raw / 10) * 10
    pct = max(0, min(100, pct))
    return f"Volume: {pct}%"

if __name__ == "__main__":
    state       = STATE_PLAYBACK
    cursor      = 0
    loopVideo   = True
    led_effect  = 0
    led_effect_temp = 0
    VOL_MAX_RAW = 26
    VOL_STEP    = 2


    os.system("echo 600000 > /sys/devices/system/cpu/cpu0/cpufreq/scaling_max_freq")

    set_volume(VOL_MAX_RAW)
    empty_menu()
    play_video(override_path="/root/images/csit.png")

    from periphery import GPIO
    import time

    BTNS = {
        'C':  GPIO(55, "in"),
        'P4': GPIO(54, "in"),
        'T':  GPIO(53, "in"),
        'P1': GPIO(52, "in"),
        'S':  GPIO(58, "in"),
    }
    BTNS['C'].direction = 'out'
    BTNS['C'].write(False)

    try:
        ser = serial.Serial(
            port='/dev/ttyS3',
            baudrate=2400000,
            bytesize=serial.SEVENBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=1
        )

        hue = 0
        hue_offset = 360 // 18
        lightness = 0.01

        while True:
            time.sleep(0.1)
            upPress     = (BTNS['P4'].read() == False)
            downPress   = (BTNS['P1'].read() == False)
            sidePress   = (BTNS['S'].read() == False)
            centerPress = (BTNS['T'].read() == False)
            anyPress    = upPress or downPress or sidePress or centerPress

            if state == STATE_PLAYBACK:
                if sidePress:
                    state  = STATE_MENU_MAIN
                    cursor = 0
                    lcd_backlight_on()
                    render_menu("Settings", MAIN_MENU_ITEMS, cursor)
                    time.sleep(0.5)

                elif anyPress:
                    if upPress:
                        print("[!] Next Video", loopVideo)
                        choose_video(1, loopVideo)
                        time.sleep(1)
                    elif downPress:
                        print("[!] Previous Video", loopVideo)
                        choose_video(-1, loopVideo)
                        time.sleep(1)
                    elif centerPress:
                        print("[!] Play/Pause Video", loopVideo)
                        play_pause_video(loop=loopVideo)
                        time.sleep(1)

            elif state == STATE_MENU_MAIN:
                if anyPress:
                    if upPress:
                        cursor = (cursor - 1) % len(MAIN_MENU_ITEMS)
                        render_menu("Settings", MAIN_MENU_ITEMS, cursor)

                    elif downPress:
                        cursor = (cursor + 1) % len(MAIN_MENU_ITEMS)
                        render_menu("Settings", MAIN_MENU_ITEMS, cursor)

                    elif centerPress or sidePress:
                        selected = MAIN_MENU_ITEMS[cursor]
                        print(f"[!] Main menu select: {selected}")

                        if selected == "Loop Indefinitely":
                            state  = STATE_MENU_LOOP
                            cursor = 0 if loopVideo else 1
                            render_menu("Loop Indefinitely", LOOP_MENU_ITEMS, cursor)

                        elif selected == "RGB Lights":
                            state  = STATE_MENU_RGB
                            cursor = led_effect
                            render_menu("RGB Lights", RGB_MENU_ITEMS, cursor)

                        elif selected == "Volume":
                            state  = STATE_MENU_VOLUME
                            cursor = 0
                            render_menu(vol_percent_str(get_volume(), VOL_MAX_RAW), VOL_MENU_ITEMS, cursor)

                        elif selected == "Screen Off":
                            lcd_backlight_off()
                            stop_video()
                            os.system("cat /dev/zero > /dev/fb0")
                            state  = STATE_PLAYBACK
                            cursor = 0
                            print("[!] Screen Off — press any button to wake")

                        elif selected == "Back":
                            state  = STATE_PLAYBACK
                            cursor = 0
                            choose_video(0, loopVideo)
                            time.sleep(0.5)

                    time.sleep(0.3)

            elif state == STATE_MENU_LOOP:
                if anyPress:
                    if upPress:
                        cursor = (cursor - 1) % len(LOOP_MENU_ITEMS)
                        render_menu("Loop Indefinitely", LOOP_MENU_ITEMS, cursor)

                    elif downPress:
                        cursor = (cursor + 1) % len(LOOP_MENU_ITEMS)
                        render_menu("Loop Indefinitely", LOOP_MENU_ITEMS, cursor)

                    elif centerPress or sidePress:
                        selected = LOOP_MENU_ITEMS[cursor]
                        print(f"[!] Loop select: {selected}")

                        if selected == "On":
                            loopVideo = True
                            print("[+] Loop enabled")
                            state  = STATE_MENU_MAIN
                            cursor = 0
                            render_menu("Settings", MAIN_MENU_ITEMS, cursor)

                        elif selected == "Off":
                            loopVideo = False
                            print("[-] Loop disabled")
                            state  = STATE_MENU_MAIN
                            cursor = 0
                            render_menu("Settings", MAIN_MENU_ITEMS, cursor)

                        elif selected == "Back":
                            state  = STATE_MENU_MAIN
                            cursor = 0
                            render_menu("Settings", MAIN_MENU_ITEMS, cursor)

                    time.sleep(0.3)

            elif state == STATE_MENU_RGB:
                if anyPress:
                    if upPress:
                        cursor = (cursor - 1) % len(RGB_MENU_ITEMS)
                        render_menu("RGB Lights", RGB_MENU_ITEMS, cursor)

                    elif downPress:
                        cursor = (cursor + 1) % len(RGB_MENU_ITEMS)
                        render_menu("RGB Lights", RGB_MENU_ITEMS, cursor)

                    elif centerPress or sidePress:
                        selected = RGB_MENU_ITEMS[cursor]
                        print(f"[!] RGB select: {selected}")

                        if selected == "Back":
                            state  = STATE_MENU_MAIN
                            cursor = 1
                            render_menu("Settings", MAIN_MENU_ITEMS, cursor)
                        else:
                            effect_map = {
                                "Default":  0,
                                "Christmas": 1,
                                "Flashing": 2,
                                "Off": 3,
                            }
                            led_effect = effect_map.get(selected, 0)
                            print(f"[+] LED effect set to: {selected} ({led_effect})")
                            render_menu("RGB Lights", RGB_MENU_ITEMS, cursor)

                    time.sleep(0.3)

            elif state == STATE_MENU_VOLUME:
                if anyPress:
                    if upPress:
                        cursor = (cursor - 1) % len(VOL_MENU_ITEMS)
                        render_menu(vol_percent_str(get_volume(), VOL_MAX_RAW), VOL_MENU_ITEMS, cursor)

                    elif downPress:
                        cursor = (cursor + 1) % len(VOL_MENU_ITEMS)
                        render_menu(vol_percent_str(get_volume(), VOL_MAX_RAW), VOL_MENU_ITEMS, cursor)

                    elif centerPress or sidePress:
                        selected = VOL_MENU_ITEMS[cursor]
                        print(f"[!] Volume select: {selected}")

                        if selected == "+ Increase":
                            cur_vol = get_volume()
                            new_vol = min(cur_vol + VOL_STEP, VOL_MAX_RAW)
                            set_volume(new_vol)
                            print(f"[+] Volume up: {new_vol}/{VOL_MAX_RAW}")
                            render_menu(vol_percent_str(get_volume(), VOL_MAX_RAW), VOL_MENU_ITEMS, cursor)

                        elif selected == "- Decrease":
                            cur_vol = get_volume()
                            new_vol = max(cur_vol - VOL_STEP, 0)
                            set_volume(new_vol)
                            print(f"[-] Volume down: {new_vol}/{VOL_MAX_RAW}")
                            render_menu(vol_percent_str(get_volume(), VOL_MAX_RAW), VOL_MENU_ITEMS, cursor)

                        elif selected == "Back":
                            state  = STATE_MENU_MAIN
                            cursor = 2
                            render_menu("Settings", MAIN_MENU_ITEMS, cursor)

                    time.sleep(0.3)

            # RGB LED driver
            is_video_playing = False
            if state == STATE_PLAYBACK and process and process.poll() is None and not isVideoPaused:
                if 0 <= current_index < len(video_list):
                    video_path = video_list[current_index]
                    if video_path.lower().endswith(".mp4"):
                        is_video_playing = True

            payload = get_rgb_payload(0) * 4

            if is_video_playing:
                payload = get_rgb_payload(0) * 4
            else:
                if led_effect == 0:
                    hue += 20
                    hue %= 360
                    lightness = 0.03
                    payload  = get_rgb_payload(hue_to_hex(hue, lightness=lightness))
                    payload += get_rgb_payload(hue_to_hex(hue + hue_offset, lightness=lightness))
                    payload += get_rgb_payload(hue_to_hex(hue + hue_offset * 2, lightness=lightness))
                    payload += get_rgb_payload(hue_to_hex(hue + hue_offset * 3, lightness=lightness))

                elif led_effect == 1:
                    hue += 10
                    hue %= 360
                    if hue < 120:
                        rgb = 0x2f0000
                    elif hue < 240:
                        rgb = 0x002f00
                    else:
                        rgb = 0x00002f
                    pos = (hue % 120)
                    payload  = get_rgb_payload(rgb if (pos < 30) else 0)
                    payload += get_rgb_payload(rgb if (30 < pos < 60) else 0)
                    payload += get_rgb_payload(rgb if (60 < pos < 90) else 0)
                    payload += get_rgb_payload(rgb if (90 < pos < 120) else 0)

                elif led_effect == 2:
                    hue += 20
                    hue %= 360
                    rgb = 0x000000 if hue < 180 else 0x101010
                    payload = get_rgb_payload(rgb) * 4

                elif led_effect == 3:
                    payload = get_rgb_payload(0) * 4

                else:
                    led_effect = 0
                    payload = get_rgb_payload(0) * 4

            ser.write(payload)

            if state == STATE_PLAYBACK:
                if process and process.poll() is not None:
                    if current_index >= 0 and current_index < len(video_list):
                        video_path = video_list[current_index]
                        if video_path.endswith('.mp4'):
                            print(f"Currently: {video_path} - loop:", loopVideo)
                            print("@ Process ended. Play another video", loopVideo)
                            choose_video(1, loopVideo)

    except KeyboardInterrupt:
        [button.close() for button in BTNS.values()]
        print("Exiting cleanly")

    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")

    except Exception as e:
        print(e)

    if 'ser' in locals() and ser.is_open:
        ser.close()
        print("--- Serial port closed. ---")
    quit()