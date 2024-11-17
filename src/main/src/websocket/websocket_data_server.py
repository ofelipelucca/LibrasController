from src.data.gestures.data_libras_gestures import DataLibrasGestures
from src.data.gestures.data_custom_gestures import DataCustomGestures 
from src.data.binds.data_binds_salvas import DataBindsSalvas
from src.data.configs.config_router import ConfigRouter
from src.camera.camera_manager import Camera
from src.logger.logger import Logger
import websockets
import asyncio
import base64
import json
import cv2

camera_detection = Camera()

logger = Logger.configure_application_logger()
data_logger = Logger.configure_json_data_logger()
error_logger = Logger.configure_error_logger()

class PyWebSocketServer:
    def __init__(self, port):
        self.port = port
        self.data_gestos = self.load_data_gestos()
        self.data_binds = self.load_data_binds()
        self.config = ConfigRouter()

    async def handle_message(self, websocket, message):
        if isinstance(message, dict):
            if "ping" in message:
                await self.send_data(websocket, {"pong": True})
                return

            if "startDetection" in message:
                message = "Iniciando o processo de deteccao."
                logger.info(message)
                await camera_detection.start()
                await self.send_data(websocket, {"status": "success", "message": message})
                return

            if "getAllBinds" in message:
                data_logger.info("Retornando bids")
                await self.send_data(websocket, {"allBinds": self.data_binds})
                return

            if "getGesto" in message:
                nome_gesto = message["getGesto"]
                gesto = self.data_gestos.get(nome_gesto, None)
                await self.send_data(websocket, {"gesto": gesto})
                return

            if "saveGesto" in message:
                novo_gesto = message["saveGesto"]
                sobreescrever = message.get("sobreescrever", True)
                await self.send_data(websocket, {"status": "success", "message": "Gesto salvo com sucesso."})
                return

            if "setCamera" in message:
                camera_name = message["setCamera"]
                self.config.atualizar_atributo("camera_selecionada", camera_name)
                await self.send_data(websocket, {"status": "success", "message": f"Camera '{camera_name}' atualizada com sucesso."})
                return

            if "getCamera" in message:
                camera = self.config.ler_atributo("camera_selecionada")
                await self.send_data(websocket, {"camera_selecionada": camera})
                return

            if "getCamerasDisponiveis" in message:
                cameras = camera_detection.listar_cameras()
                await self.send_data(websocket, {"cameras_disponiveis": cameras})
                return
            
            if "getFrame" in message: 
                frame = camera_detection.frame
                if frame is not None and frame.size > 0:
                    _, buffer = cv2.imencode('.jpg', frame)
                    frame_base64 = base64.b64encode(buffer).decode('utf-8')
                    await self.send_data(websocket, {"frame": frame_base64})
                else:
                    await self.send_data(websocket, {"error": "Nao foi possivel capturar o frame."})
                return

    async def send_data(self, websocket, data):
        json_data = json.dumps(data)
        await websocket.send(json_data)

    async def handler(self, websocket, path):
        async for message in websocket:
            try:
                message = json.loads(message)
                await self.handle_message(websocket, message)
            except json.JSONDecodeError:
                await websocket.send(json.dumps({"error": "JSON invalido."}))

    async def start(self):
        async with websockets.serve(self.handler, "localhost", self.port):
            data_logger.info(f"Servidor DataWebsocket aberto com sucesso na porta: {self.port}")
            await asyncio.Future()  
        error_logger.error(f"Erro ao abrir o servidor local na porta: {self.port}")

    def load_data_gestos(self):
        gestos_custom = DataCustomGestures().obter_gestos()
        gestos_libras = DataLibrasGestures().obter_gestos()
        return gestos_libras | gestos_custom

    def load_data_binds(self):
        data_libras = DataBindsSalvas().get_all_binds()
        return data_libras
