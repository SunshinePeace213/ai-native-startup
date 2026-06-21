# Python Traceback Semantics (not obvious from docs)

Reference for the `format-error` skill. Read when the traceback's apparent cause doesn't match what the docs would suggest.

## `__init_subclass__` errors

When a subclass declaration fails with `TypeError` inside `__init_subclass__`, the traceback shows the *class body* as the failing call, not the metaclass that ran the check. The fix usually lives in the parent class's `__init_subclass__` definition — search there first.

## `RecursionError`

Doesn't necessarily mean the function calls itself directly. Watch for:

- Property/`__getattr__` cycles (a `@property` that reads an attribute the property is supposed to compute)
- Comparison operator cycles (`__eq__` that delegates to a method that calls `==` on the same object)
- ORM relationship loading triggering re-fetch on every access

## `KeyError` from `dict.__missing__`

When a `defaultdict` or `UserDict` subclass raises `KeyError`, the key shown is the one that fell through `__missing__`. The fix isn't always "add the key" — sometimes `__missing__` is supposed to handle it but a recent change broke that path.

## `AttributeError` from `__slots__`

Shows up identically to a normal missing attribute, but the fix is different: you can't just assign the attribute. Either add it to `__slots__` or remove `__slots__` from the class.

## Async tracebacks

The frame ordering shows the awaiter first, then the awaitee. The actual failing line is usually 2-3 frames in, after the event loop scheduling frames. Look for the deepest frame in the user's code, not the deepest frame overall.

## Pytest assertion rewriting

`assert x == y` in pytest is rewritten to show both sides. The traceback shows the *rewritten* expression — if it's confusing, the user's source code may not match what you see.
