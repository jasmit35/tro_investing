from traceback import print_exc

from config import configure_app

from python.services.tro_investing import TroInvesting

if __name__ == "__main__":
    return_code = 0

    try:
        this_app = TroInvesting()
        configure_app(this_app)
        return_code = this_app.run()

    except Exception as e:
        this_app._logger.error(f"Uncaught exception while running app: {e}")
        print_exc()

    exit(return_code)
