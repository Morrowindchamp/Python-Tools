class SlidingWindow:
    def __init__(self, iterable, window_size, placeholder=None, max_bound=True, step_size=1, circular=False, cache_window=True):
        """
        Initialize a sliding window optimized for LeetCode-style problems.
        
        :param iterable: The iterable to slide over (must support indexing and length).
        :param window_size: Target size of the sliding window (positive integer).
        :param placeholder: Value used for out-of-bounds elements when max_bound=False (default None).
        :param max_bound: If True, constrains window to iterable bounds; if False, uses placeholders.
        :param step_size: Number of positions to slide per step (positive integer, default 1).
        :param circular: If True, window wraps around the iterable.
        :param cache_window: If True, caches the current window for performance.
        :raises TypeError: If iterable doesn't support indexing or length.
        :raises ValueError: If window_size or step_size is not a positive integer.
        """
        if not hasattr(iterable, '__getitem__') or not hasattr(iterable, '__len__'):
            raise TypeError("Iterable must support indexing and have a length (e.g., list, tuple).")
        if not isinstance(window_size, int) or window_size <= 0:
            raise ValueError("Window size must be a positive integer.")
        if not isinstance(step_size, int) or step_size <= 0:
            raise ValueError("Step size must be a positive integer.")
        
        self.iterable = iterable
        self.window_size = window_size
        self.placeholder = placeholder
        self.max_bound = max_bound
        self.step_size = step_size
        self.circular = circular
        self.cache_window = cache_window
        self.start = 0
        self._window_cache = None
        self._cache_valid = False
        self._update_end()

    def _update_end(self):
        """Update the end index based on start, window size, and mode."""
        if self.circular:
            self.end = (self.start + self.window_size - 1) % len(self.iterable)
        else:
            self.end = self.start + self.window_size - 1
            if self.max_bound:
                self.end = min(self.end, len(self.iterable) - 1)
        self._cache_valid = False

    def get_window(self):
        """
        Retrieve the current window efficiently.
        
        :return: List of elements in the current window.
        :note: When cache_window=True, reuses cached window if valid; impacts performance for frequent calls.
        """
        if self.cache_window and self._cache_valid:
            return self._window_cache
        
        n = len(self.iterable)
        if self.circular:
            if self.end >= self.start:
                result = self.iterable[self.start:self.end + 1]
            else:
                result = self.iterable[self.start:] + self.iterable[:self.end + 1]
        else:
            end = min(self.start + self.window_size, n) if self.max_bound else self.start + self.window_size
            result = self.iterable[self.start:end]
            if not self.max_bound and len(result) < self.window_size:
                result = list(result) + [self.placeholder] * (self.window_size - len(result))
        
        if self.cache_window:
            self._window_cache = result
            self._cache_valid = True
        return result

    def slide(self, steps=None):
        """
        Slide the window forward by the specified steps.
        
        :param steps: Number of steps to move (defaults to step_size).
        :return: True if the window moved, False otherwise.
        """
        steps = steps if steps is not None else self.step_size
        old_start = self.start
        self.start += steps
        if self.circular:
            self.start %= len(self.iterable)
        elif self.max_bound:
            self.start = min(self.start, max(0, len(self.iterable) - self.window_size))
        self._update_end()
        return self.start != old_start

    def reverse_slide(self, steps=None):
        """
        Slide the window backward by the specified steps.
        
        :param steps: Number of steps to move back (defaults to step_size).
        :return: True if the window moved, False otherwise.
        """
        steps = steps if steps is not None else self.step_size
        old_start = self.start
        self.start -= steps
        if self.circular:
            self.start %= len(self.iterable)
        else:
            self.start = max(0, self.start)
        self._update_end()
        return self.start != old_start

    def apply_function(self, func):
        """
        Apply a function to the current window efficiently.
        
        :param func: Callable to apply to the window.
        :return: Result of the function applied to the window.
        :raises TypeError: If func is not callable.
        """
        if not callable(func):
            raise TypeError("The provided function must be callable.")
        if self.circular or not self.max_bound:
            return func(self.get_window())
        end = min(self.start + self.window_size, len(self.iterable))
        return func(self.iterable[self.start:end])

    def is_valid(self, condition_func):
        """
        Check if the current window satisfies a condition.
        
        :param condition_func: Callable returning a boolean.
        :return: True if condition is met, False otherwise.
        :raises TypeError: If condition_func is not callable.
        """
        if not callable(condition_func):
            raise TypeError("The condition function must be callable.")
        if self.circular or not self.max_bound:
            return condition_func(self.get_window())
        end = min(self.start + self.window_size, len(self.iterable))
        return condition_func(self.iterable[self.start:end])

    def sliding_iterator(self, infinite=False):
        """
        Yield successive windows as the window slides.
        
        :param infinite: If True and circular=True, yields indefinitely.
        :yield: Current window at each step.
        """
        if self.circular:
            if infinite:
                while True:
                    yield self.get_window()
                    self.slide()
            else:
                initial_start = self.start
                while True:
                    yield self.get_window()
                    self.slide()
                    if self.start == initial_start:
                        break
        else:
            while True:
                yield self.get_window()
                if not self.slide():
                    break

    def reset(self):
        """Reset the window to the initial position."""
        self.start = 0
        self._update_end()

    def is_at_start(self):
        """Check if the window is at the start of the iterable."""
        return self.start == 0

    def is_at_end(self):
        """
        Check if the window is at the end of the iterable.
        
        :return: True if at end (non-circular), False otherwise.
        """
        if self.circular:
            return False
        elif self.max_bound:
            return self.start >= len(self.iterable) - self.window_size
        return False

    def target_size(self):
        """Return the target window size specified at initialization."""
        return self.window_size

    def current_size(self):
        """
        Return the current number of actual elements in the window from the iterable.
        
        :note: Excludes placeholders in unbounded mode.
        """
        if self.circular:
            return self.window_size
        end = min(self.start + self.window_size, len(self.iterable)) if self.max_bound else self.start + self.window_size
        return min(end - self.start, max(0, len(self.iterable) - self.start))

    def resize(self, new_size):
        """
        Dynamically resize the window.
        
        :param new_size: New window size (positive integer).
        :raises ValueError: If new_size is not a positive integer.
        """
        if not isinstance(new_size, int) or new_size <= 0:
            raise ValueError("New window size must be a positive integer.")
        self.window_size = new_size
        self._update_end()
