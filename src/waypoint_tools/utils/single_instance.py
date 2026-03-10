"""Single instance application support using Windows mutex."""

import logging

import win32api
import win32event
import winerror

logger = logging.getLogger(__name__)


class SingleInstance:
    """Ensures only one instance of the application runs at a time."""
    
    def __init__(self, mutex_name: str) -> None:
        """
        Initialize single instance checker.
        
        Args:
            mutex_name: Unique name for the application mutex
        """
        self.mutex_name = mutex_name
        self.mutex = None
        self._acquired = False
    
    def try_acquire(self) -> bool:
        """
        Try to acquire the single instance mutex.
        
        Returns:
            True if this is the first instance, False if another instance exists
        """
        try:
            self.mutex = win32event.CreateMutex(None, False, self.mutex_name)
            last_error = win32api.GetLastError()
            
            if last_error == winerror.ERROR_ALREADY_EXISTS:
                logger.info("Another instance is already running")
                self._acquired = False
                return False
            
            self._acquired = True
            logger.info("Successfully acquired single instance lock")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create mutex: {e}")
            self._acquired = False
            return False
    
    def release(self) -> None:
        """Release the mutex if acquired."""
        if self._acquired and self.mutex:
            try:
                win32api.CloseHandle(self.mutex)
                logger.info("Released single instance lock")
            except Exception as e:
                logger.error(f"Failed to release mutex: {e}")
            finally:
                self._acquired = False
                self.mutex = None
    
    def __enter__(self) -> "SingleInstance":
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.release()
