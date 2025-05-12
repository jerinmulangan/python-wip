class BTreeNode:
    def __init__(self, t, leaf=False):
        # t: minimum degree (here t=2 for order 4)
        self.t = t
        self.leaf = leaf
        self.keys = []      # list of keys
        self.children = []  # list of child pointers

    def is_full(self):
        # node is full if number of keys == 2*t - 1
        return len(self.keys) == 2 * self.t - 1

    def insert_non_full(self, key):
        # Insert a key into a non-full node
        i = len(self.keys) - 1
        if self.leaf:
            # Insert key into the leaf at correct position
            self.keys.append(None)
            while i >= 0 and key < self.keys[i]:
                self.keys[i + 1] = self.keys[i]
                i -= 1
            self.keys[i + 1] = key
        else:
            # Find child to descend to
            while i >= 0 and key < self.keys[i]:
                i -= 1
            i += 1
            # Preemptive split: if child is full, split it first
            if self.children[i].is_full():
                self.split_child(i)
                # After split, decide which of the two children to descend
                if key > self.keys[i]:
                    i += 1
            self.children[i].insert_non_full(key)

    def split_child(self, index):
        # Split the full child at children[index]
        full_child = self.children[index]
        t = self.t
        # Create new node to hold (t-1) keys of full_child
        new_child = BTreeNode(t, leaf=full_child.leaf)
        # Copy end of full_child.keys to new_child
        new_child.keys = full_child.keys[t:]
        # If not leaf, also copy children
        if not full_child.leaf:
            new_child.children = full_child.children[t:]
        # Reduce full_child's keys and children
        full_child.keys = full_child.keys[:t-1]
        if not full_child.leaf:
            full_child.children = full_child.children[:t]
        # Insert new child into children list
        self.children.insert(index + 1, new_child)
        # Move median key up to this node
        self.keys.insert(index, full_child.keys.pop())

class BTree:
    def __init__(self, order=4):
        # order = max children per node
        # minimum degree t = ceil(order/2)
        from math import ceil
        self.t = ceil(order / 2)
        self.root = BTreeNode(self.t, leaf=True)

    def insert(self, key):
        root = self.root
        if root.is_full():
            # Root is full, so tree grows in height
            new_root = BTreeNode(self.t, leaf=False)
            new_root.children.append(root)
            new_root.split_child(0)
            # Decide which child to insert into
            i = 0
            if key > new_root.keys[0]:
                i = 1
            new_root.children[i].insert_non_full(key)
            self.root = new_root
        else:
            root.insert_non_full(key)

    def traverse(self, node=None):
        # In-order traversal of the tree keys
        if node is None:
            node = self.root
        result = []
        for i, key in enumerate(node.keys):
            if not node.leaf:
                result.extend(self.traverse(node.children[i]))
            result.append(key)
        if not node.leaf:
            result.extend(self.traverse(node.children[-1]))
        return result

    def print_tree(self, node=None, level=0):
        # Pretty-print the tree structure
        if node is None:
            node = self.root
        print('    ' * level + f"Level {level} | Keys: {node.keys}")
        if not node.leaf:
            for child in node.children:
                self.print_tree(child, level + 1)

# Example usage
if __name__ == '__main__':
    # Order 4 B-tree: maximum 4 children, max 3 keys, min 1 key per non-root
    btree = BTree(order=4)
    values = [23, 65, 37, 60, 46, 92, 48, 71, 56, 59,
              18, 21, 10, 74, 78, 15, 16, 20, 24, 28,
              39, 43, 47, 50, 69, 75, 8, 49, 33, 38]
    for v in values:
        print(f"-- Inserting {v} --")
        btree.insert(v)
        btree.print_tree()
        print("In-order traversal:", btree.traverse())
        print()