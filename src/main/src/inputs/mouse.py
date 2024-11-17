
from src.inputs.c_structures.c_constants import INPUT_MOUSE, LEFT, MIDDLE, RIGHT, MOUSEEVENTF_LEFTUP, MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_MOVE, MOUSEEVENTF_RIGHTUP, MOUSEEVENTF_RIGHTDOWN
from src.inputs.c_structures.c_mouse_input import MOUSEINPUT, INPUT
from src.data.configs.config_router import ConfigRouter
from src.inputs.device import Device
from src.logger.logger import Logger
import numpy as np
import ctypes

RELATIVE_MOVE = MOUSEEVENTF_MOVE
ABSOLUTE_MOVE = 0

class Mouse(Device):
    """
    A classe Mouse lida com eventos de mouse, sendo possível enviar eventos (com SendInput) de Clicks, e MoveCursor. 
    """

    @staticmethod
    def _get_screen_dimensions() -> tuple:
        """
        Obtém as dimensões da tela do sistema.

        Returns:
            tuple: Largura e altura da tela.
        """
        screen_width = ctypes.windll.user32.GetSystemMetrics(0)
        screen_height = ctypes.windll.user32.GetSystemMetrics(1)
        return screen_width, screen_height

    @staticmethod
    def _get_cursor_pos() -> tuple:
        """
        Retorna a posição atual do cursor como uma tupla (x, y).

        Returns:
            tuple: Coordenadas (x, y) do cursor.
        """
        class POINT(ctypes.Structure):
            _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
        cursor_pos = POINT()
        ctypes.windll.user32.GetCursorPos(ctypes.byref(cursor_pos))
        return cursor_pos.x, cursor_pos.y

    @staticmethod
    def _send_input(inputs) -> None:
        """
        Envia os eventos de entrada para o sistema.

        Args:
            inputs (list): Lista de eventos INPUT a serem enviados.
        """
        try:
            ctypes.windll.user32.SendInput(len(inputs), ctypes.byref(inputs[0]), ctypes.sizeof(INPUT))
        except Exception as e:
            error_message = f"Ocorreu um erro ao enviar o input: {e}."
            Logger.configure_error_logger().error(error_message)
            Logger.configure_input_logger().error(error_message)
            raise ValueError(error_message)

    @staticmethod
    def _create_input(button: str, event_type: str) -> None:
        """
        Cria e configura o input para simular o clique do mouse.

        Args:
            button (str): Botão do mouse (LEFT, MIDDLE, RIGHT).
            event_type (str): Tipo de evento (DOWN ou UP).

        Raises:
            ValueError: Se 'button' não for 'left', 'middle' ou 'right', ou se 'event_type' não for 'UP' ou 'DOWN'.
        """
        if button == LEFT:
            flags = MOUSEEVENTF_LEFTDOWN if event_type == "DOWN" else MOUSEEVENTF_LEFTUP
        elif button == RIGHT:
            flags = MOUSEEVENTF_RIGHTDOWN if event_type == "DOWN" else MOUSEEVENTF_RIGHTUP
        else:
            error_message = f"'{button}' nao eh um botao do mouse valido. Deve ser 'm1' (botao esquerdo do mouse), 'm2' (botao direito do mouse) ou 'm3' (botao do meio do mouse)."
            Logger.configure_error_logger().error(error_message)
            Logger.configure_input_logger().error(error_message)
            raise ValueError(error_message)

        mi = MOUSEINPUT(0, 0, 0, flags, 0, 0)
        inputs = [INPUT(INPUT_MOUSE, mi)]
        Mouse._send_input(inputs)
        Logger.configure_input_logger().info(f"Simulacao de clique: '{button}' ({event_type}) realizado com sucesso.")

    @staticmethod
    def _move_mouse_absolute(x: int, y: int, min_diff: int = 3) -> None:
        """
        Move o cursor do mouse para as coordenadas absolutas especificadas.

        Args:
            x (int): Coordenada x.
            y (int): Coordenada y.
        """
        screen_width, screen_height = Mouse._get_screen_dimensions()
        webcam_width = int(ConfigRouter().ler_atributo("webcam_width"))
        webcam_height = int(ConfigRouter().ler_atributo("webcam_height"))

        x_atual, y_atual = Mouse._get_cursor_pos()
        x_proporcional = np.interp(webcam_width * x, (0, webcam_width), (0, screen_width))
        y_proporcional = np.interp(webcam_height * y, (0, webcam_height), (0, screen_height))

        x_novo = int(min(x_proporcional, screen_width))
        y_novo = int(min(y_proporcional, screen_height))

        if x_novo and y_novo:
            diff_x = abs(x_novo - x_atual) / screen_width * 100
            diff_y = abs(y_novo - y_atual) / screen_height * 100

            if diff_x > min_diff or diff_y > min_diff:
                ctypes.windll.user32.SetCursorPos(x_novo, y_novo)
                Logger.configure_input_logger().info(f"Cursor movido para ({x_novo}, {y_novo}) com sucesso.")

    @staticmethod
    def _move_mouse_relative(x: int, y: int, cursor_speed: int = 2) -> None:
        """
        Cria o input que move o cursor do mouse considerando a posição atual do mouse.

        Args:
            x (int): Coordenada adicionada à x.
            y (int): Coordenada adicionada à y.
        """        
        screen_width, screen_height = Mouse._get_screen_dimensions()
        webcam_width = int(ConfigRouter().ler_atributo("webcam_width"))
        webcam_height = int(ConfigRouter().ler_atributo("webcam_height"))

        x_atual, y_atual = Mouse._get_cursor_pos()
        x_ultima_pos_proporcional =  ConfigRouter().ler_atributo("x_ultima_pos_cursor") 
        y_ultima_pos_proporcional = ConfigRouter().ler_atributo("y_ultima_pos_cursor") 

        x_proporcional = np.interp(webcam_width * x, (0, webcam_width), (0, screen_width))
        y_proporcional = np.interp(webcam_height * y, (0, webcam_height), (0, screen_height))

        x_proporcional = int(x_ultima_pos_proporcional + (x_proporcional - x_ultima_pos_proporcional) / cursor_speed)
        y_proporcional = int(y_ultima_pos_proporcional + (y_proporcional - y_ultima_pos_proporcional) / cursor_speed)

        x_diff_proporcional = int(x_ultima_pos_proporcional - x_proporcional) * -1
        y_diff_proporcional = int(y_ultima_pos_proporcional - y_proporcional) * -1        

        if abs(x_diff_proporcional) > 15 or abs(y_diff_proporcional) > 15:
            x_diff_proporcional = 0
            y_diff_proporcional = 0

        ConfigRouter().atualizar_atributo("x_ultima_pos_cursor", x_proporcional)
        ConfigRouter().atualizar_atributo("y_ultima_pos_cursor", y_proporcional)

        x_novo = x_atual + x_diff_proporcional
        y_novo = y_atual + y_diff_proporcional

        if x_novo > screen_width or y_novo > screen_height:
            return
        
        mi = MOUSEINPUT(dx=x_diff_proporcional, dy=y_diff_proporcional, mouseData=0, dwFlags=MOUSEEVENTF_MOVE, time=0, dwExtraInfo=0)
        
        input_structure = INPUT(type=INPUT_MOUSE, mi=mi)
        
        Mouse._send_input([input_structure])
        Logger.configure_input_logger().info(f"Enviando input para mover o mouse para ({x_novo}, {y_novo}).")

    @staticmethod
    def up(button: str) -> None:
        """
        Simula o evento de soltar o botão do mouse.

        Args:
            button (str): Botão do mouse (LEFT, MIDDLE, RIGHT).
        """
        Logger.configure_input_logger().info(f"Iniciando clique UP no botao {button}.")
        Mouse._create_input(button, "UP")

    @staticmethod
    def down(button: str) -> None:
        """
        Simula o evento de pressionar o botão do mouse.

        Args:
            button (str): Botão do mouse (LEFT, MIDDLE, RIGHT).
        """
        Logger.configure_input_logger().info(f"Iniciando clique DOWN no botao {button}.")
        Mouse._create_input(button, "DOWN")


    @staticmethod
    def move(x: float, y: float, event_type: int) -> None:
        """
        Move o cursor do mouse de acordo com as coordenadas dadas, proporcionalmente ao tamanho da webcam.

        Args:
            x (float): Coordenada x normalizada (proporcional à largura da webcam).
            y (float): Coordenada y normalizada (proporcional à altura da webcam).
            event_type (int): Tipo de input de movimento de mouse. (ABSOLUTE_MOVE: 0, RELATIVE_MOVE: 1)
        """
        if event_type == ABSOLUTE_MOVE:
            Mouse._move_mouse_absolute(x, y)
        if event_type == RELATIVE_MOVE:
            Mouse._move_mouse_relative(x, y)
        Logger.configure_input_logger().info(f"Tentando mover o cursor para ({x}, {y}). | Tipo de input: {event_type}")
