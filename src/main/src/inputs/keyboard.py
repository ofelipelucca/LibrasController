from src.inputs.c_structures.c_constants import INPUT_KEYBOARD, KEYBOARD_KEYS, KEYEVENTF_KEYUP, KEYEVENTF_KEYDOWN
from src.inputs.c_structures.c_keyboard_input import KEYBDINPUT
from src.inputs.c_structures.c_input import INPUT
from src.inputs.device import Device
from src.logger.logger import Logger
import ctypes
from ctypes import wintypes

# Base para este código:
# https://stackoverflow.com/a/54638435 by C. Lang

# Constantes para eventos de teclado
user32 = ctypes.WinDLL('user32', use_last_error=True)
wintypes.ULONG_PTR = wintypes.WPARAM

class Keyboard(Device):
    """
    A classe Keyboard lida com eventos de teclado, permitindo simular pressionamentos e liberações de teclas.
    """
    
    @staticmethod
    def _send_input(input: INPUT) -> None:
        try:
            user32.SendInput(1, ctypes.byref(input), ctypes.sizeof(input))
        except Exception as e:
            error_message = f"Erro ao enviar o input de teclado: {e}"
            Logger.configure_error_logger().error(error_message)
            Logger.configure_input_logger().error(error_message)
            raise 
        
    @staticmethod
    def _create_input(key: str, event_type: str) -> INPUT:
        if key not in KEYBOARD_KEYS:
            error_message = f"Input nao eh valido. key: {key}, event_type: {event_type}."
            Logger.configure_error_logger().error(error_message)
            Logger.configure_input_logger().error(error_message)
            raise ValueError(error_message)
        key_code = KEYBOARD_KEYS[key]
        Logger.configure_input_logger().info(f"INPUT: Type = {INPUT_KEYBOARD} | wVk = {key_code} | dwFlags = {event_type}")
        input_event = INPUT(type=INPUT_KEYBOARD,
            ki=KEYBDINPUT(wVk=key_code, dwFlags=event_type))
        return input_event
    
    @staticmethod
    def up(key: str) -> None:
        Logger.configure_input_logger().info(f"Iniciando pressionamento da tecla '{key}'.")
        input_event = Keyboard._create_input(key, KEYEVENTF_KEYDOWN)
        Keyboard._send_input(input_event)
        
    @staticmethod
    def down(key: str) -> None:
        Logger.configure_input_logger().info(f"Iniciando liberacao da tecla '{key}'.")
        input_event = Keyboard._create_input(key, KEYEVENTF_KEYUP)
        Keyboard._send_input(input_event)