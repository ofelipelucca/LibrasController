from src.websockets.websocket import WebSocket

class FramesWebsocketServer(WebSocket):
    def __init__(self, port: int):
        super().__init__(port)
        self.connections = set()

    async def handler(self, websocket) -> None:
        """
        Este método é executado quando uma nova conexão é estabelecida.
        Ele gerencia as conexões e garante que o envio contínuo de frames 
        funcione corretamente.
        """
        self.connections.add(websocket)
        self.data_logger.info("Nova conexao WebSocket estabelecida.")
        
        try:
            async for message in websocket:
                pass 
        except Exception as e:
            self.error_logger.error(f"Erro na conexao WebSocket: {e}")
        finally:
            self.connections.remove(websocket)
            self.logger.info("Conexao WebSocket encerrada.")

    async def send_frame(self, frame: str) -> None:
        """
        Envia um frame para todas as conexões ativas.
        """
        if self.connections:
            to_remove = []
            for websocket in self.connections:
                try:
                    await self.send_data(websocket, {"frame": frame})
                except Exception as e:
                    self.error_logger.error(f"Falha ao enviar frame: {e}")
                    to_remove.append(websocket)
            
            for websocket in to_remove:
                self.connections.discard(websocket)
        else:
            self.data_logger.warning("Nenhuma conexao ativa para enviar frames.")