from traceback import print_exc

from config import configure_app

from python.services.tro_investing import TroInvesting

if __name__ == "__main__":

    #  99 is the default return code for an uncaught exception. If the app runs successfully, it will set this to 0.
    return_code: int = 99
    
    try:
        this_app = TroInvesting()
        return_code = 98
        configure_app(this_app)
        return_code = 97
        return_code = this_app.run()
    except Exception as e:
        this_app._logger.error(f"Uncaught exception while running app: {e}")
        print_exc()

    exit(return_code)