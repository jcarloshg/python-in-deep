"""
dunder_protocol_demo.py

A production-grade demonstration of Python's data model using dunder (magic) methods for advanced object-oriented architectures.

- ImmutableConfig: Shows __new__ versus __init__ for singleton/immutable configuration.
- CustomCollection: Demonstrates Python's duck typing and collection protocol (__getitem__, __setitem__, __len__).
- Includes MRO notes, interpreter hook documentation, and a comparison of duck typing with TypeScript interfaces.
"""

from typing import Any, Iterator


class ImmutableConfig:
    """
    An immutable (and optionally singleton) configuration object.

    __new__ ensures only one instance per unique configuration key.
    The object is fully immutable after creation—modifications raise exceptions.
    Demonstrates a core difference between __new__ and __init__.
    """
    _instances = {}
    _locked = False

    def __new__(cls, key: str, value: Any):
        # __new__ is called before instance creation.
        # It controls actual object allocation and allows custom construction logic,
        # such as implementing singletons or immutable value objects.
        print(f"ImmutableConfig.__new__ key=[{key!r}], value={value!r}")
        if key in cls._instances:
            # Singleton: ensure only one instance exists per key
            return cls._instances[key]
        # Allocate a new instance (object memory) before __init__ runs
        obj = super().__new__(cls)
        obj._locked = False  # Allow attribute setting during initialization
        cls._instances[key] = obj
        return obj

    def __init__(self, key: str, value: Any):
        # __init__ is called after instance is created.
        # Used for initialization, not allocation
        print(f"ImmutableConfig.__init__ key={key!r}, value={value!r}")
        if getattr(self, '_locked', False):
            print("ImmutableConfig.__init__ skipped (already initialized)")
            return  # Already initialized; skip running init again
        self.key = key
        self.value = value
        # Prevent further attribute modification (immutability)
        self._locked = True

    def __setattr__(self, name, value):
        # __setattr__ is called whenever an attribute assignment is attempted.
        # By overriding it, we enforce custom logic—here, immutability after initialization.
        # If _locked is True, only allow internal attributes ('_locked', '_instances') to be changed.
        # Raises AttributeError on any change attempt to other attributes post-init.
        print(f"ImmutableConfig.__setattr__ called for {name}={value!r}")
        if getattr(self, '_locked', False) and name not in {'_locked', '_instances'}:
            raise AttributeError(
                f"ImmutableConfig: Cannot modify attribute '{name}' after initialization")
        super().__setattr__(name, value)

    def __repr__(self):
        # __repr__ provides a developer-facing string representation of the object.
        # it was called for debugging, logging, and interactive sessions. print calls it.
        return f"<ImmutableConfig key={self.key!r} value={self.value!r}> brbr"

    def __eq__(self, other):
        # __eq__ defines equality comparison between two instances.
        # Here, two ImmutableConfig instances are equal if their keys and values match.
        print(f"ImmutableConfig.__eq__ called: self={self}, other={other}")
        if isinstance(other, ImmutableConfig):
            return self.key == other.key and self.value == other.value
        return NotImplemented

# ---- Interpreter Hook Explanation ----
# __new__ is called *before* an object is created (allocates memory, returns instance)
# __init__ is called *after* the object exists (sets attributes on the instance)
# In this pattern, __new__ controls uniqueness and immutability; __init__ only operates on a fresh object

# ---- MRO (Method Resolution Order) Note ----
# Both __new__ and __init__ are found using the MRO. If the superclass defines them,
# Python searches the MRO chain for the first matching implementation. This affects
# multi-inheritance, singletons, and advanced metaclasses.


class CustomCollection:
    """
    A custom collection supporting duck-typed list/dict operations.
    Demonstrates __getitem__, __setitem__, __len__, __repr__, __str__, and duck typing.
    """

    def __init__(self, initial=None):
        self._store = dict(initial) if initial else {}

    def __getitem__(self, key):
        print(f"CustomCollection.__getitem__ called for key={key!r}")
        return self._store[key]

    def __setitem__(self, key, value):
        print(
            f"CustomCollection.__setitem__ called for key={key!r}, value={value!r}")
        self._store[key] = value

    def __len__(self):
        len_ = len(self._store)
        print("CustomCollection.__len__ called ->", len_)
        return len_

    def __iter__(self) -> Iterator:
        iter_ = iter(self._store)
        print("CustomCollection.__iter__ called ->", iter_)
        return iter_

    def __repr__(self):
        """Developer-facing representation with technical details"""
        str_ = f"CustomCollection({self._store!r})"
        print("CustomCollection.__repr__ called ->", str_)
        return str_

    def __str__(self):
        """End-user friendly summary"""
        str_ = f"CustomCollection with {len(self)} items: {list(self._store.items())}"
        print("CustomCollection.__str__ called ->", str_)
        return str_

# ---- Interpreter Hook Explanation ----
# __getitem__ is called when you do obj[key]. __setitem__ when assigning (obj[key] = x).
# __len__ is used by len(obj). __repr__ and __str__ serve for print(), repr(), logging, formatting, etc.
# These hooks are discovered via the class's MRO when an operation is invoked.

# ---- MRO (Method Resolution Order) Note ----
# If you inherit from both dict and a custom parent, Python's MRO determines which __getitem__ is used first.

# ---- TypeScript Comparison ----
# """
# In TypeScript:
# interface Example {
#     get(key: string): number;
#     set(key: string, value: number): void;
# }
# class MyCollection implements Example {
#     ...
# }
# // Explicit contract: MyCollection must implement Example.
#
# In Python:
# class MyCollection:
#     def __getitem__(self, k): ...
#     def __setitem__(self, k, v): ...
# # Any code expecting __getitem__/__setitem__ will work with MyCollection ('duck typing').
# # No 'implements' clause needed—the protocol is implicit and structural, not nominal.
# """


if __name__ == "__main__":

    # ImmutableConfig demo

    print("─────────────────────────────────────")
    print("ImmutableConfig demo")
    print("─────────────────────────────────────")

    config1 = ImmutableConfig("API_URL", "https://example.org")
    print("\n")
    config2 = ImmutableConfig("API_URL", "ignored-value")
    print("\n")

    print(f"config1: {config1}")
    print(f"config2: {config2}")
    print("\n")

    print("config1 is config2?", config1 is config2)  # Singleton/Value-object

    try:
        config1.value = "I want to change? is it allowed?"
    except AttributeError as e:
        print("Caught immutability violation:", e)

    # CustomCollection demo

    print("─────────────────────────────────────")
    print("CustomCollection demo")
    print("─────────────────────────────────────")

    coll = CustomCollection({"a": 1, "b": 2})
    print(f"repr(coll) -> {repr(coll)} \n")
    print(f"str(coll) -> {str(coll)} \n")
    coll["c"] = 3
    print(f"list(coll) -> {list(coll)} \n")
    print(f"coll['b'] = {coll['b']} \n")
    print(f"len(coll) = {len(coll)} \n")


# RESULT:

# config1 is config2? True
# <ImmutableConfig key='API_URL' value='https://example.org'>
# Caught immutability violation: ImmutableConfig: Cannot modify attribute 'value' after initialization
# CustomCollection({'a': 1, 'b': 2})
# CustomCollection with 2 items: [('a', 1), ('b', 2)]
# ['a', 'b', 'c']
# coll['b'] = 2
# len(coll) = 3
