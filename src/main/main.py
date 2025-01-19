from src.mainloop.mainloop import MainLoop
from src.logger.logger import Logger
import asyncio
import sys

logger = Logger.configure_application_logger()
error_logger = Logger.configure_error_logger()

async def main(data_port: int, frames_port: int) -> None:
    """
    Inicializa o LibrasController com os servidores WebSocket.

    Args:
        data_port (int): Porta para o servidor WebSocket de dados.
        frames_port (int): Porta para o servidor WebSocket de frames.
    """
    logger.info("Iniciando LibrasController...")
    main_loop = MainLoop(data_port, frames_port)

    try:
        await main_loop.start()
    except Exception as e:
        error_message = f"LibrasController: {e}"
        logger.error(error_message)
        error_logger.error(error_message)
    finally:
        await main_loop.stop()
        logger.info("LibrasController encerrado.")

if __name__ == "__main__":
    port1 = int(sys.argv[1])  
    port2 = int(sys.argv[2])  
    
    asyncio.run(main(port1, port2))