from abc import ABC, abstractmethod
import ctypes

class Device(ABC):
    if ctypes.sizeof(ctypes.c_void_p) == 8:
        ULONG_PTR = ctypes.c_uint64
    else:
        ULONG_PTR = ctypes.c_uint32

    @abstractmethod
    def __send_input(self, inputs) -> None:
        """
        Envia os eventos de entrada para o sistema. Deve ser implementado nas subclasses.

        Args:
            input (INPUT): O evento INPUT a ser enviado.
        """
        pass
    
    @abstractmethod
    def __create_input(key: str, event_type: str) -> None:
        """
        Cria e configura o input para enviar corretamente para o sistema por meio da Windows API.
        
        Args:
            key (str): A tecla a ser simulada.
            event_type (str): Tipo de evento.
        """
        pass

    @abstractmethod
    def up(key: str) -> None:
        """
        Envia o evento de pressionar a tecla.

        Args:
            key (str): A tecla a ser liberada.
        """
        pass

    @abstractmethod
    def down(key: str) -> None:
        """
        Envia o evento de liberar a tecla.
        
        Args:
            key (str): A tecla a ser pressionada.
        """
        pass