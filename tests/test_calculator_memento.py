import pytest
from decimal import Decimal
from datetime import datetime
from app.calculation import Calculation
from app.calculator_memento import CalculatorMemento
from app.exceptions import OperationError

#####################################################
##### unit test for line 34 of app/calculator_memento.py
"""
This unit test verifies that CalculatorMemento.from_dict() works correctly by checking
that a memento can be deserialized from a dictionary and reconstructs
the original CalculatorMemento, including its history and timestamp.
"""

def test_calculator_memento_to_dict():
    # Arrange: create some Calculation instances
    calc1 = Calculation(operation="Addition", operand1=Decimal("2"), operand2=Decimal("3"))
    calc2 = Calculation(operation="Multiplication", operand1=Decimal("4"), operand2=Decimal("5"))

    # Create a CalculatorMemento with these calculations
    memento = CalculatorMemento(history=[calc1, calc2])

    # Act: convert to dictionary
    memento_dict = memento.to_dict()

    # Assert: dictionary has correct keys
    assert 'history' in memento_dict
    assert 'timestamp' in memento_dict

    # Assert: history is a list of dicts
    assert isinstance(memento_dict['history'], list)
    assert all(isinstance(item, dict) for item in memento_dict['history'])

    # Assert: each history dict matches the Calculation.to_dict output
    assert memento_dict['history'][0] == calc1.to_dict()
    assert memento_dict['history'][1] == calc2.to_dict()

    # Assert: timestamp is ISO formatted string
    assert isinstance(memento_dict['timestamp'], str)
    assert datetime.fromisoformat(memento_dict['timestamp']) == memento.timestamp

"""
This unit test verifies that CalculatorMemento.to_dict() works correctly when
the memento has an empty history. It ensures that the 'history' key is an empty
list and that the 'timestamp' is correctly included and formatted as an ISO string.
"""

def test_calculator_memento_to_dict_empty_history():
    # Arrange: empty history
    memento = CalculatorMemento(history=[])

    # Act
    memento_dict = memento.to_dict()

    # Assert
    assert memento_dict['history'] == []
    assert isinstance(memento_dict['timestamp'], str)
    assert datetime.fromisoformat(memento_dict['timestamp']) == memento.timestamp

#####################################################
##### unit test for line 53 of app/calculator_memento.py
"""
This unit test verifies that CalculatorMemento.from_dict() raises a KeyError
when the input dictionary is missing the required top-level 'timestamp' key.
It ensures that deserialization fails predictably with incomplete data.
"""


def test_calculator_memento_from_dict_invalid_data():
    # Arrange: invalid dictionary missing timestamp
    invalid_dict = {
        "history": [
            {
                "operation": "Addition",
                "operand1": "2",
                "operand2": "3",
                "result": "5",
                "timestamp": datetime.now().isoformat()
            }
        ]
        # 'timestamp' key missing
    }

    # Act & Assert: Should raise KeyError when trying to access missing timestamp
    with pytest.raises(KeyError):
        CalculatorMemento.from_dict(invalid_dict)


"""
This unit test verifies that CalculatorMemento.from_dict() raises an OperationError
when the input dictionary contains invalid calculation data in the history.
It ensures that deserialization fails if any Calculation cannot be reconstructed
properly, such as when operands are not valid decimals.
"""


def test_calculator_memento_from_dict_invalid_calculation():
    # Arrange: dictionary with invalid calculation data
    invalid_dict = {
        "history": [
            {
                "operation": "Addition",
                "operand1": "invalid",
                "operand2": "3",
                "result": "5",
                "timestamp": datetime.now().isoformat()
            }
        ],
        "timestamp": datetime.now().isoformat()
    }

    # Act & Assert: Should raise OperationError from Calculation.from_dict
    with pytest.raises(OperationError):
        CalculatorMemento.from_dict(invalid_dict)