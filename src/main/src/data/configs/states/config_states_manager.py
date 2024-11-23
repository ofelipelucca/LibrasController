from src.logger.logger import Logger  
import tempfile
import json
import os

class ConfigStateManager:
    """
    Classe para gerenciar o estado de configurações relacionadas a gestos.
    Salva e recupera dados de um arquivo JSON.
    """
    def __init__(self, file_path="src/main/src/data/configs/states/estado_atual.json") -> None:    
        self.config_file = file_path
        self.state = {
            "nome_gesto_direita": "MAO",
            "nome_gesto_esquerda": "MAO",
            "x_ultima_pos_cursor": 0,
            "y_ultima_pos_cursor": 0
        }
        self.config_logger = Logger.configure_json_data_logger()
        self.error_logger = Logger.configure_error_logger()

    def _verify_database(self) -> None:
        """ 
        Verifica se o arquivo de configuração existe; se não, cria com as configurações padrão.
        """
        if len(self.state) == 0: 
            if not os.path.exists(self.config_file):
                with open(self.config_file, "w") as file:
                    json.dump(self.state, file, indent=4)
                self.state = self.state
                self.config_logger.info("Arquivo de configuracao criado com as configuracoes padrao.")
                
    def get_atributes(self) -> list:
        """
        Retorna as chaves dos atributos padrão definidos em default_config.

        Returns:
            list: Lista contendo as chaves dos atributos padrão.
        """
        self._verify_database()
        return list(self.state.keys())
    
    def read_atribute(self, atributo: str) -> str:
        """ 
        Lê o valor de um atributo salvo dentro do arquivo de configuração.
        
        Args:
            atributo (str): O nome do atributo a ser lido.

        Returns:
            str: O valor do atributo, ou uma string vazia se não encontrado.
        """
        self._verify_database()
        try:
            with open(self.config_file, "r") as file:
                config = json.load(file)
                valor = config.get(atributo, "")
                self.config_logger.info(f"Atributo '{atributo}' lido com valor: '{valor}'")
                return valor
        except Exception as e:
            error_message = f"Ocorreu um erro ao ler o arquivo JSON: {e}"
            self.error_logger.error(error_message)
            self.config_logger.error(error_message)
            return ""

    def update_atribute(self, atributo: str, novo_valor: str) -> None:
        self._verify_database()
        try:
            with open(self.config_file, "r") as file:
                config = json.load(file)

            if config.get(atributo) == novo_valor:
                self.config_logger.info(f"Atributo '{atributo}' ja esta atualizado com valor: '{novo_valor}'")
                return

            config[atributo] = novo_valor

            # Usando um arquivo temporário para evitar corrupção
            with tempfile.NamedTemporaryFile("w", delete=False) as temp_file:
                json.dump(config, temp_file, indent=4)
                temp_file_path = temp_file.name

            # Substituir o arquivo original pelo temporário
            os.replace(temp_file_path, self.config_file)

            self.config_logger.info(f"Atributo '{atributo}' atualizado para: '{novo_valor}'")

        except json.JSONDecodeError:
            error_message = "Arquivo JSON corrompido. Restaurando para os valores padrão."
            self.error_logger.error(error_message)
            self.config_logger.error(error_message)
            self._restaurar_configuracoes_padrao()

        except FileNotFoundError as fnf_error:
            error_message = f"Não foi possível encontrar o arquivo JSON: {fnf_error}"
            self.error_logger.error(error_message)
            self.config_logger.error(error_message)
            
        except Exception as e:
            error_message = f"Erro ao atualizar o atributo '{atributo}': {e}"
            self.error_logger.error(error_message)
            self.config_logger.error(error_message)

    def _restaurar_configuracoes_padrao(self):
        """
        Restaura o arquivo de configuração com os valores padrão.
        """
        try:
            with open(self.config_file, "w") as file:
                json.dump(self.state, file, indent=4)
            self.config_logger.info("Configurações padrão restauradas com sucesso.")
        except Exception as e:
            error_message = f"Erro ao restaurar as configurações padrão: {e}"
            self.error_logger.error(error_message)
            self.config_logger.error(error_message)