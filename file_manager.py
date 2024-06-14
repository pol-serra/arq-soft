from spreadsheet import Spreadsheet
from cell import Cell
from content import TextContent, NumericalContent
from formula import FormulaContent
import csv
import re

class FileManager:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def save_spreadsheet(self, spreadsheet: Spreadsheet):       
        with open(self.file_path, 'w') as file:
            for coordinate, cell in spreadsheet.cells.items():
                file.write(f"{coordinate[0]}{coordinate[1]}={cell.get_value(spreadsheet)}\n")

    # def load_spreadsheet(self) -> Spreadsheet:
    #     spreadsheet = Spreadsheet()
    #     with open(self.file_path, 'r') as file:
    #         reader = csv.reader(file, delimiter=';')
    #         for row_idx, row in enumerate(reader, start=1):
    #             for col_idx, value in enumerate(row, start=0):        
    #                 if value.startswith('='):
    #                     content = FormulaContent(value[1:])
    #                     dependencies= content.get_dependencies()
    #                 elif re.match(r'^\d+(\.\d+)?$', value):
    #                     content = NumericalContent(float(value))
    #                 else:
    #                     content = TextContent(value)
    #                 col_letter = ''
    #                 while col_idx >= 0:
    #                     col_idx, remainder = divmod(col_idx, 26)
    #                     col_letter = chr(65 + remainder) + col_letter
    #                     col_idx -= 1
    #                 cell = Cell((col_letter,row_idx), content)
    #                 spreadsheet.add_cell((col_letter,row_idx), cell)
    def split_row(self, row):
        """Helper method to correctly split a row by semicolons, ignoring semicolons within functions"""
        parts = []
        current = ""
        paren_count = 0

        for char in row:
            if char == ';' and paren_count == 0:
                parts.append(current)
                current = ""
            else:
                if char == '(':
                    paren_count += 1
                elif char == ')':
                    paren_count -= 1
                current += char

        parts.append(current)
        return parts

    def load_spreadsheet(self) -> Spreadsheet:
        spreadsheet = Spreadsheet()
        with open(self.file_path, 'r') as file:
            for row_idx, row in enumerate(file, start=1):
                row = row.strip()
                cells = self.split_row(row)
                for col_idx, value in enumerate(cells, start=0):
                    dependencies = []
                    if value.startswith('='):
                        formula = value[1:]
                        content = FormulaContent(formula)
                        dependencies = content.get_dependencies()
                    elif re.match(r'^\d+(\.\d+)?$', value):
                        content = NumericalContent(float(value))
                    else:
                        content = TextContent(value)

                    col_letter = ''
                    col_idx_copy = col_idx
                    while col_idx_copy >= 0:
                        col_idx_copy, remainder = divmod(col_idx_copy, 26)
                        col_letter = chr(65 + remainder) + col_letter
                        col_idx_copy -= 1

                    cell = Cell((col_letter, row_idx), content)
                    spreadsheet.add_cell((col_letter, row_idx), cell)

                        
        return spreadsheet
