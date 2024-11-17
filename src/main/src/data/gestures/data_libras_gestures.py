from src.logger.logger import Logger
import json
import os

class DataLibrasGestures:
    def __init__(self, data_filepath="src/main/src/data/gestures/libras_gestos.json") -> None:
        self.file_data_libras_gestures = data_filepath

        if not os.path.exists(self.file_data_libras_gestures):
            with open(self.file_data_libras_gestures, 'w') as file:
                json.dump({"data_gestos": {}, "atributos_relevantes": {}}, file)

    def obter_gestos(self) -> dict:
        """
        Retorna o dicionário de gestos do banco de dados de libras.

        Returns:
            dict: Dicionário de sinais de libras.
        """
        with open(self.file_data_libras_gestures, 'r') as file:
            data = json.load(file)
        return data.get("data_gestos", {})

    def obter_atributos_relevantes(self) -> dict:
        """
        Retorna o dicionário de atributos relevantes de cada sinal de libras.

        Returns:
            dict: Dicionário de atributos relevantes.
        """
        with open(self.file_data_libras_gestures, 'r') as file:
            data = json.load(file)
        return data.get("atributos_relevantes", {})
