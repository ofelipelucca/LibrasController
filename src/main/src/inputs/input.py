from src.data.binds.data_bind_codes import DataBindCodes
from src.logger.logger import Logger

class Input:
    """
    Classe que representa uma configuração de entrada de teclado.

    A classe gerencia a tecla, o tempo pressionado e o modo contínuo de um input.
    """

    def __init__(self, tecla: str, tempo_pressionado: int, modo_toggle: bool = False) -> None:
        """
        Inicializa uma instância da classe Input.

        Args:
            tecla (str): A tecla associada ao input.
            tempo_pressionado (int): O tempo em segundos que a tecla deve permanecer pressionada.
            modo_toggle (bool): Indica se o modo contínuo está ativado.
        """
        # Configuração do logger
        self.logger = Logger.configure_input_logger()
        self.error_logger = Logger.configure_error_logger()

        try:
            self.set_tecla(tecla)
            self.set_tempo(tempo_pressionado)
            self.set_modo_toggle(modo_toggle)
            self.tipo_de_input = None
            self.logger.info(f"Criando Input: Bind '{tecla}' | Tempo Pressionado '{tempo_pressionado}' | Modo Toggle '{modo_toggle}'.")
        except ValueError as e:
            self.logger.error(f"Erro ao criar Input: {e}")
            self.error_logger.error(f"Erro ao criar Input: {e}")

    def obter_tecla(self) -> str:
        """
        Obtém a tecla associada ao input.

        Returns:
            str: A tecla associada ao input.
        """
        return self.tecla
    
    def obter_tempo(self) -> int:
        """
        Obtém o tempo pressionado associado ao input.

        Returns:
            int: O tempo pressionado em segundos.
        """
        return self.tempo_pressionado

    def obter_modo_toggle(self) -> bool:
        """
        Obtém o modo toggle associado ao input.

        Returns:
            bool: True se o modo toggle estiver ativado, False caso contrário.
        """
        return self.modo_toggle

    def set_tecla(self, tecla: str) -> None:
        """
        Define a tecla associada ao input.

        Args:
            tecla (str): A tecla a ser associada.

        Raises:
            ValueError: Se a tecla não existir no mapa de teclas.
        """
        map_keys = DataBindCodes()
        tecla = tecla.lower()
        if not map_keys.do_bind_exist(tecla):
            error_msg = f"A tecla '{tecla}' nao existe no mapa de teclas."
            self.logger.error(error_msg)
            self.error_logger.error(error_msg)
            raise ValueError(error_msg)
        self.tecla = tecla

    def set_tempo(self, tempo_pressionado: int) -> None:
        """
        Define o tempo pressionado associado ao input.

        Args:
            tempo_pressionado (int): O tempo em segundos que a tecla deve permanecer pressionada.

        Raises:
            ValueError: Se o tempo não estiver entre 0 e 60 segundos.
        """
        if tempo_pressionado < 0 or tempo_pressionado > 60:
            error_msg = f"O tempo {tempo_pressionado} deve ser maior do que 0 e menor que 60."
            self.logger.error(error_msg)
            self.error_logger.error(error_msg)
            raise ValueError(error_msg)
        self.tempo_pressionado = tempo_pressionado

    def set_modo_toggle(self, modo_toggle: bool) -> None:
        """
        Define o modo toggle associado ao input.

        Args:
            modo_toggle (bool): Indica se o modo toggle está ativado.
        """
        self.modo_toggle = modo_toggle
