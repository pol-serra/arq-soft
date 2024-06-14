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
        return self.numerical

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
        if re.match(r'SUMA\((?:[^)(]+|\((?:[^)(]+|\([^)(]*\))*\))*\)|MIN\((?:[^)(]+|\((?:[^)(]+|\([^)(]*\))*\))*\)|MAX\((?:[^)(]+|\((?:[^)(]+|\([^)(]*\))*\))*\)|PROMEDIO\((?:[^)(]+|\((?:[^)(]+|\([^)(]*\))*\))*\)|[A-Z]+\d+|\d+|[+\-*/()]',s) \
            and not s=="+" and not s=="-" and not s=="*" and not s=="/":
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

    def tokenizer(self,formula):
        import re
        # Define the token specification
        TOKEN_SPECIFICATION = [
            ('FUNC',      r'SUMA|MIN|MAX|PROMEDIO'),  # Functions
            ('NUMBER',    r'\d+(\.\d*)?'),            # Integer or decimal number
            ('PLUS',      r'\+'),                     # Addition operator
            ('MINUS',     r'-'),                      # Subtraction operator
            ('TIMES',     r'\*'),                     # Multiplication operator
            ('DIVIDE',    r'/'),                      # Division operator
            ('LPAREN',    r'\('),                     # Left parenthesis
            ('RPAREN',    r'\)'),                     # Right parenthesis
            ('SEMI',      r';'),                      # Semicolon as argument separator
            ('CELL',      r'[A-Z]+\d+'),              # Cell reference
            ('SKIP',      r'[ \t]+'),                 # Skip over spaces and tabs
            ('MISMATCH',  r'.'),                      # Any other character
        ]

        TOKEN_REGEX = '|'.join('(?P<%s>%s)' % pair for pair in TOKEN_SPECIFICATION)
        tokens = []
        pos = 0
        length = len(formula)
        
        while pos < length:
            match = re.match(TOKEN_REGEX, formula[pos:])
            if not match:
                raise RuntimeError(f'Caracter inesperado {formula[pos]} en {formula}')
            kind = match.lastgroup
            value = match.group(kind)
            
            if kind == 'NUMBER':
                value = float(value) if '.' in value else int(value)
                tokens.append((kind, value))
            elif kind == 'SKIP':
                pos += match.end() - match.start()
                continue  # Ignore spaces and tabs
            elif kind == 'MISMATCH':
                raise RuntimeError(f'{value!r} inesperado en {formula}')
            elif kind == 'FUNC':
                func_tokens, new_pos = self._parse_function(pos)
                tokens.append((kind,func_tokens))
                pos = new_pos
                continue
            else:
                tokens.append((kind, value))
            pos += match.end() - match.start()
        
        return tokens


    def _parse_function(self, start_pos):
        end_pos = start_pos
        paren_count = 0
        func_str = ""
        while end_pos < len(self.formula):
            char = self.formula[end_pos]
            func_str += char
            if char == '(':
                paren_count += 1
            elif char == ')':
                paren_count -= 1
                if paren_count == 0:
                    break
            end_pos += 1
        
        return (func_str, end_pos + 1)

    def evaluate(self, spreadsheet: 'Spreadsheet'):
        """
        Evaluates a mathematical expression using the Shunting Yard Algorithm.
        """
        #tokens = re.findall(r'[A-Z]+\d+|\d+|\+|\-|\*|\/|\(|\)|SUMA\([^()]*\)|MIN\([^()]*\)|MAX\([^()]*\)|PROMEDIO\([^()]*\)', self.formula)
        tokens = self.tokenizer(self.formula)
        values, operators = [], []
        for token in tokens:
            if token[0]=='NUMBER':
                operand = Operand().create_operand('numerical',float(token[1]))
                values.append(operand.get_value())
            elif token[0]=='CELL':
                coincidence = re.match(r"([A-Z]+)(\d+)",token[1])
                if coincidence:
                    col = coincidence.group(1)
                    row = int(coincidence.group(2))
                else:
                    raise ValueError(f"Token no válido: {token}")
                operand = Operand().create_operand('cell',spreadsheet.get_cell((col,row)))
                values.append(operand.get_value(spreadsheet))
            elif token[0]=='FUNC':
                if token[1].startswith("SUMA"): operand = Operand().create_operand('function','SUMA')
                elif token[1].startswith("MIN"): operand = Operand().create_operand('function','MIN')
                elif token[1].startswith("MAX"): operand = Operand().create_operand('function','MAX')
                elif token[1].startswith("PROMEDIO"): operand = Operand().create_operand('function','PROMEDIO')
                operand.set_arguments_from_formula(token[1],spreadsheet)
                values.append(operand.get_value(spreadsheet))
            elif token[0] == 'LPAREN':
                operators.append(token[1])
            elif token[0] == 'RPAREN':
                while self.peek(operators) and self.peek(operators) != '(':
                    self.apply_operator(operators, values)
                operators.pop() # Discard the '('
            else:
                while self.peek(operators) and self.peek(operators) not in "()" and self.greater_precedence(self.peek(operators), token[1]):
                    self.apply_operator(operators, values)
                operators.append(token[1])
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

    @staticmethod
    def parse_function(function):
    # Extract the function name
        match = re.match(r'([A-Z]+)\((.*)\)', function)
        if not match:
            raise ValueError(f"Invalid formula: {function}")

        name, arguments_str = match.groups()

        # Parse the arguments while handling nested functions
        def extract_arguments(arg_str):
            args = []
            nested_level = 0
            current_arg = []
            
            for char in arg_str:
                if char == '(':
                    nested_level += 1
                elif char == ')':
                    nested_level -= 1
                if char == ';' and nested_level == 0:
                    args.append(''.join(current_arg).strip())
                    current_arg = []
                else:
                    current_arg.append(char)
            
            # Add the last argument
            if current_arg:
                args.append(''.join(current_arg).strip())

            return args

        arguments = extract_arguments(arguments_str)
        return arguments

    def set_arguments_from_formula(self, function: str, spreadsheet: 'Spreadsheet' = None):
        """
        Extract and set arguments from the formula string.
        """
        # Extract arguments from the formula string (e.g., SUMA(A1;2;3;A1:A2))
        # Split the formula by the function name and parenthesis
        arguments = self.parse_function(function)
        for arg in arguments:
            if re.match(r'^[A-Z]+[0-9]+:[A-Z]+[0-9]+$', arg):
                argument = Argument.create("Range",self.name)
                range_cells = arg.split(":")
                argument.set_range(range_cells[0], range_cells[1], spreadsheet)
            elif re.match(r'SUMA\((?:[^)(]+|\((?:[^)(]+|\([^)(]*\))*\))*\)|'
                        r'MIN\((?:[^)(]+|\((?:[^)(]+|\([^)(]*\))*\))*\)|'
                        r'MAX\((?:[^)(]+|\((?:[^)(]+|\([^)(]*\))*\))*\)|'
                        r'PROMEDIO\((?:[^)(]+|\((?:[^)(]+|\([^)(]*\))*\))*\)|'
                        r'[A-Z]+\d+|'
                        r'[+\-*/()]', arg):
                if arg.startswith("SUMA"):
                    operand = Operand().create_operand('function', 'SUMA')
                elif arg.startswith("MIN"):
                    operand = Operand().create_operand('function', 'MIN')
                elif arg.startswith("MAX"):
                    operand = Operand().create_operand('function', 'MAX')
                elif arg.startswith("PROMEDIO"):
                    operand = Operand().create_operand('function', 'PROMEDIO')
                operand.set_arguments_from_formula(arg, spreadsheet)
                argument = Argument.create("Function", operand)
            elif re.match(r'[A-Z]+\d+', arg):
                coincidence = re.match(r"([A-Z]+)(\d+)", arg)
                col = coincidence.group(1)
                row = int(coincidence.group(2))
                argument = Argument.create("Cell", spreadsheet.get_cell((col, row)))
            elif re.match(r'^[+\-]?\d*\.?\d+$', arg):
                argument = Argument.create("Numerical", float(arg))
            else:
                # Handle unrecognized arguments
                argument = None
            
            if argument:
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
        elif argument_type == "Function":
            return FunctionArgument(*args, **kwargs)
        else:
            raise ValueError("Invalid argument type")

    def get_value(self):
        raise NotImplementedError("Subclasses should implement this method")

class RangeArgument(Argument):
    def __init__(self,type_of_function):
        self.cells = []
        self.type_function=type_of_function

    def set_range(self, start_cell, end_cell, spreadsheet):
        start_col, start_row = self._parse_cell(start_cell)
        end_col, end_row = self._parse_cell(end_cell)

        # Ensure start cell is before or same as end cell
        if start_col > end_col or start_row > end_row:
            raise ValueError("Start cell must be before or same as end cell")

        self.cells = []

        for col in range(start_col, end_col + 1):
            col_letter = self._index_to_col_str(col)
            for row in range(start_row, end_row + 1):
                cell_ref = f"{col_letter}{row}"
                cell = spreadsheet.get_cell((col_letter,row))
                if cell:
                    self.cells.append(cell)

    def get_value(self,spreadsheet):
        # Example implementation, return some value
        if self.type_function == 'SUMA':
            return sum(cell.get_value(spreadsheet) for cell in self.cells)
        elif self.type_function == 'MIN':
            return min(cell.get_value(spreadsheet) for cell in self.cells)
        elif self.type_function == 'MAX':
            return max(cell.get_value(spreadsheet) for cell in self.cells)
        elif self.type_function == 'PROMEDIO':
            values = [cell.get_value(spreadsheet) for cell in self.cells]
            return sum(values) / len(values) if values else 0

    def _parse_cell(self, cell):
        col_str = ""
        row_str = ""
        for char in cell:
            if char.isalpha():
                col_str += char
            elif char.isdigit():
                row_str += char
        col = self._col_str_to_index(col_str)
        row = int(row_str)
        return col, row

    def _col_str_to_index(self, col_str):
        base = ord('A')
        col_num = 0
        for char in col_str:
            col_num = col_num * 26 + (ord(char) - base + 1)
        return col_num - 1

    def _index_to_col_str(self, col):
        result = ""
        while col >= 0:
            result = chr(col % 26 + ord('A')) + result
            col = col // 26 - 1
        return result



class FunctionArgument(Argument):
    def __init__(self, function: 'FunctionOperand'):
        self.function = function

    def get_value(self,spreadsheet):
        return self.function.get_value(spreadsheet)  # Simplified


class NumericalArgument(Argument):
    def __init__(self, number: float):
        self.number = number

    def get_value(self,spreadsheet):
        return self.number


class CellArgument(Argument):
    def __init__(self, cell: 'Cell'):
        self.cell = cell

    def get_value(self,spreadsheet):
        return self.cell.get_value(spreadsheet)  # Simplified

