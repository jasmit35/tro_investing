from traceback import print_exc

from config import configure_app

from python.services.tro_investing import TroInvesting

if __name__ == "__main__":
    try:
        this_app = TroInvesting()

        configure_app(this_app)
        
        return_code = this_app.run()
        del this_app

        exit(return_code)

    except Exception as e:
        print(f"Following uncaught exception occured. {e}")
        print_exc()

