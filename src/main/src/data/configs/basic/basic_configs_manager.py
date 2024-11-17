from src.logger.logger import Logger  
import json
import os

class BasicConfigManager:
    """
    Classe para gerenciar as configurações básicas, como a câmera selecionada.
    Salva e recupera dados de um arquivo JSON.
    """
    
    config_file = "src/main/src/data/configs/basic/config_basica.json"
    default_config = {
        "camera_selecionada": "",
        "webcam_width": 640,
        "webcam_height": 480
    }

    config_logger = Logger.configure_json_data_logger()
    error_logger = Logger.configure_error_logger()
    
    @staticmethod
    def _verificando_arquivo() -> None:
        """ 
        Verifica se o arquivo de configuração existe; se não, cria com as configurações padrão.
        """
        if not os.path.exists(BasicConfigManager.config_file):
            with open(BasicConfigManager.config_file, "w") as file:
                json.dump(BasicConfigManager.default_config, file, indent=4)
            BasicConfigManager.config_logger.info("Arquivo de configuracao criado com as configuracoes padrao.")

    @staticmethod
    def get_atributos() -> list:
        """
        Retorna as chaves dos atributos padrão definidos em default_config.

        Returns:
            list: Lista contendo as chaves dos atributos padrão.
        """
        return list(BasicConfigManager.default_config.keys())
    
    @staticmethod
    def ler_atributo(atributo: str) -> str:
        """ 
        Lê o valor de um atributo salvo dentro do arquivo de configuração.
        
        Args:
            atributo (str): O nome do atributo a ser lido.

        Returns:
            str: O valor do atributo, ou uma string vazia se não encontrado.
        """
        BasicConfigManager._verificando_arquivo()
        try:
            with open(BasicConfigManager.config_file, "r") as file:
                config = json.load(file)
                valor = config.get(atributo, "")
                BasicConfigManager.config_logger.info(f"Atributo '{atributo}' lido com valor: '{valor}'")
                return valor
        except Exception as e:
            error_message = f"Ocorreu um erro ao ler o arquivo JSON: {e}"
            BasicConfigManager.error_logger.error(error_message)
            BasicConfigManager.config_logger.error(error_message)
            return ""

    @staticmethod
    def atualizar_atributo(atributo: str, novo_valor: str) -> None:
        """
        Atualiza o valor de um atributo no arquivo de configuração.
        
        Args:
            atributo (str): O nome do atributo a ser atualizado.
            novo_valor (str): O novo valor para o atributo.
        """
        BasicConfigManager._verificando_arquivo()
        try:
            with open(BasicConfigManager.config_file, "r") as file:
                config = json.load(file)
            
            if config.get(atributo) == novo_valor:
                BasicConfigManager.config_logger.info(f"Atributo '{atributo}' ja esta atualizado com valor: '{novo_valor}'")
                return
            
            config[atributo] = novo_valor

            with open(BasicConfigManager.config_file, "w") as file:
                json.dump(config, file, indent=4)
            
            BasicConfigManager.config_logger.info(f"Atributo '{atributo}' atualizado para: '{novo_valor}'")
        
        except FileNotFoundError as fnf_error:
            error_message = f"Nao foi possível encontrar o arquivo JSON: {fnf_error}"
            BasicConfigManager.error_logger.error(error_message)
            BasicConfigManager.config_logger.error(error_message)
        except Exception as e:
            error_message = f"Erro ao atualizar o atributo '{atributo}': {e}"
            BasicConfigManager.error_logger.error(error_message)
            BasicConfigManager.config_logger.error(error_message)