from utils.Logger import Logger
from AppManager import AppManager


if __name__ == '__main__':
    logger = Logger()
    app_manager = AppManager(logger)
    try:
        app_manager.initialize_vpc_and_aws_resources()
        logger.info(f"App Link: {app_manager.server_link}")
    except Exception as e:
        logger.error(e)
        # logger.error(traceback.print_exc())
    finally:
        input("Press any key to cleanup resources..")
        app_manager.clean_resources()
