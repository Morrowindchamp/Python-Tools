class SlidingWindow:
    def __init__(self, iterable, window_size, placeholder=None, max_bound=True, step_size=1, circular=False, cache_window=True):
        """
        Initialize a sliding window with optimizations for LeetCode problems.
        :param iterable: The iterable to operate on (e.g., list, tuple, string). Converts non-indexable iterables to list.
        :param window_size: Initial size of the window (positive integer).
        :param placeholder: Value for out-of-bounds access (default None).
        :param max_bound: If True, keeps window within bounds; False allows placeholders.
        :param step_size: Number of steps to slide (default 1).
        :param circular: Enables circular wraparound when True.
        :param cache_window: If True, caches the current window for reuse.
        """
        if not hasattr(iterable, '__getitem__'):
            raise TypeError("Iterable must support indexing (e.g., list, array).")
        if not isinstance(window_size, int) or window_size <= 0:
            raise ValueError("Window size must be a positive integer.")
        
        # Preserve iterable if indexable and sized, otherwise convert to list
        self.iterable = iterable if hasattr(iterable, '__len__') else list(iterable)
        self.window_size = window_size
        self.placeholder = placeholder
        self.max_bound = max_bound
        self.step_size = step_size
        self.circular = circular
        self.cache_window = cache_window
        self.start = 0
        self.end = min(window_size - 1, len(self.iterable) - 1) if max_bound else window_size - 1
        self._window_cache = None
        self._cache_valid = False
        self._validate_bounds()

    def _validate_bounds(self):
        """Ensure start and end are within limits."""
        if self.max_bound:
            self.start = max(0, min(self.start, len(self.iterable) - self.window_size))
            self.end = min(self.start + self.window_size - 1, len(self.iterable) - 1)
        else:
            self.end = self.start + self.window_size - 1
        self._cache_valid = False

    def get_window(self):
        """Retrieve the current window efficiently."""
        if self.cache_window and self._cache_valid:
            return self._window_cache
        
        if self.circular:
            n = len(self.iterable)
            result = [self.iterable[i % n] for i in range(self.start, self.start + self.window_size)]
        else:
            end = min(self.start + self.window_size, len(self.iterable)) if self.max_bound else self.start + self.window_size
            result = self.iterable[self.start:end]
            if len(result) < self.window_size:
                result = list(result) + [self.placeholder] * (self.window_size - len(result))
        
        if self.cache_window:
            self._window_cache = result
            self._cache_valid = True
        return result

    def slide(self, steps=None):
        """Slide the window forward by steps. Returns True if moved."""
        steps = steps if steps is not None else self.step_size
        old_start = self.start
        self.start += steps
        if self.circular:
            self.start %= len(self.iterable)
            self._validate_bounds()
        elif self.max_bound:
            self.start = min(self.start, max(0, len(self.iterable) - self.window_size))
            self._validate_bounds()
        else:
            self.end = self.start + self.window_size - 1
            self._cache_valid = False
        return self.start != old_start

    def reverse_slide(self, steps=None):
        """Slide the window backward by steps. Returns True if moved."""
        steps = steps if steps is not None else self.step_size
        old_start = self.start
        self.start -= steps
        if self.circular:
            self.start %= len(self.iterable)
            self._validate_bounds()
        else:
            self.start = max(0, self.start)
            self._validate_bounds()
        return self.start != old_start

    def apply_function(self, func):
        """Apply a function to the current window."""
        if not callable(func):
            raise TypeError("The provided function must be callable.")
        if self.circular:
            return func(self.get_window())
        end = min(self.start + self.window_size, len(self.iterable)) if self.max_bound else self.start + self.window_size
        return func(self.iterable[self.start:end])

    def is_valid(self, condition_func):
        """Check if the current window satisfies a condition."""
        if not callable(condition_func):
            raise TypeError("The condition function must be callable.")
        if self.circular:
            return condition_func(self.get_window())
        end = min(self.start + self.window_size, len(self.iterable)) if self.max_bound else self.start + self.window_size
        return condition_func(self.iterable[self.start:end])

    def on_slide(self, callback):
        """Trigger a callback after sliding."""
        if not callable(callback):
            raise TypeError("Callback must be callable.")
        callback(self.get_window())

    def sliding_iterator(self, infinite=False):
        """
        Yield windows as the sliding window moves.
        :param infinite: If True and circular=True, loops indefinitely.
        """
        if self.circular and infinite:
            while True:
                yield self.get_window()
                self.slide()
        else:
            while not self.is_at_end():
                yield self.get_window()
                self.slide()

    def reset(self):
        """Reset the window to initial position."""
        self.start = 0
        self.end = min(self.window_size - 1, len(self.iterable) - 1) if self.max_bound else self.window_size - 1
        self._cache_valid = False

    def is_at_start(self):
        """Check if window is at the start."""
        return self.start == 0

    def is_at_end(self):
        """Check if window is at the end."""
        return self.end >= len(self.iterable) - 1 if self.max_bound else False

    def size(self):
        """Return current window size."""
        return self.window_size
