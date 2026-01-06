To understand how Python code transforms from text into an active process, you have to look at the **CPython Pipeline**. CPython (the standard version of Python) acts as both a compiler and an interpreter.

Here is the step-by-step architectural breakdown of that execution flow.

### Step 1: Lexical Analysis and Parsing

When you run `python script.py`, the first thing the engine does is read your source code.

- **Tokenizing:** The **Lexer** breaks your text into "tokens" (keywords, variables, operators).
- **Parsing:** The **Parser** takes those tokens and organizes them into a tree structure called the **Abstract Syntax Tree (AST)**. This validates that your code follows Python's grammar rules.

### Step 2: Compiling to Bytecode

Once the AST is ready, the Python compiler converts it into **Bytecode**.

- **What is Bytecode?** It is a low-level, platform-independent set of instructions. It isn't machine code (binary that your CPU understands); it is code specifically designed for the **Python Virtual Machine (PVM)**.
- **The `.pyc` File:** If you see a `__pycache__` folder, those are your compiled bytecode files. This step happens once so that the next time you run the script, Python can skip Step 1 and 2.

### Step 3: Initializing the PVM (The Interpreter)

Now the **Python Virtual Machine** kicks in. It is a "stack-based" evaluator.

- Unlike your physical CPU, which uses "Registers" to do math, the PVM uses a **Stack**.
- To add two numbers, it "pushes" them onto a stack, calls an `ADD` instruction, and "pops" the result off.

### Step 4: The Eval Loop and the GIL

This is the most critical step for performance. The PVM starts a giant loop (the **Eval Loop**) that reads your bytecode instructions one by one.

- **Acquiring the GIL:** Before the Eval Loop can execute even a single line of bytecode, the thread must acquire the **Global Interpreter Lock (GIL)**.
- **Thread Safety:** Because Python’s memory management (Reference Counting) is not "thread-safe," the GIL acts as a bottleneck. It ensures that only one thread can hold the "key" to the PVM at a time.
- **The Context Switch:** If you have multiple threads, they must take turns. Thread A runs for a bit, then Python forces it to release the GIL so Thread B can run.

### Step 5: C-Level Execution

Finally, the PVM maps each bytecode instruction to a specific function written in **C**.

- For example, the bytecode `BINARY_ADD` triggers a C function in the Python source code (`ceval.c`) that handles the addition of two Python objects.
- The C code interacts with your hardware (CPU/RAM) to perform the actual work.

### Summary Checklist

1. **Source Code:** Human-readable `.py`.
2. **AST:** Structural map of your logic.
3. **Bytecode:** The `.pyc` instructions for the VM.
4. **GIL:** The lock that ensures only 1 thread "speaks" to the VM at a time.
5. **PVM:** The stack-based engine that executes the instructions using C.
