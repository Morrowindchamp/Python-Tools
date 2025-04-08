class SafeArray(list):
    def __init__(self, arr, placeholder="OUT_OF_BOUNDS"):
        super().__init__(arr)
        self.placeholder = placeholder

    def __getitem__(self, index):
        if isinstance(index, int):  # Handle single index access
            if 0 <= index < len(self):
                return list.__getitem__(self, index)
            return self.placeholder
        elif isinstance(index, slice):  # Handle slice access
            # Constrain stop value to len(self)
            start, stop, step = index.start or 0, min(index.stop or len(self), len(self)), index.step or 1
            return SafeArray([list.__getitem__(self, i) for i in range(start, stop, step) if 0 <= i < len(self)], placeholder=self.placeholder)
        else:
            raise TypeError("Invalid index type")
