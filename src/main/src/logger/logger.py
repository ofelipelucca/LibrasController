import os
import logging
from logging.handlers import RotatingFileHandler

class Logger:
    """
    Classe para configuração e gerenciamento de loggers com rotação de arquivos.
    
    A classe `Logger` fornece métodos estáticos para criar e configurar loggers para diferentes propósitos,
    como logs gerais da aplicação, entradas e erros. Garante que os diretórios necessários para os arquivos de log
    existam e configura os loggers com os níveis e formatos apropriados, incluindo rotação de arquivos de log.
    """

    @staticmethod
    def _ensure_log_dir_exists() -> None:
        """
        Garante que o diretório para arquivos de log exista.
        
        Se o diretório não existir, ele será criado.
        """
        log_dir = 'src/data/logs'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

    @staticmethod
    def _configure_logger(name: str, file_name: str) -> logging.Logger:
        """
        Configura um logger para o nome e arquivo especificados, com rotação de arquivos.
        
        Args:
            name (str): O nome do logger.
            file_name (str): O nome do arquivo de log.
        
        Returns:
            logging.Logger: O logger configurado.
        """
        Logger._ensure_log_dir_exists()
        
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        
        if not logger.hasHandlers():
            # Configuração do handler de rotação de arquivos
            file_handler = RotatingFileHandler(
                f'src/data/logs/{file_name}',
                maxBytes=5 * 1024 * 1024,  # 5 MB por arquivo
                backupCount=3  # Mantém 3 arquivos antigos
            )
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(message)s')
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        return logger

    @staticmethod
    def configure_application_logger() -> logging.Logger:
        """
        Configura o logger principal da aplicação.
        
        Returns:
            logging.Logger: O logger configurado para a aplicação.
        """
        return Logger._configure_logger('application', 'application.log')

    @staticmethod
    def configure_input_logger() -> logging.Logger:
        """
        Configura o logger para logs de entradas.
        
        Returns:
            logging.Logger: O logger configurado para entradas.
        """
        return Logger._configure_logger('input', 'inputs.log')

    @staticmethod
    def configure_gestures_logger() -> logging.Logger:
        """
        Configura o logger para logs de gestos.
        
        Returns:
            logging.Logger: O logger configurado para gestos.
        """
        return Logger._configure_logger('gestures', 'gestures.log')

    @staticmethod
    def configure_json_data_logger() -> logging.Logger:
        """
        Configura o logger para logs de data files.
        
        Returns:
            logging.Logger: O logger configurado para data files.
        """
        return Logger._configure_logger('data', 'data.log')

    @staticmethod
    def configure_error_logger() -> logging.Logger:
        """
        Configura o logger para logs de erros.
        
        Returns:
            logging.Logger: O logger configurado para erros.
        """
        return Logger._configure_logger('error', 'errors.log')
