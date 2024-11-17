from src.data.configs.states.config_states_manager import ConfigStateManager
from src.data.configs.basic.basic_configs_manager import BasicConfigManager
from src.logger.logger import Logger  

class ConfigRouter:
    """
    Classe para rotear a leitura e atualização de atributos entre os gerenciadores de configuração.
    """
    state_manager = ConfigStateManager()
    config_logger = Logger.configure_json_data_logger()
    error_logger = Logger.configure_error_logger()

    @staticmethod
    def ler_atributo(atributo: str) -> str:
        """ 
        Decide qual classe filha deve lidar com a leitura do atributo e realiza a leitura.

        Args:
            atributo (str): O nome do atributo a ser lido.

        Returns:
            str: O valor do atributo, ou uma string vazia se não encontrado.

        Raises:
            ValueError: Se o atributo passado não é reconhecido.
            Exception: Qualquer erro inesperado ao tentar ler o atributo será logado.
        """
        ConfigRouter.config_logger.info(f"Tentando ler o atributo: {atributo}")
        try:
            if atributo in BasicConfigManager.get_atributos():
                valor = BasicConfigManager.ler_atributo(atributo)
            elif atributo in ConfigRouter.state_manager.get_atributos():
                valor = ConfigRouter.state_manager.ler_atributo(atributo)
            else:
                raise ValueError(f"Atributo desconhecido: {atributo}")
            
            ConfigRouter.config_logger.info(f"Atributo '{atributo}' lido com valor: '{valor}'")
            return valor
        except ValueError as ve:
            error_message = f"Erro: {ve}"
            ConfigRouter.error_logger.error(error_message)
            ConfigRouter.config_logger.error(error_message)
            raise
        except Exception as e:
            error_message = f"Erro ao ler o atributo '{atributo}': {e}"
            ConfigRouter.error_logger.error(error_message)
            ConfigRouter.config_logger.error(error_message)
            return ""

    @staticmethod
    def atualizar_atributo(atributo: str, novo_valor: str) -> None:
        """
        Decide qual classe filha deve lidar com a atualização do atributo e realiza a atualização.

        Args:
            atributo (str): O nome do atributo a ser atualizado.
            novo_valor (str): O novo valor para o atributo.

        Raises:
            ValueError: Se o atributo passado não é reconhecido.
            Exception: Qualquer erro inesperado ao tentar atualizar o atributo será logado.
        """
        ConfigRouter.config_logger.info(f"Tentando atualizar o atributo: {atributo}, novo valor = {novo_valor}")
        try:
            if atributo in BasicConfigManager.get_atributos():
                BasicConfigManager.atualizar_atributo(atributo, novo_valor)
            elif atributo in ConfigRouter.state_manager.get_atributos():
                ConfigRouter.state_manager.atualizar_atributo(atributo, novo_valor)
            else:
                raise ValueError(f"Atributo desconhecido: {atributo}")

            ConfigRouter.config_logger.info(f"Atributo '{atributo}' atualizado para: '{novo_valor}'")
        
        except ValueError as ve:
            error_message = f"Erro: {ve}"
            ConfigRouter.error_logger.error(error_message)
            ConfigRouter.config_logger.error(error_message)
            raise
        except Exception as e:
            error_message = f"Erro ao atualizar o atributo '{atributo}': {e}"
            ConfigRouter.error_logger.error(error_message)
            ConfigRouter.config_logger.error(error_message)
            raise