from src.data.configs.config_router import ConfigRouter
from src.gestures.gesture_reader import GestureReader
from pygrabber.dshow_graph import FilterGraph
from src.logger.logger import Logger
import threading
import pythoncom  
import traceback
import time
import cv2

LEFT = "Left"
RIGHT = "Right"
WINDOW_NAME = "LibrasController"
FONT = cv2.FONT_HERSHEY_SIMPLEX

class Camera:
    """
    Classe responsável por capturar vídeo da câmera, detectar gestos e exibir os frames processados.
    """

    def __init__(self) -> None:
        """
        Inicializa o CameraReader com os componentes de captura de vídeo, leitor de gestos e configuração.
        """
        self.stop_flag = threading.Event()  
        self.cap: cv2.VideoCapture = None
        self.frame: cv2.Mat = None
        self.crop_hand_mode: bool = False

        self.gesture_reader = GestureReader()

        self.nome_gesto_direita: str = "MAO"
        self.nome_gesto_esquerda: str = "MAO"

        ConfigRouter().update_atribute("nome_gesto_esquerda", self.nome_gesto_esquerda)
        ConfigRouter().update_atribute("nome_gesto_direita", self.nome_gesto_direita)

        self.logger = Logger.configure_application_logger()

    async def start(self) -> None:
        camera_nome = ConfigRouter.read_atribute("camera_selecionada")
        self.logger.info("Processo de deteccao iniciado.")
        try:
            self.select_camera_by_name(camera_nome)

            def detection_loop():
                try:
                    self.logger.info("Iniciando loop de deteccao.")
                    while not self.stop_flag.is_set():
                        unready_frame = self.read_frame()
                        if unready_frame is None:
                            time.sleep(0.01) 
                            continue

                        results = self.gesture_reader._detect_hand(unready_frame)
                        unready_frame = self.draw_hand(unready_frame, results)

                        if self.crop_hand_mode:
                            unready_frame = self.crop_hand(results)
                            continue

                        self.frame = unready_frame

                        if results.multi_hand_landmarks:
                            self.gesture_reader.read_gesture(results)
                    self.logger.info("Saindo do loop de deteccao.")
                except Exception as e:
                    self.logger.error(f"Erro no loop de deteccao: {traceback.format_exc()}")

            detection_thread = threading.Thread(target=detection_loop)
            detection_thread.daemon = True  
            detection_thread.start()

        except Exception as e:
            error_message = f"Erro durante a captura de video: {traceback.format_exc()}"
            self.logger.error(error_message)
            raise RuntimeError(error_message)

    def stop(self) -> None:
        """
        Para a captura de vídeo e libera a câmera.
        """
        self.stop_flag.set()
        if self.cap:
            self.cap.release()
            self.cap = None
        self.logger.info("Camera liberada.")
        self.logger.info("Objetos e recursos limpos.")

    def crop_hand(self, results) -> cv2.Mat:
        """
        Corta o frame nos limites da mão detectada.

        Args:
            results: Os resultados da detecção de mão.
        
        Returns:
            cv2.Mat: O frame com a mão cropada ou um frame vazio se não há nenhuma lista.
        """
        hand_landmarks_list = self.gesture_reader.get_hand_landmarks(results)
        if hand_landmarks_list:
            for hand_landmarks, handedness in zip(hand_landmarks_list, results.multi_handedness):
                mao_detectada = self.gesture_reader.classify_hand(handedness)
                if mao_detectada == RIGHT:
                    x_left, y_left, x_right, y_right = self.calculate_hand_rectangle(self.frame, hand_landmarks)
                    return self.frame[y_left:y_right, x_left:x_right]
        return self.frame

    def list_cameras(self) -> list[str]:
        """
        Lista todas as câmeras disponíveis no sistema.

        Returns:
            list: Uma lista com os nomes dos dispositivos de câmera.
        """
        pythoncom.CoInitialize()
        try:
            graph = FilterGraph()
            return graph.get_input_devices()
        finally:
            pythoncom.CoUninitialize()
            
    def select_camera_by_name(self, camera_nome: str) -> None:
        """
        Seleciona a câmera pelo nome do dispositivo.

        Args:
            camera_nome (str): O nome da câmera a ser utilizada.

        Raises:
            ValueError: Se a câmera com o nome fornecido não for encontrada.
        """
        dispositivos_video = self.list_cameras()
        if camera_nome in dispositivos_video:
            index = dispositivos_video.index(camera_nome)
            self.cap = cv2.VideoCapture(index)
            if not self.cap.isOpened():
                raise ValueError(f"Não foi possível abrir a câmera: {camera_nome}")
            self.logger.info(f"Camera selecionada e aberta: {camera_nome}")
        else:
            error_message = f"Camera '{camera_nome}' nao encontrada."
            self.logger.error(error_message)
            raise ValueError(error_message)

    def read_frame(self) -> cv2.Mat:
        """
        Lê o frame da webcam.

        Returns:
            cv2.Mat: O frame lido.

        Raises:
            SystemError: Se houver erro ao capturar o frame da câmera.
        """
        if self.is_camera_opened():
            ret, frame = self.cap.read()
        if not ret:
            error_message = "Erro ao capturar a imagem da camera."
            raise SystemError(error_message)
        return cv2.flip(frame, 1)

    def draw_hand(self, frame: cv2.Mat, results) -> cv2.Mat:
        """
        Desenha a mão detectada no frame.

        Args:
            frame (cv2.Mat): O frame atual.
            results: Os resultados da detecção de mão.

        Returns:
            cv2.Mat: O frame com a mão desenhada.

        Raises:
            ValueError: Se a mão detectada não for 'Left' ou 'Right'.
        """
        hand_landmarks_list = self.gesture_reader.get_hand_landmarks(results)
        if hand_landmarks_list:
            for hand_landmarks, handedness in zip(hand_landmarks_list, results.multi_handedness):
                self.gesture_reader.mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.gesture_reader.mp_hands.HAND_CONNECTIONS
                )

                x_left, y_top, x_right, y_bottom = self.calculate_hand_rectangle(frame, hand_landmarks)

                # Quadrado em volta da mão
                cv2.rectangle(frame, (x_left, y_top), (x_right, y_bottom), (0, 0, 0), 1)  

                mao_detectada = self.gesture_reader.classify_hand(handedness)

                if mao_detectada not in {LEFT, RIGHT}:
                    error_message = "'mao_detectada' deve ser 'Left' ou 'Right'."
                    self.logger.error(error_message)
                    raise ValueError(error_message)

                gesture_text = (
                    ConfigRouter().read_atribute("nome_gesto_esquerda") if mao_detectada == LEFT
                    else ConfigRouter().read_atribute("nome_gesto_direita")
                )

                text_size = cv2.getTextSize(gesture_text, FONT, 0.5, 1)[0]  # [width, height]
                text_width = max(text_size[0] + 6, x_right - x_left)  
                text_height = text_size[1] + 4  

                background_left = x_left + (x_right - x_left - text_width) // 2
                background_right = background_left + text_width
                background_top = y_top - text_height - 3
                background_bottom = y_top

                # Background do texto
                cv2.rectangle(frame, (background_left, background_top), (background_right, background_bottom), (0, 0, 0), -1)

                text_x = background_left + 3  
                text_y = background_bottom - 3  
                cv2.putText(frame, gesture_text, (text_x, text_y), FONT, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

        return frame
        
    def calculate_hand_rectangle(self, frame: cv2.Mat, hand_landmarks) -> tuple:
        """
        Calcula os limites do retângulo ao redor da mão detectada.

        Args:
            frame (cv2.Mat): O frame atual.
            hand_landmarks: Os landmarks da mão detectada.

        Returns:
            tuple: Coordenadas (x_left, y_top, x_right, y_bottom) do retângulo.
        """
        h, w, _ = frame.shape
        crop_padding = 0.15

        x_left = int(min([lm.x for lm in hand_landmarks.landmark]) * w)
        x_right = int(max([lm.x for lm in hand_landmarks.landmark]) * w)
        
        y_top = int(min([lm.y for lm in hand_landmarks.landmark]) * h) 
        y_bottom = int(max([lm.y for lm in hand_landmarks.landmark]) * h)

        return x_left, y_top, x_right, y_bottom 

    def show_frame(self, frame: cv2.Mat) -> None:
        """
        Exibe o frame capturado em uma janela.
        """
        cv2.imshow(WINDOW_NAME, frame)
        cv2.waitKey(1)

    def is_camera_opened(self) -> bool:
        """
        Verifica se a câmera está aberta.

        Returns:
            bool: True se a câmera estiver aberta, False caso contrário.
        """
        return self.cap is not None and self.cap.isOpened()
