"""Input handling for joystick and button mapping."""

from retro_console import settings


class InputHandler:
    """Handles input from the terminal and maps to logical buttons."""

    def __init__(self, terminal):
        self.terminal = terminal
        self._build_reverse_mapping()

    def _build_reverse_mapping(self):
        """Build reverse mapping from key names to logical buttons."""
        self._key_to_logical = {}
        for logical, physical in settings.KEY_MAPPING.items():
            self._key_to_logical[physical] = logical

    def read_key(self, timeout=None):
        """Read a key press and return (raw_key, logical_key) tuple.

        Returns (None, None) if timeout expires with no input.
        """
        with self.terminal.cbreak():
            if timeout is not None:
                key = self.terminal.inkey(timeout=timeout)
            else:
                key = self.terminal.inkey()

        if not key:
            return (None, None)

        # Get the key name (e.g., "KEY_UP") or the character itself
        if key.is_sequence:
            raw_key = key.name
        else:
            raw_key = str(key)

        logical_key = self._key_to_logical.get(raw_key)
        return (raw_key, logical_key)

    def wait_for_any_key(self, timeout=None):
        """Wait for any key press. Returns True if a key was pressed."""
        raw_key, _ = self.read_key(timeout=timeout)
        return raw_key is not None

    def wait_for_logical_key(self, allowed_keys=None, timeout=None):
        """Wait for a logical key press.

        If allowed_keys is specified, only return when one of those keys is pressed.
        Returns the logical key name, or None on timeout.
        """
        while True:
            raw_key, logical_key = self.read_key(timeout=timeout)

            if raw_key is None:
                return None

            if logical_key is None:
                continue

            if allowed_keys is None or logical_key in allowed_keys:
                return logical_key

    def is_debug_key(self, raw_key):
        """Check if the given key is the debug key."""
        return raw_key == settings.DEBUG_KEY
