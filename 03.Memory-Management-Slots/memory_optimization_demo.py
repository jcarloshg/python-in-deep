"""
memory_optimization_demo.py

Technical demonstration: memory impact of Python classes with and without __slots__,
including GC and circular references.

- StandardCoordinate: typical class
- OptimizedCoordinate: memory-optimized with __slots__
- Benchmarks memory for 1 million instances
- Shows a circular reference scenario for GC explanation
- Rich comments compare CPython vs Node.js V8 GC and explain tradeoffs of __slots__
"""

import sys
import gc
from time import perf_counter

try:
    from pympler import asizeof  # type: ignore
    pympler_available = True
except ImportError:
    asizeof = None
    pympler_available = False


class StandardCoordinate:
    """Standard, flexible Python class. Each instance has a __dict__ and can have new attributes attached dynamically."""

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        # Demonstrating attribute flexibility (no __slots__):
        # self.z = 123  # Would work


class OptimizedCoordinate:
    """
    Memory-optimized using __slots__.
    __slots__ disables the per-instance __dict__ (saves memory) and __weakref__ by default.
    Attribute set is static: cannot add attributes beyond those in __slots__.
    Behaves more like a C struct or TS Interface (hidden class in V8).
    """
    __slots__ = ('x', 'y')

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y


def get_total_size(obj_list, label):
    if pympler_available and asizeof is not None:
        size = asizeof.asizeof(obj_list)
        print(f"[pympler] {label:>30}: {size/1024/1024:.2f} MB (deep size)")
    else:
        summed = sum(sys.getsizeof(o)
                     for o in obj_list) + sys.getsizeof(obj_list)
        print(
            f"[sys.getsizeof] {label:>30}: {summed/1024/1024:.2f} MB (*shallow* size)")


def main():

    print("─────────────────────────────────────")
    print("Python Memory Management: __slots__ vs Standard Class")
    print("─────────────────────────────────────")

    COUNT = 1_000_000

    t0 = perf_counter()
    standard_objs = [StandardCoordinate(i, -i) for i in range(COUNT)]
    t1 = perf_counter()
    get_total_size(standard_objs, "StandardCoordinate x 1,000,000")
    print(f"  Creation time: {t1-t0:.2f}s\n")

    t2 = perf_counter()
    optimized_objs = [OptimizedCoordinate(i, -i) for i in range(COUNT)]
    t3 = perf_counter()
    get_total_size(optimized_objs, "OptimizedCoordinate x 1,000,000")
    print(f"  Creation time: {t3-t2:.2f}s\n")

    print("─────────────────────────────────────")
    print("Circular Reference & Garbage Collector Demo")
    print("─────────────────────────────────────")
    # Circular reference: Not freed by immediate reference counting
    from typing import Optional

    class Circular:
        def __init__(self):
            # type: ignore for forward reference
            self.friend: Optional["Circular"] = None
    a = Circular()
    b = Circular()
    a.friend = b
    b.friend = a  # Create cycle: a <-> b
    del a, b  # Reference count for each is nonzero due to cycle!
    unreachable = gc.collect()
    print(
        f"  gc.collect() ran; unreachable objects found and cleaned: {unreachable}")
    # Refcounting cannot reclaim cycles. CPython's generational GC solves this.

    print("\n--- Technical Annotations ---")
    print("- __slots__ prevents the creation of __dict__ and __weakref__ attributes on each instance,\n  which offers significant memory savings when you have many objects of the same type.")
    print("- Tradeoff: You cannot add new attributes at runtime. __slots__ classes are 'static'.")
    print("  Like a C struct or a fixed-shape object in JavaScript V8.")
    print("- Standard classes are more flexible, but each instance stores a dict (even if unused), costing memory.")

    print("\n--- Comparison Context ---")
    print('''\
"""
In CPython, most objects are managed by reference counting—when all references disappear, the object is deleted immediately.
But cycles (such as objects referencing each other) require an extra garbage collector pass (generational, using the gc module).

Node.js V8, in contrast, uses mark-and-sweep GC by default, which means objects are only cleaned up during scheduled GC passes,
not as soon as they're unreachable. V8 optimizes memory via "hidden classes"—very similar to how __slots__ works in Python:
it locks down property names (attributes), reducing lookup and storage overhead, like a C struct or TypeScript interface.
"""
''')


if __name__ == "__main__":
    main()
