import functools

from semantic_version import Version as _V

from .. import errors


def minimum_version(version):
    def decorator(f):
        @functools.wraps(f)
        def wrapper(self, *args, **kwargs):
            if _V(self.dce_version) < _V(version):
                raise errors.InvalidVersion(
                    '{0} is not available for DCE version < {1}'.format(
                        f.__name__, version
                    )
                )
            return f(self, *args, **kwargs)

        return wrapper

    return decorator


def maximum_version(version):
    def decorator(f):
        @functools.wraps(f)
        def wrapper(self, *args, **kwargs):
            if _V(self.dce_version) > _V(version):
                raise errors.InvalidVersion(
                    '{0} is not available for DCE version > {1}'.format(
                        f.__name__, version
                    )
                )
            return f(self, *args, **kwargs)

        return wrapper

    return decorator
