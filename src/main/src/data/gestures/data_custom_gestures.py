from src.data.binds.data_binds_salvas import DataBindsSalvas
from src.logger.logger import Logger
import json
import os

class DataCustomGestures:
    def __init__(self, data_filepath="src/main/src/data/gestures/custom_gestos.json") -> None:
        self.file_data_custom_gestures = data_filepath

        if not os.path.exists(self.file_data_custom_gestures):
            with open(self.file_data_custom_gestures, 'w') as file:
                json.dump({"data_gestos": {}, "atributos_relevantes": {}}, file)

    def obter_gestos(self) -> dict:
        """
        Retorna o dicionário de gestos do banco de dados de gestos custom.

        Returns:
            dict: Dicionário de gestos custom.
        """
        try:
            with open(self.file_data_custom_gestures, 'r') as file:
                data = json.load(file)
            return data.get("data_gestos", {})
        
        except json.JSONDecodeError:
            raise ValueError("Erro ao decodificar o arquivo JSON de gestos custom.")
        except FileNotFoundError:
            raise FileNotFoundError("O arquivo de gestos custom não foi encontrado.")
        except Exception as e:
            raise RuntimeError(f"Ocorreu um erro ao obter os gestos: {e}")

    def obter_atributos_relevantes(self) -> dict:
        """
        Retorna o dicionário de atributos relevantes de cada gesto custom.

        Returns:
            dict: Dicionário de atributos relevantes.
        """
        try:
            with open(self.file_data_custom_gestures, 'r') as file:
                data = json.load(file)
            return data.get("atributos_relevantes", {})
        
        except json.JSONDecodeError:
            raise ValueError("Erro ao decodificar o arquivo JSON de atributos relevantes.")
        except FileNotFoundError:
            raise FileNotFoundError("O arquivo de gestos custom não foi encontrado.")
        except Exception as e:
            raise RuntimeError(f"Ocorreu um erro ao obter os atributos relevantes: {e}")

    def salvar_novo_gesto(self, novo_gesto_custom: dict, atributos_relevantes: dict, bind: str, tempo_pressionado: int, sobreescrever: bool) -> None:
        """
        Salva um novo gesto custom no banco de dados.

        Args:
            novo_gesto_custom (dict): O novo gesto a ser salvo no banco de dados.
            atributos_relevantes (dict): Dicionário de atributos relevantes do novo gesto.
            bind (str): A bind vinculada ao novo gesto.
            tempo_pressionado (int): O tempo que a bind será pressionada (MODO_SINGULAR).
            sobreescrever (bool): Se o gesto já existe, sobreescrever com o novo.
        """
        try:
            with open(self.file_data_custom_gestures, 'r') as file:
                data = json.load(file)

            if "data_gestos" not in data:
                data["data_gestos"] = {}
            if "atributos_relevantes" not in data:
                data["atributos_relevantes"] = {}

            if not sobreescrever:
                nome_do_gesto = next(iter(novo_gesto_custom))
                if nome_do_gesto in data["data_gestos"]:
                    raise ValueError(f"O gesto '{nome_do_gesto}' ja existe e nao pode ser sobrescrito.")

            data["data_gestos"].update(novo_gesto_custom)
            data["atributos_relevantes"].update(atributos_relevantes)

            with open(self.file_data_custom_gestures, 'w') as file:
                json.dump(data, file, indent=4)

            nome_do_gesto = next(iter(novo_gesto_custom))

            DataBindsSalvas.adicionar_nova_bind(nome_do_gesto, bind, tempo_pressionado, sobreescrever)

        except json.JSONDecodeError:
            raise ValueError("Erro ao decodificar o arquivo JSON de gestos custom.")
        except FileNotFoundError:
            raise FileNotFoundError("O arquivo de gestos custom não foi encontrado.")
        except Exception as e:
            raise RuntimeError(f"Ocorreu um erro ao salvar o novo gesto: {e}")
                
    def remover_gesto(self, nome_do_gesto: str) -> None:
            """
            Remove um gesto custom do banco de dados e remove a bind associada.

            Args:
                nome_do_gesto (str): O nome do gesto a ser removido.
            """
            try:
                with open(self.file_data_custom_gestures, 'r') as file:
                    data = json.load(file)

                if "data_gestos" in data:
                    if nome_do_gesto in data["data_gestos"]:
                        del data["data_gestos"][nome_do_gesto]

                if "atributos_relevantes" in data:
                    if nome_do_gesto in data["atributos_relevantes"]:
                        del data["atributos_relevantes"][nome_do_gesto]

                with open(self.file_data_custom_gestures, 'w') as file:
                    json.dump(data, file, indent=4)

                DataBindsSalvas.remover_bind(nome_do_gesto)

            except json.JSONDecodeError:
                raise ValueError("Erro ao decodificar o arquivo JSON de gestos custom.")
            except FileNotFoundError:
                raise FileNotFoundError("O arquivo de gestos custom não foi encontrado.")
            except Exception as e:
                raise RuntimeError(f"Ocorreu um erro ao remover o gesto: {e}")