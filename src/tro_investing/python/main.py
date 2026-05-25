from traceback import print_exc

from python.services.tro_investing import TroInvesting

if __name__ == "__main__":
    try:
        this_app = TroInvesting()
        this_app.configure()
        return_code = this_app.run()
        del this_app
        exit(return_code)

    except Exception as e:
        print(f"Following uncaught exception occured. {e}")
        print_exc()

