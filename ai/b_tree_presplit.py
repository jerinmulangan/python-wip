# B-Tree of order 4 (max children = 4, max keys = 3) with preemptive splitting insertions
class BTreeNode:
    def __init__(self, leaf=False):
        self.keys = []
        self.children = []
        self.leaf = leaf

class BTree:
    def __init__(self, order=4):
        self.root = BTreeNode(leaf=True)
        self.order = order  # max children

    def split_child(self, parent, index):
        order = self.order
        child = parent.children[index]
        mid = len(child.keys) // 2  # median index

        new_node = BTreeNode(leaf=child.leaf)
        promote_key = child.keys[mid]

        new_node.keys = child.keys[mid+1:]
        child.keys = child.keys[:mid]

        if not child.leaf:
            new_node.children = child.children[mid+1:]
            child.children = child.children[:mid+1]

        parent.keys.insert(index, promote_key)
        parent.children.insert(index+1, new_node)

    def insert(self, key):
        root = self.root
        if len(root.keys) == self.order - 1:
            new_root = BTreeNode(leaf=False)
            new_root.children.append(root)
            self.split_child(new_root, 0)
            self.root = new_root
        self._insert_nonfull(self.root, key)

    def _insert_nonfull(self, node, key):
        if node.leaf:
            import bisect
            bisect.insort(node.keys, key)
        else:
            i = len(node.keys)
            for j, k in enumerate(node.keys):
                if key < k:
                    i = j
                    break
            if len(node.children[i].keys) == self.order - 1:
                self.split_child(node, i)
                if key > node.keys[i]:
                    i += 1
            self._insert_nonfull(node.children[i], key)

    def ascii_tree(self, node=None, is_root=True):
        if node is None:
            node = self.root
        lines = []
        if is_root:
            lines.append("Root: [" + " | ".join(str(k) for k in node.keys) + "]")
        else:
            lines.append("[" + " | ".join(str(k) for k in node.keys) + "]")
        if not node.leaf:
            n = len(node.children)
            for idx, child in enumerate(node.children):
                branch = "├─" if idx < n-1 else "└─"
                sub = self.ascii_tree(child, is_root=False)
                lines.append(branch + " " + sub[0])
                for extra in sub[1:]:
                    connector = "│  " if idx < n-1 else "   "
                    lines.append(connector + extra)
        return lines

# Sequence of inserts
sequence = [23, 65, 37, 60, 46, 92, 48, 71, 56, 59, 18, 21, 10, 74, 78, 15, 16, 20, 24, 28, 39, 43, 47, 50, 69, 75, 8, 49, 33, 38]

tree = BTree(order=4)
for num in sequence:
    tree.insert(num)
    print(f"-- After inserting {num} --")
    for line in tree.ascii_tree():
        print(line)
    print()
