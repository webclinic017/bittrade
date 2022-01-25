'''
Tree node is used for validation of the expression tree
'''
from collections import deque


class TreeNodeValidator:
    def __init__(self, value, node_type):
        self.value = value
        self.node_type = node_type

        self.right_child = None
        self.left_child = None

    @classmethod
    def from_dict(cls, data: dict):
        node = cls(value=data['value'], node_type=data['type'])

        if 'left_child' in data:
            node.left_child = cls.from_dict(data['left_child'])

        if 'right_child' in data:
            node.right_child = cls.from_dict(data['right_child'])

        return node

    @classmethod
    def is_complete_binary_tree(cls, root):
        if root == None:
            return True

        if root.left_child == None and root.right_child == None:
            return True
        elif root.left_child != None and root.right_child != None:
            return cls.is_complete_binary_tree(root.left_child) and cls.is_complete_binary_tree(root.right_child)

        return False
