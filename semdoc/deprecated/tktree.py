import tkinter as tk
from tkinter import ttk

# Initialize TKinter root
root = tk.Tk()
root.title("Tree Structure Navigation")

# Setup Treeview
tree = ttk.Treeview(root)
tree.pack(expand=True, fill="both")

# Example tree-like data structure
data = {"root": {"child1": {"grandchild1": {}}, "child2": {}}}


def populate_tree(parent, node, tree_dict):
    """Recursively populate the tree"""
    for child in tree_dict:
        child_id = tree.insert(parent, "end", text=child)
        populate_tree(child_id, child, tree_dict[child])


# Populate tree with our data
populate_tree("", "root", data["root"])

# Run the application
root.mainloop()
