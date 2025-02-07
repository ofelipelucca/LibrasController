import os
import cv2
import time
import base64
import asyncio
import threading
from src.logger.logger import Logger
from src.camera.camera_manager import Camera
from src.websockets.frames_websocket.frames_websocket import FramesWebsocketServer

logger = Logger().configure_application_logger()
data_logger = Logger().configure_json_data_logger()
error_logger = Logger().configure_error_logger()

class CameraStream:
    def __init__(self, frames_server: FramesWebsocketServer):
        self.frames_sender = frames_server
        self.camera_capture = Camera()
        self.stop_flag = threading.Event()

    async def start_stream(self) -> None:
        """Inicia a captura de frames da câmera."""
        logger.info("Tentando iniciar o stream da camera.")
        self.stop_flag.clear()
        if self.camera_capture:
            await self.camera_capture.start()
            while self.__get_cv2_frame() is None:
                time.sleep(0.25)
            data_logger.info("Primeiro frame encontrado.")
            asyncio.create_task(self.__stream_frames())

    async def stop_stream(self) -> None:
        """Encerra a captura da câmera."""
        self.stop_flag.set()
        self.camera_capture.stop()
        logger.info("Parando a captura de frames.")

    async def __stream_frames(self) -> None:
        """Loop de captura e envio dos frames"""
        loop = asyncio.get_event_loop()
        while not self.stop_flag.is_set():
            frame = await loop.run_in_executor(None, self.get_frame)
            if frame == "": continue
            await self.frames_sender.send_frame(frame)
            time.sleep(0.0001)

    def get_frame(self) -> str:
        """Retorna o frame atual convertido para jpeg"""
        frame = self.__get_cv2_frame()
        if frame is not None:
            jpeg_frame = self.__convert_cv2_mat_to_string(frame)
            return jpeg_frame

        current_dir = os.path.dirname(os.path.abspath(__file__))
        png_placeholder_path = os.path.abspath(os.path.join(current_dir, '../../../../public/assets/camera_off.png'))

        if not os.path.exists(png_placeholder_path):
            raise FileNotFoundError(f"Frame '{png_placeholder_path}' nao encontrado!")

        png_placeholder_frame = cv2.imread(png_placeholder_path)
        if png_placeholder_frame is not None:
            png_placeholder = self.__convert_cv2_mat_to_string(png_placeholder_frame)
        return png_placeholder

    def __get_cv2_frame(self) -> cv2.Mat:
        """
        Obtém um frame capturado e o converte.
        Returns: o frame (cv2.Mat) capturado se estiver disponível, caso contrário, retorna None.
        """
        return self.camera_capture.frame if self.camera_capture.frame is not None else None

    def __convert_cv2_mat_to_string(self, frame: cv2.Mat) -> str:
        """
        Converte um frame (cv2.Mat) para string (base64).
        """
        try:
            if frame is None: 
                raise TypeError("O frame deve estar no formato cv2.Mat")
            _, buffer = cv2.imencode('.jpg', frame)
            frame_base64 = base64.b64encode(buffer).decode('utf-8')
            return frame_base64
        except Exception as e:
            error_logger.error(f"Falha na conversao de frame para JPEG: {e}")
            return ""
