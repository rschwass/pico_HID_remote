import time
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode

# Initialize HID Keyboard
kbd = Keyboard(usb_hid.devices)

# Define Special Key Combos
SPECIAL_KEYS = {
    "CTRL_ALT_DEL": [Keycode.CONTROL, Keycode.ALT, Keycode.DELETE],
    "ALT_F4": [Keycode.ALT, Keycode.F4],
    "CTRL_C": [Keycode.CONTROL, Keycode.C],
}

def send_key(key_name):
    """Send a single keypress."""
    key = getattr(Keycode, key_name.upper(), None)
    if key:
        if key_name.isupper():
            kbd.press(Keycode.SHIFT)
            kbd.send(key)
            kbd.release(Keycode.SHIFT)
        else:
            kbd.send(key)
        return f"Sent key: {key_name}"
    return "Invalid key"

def send_string(text):
    """Send a full string as keyboard input."""
    for char in text:
        if char.isupper():
            kbd.press(Keycode.SHIFT)
            if char.upper() in Keycode.__dict__:
                kbd.send(getattr(Keycode, char.upper()))
            kbd.release(Keycode.SHIFT)
        else:
            if char.upper() in Keycode.__dict__:
                kbd.send(getattr(Keycode, char.upper()))
        time.sleep(0.1)
    return f"Sent string: {text}"

def send_special_combo(combo_name):
    """Send a special key combination."""
    combo = SPECIAL_KEYS.get(combo_name.upper())
    if combo:
        kbd.press(*combo)
        time.sleep(0.1)
        kbd.release_all()
        return f"Sent special combo: {combo_name}"
    return "Invalid special combo"
