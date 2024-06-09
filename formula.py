from content import Content, NumericalContent
import re


class Operand:
    @staticmethod
    def create_operand(content_type, content):
        if content_type == 'function':
            return FunctionOperand(content)
        elif content_type == 'numerical':
            return NumericalOperand(content)
        elif content_type == 'cell':
            return CellOperand(content)
        else:
            raise ValueError("Tipo de contenido no válido")

class NumericalOperand(Operand):
    def __init__(self, numerical):
        self.numerical = numerical

    def get_value(self):
        return self.numerical.get_number()

class CellOperand(Operand):
    def __init__(self, cell: 'Cell'):
        self.cell = cell

    def get_value(self,spreadsheet):
        return self.cell.get_value(spreadsheet)

class Operator:
    def __init__(self, symbol: str):
        self.symbol = symbol

    def get_symbol(self) -> str:
        return self.symbol


class FormulaContent(Content):
    def __init__(self, formula: str):
        super().__init__()
        self.formula = formula
        self.operands = []
        self.operators = []

    def is_number(self,s):
        """
        Determines if a given string represents a number.
        """
        if re.match(r'^\d+(\.\d+)?$', s):
            return True

    def is_cell_reference(self,s):
        if re.match(r'[A-Z]+\d+', s):  # Verifica si es una referencia de celda (por ejemplo, A1, AB1)
            return True

    def is_function(self,s):
        if re.match(r'SUMA\([^()]*\)|MIN\([^()]*\)|MAX\([^()]*\)|PROMEDIO\([^()]',s):
            return True

    def peek(self,stack):
        """
        Peeks at the top element of a stack without popping it.
        """
        return stack[-1] if stack else None

    def apply_operator(self,operators, values):
        """
        Applies an operator to the two most recent values in the values stack.
        """
        operator = operators.pop()
        right = values.pop()
        left = values.pop()
        formula = "{0}{1}{2}".format(left, operator, right)
        values.append(eval(formula))

    def greater_precedence(self,op1, op2):
        """
        Determines if the precedence of op1 is greater than op2.
        """
        precedences = {'+' : 0, '-' : 0, '*' : 1, '/' : 1}
        return precedences[op1] > precedences[op2]

    def evaluate(self, spreadsheet: 'Spreadsheet'):
        """
        Evaluates a mathematical expression using the Shunting Yard Algorithm.
        """
        tokens = re.findall(r'[A-Z]+\d+|\d+|\+|\-|\*|\/|\(|\)|SUMA\([^()]*\)|MIN\([^()]*\)|MAX\([^()]*\)|PROMEDIO\([^()]*\)', self.formula)
        values, operators = [], []
        for token in tokens:
            if self.is_number(token):
                operand = Operand().create_operand('numerical',float(token))
                values.append(operand.get_value())
            elif self.is_cell_reference(token):
                coincidence = re.match(r"([A-Z]+)(\d+)",token)
                if coincidence:
                    col = coincidence.group(1)
                    row = int(coincidence.group(2))
                else:
                    raise ValueError(f"Token no válido: {token}")
                operand = Operand().create_operand('cell',spreadsheet.get_cell((col,row)))
                values.append(operand.get_value(spreadsheet))
            elif self.is_function(token):
                if token.startswith("SUMA"): operand = Operand().create_operand('function','SUMA')
                if token.startswith("MIN"): operand = Operand().create_operand('function','MIN')
                if token.startswith("MAX"): operand = Operand().create_operand('function','MAX')
                if token.startswith("PROMEDIO"): operand = Operand().create_operand('function','PROMEDIO')
                operand.set_arguments_from_formula(token,spreadsheet)
                values.append(operand.get_value(spreadsheet))
            elif token == '(':
                operators.append(token)
            elif token == ')':
                while self.peek(operators) and self.peek(operators) != '(':
                    self.apply_operator(operators, values)
                operators.pop() # Discard the '('
            else:
                while self.peek(operators) and self.peek(operators) not in "()" and self.greater_precedence(self.peek(operators), token):
                    self.apply_operator(operators, values)
                operators.append(token)
        while self.peek(operators):
            self.apply_operator(operators, values)
        return values[0]
    
    def get_dependencies(self):
        """
        Get all cell references that this formula depends on.
        """
        tokens = re.findall(r'[A-Z]+\d+', self.formula)
        dependencies = set()
        for token in tokens:
            if self.is_cell_reference(token):
                dependencies.add(token)
        return dependencies
    
    def get_value(self,spreadsheet):
        return self.evaluate(spreadsheet)



class FunctionOperand(Operand):
    def __init__(self, name: str):
        self.name = name
        self.arguments = []

    def add_argument(self, argument: 'Argument'):
        self.arguments.append(argument)

    def set_arguments_from_formula(self, function: str, spreadsheet: 'Spreadsheet' = None):
        """
        Extract and set arguments from the formula string.
        """
        # Extract arguments from the formula string (e.g., SUMA(A1;2;3;A1:A2))
        # Split the formula by the function name and parenthesis
        function_parts = function.split(self.name + '(')
        if len(function_parts) != 2:
            raise ValueError(f"Invalid formula: {function}")
        # Extract the arguments part (e.g., A1;2;3;A1:A2)
        arguments_str = function_parts[1].rstrip(')')
        # Split the arguments by ';' and trim whitespace
        arguments = [arg.strip() for arg in arguments_str.split(',')]
        # Create Argument instances based on the argument type
        for arg in arguments:
            print(arg)
            coincidence = re.match(r"([A-Z]+)(\d+)",arg)
            if coincidence:
                col = coincidence.group(1)
                row = int(coincidence.group(2))
            else:
                raise ValueError(f"Token no válido: {arg}")
            if re.match(r'[A-Z]+\d+', arg):
                argument=Argument.create("Cell",spreadsheet.get_cell((col,row)))
            elif float(arg):
                argument=Argument.create("Numerical",float(arg))
            else: 
                argument=Argument.create("Range",arg)
            self.arguments.append(argument)

    def calculate(self,spreadsheet):
        # Simplified function logic
        if self.name == 'SUMA':
            return sum(arg.get_value(spreadsheet) for arg in self.arguments)
        elif self.name == 'MIN':
            return min(arg.get_value(spreadsheet) for arg in self.arguments)
        elif self.name == 'MAX':
            return max(arg.get_value(spreadsheet) for arg in self.arguments)
        elif self.name == 'PROMEDIO':
            values = [arg.get_value(spreadsheet) for arg in self.arguments]
            return sum(values) / len(values) if values else 0
        return None
    
    def get_value(self,spreadsheet):
        return self.calculate(spreadsheet)

class Sum(FunctionOperand):
    def __init__(self):
        super().__init__('SUMA')


class Min(FunctionOperand):
    def __init__(self):
        super().__init__('MIN')


class Max(FunctionOperand):
    def __init__(self):
        super().__init__('MAX')


class Average(FunctionOperand):
    def __init__(self):
        super().__init__('PROMEDIO')


class Argument:
    @staticmethod
    def create(argument_type, *args, **kwargs):
        if argument_type == "Range":
            return RangeArgument(*args, **kwargs)
        elif argument_type == "Numerical":
            return NumericalArgument(*args, **kwargs)
        elif argument_type == "Cell":
            return CellArgument(*args, **kwargs)
        #elif argument_type == "Function":

        else:
            raise ValueError("Invalid argument type")

    def get_value(self):
        raise NotImplementedError("Subclasses should implement this method")


class RangeArgument(Argument):
    def __init__(self, cells: list):
        self.cells = cells

    def get_value(self):
        return sum(cell.get_value() for cell in self.cells)  # Simplified


class NumericalArgument(Argument):
    def __init__(self, number: float):
        self.number = number

    def get_value(self):
        return self.number


class CellArgument(Argument):
    def __init__(self, cell: 'Cell'):
        self.cell = cell

    def get_value(self,spreadsheet):
        return self.cell.get_value(spreadsheet)  # Simplified

