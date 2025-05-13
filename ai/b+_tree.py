import math

class BPlusNode:
    def __init__(self, order, leaf=False):
        self.order = order
        self.leaf = leaf
        self.keys = []
        self.children = []          # for internal nodes: child pointers; for leaves: not used
        self.next = None            # pointer to next leaf for leaf nodes

    def is_full(self):
        # Node overflows when it has > order - 1 keys
        return len(self.keys) > (self.order - 1)

class BPlusTree:
    def __init__(self, order=3):
        self.order = order
        self.root = BPlusNode(order, leaf=True)

    def _find_leaf(self, node, key):
        # Traverse internal nodes to reach the appropriate leaf
        if node.leaf:
            return node
        for i, item in enumerate(node.keys):
            if key < item:
                return self._find_leaf(node.children[i], key)
        return self._find_leaf(node.children[-1], key)

    def insert(self, key):
        leaf = self._find_leaf(self.root, key)
        self._insert_into_leaf(leaf, key)
        if leaf.is_full():
            self._split_leaf(leaf)

    def _insert_into_leaf(self, leaf, key):
        # Insert key in sorted order in the leaf
        idx = 0
        while idx < len(leaf.keys) and leaf.keys[idx] < key:
            idx += 1
        leaf.keys.insert(idx, key)

    def _split_leaf(self, leaf):
        # Split overflowing leaf into two
        new_leaf = BPlusNode(self.order, leaf=True)
        # mid = ceil((order-1)/2)
        mid = math.ceil((self.order - 1) / 2)
        # distribute keys
        new_leaf.keys = leaf.keys[mid:]
        leaf.keys = leaf.keys[:mid]
        # link sibling
        new_leaf.next = leaf.next
        leaf.next = new_leaf
        # propagate smallest key of the new leaf
        split_key = new_leaf.keys[0]
        self._insert_into_parent(leaf, split_key, new_leaf)

    def _insert_into_parent(self, node, key, new_node):
        # If splitting the root
        if node is self.root:
            new_root = BPlusNode(self.order)
            new_root.keys = [key]
            new_root.children = [node, new_node]
            self.root = new_root
            return
        # Otherwise find parent and insert
        parent = self._find_parent(self.root, node)
        # insert key and new_node pointer
        idx = 0
        while idx < len(parent.keys) and parent.keys[idx] < key:
            idx += 1
        parent.keys.insert(idx, key)
        parent.children.insert(idx+1, new_node)
        # split internal if overflow
        if len(parent.keys) > (self.order - 1):
            self._split_internal(parent)

    def _split_internal(self, node):
        # internal split with mid = ceil(order/2)
        mid = math.ceil(self.order / 2)
        # key to push up
        split_key = node.keys[mid-1]
        # new internal node
        new_int = BPlusNode(self.order)
        # distribute keys and children
        new_int.keys = node.keys[mid:]
        node.keys = node.keys[:mid-1]
        new_int.children = node.children[mid:]
        node.children = node.children[:mid]
        # propagate up
        self._insert_into_parent(node, split_key, new_int)

    def _find_parent(self, current, child):
        # Return parent of 'child' starting from 'current'
        if current.leaf:
            return None
        for idx, c in enumerate(current.children):
            if c is child:
                return current
            if not c.leaf:
                parent = self._find_parent(c, child)
                if parent:
                    return parent
        return None

    def search(self, key):
        leaf = self._find_leaf(self.root, key)
        return key in leaf.keys

    def traverse_leaves(self):
        # Return all keys in sorted order via leaf-level traversal
        node = self.root
        while not node.leaf:
            node = node.children[0]
        result = []
        while node:
            result.extend(node.keys)
            node = node.next
        return result

    def print_tree(self, node=None, level=0):
        # Recursively print the tree structure
        if node is None:
            node = self.root
        indent = '    ' * level
        if node.leaf:
            print(f"{indent}Leaf: {node.keys}")
        else:
            print(f"{indent}Internal: {node.keys}")
            for child in node.children:
                self.print_tree(child, level+1)

# Example usage with step-by-step printing
def main():
    bpt = BPlusTree(order=4)
    print("Initial tree (empty):")
    bpt.print_tree()
    print()
    for key in [23, 65, 37, 60, 46, 92, 48, 71, 56, 59, 
                18, 21, 10, 74, 78, 15, 16, 20, 24, 28, 
                39, 43, 47, 50, 69, 75, 8, 49, 33, 38]:
        print(f"-- Inserting {key} --")
        bpt.insert(key)
        bpt.print_tree()
        print(f"Leaf traversal: {bpt.traverse_leaves()}")
        print()

if __name__ == "__main__":
    main()

