class Node:
    def __init__(self, data, previous=None, next=None):
        self.data = data
        self.previous = previous
        self.next = next

    def prepend(self, item):
        # Inserts the given item before this node.
        if isinstance(item, Node):
            if self.previous is not None:
                self.previous.next = item
                item.previous = self.previous
            self.previous = item
            item.next = self
        else:
            self.insertBefore(Node(item))

    def append(self, item):
        # Inserts the given item after this node.
        if isinstance(item, Node):
            if self.next is not None:
                self.next.previous = item
                item.next = self.next
            self.next = item
            item.previous = self
        else:
            self.insertAfter(Node(item))

    def remove(self):
        # Removes this node from between its neighbors.
        if self.previous is not None:
            self.previous.next = self.next

        if self.next is not None:
            self.next.previous = self.previous


class LinkedList:
    def __init__(self):
        self.clear()

    def __len__(self):
        return self.length

    def __iter__(self):
        currentNode = self.firstNode
        while currentNode is not None:
            yield currentNode.data
            currentNode = currentNode.next

    @property
    def isEmpty(self):
        return self.firstNode is not None

    def clear(self):
        # Empties the list.
        self.firstNode = self.lastNode = None
        self.length = 0

    def prepend(self, item):
        # Prepends the given item to the beginning of the list.
        if isinstance(item, Node):
            if self.length == 0:
                self.firstNode = self.lastNode = item
            else:
                self.firstNode.prepend(item)
                self.firstNode = item
            self.length += 1
        else:
            self.prepend(Node(item))

    def append(self, item):
        # Appends the given item to the end of the list.
        if isinstance(item, Node):
            if self.length == 0:
                self.firstNode = self.lastNode = item
            else:
                self.lastNode.append(item)
                self.lastNode = item
            self.length += 1
        else:
            self.append(Node(item))

    def insertBefore(self, node, item):
        # Inserts the given item before the given node. If `node` is None, prepends the item to the beginning of the list.
        if isinstance(item, Node):
            node.prepend(item)
            if node is self.firstNode:
                self.firstNode = item
            self.length += 1
        elif item is None:
            self.append(item)
        else:
            self.append(Node(item))

    def insertAfter(self, node, item):
        # Inserts the given item after the given node. If `node` is None, appends the item to the end of the list.
        if isinstance(item, Node):
            node.append(item)
            if node is self.lastNode:
                self.lastNode = item
            self.length += 1
        elif item is None:
            self.prepend(item)
        else:
            self.append(Node(item))

    def remove(self, node):
        # Removes the given node from the list.
        if node is self.firstNode:
            self.firstNode = self.firstNode.next

        if node is self.lastNode:
            self.lastNode = self.lastNode.previous
        node.remove()
        self.length -= 1

