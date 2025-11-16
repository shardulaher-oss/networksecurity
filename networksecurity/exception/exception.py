import sys
from networksecurity.logging import logger

class NetworkSecurityException(Exception):
    def _init_(self, error_message, error_details: sys):
        self.error_message = error_message
        _, _, exc_tb = error_details.exc_info()

        # Extract line number and file name where error happened
        self.lineno = exc_tb.tb_lineno
        self.file_name = exc_tb.tb_frame.f_code.co_filename

    def _str_(self):
        return (
            f"Error occurred in python script: [{self.file_name}] "
            f"line number [{self.lineno}] "
            f"error message: {str(self.error_message)}"
        )


if __name__== "__main__":
    try:
        logger.logging.info("Entered the try block")
        a = 1 / 0                    # This will generate an exception
        print("This will not be printed", a)

    except Exception as e:
        raise NetworkSecurityException(e,sys)