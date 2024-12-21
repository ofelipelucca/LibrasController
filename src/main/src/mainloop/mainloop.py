from src.data_websocket.data_websocket_server import PyWebSocketServer
from src.logger.logger import Logger
import threading
import asyncio

class MainLoop:
    def __init__(self, data_port, frames_port) -> None:
        self.logger = Logger.configure_application_logger()
        self.stop_flag = threading.Event()  

        self.data_server = PyWebSocketServer(port=data_port)
        self.data_server_thread = None
        self.data_server_loop = None

        self.frames_server = PyWebSocketServer(port=frames_port)
        self.frames_server_thread = None
        self.frames_server_loop = None

    def start(self) -> None:
        """
        Inicia os servidores WebSocket em threads separadas.
        """
        try:
            self.data_server_thread = threading.Thread(target=self.start_server, 
                                                       args=(self.data_server, "data_server_loop"))
            self.data_server_thread.start()

            self.frames_server_thread = threading.Thread(target=self.start_server, 
                                                       args=(self.frames_server, "frames_server_loop"))
            self.frames_server_thread.start()

        except Exception as e:
            error_message = f"Erro durante a execução dos servidores WebSocket: {e}"
            self.logger.error(error_message)
            raise RuntimeError(error_message)

    def stop(self) -> None:
        """
        Para os servidores WebSocket e espera que as threads sejam encerradas.
        """
        self.logger.info("Parando o MainLoop e servidores...")

        self.stop_flag.set()

        self.logger.info("Esperando servidores pararem...")
        
        if self.data_server_thread:
            self.logger.info("Esperando servidor de data...")
            self.data_server_thread.join()

        if self.frames_server_thread:
            self.logger.info("Esperando servidor de frames...")
            self.frames_server_thread.join()

        self.logger.info("MainLoop e servidores parados.")

    def start_server(self, server: PyWebSocketServer, server_loop_var_name: str):
        """
        Método para iniciar um servidor WebSocket em uma thread separada.
        O server_loop_var_name é o nome da variável do loop que será atualizada.
        """
        loop = asyncio.new_event_loop()
        setattr(self, server_loop_var_name, loop)  
        asyncio.set_event_loop(loop)

        try:
            self.logger.info(f"{server_loop_var_name} iniciando na porta {server.port}...")
            loop.run_until_complete(server.start())  

            while not self.stop_flag.is_set():
                loop.run_forever()  
        except Exception as e:
            error_message = f"Erro no servidor WebSocket ({server.__class__.__name__}): {e}"
            self.logger.error(error_message)
            raise RuntimeError(error_message)
        finally:
            loop.close()
            
    def __del__(self):
        """Método chamado ao destruir a instância da classe."""
        self.stop()