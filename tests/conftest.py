import os
import sys


_unlink = os.unlink
_deferred = set()


if sys.platform == "win32":
    def _windows_safe_unlink(path, *args, **kwargs):
        try:
            return _unlink(path, *args, **kwargs)
        except PermissionError:
            _deferred.add(os.fspath(path))

    os.unlink = _windows_safe_unlink
