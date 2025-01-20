from src.websockets.data_websocket.data_websocket import DataWebsocketServer
from src.websockets.frames_websocket.frames_websocket import FramesWebsocketServer 
from src.logger.logger import Logger
import asyncio

class MainLoop:
    def __init__(self, data_port: int, frames_port: int) -> None:
        """
        Inicializa o MainLoop com os servidores WebSocket de dados e frames.

        Args:
            data_port (int): Porta para o servidor WebSocket de dados.
            frames_port (int): Porta para o servidor WebSocket de frames.
        """
        self.logger = Logger.configure_application_logger()
        self.stop_flag = asyncio.Event()  

        self.frames_server = FramesWebsocketServer(port=frames_port)
        self.data_server = DataWebsocketServer(port=data_port, frames_server=self.frames_server)

    async def start(self) -> None:
        """
        Inicia os servidores WebSocket utilizando asyncio.gather.
        """
        try:
            self.logger.info("Iniciando os servidores WebSocket...")

            await asyncio.gather(
                self.frames_server.start(),
                self.data_server.start(),
            )
        except Exception as e:
            error_message = f"Erro durante a execução dos servidores WebSocket: {e}"
            self.logger.error(error_message)
            raise RuntimeError(error_message)

    async def stop(self) -> None:
        """
        Para os servidores WebSocket de forma assíncrona.
        """
        self.logger.info("Parando o MainLoop e servidores...")

        self.stop_flag.set()

        await self.frames_server.stop()
        await self.data_server.stop()

        self.logger.info("MainLoop e servidores parados.")