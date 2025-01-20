from src.inputs.c_structures.c_constants import KEYBOARD_KEYS, LEFT, MIDDLE, RIGHT

class DataBindCodes:
    def __init__(self):
        self.KEYBOARD_KEYS = set(KEYBOARD_KEYS.keys())
        self.MOUSE_KEYS = {LEFT, MIDDLE, RIGHT}

    def do_bind_exist(self, tecla: str) -> bool:
        """
        Verifica se a tecla está presente no banco de dados de binds.
        """
        tecla = tecla.lower()
        return tecla in self.KEYBOARD_KEYS or tecla in self.MOUSE_KEYS
    
    def bind_type_check(self, tecla: str) -> tuple:
        """
        Verifica qual o tipo de bind.

        Returns:
            tuple (bool, bool):
                [0] = A bind está na lista de KEYBOARD_KEYS
                [1] = A bind está na lista de MOUSE_KEYS
        """
        tecla = tecla.lower()
        return tecla in self.KEYBOARD_KEYS, tecla in self.MOUSE_KEYS