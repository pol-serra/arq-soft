from content import NumericalContent, TextContent
from formula import FormulaContent
from file_manager import FileManager
from spreadsheet import Spreadsheet
from cell import Cell
import re
from entities.circular_dependency_exception import CircularDependencyException
from entities.bad_coordinate_exception import BadCoordinateException

class UserInterface:
    def __init__(self, spreadsheet: 'Spreadsheet'):
        self.spreadsheet = spreadsheet

    def display_menu(self):
        print("Spreadsheet Menu")
        print("RF <text file pathname> - Read commands from File")
        print("C - Create a New Spreadsheet")
        print("E <cell coordinate> <new cell content> - Edit a cell")
        print("L <SV2 file pathname> - Load a Spreadsheet from a file")
        print("S <SV2 file pathname> - Save the Spreadsheet to a file")
        print("X - Exit")

    def run(self):
        while True:
            self.display_menu()
            choice = input("Enter command: ").strip()
            if choice.startswith("RF"):
                self.read_commands_from_file(choice.split()[1])
            elif choice == "C":
                self.create_new_spreadsheet()
            elif choice.startswith("E"):
                parts = choice.split(maxsplit=2)
                if len(parts) == 3:
                    self.edit_cell(parts[1], parts[2])
                else:
                    print("Invalid command format. Use E <cell coordinate> <new cell content>")
            elif choice.startswith("L"):
                self.load_spreadsheet(choice.split()[1])
            elif choice.startswith("S"):
                self.save_spreadsheet(choice.split()[1])
            elif choice == "X":
                break
            else:
                print("Invalid command. Please try again.")

    def read_commands_from_file(self, filepath):
        try:
            with open(filepath, 'r') as file:
                for line in file:
                        self.execute_command(line.strip())
        except FileNotFoundError:
            print(f"File not found: {filepath}")

    def execute_command(self, command):
        if command.startswith("C"):
            self.create_new_spreadsheet()
        elif command.startswith("E"):
            parts = command.split(maxsplit=2)
            if len(parts) == 3:
                self.edit_cell(parts[1], parts[2])
            else:
                print("Invalid command format. Use E <cell coordinate> <new cell content>")
        elif command.startswith("L"):
            self.load_spreadsheet(command.split()[1])
        elif command.startswith("S"):
            self.save_spreadsheet(command.split()[1])
        else:
            print("Invalid command in file. Skipping.")

    def create_new_spreadsheet(self):
        self.spreadsheet = Spreadsheet()
        self.spreadsheet.print_spreadsheet()
        print("New spreadsheet created.")

    def edit_cell(self, coord, content):
        col, row = self.parse_coordinate(coord)
        if content.startswith('='):
            cell_content = FormulaContent(content[1:])
        elif content.isdigit():
            cell_content = NumericalContent(float(content))
        else:
            cell_content = TextContent(content)
        cell = Cell((col, row), cell_content)
        try:
            if self.spreadsheet.can_add_cell_without_cycle((col, row), cell):
                self.spreadsheet.add_cell((col, row), cell)
                self.spreadsheet.update_graph()
                if self.spreadsheet.detect_circular_dependencies():
                    raise CircularDependencyException("Circular dependency detected.")
                self.spreadsheet.print_spreadsheet()
            else:
                raise CircularDependencyException("New cell incurs in a circular dependency, so it has not been updated.")
        except CircularDependencyException as e:
            print(e)

    def load_spreadsheet(self, filepath):
        try:
            self.spreadsheet = FileManager(filepath).load_spreadsheet()
            self.spreadsheet.print_spreadsheet()
            print("Spreadsheet loaded.")
        except FileNotFoundError:
            print(f"File not found: {filepath}")

    def save_spreadsheet(self, filepath):
        FileManager(filepath).save_spreadsheet(self.spreadsheet)
        print("Spreadsheet saved.")

    def parse_coordinate(self, coord):
        match = re.match(r"([A-Z]+)(\d+)", coord)
        if match:
            col = match.group(1)
            row = int(match.group(2))
            return col, row
        else:
            raise BadCoordinateException(f"Invalid cell coordinate: {coord}")
