import os
import json

class DataBindsSalvas:
    data_file = "src/main/src/data/binds/binds_salvas.json" 
    binds_dict = {}  # Armazena (bind, tempo_pressionado, modo_toggle) para cada chave

    @staticmethod
    def verificar_nome(nome_do_gesto: str) -> bool:
        """
        Verifica se um gesto está salvo no banco de dados de binds.

        Args:
            nome_do_gesto (str): O nome do gesto a ser recuperado.

        Returns:
            bool: True se o gesto foi encontrado no banco de dados de binds.
            bool: False caso contrário.
        """
        DataBindsSalvas.ler_arquivo()
        return nome_do_gesto in DataBindsSalvas.binds_dict

    @staticmethod
    def get_all_binds() -> dict:
        """
        Retorna toda a lista de binds.
        """
        DataBindsSalvas.ler_arquivo()
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
        DataBindsSalvas.ler_arquivo()
        return DataBindsSalvas.binds_dict.get(nome_do_gesto, {}).get('bind', None)

    @staticmethod
    def obter_tempo_pressionado(nome_do_gesto: str) -> int:
        """
        Obtém o tempo pressionado associado à chave, se a chave existir.

        Args:
            nome_do_gesto (str): O nome do gesto a ser recuperado.

        Returns:
            int: O tempo pressionado associado ao gesto.
            int: 5, caso a informação não exista no banco de dados de binds.
        """
        DataBindsSalvas.ler_arquivo()
        return DataBindsSalvas.binds_dict.get(nome_do_gesto, {}).get('tempo_pressionado', 5)

    @staticmethod
    def obter_modo_toggle(nome_do_gesto: str) -> bool:
        """
        Obtém o valor de modo_toggle associado à chave, se a chave existir.

        Args:
            nome_do_gesto (str): O nome do gesto a ser recuperado.

        Returns:
            bool: O valor de modo_toggle associado ao gesto.
            bool: False, caso a informação não exista no banco de dados de binds.
        """
        DataBindsSalvas.ler_arquivo()
        return DataBindsSalvas.binds_dict.get(nome_do_gesto, {}).get('modo_toggle', False)

    @staticmethod
    def ler_arquivo() -> None:
        """
        Obtém todos os dados salvos no banco de dados de binds.
        """
        if not os.path.isfile(DataBindsSalvas.data_file):
            raise FileExistsError(f"O arquivo {DataBindsSalvas.data_file} não existe.")

        with open(DataBindsSalvas.data_file, 'r') as file:
            DataBindsSalvas.binds_dict = json.load(file)

    @staticmethod
    def salvar_arquivo() -> None:
        """
        Salva os dados no banco de dados de binds.
        """
        DataBindsSalvas.ler_arquivo()
        with open(DataBindsSalvas.data_file, 'w') as file:
            json.dump(DataBindsSalvas.binds_dict, file, indent=4)

    @staticmethod
    def adicionar_nova_bind(nome_do_gesto: str, bind: str, tempo_pressionado: int, modo_toggle: bool, sobreescrever: bool) -> None:
        """
        Salva uma nova bind no banco de dados de binds.

        Args:
            nome_do_gesto (str): O nome do novo gesto a ser adicionado.
            bind (str): A bind que o gesto será vinculado.
            tempo_pressionado (int): O tempo que a bind será pressionada (MODO_SINGULAR).
            modo_toggle (bool): Define se a bind será contínua ou singular.
            sobreescrever (bool): Se o gesto já existe, sobreescrever com o novo.
        """
        DataBindsSalvas.ler_arquivo()

        if not sobreescrever:
            if DataBindsSalvas.verificar_nome(nome_do_gesto):
                print(f"Erro: O gesto '{nome_do_gesto}' ja existe no banco de dados.")
                return

        DataBindsSalvas.binds_dict[nome_do_gesto] = {
            "bind": bind,
            "tempo_pressionado": tempo_pressionado,
            "modo_toggle": modo_toggle
        }

        DataBindsSalvas.salvar_arquivo()

    @staticmethod
    def remover_bind(nome_do_gesto: str) -> None:
        """
        Remove uma bind do banco de dados de binds.

        Args:
            nome_do_gesto (str): O nome do gesto a ser removido.
        """
        DataBindsSalvas.ler_arquivo()
        if not DataBindsSalvas.verificar_nome(nome_do_gesto):
            return

        del DataBindsSalvas.binds_dict[nome_do_gesto]

        DataBindsSalvas.salvar_arquivo()