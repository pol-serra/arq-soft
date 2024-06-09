from spreadsheet import Spreadsheet
from user_interface import UserInterface

def main():
    spreadsheet = Spreadsheet()
    ui = UserInterface(spreadsheet)
    ui.run()

if __name__ == "__main__":
    main()
