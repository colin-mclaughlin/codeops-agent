# Demo Calculator

A simple calculator with basic arithmetic operations.

## Features

- Addition
- Subtraction  
- Multiplication
- Division (with zero-division protection)

## Running Tests

```bash
pytest test_calculator.py -v
```

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```python
from calculator import add, subtract, multiply, divide

result = add(2, 3)  # 5
result = divide(10, 2)  # 5.0
```
