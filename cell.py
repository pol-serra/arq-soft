from content import Content,NumericalContent,TextContent
from formula import FormulaContent



class Cell:
    def __init__(self, coordinate: tuple, content: Content = None):
        self.coordinate = coordinate
        self.content = content
        if content:
            content.set_cell(self)

    def get_coordinate(self) -> tuple:
        return self.coordinate

    def get_content(self) -> Content:
        return self.content

    def set_content(self, content: Content) -> None:
        self.content = content
        content.set_cell(self)

    def get_value(self,spreadsheet):
        return self.content.get_value(spreadsheet) if self.content else None


# Example usage:
if __name__ == "__main__":
    text_content = TextContent("Example text")
    cell = Cell(("A", 1), text_content)
    print(text_content.get_cell().get_coordinate())  # Output: ("A", 1)

    numerical_content = NumericalContent(42.0)
    cell.set_content(numerical_content)
    print(cell.get_value())  # Output: 42.0
    print(numerical_content.get_cell().get_coordinate())  # Output: ("A", 1)

    # Test with FormulaContent
    formula_content = FormulaContent("=3+5", None)  # `None` is used instead of a spreadsheet instance for simplicity
    cell.set_content(formula_content)
    print(cell.get_value())
