class Graph:
    def __init__(self):
        self.nodes = set()  # Set of cells
        self.edges = {}  # Dictionary mapping cells to a set of dependent cells

    def add_node(self, cell):
        """Add a node to the graph."""
        if cell not in self.nodes:
            self.nodes.add(cell)
            self.edges[cell] = set()

    def add_edge(self, from_cell, to_cell):
        """Add a directed edge from 'from_cell' to 'to_cell'."""
        if from_cell not in self.nodes:
            self.add_node(from_cell)
        if to_cell not in self.nodes:
            self.add_node(to_cell)
        self.edges[from_cell].add(to_cell)

    def get_dependencies(self, cell):
        """Get all cells that the given cell depends on."""
        dependencies = set()
        for from_cell, to_cells in self.edges.items():
            if cell in to_cells:
                dependencies.add(from_cell)
        return dependencies

    def get_dependents(self, cell):
        """Get all cells that depend on the given cell."""
        if cell in self.edges:
            return self.edges[cell]
        else:
            return set()

    def __str__(self):
        """Return a string representation of the graph."""
        result = "Graph:\n"
        for from_cell, to_cells in self.edges.items():
            result += f"{from_cell} -> {', '.join(to_cells)}\n"
        return result

# Example usage
# if __name__ == "__main__":
#     g = Graph()
#     g.add_edge("A1", "B1")
#     g.add_edge("A1", "C1")
#     g.add_edge("B1", "D1")

#     print("Graph:")
#     print(g)

#     print("Dependencies of B1:", g.get_dependencies("B1"))
#     print("Dependents of A1:", g.get_dependents("A1"))
