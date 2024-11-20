# Text-Based Spreadsheet Application

## Overview

This project implements a **text-based spreadsheet application** that supports numerical, text, and formula-based cells. It simulates the core functionalities of spreadsheet software while focusing on efficient computation and a robust design.

The project covers the complete software development lifecycle:
1. **Requirements Analysis**: Define user needs and system constraints.
2. **Domain Modeling**: Capture the core concepts of a spreadsheet system.
3. **Design**: Create a Design Class Diagram to detail the system's architecture.
4. **Implementation**: Develop a working program based on the design.

## Features

- **Cell Content Types**:
  - **Numerical**: Cells storing integers or real numbers.
  - **Text**: Cells storing strings (e.g., headers or notes).
  - **Formulas**: Dynamic content calculated based on mathematical expressions and references to other cells.

- **Supported Functions**:
  - `SUM(range;...)`: Computes the sum of the specified cell values.
  - `MIN(range;...)`: Returns the minimum value.
  - `MAX(range;...)`: Returns the maximum value.
  - `AVERAGE(range;...)`: Calculates the arithmetic mean.

- **Data Management**:
  - Store spreadsheets in **Semicolon Separated Values (S2V)** format.
  - Load spreadsheets from S2V files and process their contents.

- **User Interaction**:
  - Text-based menu system for user input and operations.
  - Error handling for invalid formulas, syntax issues, and circular dependencies.

## Usage

### Running the Program

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/spreadsheet-app.git

