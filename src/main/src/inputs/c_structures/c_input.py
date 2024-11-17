import ctypes
from ctypes import wintypes
from src.inputs.c_structures.c_keyboard_input import KEYBDINPUT
from src.inputs.c_structures.c_mouse_input import MOUSEINPUT
from src.inputs.c_structures.c_hardware_input import HARDWAREINPUT

class INPUT(ctypes.Structure):
    class _INPUT(ctypes.Union):
        _fields_ = (("ki", KEYBDINPUT),
                    ("mi", MOUSEINPUT),
                    ("hi", HARDWAREINPUT))
    _anonymous_ = ("_input",)
    _fields_ = (("type",   wintypes.DWORD),
                ("_input", _INPUT))
LPINPUT = ctypes.POINTER(INPUT)