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




