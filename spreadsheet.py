from cell import Cell
from graph import Graph
from formula import FormulaContent
import re

class Spreadsheet:
    def __init__(self):
        self.cells = {}
        self.dependency_graph=Graph()

    def add_cell(self, coordinate: tuple, cell: Cell) -> None:
        self.cells[coordinate] = cell

    def get_cell(self, coordinate: tuple) -> Cell:
        return self.cells.get(coordinate)

    def compute_cell(self, coordinate):
        cell = self.cells.get(coordinate)
        if cell and isinstance(cell.content, str) and cell.content.startswith('='):
            formula = FormulaContent(cell.content[1:],self)
            cell.value = formula.evaluate(self)
        return cell.value if cell else None

    def print_spreadsheet(self):
        # Create a sorted list of cell coordinates
        sorted_coords = sorted(self.cells.keys(), key=lambda x: (int(x[1:]), x[0]))
        # Extract row and column labels
        rows = sorted(set(int(coord[1:]) for coord in sorted_coords))
        cols = sorted(set(coord[0] for coord in sorted_coords))

        # Print column headers
        print("\t" + "\t".join(cols))
        for row in rows:
            # Print row headers and cell values
            row_cells = [self.cells.get(col + str(row), Cell(col + str(row), "")).content for col in cols]
            row_values = [self.compute_cell(col + str(row)) if col + str(row) in self.cells else '' for col in cols]
            print(f"{row}\t" + "\t".join(str(value) for value in row_values))

    def calculate_all(self):
        # Implement the logic to calculate all cell values
        pass

    def update_dependent_cells(self, coordinate: tuple):
        # Implement logic to update dependent cells
        pass

    def parse_formula(self, formula):
        # Implementa la lógica para analizar la fórmula y extraer las referencias de celdas.
        return re.findall(r'[A-Z]+\d+', formula)

    def update_graph(self):
        self.graph = Graph()
        for cell_ref, cell in self.cells.items():
            cell_ref_=cell_ref[0]+str(cell_ref[1])
            if isinstance(cell.content, FormulaContent):
                dependencies = self.parse_formula(cell.content.formula)
                for dep in dependencies:
                    self.graph.add_edge(dep, cell_ref_)

    def detect_circular_dependencies(self):
        if self.graph.has_cycle():
            print("Hay dependencias circulares en la hoja de cálculo.")
        else:
            print("No hay dependencias circulares en la hoja de cálculo.")


# # Example usage:
# if __name__ == "__main__":
#     spreadsheet = Spreadsheet()
#     cell = Cell(("A", 1), NumericalContent(42.0))
#     spreadsheet.add_cell(("A", 1), cell)
#     print(spreadsheet.get_cell(("A", 1)).get_value())  # Output: 42.0
