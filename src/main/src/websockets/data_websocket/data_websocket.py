from src.websockets.frames_websocket.frames_websocket import FramesWebsocketServer
from src.data.gestures.data_libras_gestures import DataLibrasGestures
from src.data.gestures.data_custom_gestures import DataCustomGestures 
from src.data.binds.data_binds_salvas import DataBindsSalvas
from src.data.configs.config_router import ConfigRouter
from src.camera.camera_stream import CameraStream
from src.websockets.websocket import WebSocket
from src.camera.camera_manager import Camera

class DataWebsocketServer(WebSocket):
    def __init__(self, port: int, frames_server: FramesWebsocketServer):
        super().__init__(port)
        self.data_gestos = self.load_data_gestos() # Nome dos gestos
        self.data_binds = self.load_data_binds() # Atributos dos gestos (bind, toggle, tempo pressionado, customizable)
        self.config = ConfigRouter()
        self.camera_stream = CameraStream(frames_server) 

    def load_data_gestos(self) -> dict:
        gestos_custom = DataCustomGestures().get_gestos()
        gestos_libras = DataLibrasGestures().get_gestos()
        return gestos_libras | gestos_custom

    def load_data_binds(self) -> dict:
        data_libras = DataBindsSalvas().get_all_binds()
        return data_libras

    async def handle_message(self, websocket, message) -> None:
        try:
            if isinstance(message, dict):
                if "ping" in message:
                    await self.send_data(websocket, {"pong": True})
                    return

                if "START_DETECTION" in message:
                    msg = "Iniciando o processo de deteccao."
                    if self.camera_stream is None: 
                        self.error_logger.error("O socket de stream nao esta aberto no momento.")
                        return
                    await self.camera_stream.start_stream()
                    self.logger.info(msg)
                    await self.send_data(websocket, {"status": "success", "message": msg})
                    return

                if "STOP_DETECTION" in message:
                    msg = "Encerrando o processo de deteccao."
                    if self.camera_stream is None:
                        self.error_logger.error("O socket de stream nao esta aberto no momento.")
                        return
                    await self.camera_stream.stop_stream()
                    self.logger.info(msg)
                    await self.send_data(websocket, {"status": "success", "message": msg})
                    return

                if "START_CROP_HAND_MODE" in message:
                    msg = "Iniciando o modo de crop_hand."
                    self.logger.info(msg)
                    if not self.camera_stream.camera_capture:
                        await self.send_data(websocket, {"error": "Nao existe um processo de deteccao ativo no momento, envie 'START_DETECTION' antes de fazer esta requisição."})    
                        return
                    self.camera_stream.camera_capture.start_crop_hand_mode()
                    await self.send_data(websocket, {"status": "success", "message": msg})
                    return
                
                if "STOP_CROP_HAND_MODE" in message:
                    msg = "Encerrando o modo de crop_hand."
                    self.logger.info(msg)
                    if not self.camera_stream.camera_capture:
                        await self.send_data(websocket, {"error": "Nao existe um processo de deteccao ativo no momento."})    
                        return
                    self.camera_stream.camera_capture.stop_crop_hand_mode()
                    await self.send_data(websocket, {"status": "success", "message": msg})  
                    return

                if "GET_ALL_GESTOS" in message:
                    self.data_logger.info("Retornando todos os gestos.")
                    await self.send_data(websocket, {"allGestos": self.data_binds})
                    return

                if "GET_GESTO_BY_NAME" in message:
                    nome_gesto = message["GET_GESTO_BY_NAME"]
                    self.data_logger.info(f"Retornando o gesto: {nome_gesto}")
                    gesto = self.data_gestos.get(nome_gesto, None)
                    await self.send_data(websocket, {"gesto": gesto})
                    return
                
                if "GET_CUSTOMIZABLE_STATE" in message:
                    nome_gesto = message["GET_CUSTOMIZABLE_STATE"]
                    self.data_logger.info(f"Retornando o estado 'customizable' do gesto: {nome_gesto}")
                    is_custom = DataBindsSalvas().get_customizable(nome_gesto)
                    await self.send_data(websocket, {"customizableState": is_custom})
                    return

                if "SAVE_GESTO" in message:
                    novo_gesto = message["SAVE_GESTO"]
                    sobreescrever = message.get("sobreescrever", False)
                    
                    nome = novo_gesto["nome"]
                    bind = novo_gesto["bind"]
                    toggle = novo_gesto["modoToggle"]
                    tempo = novo_gesto["tempoPressionado"]

                    DataBindsSalvas().add_new_bind(nome, bind, tempo, toggle, sobreescrever)

                    msg = f"Gesto '{nome}' recebido com sucesso: bind: {bind}; toggle: {toggle}; tempo: {tempo}; sobreescrever: {sobreescrever}"
                    self.data_logger.info(msg)

                    self.data_binds = self.load_data_binds()
                    await self.send_data(websocket, {"status": "success", "message": msg})
                    return

                if "SET_CAMERA" in message:
                    camera_name = message["SET_CAMERA"]
                    msg = f"Camera '{camera_name}' atualizada com sucesso."
                    self.data_logger.info(msg)
                    self.config.update_atribute("camera_selecionada", camera_name)
                    await self.send_data(websocket, {"status": "success", "message": msg})
                    return

                if "GET_CAMERA" in message:
                    camera = self.config.read_atribute("camera_selecionada")
                    self.data_logger.info(f"Retornando o nome da camera selecionada:  {camera}")
                    await self.send_data(websocket, {"cameraSelecionada": camera})
                    return

                if "GET_CAMERAS_DISPONIVEIS" in message:
                    self.data_logger.info("Retornando cameras disponiveis.")
                    camera_manager = Camera()
                    cameras = camera_manager.list_cameras()
                    if cameras: await self.send_data(websocket, {"camerasDisponiveis": cameras})
                    else: await self.send_data(websocket, {"error": "Nao foi possivel retornar as cameras disponiveis."})
                    return
                
        except Exception as e:
            msg = "Erro na conexao do WebSocket: ", e
            self.data_logger.error(msg)
            self.error_logger.error(msg)
            raise ConnectionError(msg)