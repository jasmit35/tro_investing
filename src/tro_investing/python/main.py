from traceback import print_exc

from python.models.application.tro_investing import TroInvesting

#=============================================================================
#  The main entry point for the application.
#  It creates an instance of the TroInvesting class, configures it, runs it and then deletes it.
#  If any uncaught exceptions occur, they are printed to the console.

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

