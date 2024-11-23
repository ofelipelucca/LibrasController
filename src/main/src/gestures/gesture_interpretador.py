from src.data.gestures.data_libras_gestures import DataLibrasGestures
from src.data.gestures.data_custom_gestures import DataCustomGestures
from src.data.binds.data_binds_salvas import DataBindsSalvas
from src.data.configs.config_router import ConfigRouter
from src.inputs.execute_input import ExecuteInput
from src.logger.logger import Logger
from src.inputs.input import Input
import numpy as np
import threading
import time
import math

###############################################################################################
#           
#           GESTOS QUE JA TAO SENDO IDENTIFICADOS:
#               - A, B, C, D, E, F, G, H, I, L, M*, N, O*, Q*, R, S, U, W, Y
#                   *Com dificuldade
#
#
#           TODO:
#               - Implementar a lógica para ler e identificar gestos 
#                   que possuem movimento (J, K, X).
#               - Ao verificar o gesto no self.verificar_gesto(), se 
#                   "has_movement" for um atributo relevante do candidato,
#                   começar a verificação de movimento 
#               
#
###############################################################################################

class GestureInterpretador:
    """
    Classe responsável por interpretar e identificar gestos com base em landmarks de mãos.

    A classe `GestureInterpretador` usa landmarks de mãos para identificar gestos tanto de Libras quanto gestos personalizados configurados pelo usuário. Ela verifica a presença e a interação de dedos para determinar o gesto executado e executa ações associadas a esse gesto.
    """

    def __init__(self) -> None:
        self.execute_input = ExecuteInput()

        # Configuração dos loggers
        self.logger = Logger.configure_application_logger()
        self.gestos_logger = Logger.configure_gestures_logger()
        self.error_logger = Logger.configure_error_logger()

        self.data_libras = DataLibrasGestures()
        self.data_custom_gestures = DataCustomGestures()

        self.gestos_libras = self.data_libras.get_gestos()
        self.libras_atributos_relevantes = self.data_libras.get_atributos_relevantes()

        self.gestos_custom = self.data_custom_gestures.obter_gestos()
        self.custom_atributos_relevantes = self.data_custom_gestures.obter_atributos_relevantes()

        self.libras_hand = "Right"          # A mão que o programa vai ler os sinais de Libras
        self.custom_gesture_hand = "Left"   # A mão que o programa vai ler os gestos configurados pelo usuário

        self.capturing_movement = False
        self.landmarks_after_movement = None
        
        # Definindo os índices dos landmarks para cada dedo
        self.finger_landmarks = {
            'thumb': [1, 2, 3, 4],
            'index': [5, 6, 7, 8],
            'middle': [9, 10, 11, 12],
            'ring': [13, 14, 15, 16],
            'pinky': [17, 18, 19, 20]
        }
        
        # Pares de dedos para verificar intercessão
        self.finger_pairs = [
            ('thumb', 'middle'),
            ('thumb', 'ring'),
            ('thumb', 'pinky'),
            ('index', 'middle'),
            ('middle', 'ring'),
            ('ring', 'pinky'),
        ]

    def interpretar(self, hand_landmarks, mao_a_interpretar: str) -> None:
        """
        Realiza a interpretação de gestos baseada nos dados de entrada.

        Args:
            hand_landmarks (NormalizedLandmarkList): Os landmarks da mão a ser interpretada.
            mao_a_interpretar (str): A mão a ser interpretada.
        """

        if self.capturing_movement and mao_a_interpretar == self.libras_hand:
            self.landmarks_after_movement = hand_landmarks
            return

        gesto_atual = {
            "pointing_down": self.is_pointing_down(hand_landmarks, self.finger_landmarks['index'], self.finger_landmarks['middle'], self.finger_landmarks['ring'], self.finger_landmarks['pinky']),
            "fingers_overlap": self.are_fingers_overlapping(hand_landmarks, self.finger_pairs),
            "thumb_finger_inside_hand": not self.is_finger_up(hand_landmarks, self.finger_landmarks['thumb'][2:]),
            "index_finger_up": self.is_finger_up(hand_landmarks, self.finger_landmarks['index'][1:]),
            "middle_finger_up": self.is_finger_up(hand_landmarks, self.finger_landmarks['middle'][1:]),
            "ring_finger_up": self.is_finger_up(hand_landmarks, self.finger_landmarks['ring'][1:]),
            "pinky_finger_up": self.is_finger_up(hand_landmarks, self.finger_landmarks['pinky'][1:]),
            "thumb_middle_touch": self.are_finger_tips_touching(hand_landmarks, self.finger_landmarks['thumb'][3:], self.finger_landmarks['middle'][3:]),
            "thumb_cross_index": self.are_fingers_overlapping(hand_landmarks, [('thumb', 'index')]),
            "index_and_middle_together": self.are_fingers_together(hand_landmarks, self.finger_landmarks['index'], self.finger_landmarks['middle']),
            "bent_index": self.is_index_bent(),
            "has_movement": False,
            "type_of_movement": ""
        }
        #print(hand_landmarks.landmark[12].x)
        if mao_a_interpretar == self.libras_hand:
            thread_mao_direita = threading.Thread(target=self._interpretar_libras, args=(hand_landmarks, gesto_atual))
            thread_mao_direita.start()
            self.gestos_logger.info(f"Gesto de libras interpretado: {gesto_atual}")
        if mao_a_interpretar == self.custom_gesture_hand:
            self._interpretar_gesto_custom(hand_landmarks, gesto_atual)
            self.gestos_logger.info(f"Gesto custom interpretado: {gesto_atual}")

    def _interpretar_libras(self, hand_landmarks, gesto_atual: list):
        candidatos = list(self.gestos_libras.keys())

        for key in gesto_atual:
            if len(candidatos) == 1:
                break
            candidatos = [gesto for gesto in candidatos if self.gestos_libras[gesto][key] == gesto_atual[key]] # Filtrando os gestos do banco de dados
                
        for candidato in candidatos:
            if self.gestos_libras[candidato]["has_movement"]:
                tipo_de_movimento, tem_movimento = self._categorizar_movimento(hand_landmarks, self.gestos_libras[candidato]["type_of_movement"])
                gesto_atual["type_of_movement"] = tipo_de_movimento
                gesto_atual["has_movement"] = tem_movimento

        if len(candidatos) == 1:
            gesto_identificado = candidatos[0]
            if self._verify_gesto(gesto_atual, gesto_identificado):
               ConfigRouter().update_atribute("nome_gesto_direita", gesto_identificado)
               self._execute_acao_gesto(hand_landmarks, gesto_identificado)
               return

        ConfigRouter().update_atribute("nome_gesto_direita", "MAO")
        
    def _interpretar_gesto_custom(self, hand_landmarks, gesto_atual: list):
        candidatos = list(self.gestos_custom.keys())

        for key in gesto_atual:
            if len(candidatos) == 1:
                break
            candidatos = [gesto for gesto in candidatos if self.gestos_custom[gesto][key] == gesto_atual[key]] # Filtrando os gestos do banco de dados

        if len(candidatos) == 1:
            gesto_identificado = candidatos[0]
            if self._verify_gesto(gesto_atual, gesto_identificado):
               self._execute_acao_gesto(hand_landmarks, gesto_identificado)
               ConfigRouter().update_atribute("nome_gesto_esquerda", gesto_identificado)
               return
        
        ConfigRouter().update_atribute("nome_gesto_esquerda", "MAO")

    def _verify_gesto(self, gesto: list, gesto_candidato: str) -> bool:
        """
        Verifica, atributo por atributo (dentre os atributos relevantes para o gesto), se o gesto detectado é igual ao gesto candidato do banco de dados.

        Args:
            gesto (list): Os atributos do gesto detectado.
            gesto_candidato (str): O nome do gesto candidato.

        Returns:
            bool: True se os atributos relevantes do gesto detectado são iguais aos do gesto candidato.
            bool: False caso contrário.
        """
        def _concatenar_dicts(*dict_args):
            result = {}
            for dict in dict_args:
                result.update(dict)
            return result

        dict_atributos_relevantes = _concatenar_dicts(self.libras_atributos_relevantes, self.custom_atributos_relevantes)
        dict_gestos = _concatenar_dicts(self.gestos_libras, self.gestos_custom)

        atributos_relevantes = dict_atributos_relevantes[gesto_candidato]
        gesto_candidato = dict_gestos[gesto_candidato]

        for atributo in atributos_relevantes:
            if gesto[atributo] != gesto_candidato[atributo]:
                return False
        return True

    def _execute_acao_gesto(self, hand_landmarks, gesto: str) -> None:
        """
        Executa o input do gesto identificado.

        Args:
            hand_landmarks (NormalizedLandmarkList): Os landmarks da mão a ser interpretada.
            gesto (str): O nome do gesto identificado.
        """
        if DataBindsSalvas.do_bind_exist(gesto): 
            bind = DataBindsSalvas.get_bind(gesto)
            tempo = DataBindsSalvas.get_time_pressed(gesto)
            modo_continuo = DataBindsSalvas.get_toggle(gesto)
            input = Input(bind, tempo, modo_continuo)
            self.execute_input.executar_input(bind, input)
        if gesto == "mouse_tracking":
            x_coords = hand_landmarks.landmark[8].x
            y_coords = hand_landmarks.landmark[8].y
            self.execute_input.executar_mouse_tracking(x_coords, y_coords)

    def is_finger_up(self, hand_landmarks, finger_indices: list) -> bool:
        """
        Verifica se o dedo está levantado.

        Args:
            hand_landmarks (NormalizedLandmarkList): Os landmarks da mão.
            finger_indices (list): Os índices do dedo a ser verificado.

        Returns:
            bool: True se o dedo estiver levantado. 
            bool: False caso contrário.
        """
        # Pontos de referência para a base do quadrado imaginário
        base_points = [
            hand_landmarks.landmark[0],  # Pulso
            hand_landmarks.landmark[1],  # Base do dedão
            hand_landmarks.landmark[5],  # Base do dedo indicador
            hand_landmarks.landmark[9],  # Base do dedo médio
            hand_landmarks.landmark[13], # Base do dedo anelar
            hand_landmarks.landmark[17]  # Base do dedo mínimo
        ]
        
        # Criando um quadrado imaginário na tela, usando as coordenadas das extremidades da mão.
        image_height, image_width = 640, 480

        x_coords = [int(point.x * image_width) for point in base_points]
        y_coords = [int(point.y * image_height) for point in base_points]

        min_x, max_x = min(x_coords) - 15, max(x_coords) + 15
        min_y, max_y = min(y_coords) - 15, max(y_coords) + 15

        for index in finger_indices:
            finger_point = hand_landmarks.landmark[index]           #      Premissa:
            finger_point_x = int(finger_point.x * image_width)      #       Se pelo menos um dos landmarks do dedo estiver DENTRO do quadrado,
            finger_point_y = int(finger_point.y * image_height)     #       o dedo será considerado como ABAIXADO

            if max_x >= finger_point_x >= min_x and max_y >= finger_point_y >= min_y:
                return False
        return True

    def are_fingers_overlapping(self, hand_landmarks, finger_pairs: list) -> bool:
        """
        Verifica se os dedos estão sobrepostos.

        Args:
            hand_landmarks (NormalizedLandmarkList): Os landmarks da mão.
            finger_pairs (list): Os pares de dedos a serem verificados.

        Returns:
            bool: True se os dedos estiverem sobrepostos.
            bool: False caso contrário.
        """

        for pair in finger_pairs:
            if self._retas_se_intersectam(
                hand_landmarks, 
                self.finger_landmarks[pair[0]], 
                self.finger_landmarks[pair[1]]
            ):
                return True

        return False

    def _retas_se_intersectam(self, hand_landmarks, finger1: list, finger2: list) -> bool:
        """
        Verifica se há interseção entre as linhas dos dedos fornecidos.

        Args:
            hand_landmarks (NormalizedLandmarkList): Lista de pontos de referência das mãos.
            finger1 (list): Lista de índices de landmarks para o primeiro dedo.
            finger2 (list): Lista de índices de landmarks para o segundo dedo.

        Returns:
            bool: True se as linhas entre os dedos se intersectarem.
            bool: False caso contrário.
        """
        p1 = np.array([hand_landmarks.landmark[finger1[0]].x, hand_landmarks.landmark[finger1[0]].y])
        p2 = np.array([hand_landmarks.landmark[finger1[-1]].x, hand_landmarks.landmark[finger1[-1]].y])
        q1 = np.array([hand_landmarks.landmark[finger2[0]].x, hand_landmarks.landmark[finger2[0]].y])
        q2 = np.array([hand_landmarks.landmark[finger2[-1]].x, hand_landmarks.landmark[finger2[-1]].y])

        return self._do_intersect(p1, p2, q1, q2)

    def _do_intersect(self, p1, p2, q1, q2) -> bool:
        """
        Verifica se duas linhas definidas por quatro pontos se intersectam.

        Args:
            p1, p2 (numpy.ndarray): Pontos que definem a primeira linha.
            q1, q2 (numpy.ndarray): Pontos que definem a segunda linha.

        Returns:
            bool: True se as linhas se intersectam.
            bool: False caso contrário.
        """
        def __orientation(p, q, r):
            val = (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])
            if val == 0:
                return 0  # Colinear
            return 1 if val > 0 else 2  # Horário ou anti-horário

        def __is_on_the_segment(p, q, r):
            if (min(p[0], r[0]) <= q[0] <= max(p[0], r[0]) and
                    min(p[1], r[1]) <= q[1] <= max(p[1], r[1])):
                return True
            return False

        # Obter as orientações para diferentes combinações de pontos
        o1 = __orientation(p1, p2, q1)
        o2 = __orientation(p1, p2, q2)
        o3 = __orientation(q1, q2, p1)
        o4 = __orientation(q1, q2, p2)

        # Caso geral
        if o1 != o2 and o3 != o4:
            return True

        # Casos especiais de colinearidade
        if o1 == 0 and __is_on_the_segment(p1, q1, p2):
            return True
        if o2 == 0 and __is_on_the_segment(p1, q2, p2):
            return True
        if o3 == 0 and __is_on_the_segment(q1, p1, q2):
            return True
        if o4 == 0 and __is_on_the_segment(q1, p2, q2):
            return True

        return False
    
    def are_finger_tips_touching(self, hand_landmarks, finger1: list, finger2: list, min_distance=0.05) -> bool:
        """
        Verifica se o a ponta dos dedos estão se tocando.

        Args:
            hand_landmarks (NormalizedLandmarkList): Lista de pontos de referência das mãos.
            finger1 (list): Lista de índices de landmarks para o primeiro dedo.
            finger2 (list): Lista de índices de landmarks para o segundo dedo.
            min_distance (float): Distancia mínima para os dedos serem considerados separados.

        Returns:
            bool: True se a ponta dos dedos estiverem se tocando.
            bool: False caso contrário.
        """

        finger1_tip_x, finger1_tip_y = hand_landmarks.landmark[finger1[-1]].x, hand_landmarks.landmark[finger1[-1]].y
        finger2_tip_x, finger2_tip_y = hand_landmarks.landmark[finger2[-1]].x, hand_landmarks.landmark[finger2[-1]].y

        distance = math.sqrt((finger2_tip_x - finger1_tip_x) ** 2 + (finger2_tip_y - finger1_tip_y) ** 2)

        return distance <= min_distance

    def _categorizar_movimento(self, hand_landmarks, type_of_movement: str) -> tuple:
        """
        Verifica se há movimento no gesto e retorna o nome do atributo verdadeiro.

        Args:
            hand_landmarks (NormalizedLandmarkList): Lista de pontos de referência das mãos.
            type_of_movement (str): O nome do movimento a ser verificado.

        Returns:
            tuple: Uma tupla contendo:
                - str: O nome do atributo verdadeiro (se houver algum) ou uma string vazia se nenhum atributo for verdadeiro.
                - bool: True se qualquer tipo de movimento for detectado, False caso contrário.
        """

        def _wrist_rotate(hand_landmarks) -> bool:
            """
            Verifica se o pulso rotaciona.

            Args:
                hand_landmarks (NormalizedLandmarkList): Lista de pontos de referência das mãos.

            Returns:
                bool: True se o pulso rotacionar.
                bool: False caso contrário.
            """
            x_wrist_left_i = hand_landmarks.landmark[5].x
            x_wrist_right_i = hand_landmarks.landmark[17].x

            inicial_distance = x_wrist_right_i - x_wrist_left_i
            
            time.sleep(1)
            
            if self.landmarks_after_movement == None:
                return False
            
            x_wrist_left_f = self.landmarks_after_movement.landmark[5].x
            x_wrist_right_f = self.landmarks_after_movement.landmark[17].x

            self.capturing_movement = False

            final_distance = x_wrist_right_f - x_wrist_left_f

            diff = inicial_distance / final_distance


            return not 0.9 < diff < 1.2

        def _finger_tip_moves(hand_landmarks, finger: str, min_diff: float, max_diff: float) -> tuple:
            """
            Verifica se a posição do dedo muda.

            Args:
                hand_landmarks (NormalizedLandmarkList): Lista de pontos de referência das mãos.
                finger (str): O dedo ser verificado.

            Returns:
                tuple: Uma tupla contendo: 
                    bool: True se a posição mudar.
                    bool: False caso contrário.
            """
            x_index_tip_i = hand_landmarks.landmark[self.finger_landmarks[finger][3]].x
            y_index_tip_i = hand_landmarks.landmark[self.finger_landmarks[finger][3]].y

            time.sleep(1)

            if self.landmarks_after_movement == None:
                return False
            
            x_index_tip_f = self.landmarks_after_movement.landmark[self.finger_landmarks[finger][3]].x
            y_index_tip_f = self.landmarks_after_movement.landmark[self.finger_landmarks[finger][3]].y

            self.capturing_movement = False

            x_diff = x_index_tip_i / x_index_tip_f
            y_diff = y_index_tip_i / y_index_tip_f 


            return not 0.9 < x_diff < 1.2, not 0.9 < y_diff < 1.2
        
        self.capturing_movement = True

        movement_methods = {
            "wrist_rotate": lambda hand_landmarks: _wrist_rotate(hand_landmarks),
            "y_index_tip_changes": lambda hand_landmarks: _finger_tip_moves(hand_landmarks, 'index', 0.9, 1.2)[0],
            "x_index_tip_changes": lambda hand_landmarks: _finger_tip_moves(hand_landmarks, 'index', 0.9, 1.2)[1],
            "pinky_pos_changes": lambda hand_landmarks: _finger_tip_moves(hand_landmarks, 'pinky', 0.9, 1.5)[1],
        }

        if type_of_movement in movement_methods:
            return type_of_movement, movement_methods[type_of_movement](hand_landmarks)
        
        self.capturing_movement = False
        return "", False

    def is_pointing_down(self, hand_landmarks, finger1: list, finger2: list, finger3: list, finger4: list) -> bool:
        """
        Verifica se qualquer um dos dedos especificados está apontando para baixo.

        Args:
            hand_landmarks (NormalizedLandmarkList): Lista de landmarks da mão.
            finger1 (list): Lista de índices de landmarks para o primeiro dedo.
            finger2 (list): Lista de índices de landmarks para o segundo dedo.
            finger3 (list): Lista de índices de landmarks para o terceiro dedo.
            finger4 (list): Lista de índices de landmarks para o quarto dedo.
        
        Returns:
            bool: True se qualquer um dos dedos especificados estiver apontando para baixo.
            bool: False caso contrário.
        """
        
        # tip: Landmark da ponta do dedo
        # pip: Landmark da base do dedo

        wrist_y = hand_landmarks.landmark[0].y
        finger1_tip_y, finger1_pip_y = hand_landmarks.landmark[finger1[3]].y, hand_landmarks.landmark[finger1[2]].y
        finger2_tip_y, finger2_pip_y = hand_landmarks.landmark[finger2[3]].y, hand_landmarks.landmark[finger2[2]].y
        finger3_tip_y, finger3_pip_y = hand_landmarks.landmark[finger3[3]].y, hand_landmarks.landmark[finger3[2]].y
        finger4_tip_y, finger4_pip_y = hand_landmarks.landmark[finger4[3]].y, hand_landmarks.landmark[finger4[2]].y

        return ((finger1_tip_y > finger1_pip_y and finger1_tip_y > wrist_y) or      #      Premissa:
                (finger2_tip_y > finger2_pip_y and finger2_tip_y > wrist_y) or      #       Se o landmark da ponta do dedo está abaixo do  
                (finger3_tip_y > finger3_pip_y and finger3_tip_y > wrist_y) or      #       landmark da base do dedo e do landmark do pulso,
                (finger4_tip_y > finger4_pip_y and finger4_tip_y > wrist_y))        #       a mão será considerada como apontada para baixo
    
    def are_fingers_together(self, hand_landmarks, finger1: list, finger2: list, min_percentage_difference=12.0) -> bool:
        """
        Verifica se os dedos estão juntos com base na porcentagem de diferença de distância entre PIPs e TIPs.

        Args:
            hand_landmarks (NormalizedLandmarkList): Objeto que contém as landmarks da mão.
            finger1 (list): Índices dos landmarks do primeiro dedo.
            finger2 (list): Índices dos landmarks do segundo dedo.
            min_percentage_difference (float): Diferença percentual mínima para considerar os dedos juntos.

        Returns:
            bool: True se os dedos estiverem juntos.
            bool: False caso contrário.
        """

        # tip: Landmark da ponta do dedo
        # pip: Landmark da base do dedo

        finger1_tip_x, finger1_tip_y = hand_landmarks.landmark[finger1[3]].x, hand_landmarks.landmark[finger1[3]].y
        finger2_tip_x, finger2_tip_y = hand_landmarks.landmark[finger2[3]].x, hand_landmarks.landmark[finger2[3]].y
        
        finger1_pip_x, finger1_pip_y = hand_landmarks.landmark[finger1[2]].x, hand_landmarks.landmark[finger1[2]].y
        finger2_pip_x, finger2_pip_y = hand_landmarks.landmark[finger2[2]].x, hand_landmarks.landmark[finger2[2]].y

        distance_tips = math.sqrt((finger2_tip_x - finger1_tip_x) ** 2 + (finger2_tip_y - finger1_tip_y) ** 2)
        distance_pips = math.sqrt((finger2_pip_x - finger1_pip_x) ** 2 + (finger2_pip_y - finger1_pip_y) ** 2)

        percentage_difference = abs(distance_tips - distance_pips) / min(distance_tips, distance_pips) * 100

        return percentage_difference <= min_percentage_difference

    def is_index_bent(self) -> bool:
        """
        Verifica se o dedo indicador está dobrado.

        Returns:
            bool: True se o indicador estiver dobrado.
            bool: False caso contrário.
        """
        return False
