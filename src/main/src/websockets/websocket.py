from src.logger.logger import Logger
import websockets
import asyncio
import json

class WebSocket:
    def __init__(self, port: int):
        self.logger = Logger.configure_application_logger()
        self.data_logger = Logger.configure_json_data_logger()
        self.error_logger = Logger.configure_error_logger()
        self.port = port
        self.server = None  

    async def start(self) -> None:
        """
        Inicia o servidor WebSocket na porta especificada.
        """
        try:
            self.server = await websockets.serve(self.handler, "localhost", self.port)
            self.data_logger.info(f"Servidor Websocket aberto com sucesso na porta: {self.port}")
            await asyncio.Future()  
        except Exception as e:
            self.error_logger.error(f"Erro ao abrir o servidor local na porta {self.port}: {e}")

    async def stop(self) -> None:
        """
        Para o servidor WebSocket, fechando todas as conexões.
        """
        if self.server:
            self.server.close()  
            await self.server.wait_closed()  
            self.logger.info(f"Servidor WebSocket na porta {self.port} foi encerrado.")

    def handle_message(self, websocket, message) -> None:
        """
        Manipula mensagens recebidas pelo WebSocket. Deve ser implementado por subclasses.

        Args:
            websocket: WebSocket ativo para envio.
            message: Mensagem recebida.
        """
        pass

    async def send_data(self, websocket, data) -> None:
        """
        Envia dados em formato JSON para o cliente conectado.

        Args:
            websocket: WebSocket ativo para envio.
            data: Dados a serem enviados, no formato de um dicionário.
        """
        json_data = json.dumps(data)
        await websocket.send(json_data) 

    async def handler(self, websocket) -> None:
        """
        Manipula conexões e mensagens recebidas no servidor WebSocket.

        Args:
            websocket: Conexão WebSocket ativa.
            path: Caminho da requisição WebSocket (não utilizado).
        """
        async for message in websocket:
            try:
                message = json.loads(message)
                self.data_logger.info("RECEBI: %s", message)
                await self.handle_message(websocket, message)
            except json.JSONDecodeError:
                await websocket.send(json.dumps({"error": "JSON invalido."}))