from content import NumericalContent,TextContent
from formula import FormulaContent
from file_manager import FileManager
from cell import Cell
import re

class UserInterface:
    def __init__(self, spreadsheet: 'Spreadsheet'):
        self.spreadsheet = spreadsheet

    def display_menu(self):
        print("Spreadsheet Menu")
        print("1. Add/Update Cell")
        print("2. Display Cell Value")
        print("3. Save Spreadsheet")
        print("4. Load Spreadsheet")
        print("5. Exit")

    def run(self):
        while True:
            self.display_menu()
            choice = input("Select an option: ")
            if choice == "1":
                self.add_update_cell()
            elif choice == "2":
                self.display_cell_value()
            elif choice == "3":
                self.save_spreadsheet()
            elif choice == "4":
                self.load_spreadsheet()
            elif choice == "5":
                break
            else:
                print("Invalid choice. Please try again.")

    def add_update_cell(self):
        coord = input("Enter cell coordinate (e.g., A1): ")
        content = input("Enter cell content: ")
        col, row = coord[0], int(coord[1:])
        if content.startswith('='):
            cell_content = FormulaContent(content)
        elif content.isdigit():
            cell_content = NumericalContent(float(content))
        else:
            cell_content = TextContent(content)
        cell = Cell((col, row), cell_content)
        self.spreadsheet.add_cell((col, row), cell)
        self.spreadsheet.update_graph()
        if self.spreadsheet.detect_circular_dependencies():
            print("there is a circular dependence")

    def display_cell_value(self):
        coord = input("Enter cell coordinate (e.g., A1): ")
        coincidence = re.match(r"([A-Z]+)(\d+)",coord)
        if coincidence:
            col = coincidence.group(1)
            row = int(coincidence.group(2))
        else:
            raise ValueError(f"Celda no válida: {coord}")
        col, row = coord[0], int(coord[1:])
        cell = self.spreadsheet.get_cell((col, row))
        if cell:
            print(f"Value of {coord}: {cell.get_value(self.spreadsheet)}")
        else:
            print(f"Cell {coord} not found.")

    def save_spreadsheet(self):
        file_path = input("Enter file path to save: ")
        FileManager(file_path).save_spreadsheet(self.spreadsheet)
        print("Spreadsheet saved.")

    def load_spreadsheet(self):
        file_path = input("Enter file path to load: ")
        self.spreadsheet = FileManager(file_path).load_spreadsheet()
        print("Spreadsheet loaded.")
