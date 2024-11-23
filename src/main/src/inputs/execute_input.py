from src.data.binds.data_bind_codes import DataBindCodes
from src.inputs.keyboard import Keyboard
from src.logger.logger import Logger
from src.inputs.mouse import Mouse
from src.inputs.input import Input
import threading
import time

class ExecuteInput:
    """
    Classe para execução e gerenciamento de inputs de teclado e mouse.

    A classe `ExecuteInput` gerencia a execução de inputs simulados e o rastreamento do mouse. 
    
    Ela lida com a simulação de inputs de teclado e mouse, liberando inputs anteriores e controlando a execução contínua de inputs.
    """
    
    def __init__(self) -> None:
        self.ultimo_gesto: str = None
        self.ultimo_input_code: str = None
        self.input_em_andamento: bool = False
        self.travar_novos_inputs: bool = False

        self.data_bind_codes = DataBindCodes()

        self.logger = Logger.configure_application_logger()
        self.input_logger = Logger.configure_input_logger()

    def _liberar_input_atual(self) -> None:
        """
        Libera o input atual em andamento, caso exista.

        Interrompe a simulação de qualquer input de teclado ou mouse que esteja ativo.
        """
        if self.ultimo_input_code and self.input_em_andamento:
            eh_input_teclado, eh_input_mouse = self.data_bind_codes.bind_type_check(self.ultimo_input_code)
            if eh_input_teclado:
                Keyboard.up(self.ultimo_input_code)
            if eh_input_mouse:
                Mouse.up(self.ultimo_input_code)
            self.input_em_andamento = False

    def _simular_input(self, bind: str, tempo_pressionado: int, modo_toggle_ativado: bool) -> None:
        """
        Simula a execução de um input de teclado ou mouse.

        Args:
            bind (str): O código do input a ser simulado.
            tempo_pressionado (int): O tempo que o input deve permanecer ativo.
            modo_toggle_ativado (bool): Indica se o modo toggle está ativado.
        """
        self._liberar_input_atual()
        self.input_em_andamento = True

        eh_input_teclado, eh_input_mouse = self.data_bind_codes.bind_type_check(bind)
        if eh_input_teclado:
            Keyboard.down(bind)
        if eh_input_mouse:
            Mouse.down(bind)

        self.ultimo_input_code = bind

        self.input_logger.info(f"Input simulado: '{bind}' | Tempo Pressionado: '{tempo_pressionado}' | Modo Toggle: '{modo_toggle_ativado}'")

        if modo_toggle_ativado:
            time.sleep(tempo_pressionado)
        
        time.sleep(0.1)
        self._liberar_input_atual()
        self.input_em_andamento = False
        self.travar_novos_inputs = False

    def executar_input(self, gesto: str, input: Input) -> None:
        """
        Executa um input baseado em um gesto e uma configuração de input.

        Args:
            gesto (str): O gesto que está sendo executado.
            input (Input): A configuração do input a ser simulado.
        """
        self.travar_novos_inputs = True
        
        modo_toggle_ativado = input.obter_modo_toggle()
        tempo_pressionado = input.obter_tempo()
        bind = input.obter_tecla()

        if not self.input_em_andamento:
            thread = threading.Thread(target=self._simular_input, args=(bind, tempo_pressionado, modo_toggle_ativado))
            thread.start() 
            self.ultimo_gesto = gesto

            self.input_logger.info(f"Inicio da execucao do input: {bind}")

    def executar_mouse_tracking(self, x_coords: float, y_coords: float) -> None:
        """
        Executa o rastreamento do mouse para as coordenadas fornecidas.

        Args:
            x_coords (float): Coordenada X para movimentar o mouse.
            y_coords (float): Coordenada Y para movimentar o mouse.
        """
        self.input_logger.info("Realizando mouse_tracking.")
        Mouse.move(x_coords, y_coords, 1)
