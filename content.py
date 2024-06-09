class Content:
    def __init__(self):
        self.cell = None

    def get_value(self):
        raise NotImplementedError("Subclasses should implement this method")

    def set_cell(self, cell: 'Cell') -> None:
        self.cell = cell


class TextContent(Content):
    def __init__(self, text: str):
        super().__init__()
        self.text = text

    def get_value(self,spreadsheet):
        return self.text

    def get_text(self) -> str:
        return self.text

    def get_number(self):
        if self.text == "":
            return 0
        try:
            return float(self.text)
        except ValueError:
            raise ValueError("The text content is not a number")

    def set_text(self, text: str) -> None:
        self.text = text


class NumericalContent(Content):
    def __init__(self, number: float):
        super().__init__()
        self.number = number

    def get_value(self, spreadsheet):
        return self.number

    def get_number(self) -> float:
        return self.number

    def get_text(self) -> str:
        return str(self.number)

    def set_number(self, number: float) -> None:
        self.number = number


