class SafeArray(list):
    def __init__(self, arr, placeholder="OUT_OF_BOUNDS"):
        super().__init__(arr)
        self.placeholder = placeholder

    def __getitem__(self, index):
        if isinstance(index, int):
            # Check bounds explicitly, no wraparound for negative indices
            if -len(self) <= index < len(self):
                return list.__getitem__(self, index)
            return self.placeholder

        elif isinstance(index, slice):
            # Handle all slice cases including negative steps
            start, stop, step = self._normalize_slice(index)
            if step > 0:
                indices = range(max(0, start), min(len(self), stop), step)
            else:
                indices = range(min(len(self) - 1, start), max(-1, stop), step)
            
            result = [list.__getitem__(self, i) for i in indices]
            return SafeArray(result, placeholder=self.placeholder) if result else SafeArray([], placeholder=self.placeholder)

        else:
            raise TypeError("Invalid index type")

    def _normalize_slice(self, slice_obj):
        """Normalize slice parameters to handle all edge cases."""
        length = len(self)
        start = slice_obj.start
        stop = slice_obj.stop
        step = slice_obj.step or 1

        # Handle None values and normalize negative indices
        if start is None:
            start = 0 if step > 0 else length - 1
        elif start < 0:
            start = max(0, length + start)
        start = min(max(start, 0), length - 1) if step > 0 else min(max(start, -1), length - 1)

        if stop is None:
            stop = length if step > 0 else -1
        elif stop < 0:
            stop = max(-1, length + stop)
        stop = min(max(stop, -1), length)

        return start, stop, step

    def __len__(self):
        return super().__len__()
