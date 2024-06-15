from spreadsheet import Spreadsheet
from cell import Cell
from content import TextContent, NumericalContent
from formula import FormulaContent
import csv
import re

class FileManager:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def col_to_num(self,column):
        """Convierte una letra o cadena de letras de columna en su número correspondiente."""
        base = ord('A') - 1  # Valor base para las letras 'A' = 1, 'B' = 2, ..., 'Z' = 26
        column_number = 0
        
        for char in column:
            if 'A' <= char <= 'Z':
                column_number = column_number * 26 + (ord(char) - base)
        
        return column_number
    
    def num_to_col(self,num):
        """Convierte un número entero en su equivalente en letras de columna de Excel."""
        result = ""
        base = ord('A')
        
        while num > 0:
            remainder = (num - 1) % 26  # Obtener el residuo
            result = chr(base + remainder) + result  # Convertir el residuo en letra y concatenar al resultado
            num = (num - 1) // 26  # Obtener el siguiente número para dividir
            
        return result


    def save_spreadsheet(self, spreadsheet: Spreadsheet):       
        with open(self.file_path, 'w') as file:
            rows_with_data = set()  # Conjunto para almacenar las filas que contienen datos

            # Obtener todas las filas y columnas que contienen datos
            rows_with_data = sorted(set(coord[1] for coord in spreadsheet.cells.keys()))

            # Iterar sobre todas las filas que contienen datos
            for row_number in rows_with_data:
                current_column = None     
                # Iterar sobre cada columna en la fila actual
                column_letters = sorted(set(coord[0] for coord in spreadsheet.cells.keys() if coord[1] == row_number))
                col_num = self.col_to_num(column_letters[-1])
                for col_num_ in range(1, col_num+1):
                    column_letter = self.num_to_col(col_num_)
                    cell = spreadsheet.get_cell((column_letter,row_number))

                    if cell:
                        # Determinar qué contenido guardar según el tipo de contenido de la celda
                        if isinstance(cell.content, FormulaContent):
                            to_save = "=" + cell.content.formula
                            to_save=to_save.replace(';',',')
                        elif isinstance(cell.content, NumericalContent):
                            to_save = str(cell.content.number)
                            if to_save.endswith('.0'):
                                to_save = to_save[:-2]  # Eliminar '.0' para números enteros
                        elif isinstance(cell.content, TextContent):
                            to_save = cell.content.text
                        else:
                            to_save = ""  # Manejo para otros tipos de contenido

                        file.write(f"{to_save}")  # Escribir contenido de la celda seguido de punto y coma
                    if not col_num_== col_num:file.write(";")
                file.write("\n")

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
                #cells = self.split_row(row)
                cells = row.split(';')
                for col_idx, value in enumerate(cells, start=0):
                    dependencies = []
                    if value.startswith('='):
                        formula = value[1:].replace(',',';')
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
        spreadsheet.update_graph()
                        
        return spreadsheet
