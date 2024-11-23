from src.logger.logger import Logger
import os
import json

logger = Logger.configure_application_logger()
data_logger = Logger.configure_json_data_logger()
error_logger = Logger.configure_error_logger()

class DataBindsSalvas:
    data_file = "src/main/src/data/binds/binds_salvas.json" 
    binds_dict = {}  # Armazena (bind, tempo_pressionado, modo_toggle, customizable) para cada chave

    @staticmethod
    def do_bind_exist(nome_do_gesto: str) -> bool:
        """
        Verifica se um gesto está salvo no banco de dados de binds.

        Args:
            nome_do_gesto (str): O nome do gesto a ser recuperado.

        Returns:
            bool: True se o gesto foi encontrado no banco de dados de binds.
            bool: False caso contrário.
        """
        DataBindsSalvas.read_database()
        return nome_do_gesto in DataBindsSalvas.binds_dict

    @staticmethod
    def get_all_binds() -> dict:
        """
        Retorna toda a lista de binds.
        """
        DataBindsSalvas.read_database()
        return DataBindsSalvas.binds_dict
    
    @staticmethod
    def get_bind(nome_do_gesto: str) -> str:
        """
        Obtém a bind associada ao gesto, se existir.

        Args:
            nome_do_gesto (str): O nome do gesto a ser recuperado.

        Returns:
            str: A bind associada ao gesto.
            None: Caso o gesto não exista no banco de dados de binds.
        """
        DataBindsSalvas.read_database()
        return DataBindsSalvas.binds_dict.get(nome_do_gesto, {}).get('bind', None)

    @staticmethod
    def get_time_pressed(nome_do_gesto: str) -> int:
        """
        Obtém o tempo pressionado associado à chave, se a chave existir.

        Args:
            nome_do_gesto (str): O nome do gesto a ser recuperado.

        Returns:
            int: O tempo pressionado associado ao gesto.
            int: 5, caso a informação não exista no banco de dados de binds.
        """
        DataBindsSalvas.read_database()
        return DataBindsSalvas.binds_dict.get(nome_do_gesto, {}).get('tempo_pressionado', 5)

    @staticmethod
    def get_toggle(nome_do_gesto: str) -> bool:
        """
        Obtém o valor de 'modo_toggle' associado à chave, se a chave existir.

        Args:
            nome_do_gesto (str): O nome do gesto a ser recuperado.

        Returns:
            bool: O valor de 'modo_toggle' associado ao gesto.
            bool: False, caso a informação não exista no banco de dados de binds.
        """
        DataBindsSalvas.read_database()
        return DataBindsSalvas.binds_dict.get(nome_do_gesto, {}).get('modo_toggle', False)
    
    @staticmethod
    def get_customizable(nome_do_gesto: str) -> bool:
        """
        Obtém o valor de 'customizable' associado à chave, se a chave existir.

        Args:
            nome_do_gesto (str): O nome do gesto a ser recuperado.

        Returns:
            bool: O valor de 'customizable' associado ao gesto.
            bool: False, caso a informação não exista no banco de dados de binds.
        """
        DataBindsSalvas.read_database()
        return DataBindsSalvas.binds_dict.get(nome_do_gesto, {}.get('customizable', False))

    @staticmethod
    def read_database() -> None:
        """
        Obtém todos os dados salvos no banco de dados de binds.
        """
        if not os.path.isfile(DataBindsSalvas.data_file):
            msg = f"O arquivo {DataBindsSalvas.data_file} não existe."
            error_logger.info(msg)
            raise FileExistsError(msg)

        with open(DataBindsSalvas.data_file, 'r') as file:
            DataBindsSalvas.binds_dict = json.load(file)

    @staticmethod
    def save_database() -> None:
        """
        Salva os dados no banco de dados de binds.
        """
        try:
            with open(DataBindsSalvas.data_file, 'w') as file:
                json.dump(DataBindsSalvas.binds_dict, file, indent=4)
                data_logger.info("Dados salvos com sucesso.")
        except Exception as e:
            error_logger.info(f"Não foi possível salvar no banco de dados: {e}")

    @staticmethod
    def add_new_bind(nome_do_gesto: str, bind: str, tempo_pressionado: int, modo_toggle: bool, sobreescrever: bool) -> None:
        """
        Salva uma nova bind no banco de dados de binds.
        """
        DataBindsSalvas.read_database()

        if DataBindsSalvas.do_bind_exist(nome_do_gesto) and not sobreescrever:
            msg = f"O gesto '{nome_do_gesto}' ja existe no banco de dados e a autorizacao para sobreescrever eh False."
            error_logger.info(msg)
            return

        DataBindsSalvas.binds_dict[nome_do_gesto] = {
            "bind": bind,
            "modo_toggle": modo_toggle,
            "tempo_pressionado": tempo_pressionado,
            "customizable": DataBindsSalvas.binds_dict[nome_do_gesto]["customizable"]
        }
        
        gesto_atual = DataBindsSalvas.binds_dict[nome_do_gesto]
        data_logger.info(f"Gesto salvo no database: bind: {gesto_atual['bind']}; "
                                                    f"tempo: {gesto_atual['tempo_pressionado']}; "
                                                    f"toggle: {gesto_atual['modo_toggle']}")

        DataBindsSalvas.save_database()
        
    @staticmethod
    def remove_bind(nome_do_gesto: str) -> None:
        """
        Remove uma bind do banco de dados de binds.

        Args:
            nome_do_gesto (str): O nome do gesto a ser removido.
        """
        DataBindsSalvas.read_database()
        if not DataBindsSalvas.do_bind_exist(nome_do_gesto):
            return

        del DataBindsSalvas.binds_dict[nome_do_gesto]

        DataBindsSalvas.save_database()