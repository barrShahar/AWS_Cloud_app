import inspect
import os


def _get_line_info():
    frame = inspect.currentframe().f_back.f_back
    file_name = os.path.basename(frame.f_code.co_filename)
    line_number = frame.f_lineno
    return f"{file_name}, Line {line_number}"


class Logger:
    def __init__(self, output_function=print):
        self.output_function = output_function

    def log(self, msg):
        line_info = _get_line_info()
        self.output_function(f"**LOG:**({line_info}) {msg}")

    def debug(self, msg):
        line_info = _get_line_info()
        self.output_function(f"**DEBUG:**({line_info}) {msg}")

    def info(self, msg):
        line_info = _get_line_info()
        self.output_function(f"**INFO:**({line_info}) {msg}")

    def warning(self, msg):
        line_info = _get_line_info()
        self.output_function(f"**WARNING:**({line_info}) {msg}")

    def error(self, msg):
        line_info = _get_line_info()
        self.output_function(f"**ERROR:**({line_info}) {msg}")


# Example usage:
def custom_output(message):
    # Replace with your custom logic
    print(f"Custom output: {message}")


if __name__ == "__main__":
    # Create a log instance with default print output
    logger = Logger()

    # Log a message using the default output function
    logger.log("This message will be printed")

    # Create a log instance with custom output function
    custom_logger = Logger(output_function=custom_output)

    # Log a message using the custom output function
    custom_logger.log("This message will be sent to custom output")
