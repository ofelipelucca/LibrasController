from src.gestures.gesture_interpretador import GestureInterpretador
from src.data.configs.config_router import ConfigRouter
from src.logger.logger import Logger
import mediapipe as mp
import threading
import cv2

class GestureReader:
    """
    Classe para detecção e interpretação de gestos das mãos com MediaPipe.

    A `GestureReader` usa MediaPipe para detectar e processar gestos das mãos em frames de vídeo. Interpreta os gestos detectados e atualiza as configurações conforme necessário.
    """

    def __init__(self) -> None:
        self.interpretador = GestureInterpretador()

        self.ongoing_threads = []
        self.stop_event = threading.Event()

        self.max_num_maos = 2

        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            static_image_mode           = False,
            max_num_hands               = self.max_num_maos,
            min_detection_confidence    = 0.75,
            min_tracking_confidence     = 0.75
        )

        # Configuração dos loggers
        self.logger = Logger.configure_application_logger()
        self.gestos_logger = Logger.configure_gestures_logger()
        self.error_logger = Logger.configure_error_logger()

    def _detect_hand(self, frame: cv2.Mat):
        """
        Detecta a mão dentro do frame.

        Args:
            frame (cv2.Mat): Imagem do frame onde a detecção será realizada.

        Returns:
            results: Resultado da detecção das mãos.
        """
        try:
            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(image_rgb)
            return results
        except Exception as e:
            error_message = f"Erro ao detectar maos: {e}"
            self.logger.error(error_message)
            self.gestos_logger.error(error_message)
            self.error_logger.error(error_message)
            raise

    def read_gesture(self, results) -> None:
        """
        Se for possível detectar uma mão no frame, passa para o interpretador.

        Args:
            results: Resultados da detecção das mãos.
        """
        try:
            if not self.stop_event.is_set():
                mao_direita = self._filter_hand(results, "Right")
                mao_esquerda = self._filter_hand(results, "Left")
                if mao_direita:
                    self.interpretador.interpretar(mao_direita, "Right")
                    self.gestos_logger.info("Gesto da mao direita interpretado com sucesso.")
                else:
                    ConfigRouter().update_atribute("nome_gesto_direita", "MAO")
                
                if mao_esquerda:
                    self.interpretador.interpretar(mao_esquerda, "Left")
                    self.gestos_logger.info("Gesto da mao esquerda interpretado com sucesso.")
                else:
                    ConfigRouter().update_atribute("nome_gesto_esquerda", "MAO")
        except Exception as e:
            error_message = f"Erro ao ler gesto: {e}"
            self.logger.error(error_message)
            self.gestos_logger.error(error_message)
            self.error_logger.error(error_message)

    def _filter_hand(self, results, mao_para_filtrar: str):
        """
        Filtra as mãos desejadas dentro de `results` e remove aquelas que não correspondem ao filtro.

        Args:
            results: Resultados da detecção das mãos.
            mao_para_filtrar (str): Mão para filtrar ("Right" ou "Left").

        Returns:
            hand_landmarks: Pontos da mão detectada.
        """
        try:
            hands = zip(results.multi_hand_landmarks, results.multi_handedness)
            for hand_landmarks, handedness in hands:
                if handedness.classification[0].label == mao_para_filtrar:
                    return hand_landmarks
        except Exception as e:
            error_message = f"Erro ao filtrar mao: {e}"
            self.logger.error(error_message)
            self.gestos_logger.error(error_message)
            self.error_logger.error(error_message)

    def classify_hand(self, handedness) -> str:
        """
        Determina qual mão está sendo detectada.

        Args:
            handedness: Dados da mão detectada.

        Returns:
            str: "Right" caso seja a mão direita, "Left" caso seja a mão esquerda.
        """
        try:
            classificacao = handedness.classification[0].label
            self.gestos_logger.info(f"Mao classificada como: {classificacao}.")
            return classificacao
        except Exception as e:
            error_message = f"Erro ao classificar mao: {e}"
            self.logger.error(error_message)
            self.gestos_logger.error(error_message)
            self.error_logger.error(error_message)
            raise
