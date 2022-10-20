class SuggestionList:
    def __init__(self, items=None):
        self.clear()
        self.items = [] if items is None else items

    @property
    def numberOfItems(self):
        # Returns the number of items in the list.
        return len(self.items)

    @property
    def currentItem(self):
        # Returns the current item in the list.
        return self.items[self.currentItemIndex] if self.currentItemIndex < self.numberOfItems else None

    @property
    def isAtBeginning(self):
        # Returns whether the first item of the list is selected.
        return self.currentItemIndex == 0

    @property
    def isAtEnd(self):
        # Returns whether the last item of the list is selected.
        return self.currentItemIndex == self.numberOfItems - 1

    def clear(self):
        self.items = []
        self.currentItemIndex = 0
        self.scrollY = 0

    def adjustScroll(self, height):
        # Adjusts the list's scroll.
        if self.currentItemIndex < self.scrollY:
            self.scrollY = self.currentItemIndex
        elif self.currentItemIndex >= self.scrollY + height - 1:
            self.scrollY = self.currentItemIndex - height + 1

    def nextItem(self, amount=1):
        # Selects the next item in the list.
        for i in range(amount):
            if self.currentItemIndex < self.numberOfItems - 1:
                self.currentItemIndex += 1
            else:
                break

    def previousItem(self, amount=1):
        # Selects the previous item in the list.
        for i in range(amount):
            if self.currentItemIndex > 0:
                self.currentItemIndex -= 1
            else:
                break

