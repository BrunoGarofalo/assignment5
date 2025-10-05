import pytest
import unittest
from unittest.mock import patch, MagicMock
from app.calculator_repl import calculator_repl
from app.calculation import Calculation
from decimal import Decimal
from app.exceptions import ValidationError, OperationError
from unittest.mock import patch
from io import StringIO
from app.calculator_repl import calculator_repl


#########################################################
########### Unit test for lines 54-55 of app/calculator_repl.py

"""
This unit test verifies that calculator_repl() prints a warning message
when Calculator.save_history() raises an exception during exit.
"""

def test_calculator_repl_save_history_exception(capsys):
    # Arrange: mock Calculator instance and its save_history method
    mock_calc = MagicMock()
    mock_calc.save_history.side_effect = Exception("Simulated save failure")

    # Patch Calculator to return our mock
    with patch("app.calculator_repl.Calculator", return_value=mock_calc):
        # Patch input to simulate user typing 'exit' immediately
        with patch("builtins.input", side_effect=["exit"]):
            # Act: run the REPL
            calculator_repl()

    # Assert: capture printed output and check for warning
    captured = capsys.readouterr()
    assert "Warning: Could not save history: Simulated save failure" in captured.out


"""
Test that calculator_repl prints the correct output when showing history.
Covers both empty history and non-empty history cases.
"""
def test_calculator_repl_show_history(capsys):


    # Arrange: create a mock Calculator
    mock_calc = MagicMock()

    # Case 1: empty history
    mock_calc.show_history.return_value = []
    with patch("app.calculator_repl.Calculator", return_value=mock_calc):
        with patch("builtins.input", side_effect=["history", "exit"]):
            calculator_repl()
    captured = capsys.readouterr()
    assert "No calculations in history" in captured.out

    # Case 2: non-empty history
    calc1 = Calculation(operation="Addition", operand1=Decimal("2"), operand2=Decimal("3"))
    calc2 = Calculation(operation="Multiplication", operand1=Decimal("4"), operand2=Decimal("5"))
    mock_calc.show_history.return_value = [calc1, calc2]

    with patch("app.calculator_repl.Calculator", return_value=mock_calc):
        with patch("builtins.input", side_effect=["history", "exit"]):
            calculator_repl()
    captured = capsys.readouterr()
    assert "Calculation History:" in captured.out
    assert f"1. {calc1}" in captured.out
    assert f"2. {calc2}" in captured.out

############################################################
######### unit tests for lines 135-140 of apps/calculator_repl.py

"""
Test that calculator_repl prints appropriate messages when exceptions occur
during arithmetic operations.
"""

def test_calculator_repl_handles_exceptions(capsys):


    # Arrange: mock Calculator and its methods
    mock_calc = MagicMock()
    # simulate set_operation() / perform_operation() behavior if needed
    mock_calc.perform_operation.side_effect = ValidationError("Invalid input")

    # Patch Calculator to return our mock
    with patch("app.calculator_repl.Calculator", return_value=mock_calc):
        # Simulate user entering a calculation command then exit
        with patch("builtins.input", side_effect=["add", "1", "2", "exit"]):
            calculator_repl()
    captured = capsys.readouterr()
    assert "Error: Invalid input" in captured.out

    # Now test OperationError
    mock_calc.perform_operation.side_effect = OperationError("Operation failed")
    with patch("app.calculator_repl.Calculator", return_value=mock_calc):
        with patch("builtins.input", side_effect=["add", "1", "2", "exit"]):
            calculator_repl()
    captured = capsys.readouterr()
    assert "Error: Operation failed" in captured.out

    # Now test a generic unexpected Exception
    mock_calc.perform_operation.side_effect = Exception("Unexpected issue")
    with patch("app.calculator_repl.Calculator", return_value=mock_calc):
        with patch("builtins.input", side_effect=["add", "1", "2", "exit"]):
            calculator_repl()
    captured = capsys.readouterr()
    assert "Unexpected error: Unexpected issue" in captured.out


#################################################
##### Unit test for lines 103-108 of apps/calculator_repl.py


"""
Test that calculator_repl prints the correct message when loading history.
Covers both successful load and exception scenarios.
"""

def test_calculator_repl_load_history(capsys):


    # Arrange: mock Calculator
    mock_calc = MagicMock()

    # Case 1: successful load
    mock_calc.load_history.return_value = None
    with patch("app.calculator_repl.Calculator", return_value=mock_calc):
        with patch("builtins.input", side_effect=["load", "exit"]):
            calculator_repl()
    captured = capsys.readouterr()
    assert "History loaded successfully" in captured.out

    # Case 2: load_history raises Exception
    mock_calc.load_history.side_effect = Exception("Failed to load")
    with patch("app.calculator_repl.Calculator", return_value=mock_calc):
        with patch("builtins.input", side_effect=["load", "exit"]):
            calculator_repl()
    captured = capsys.readouterr()
    assert "Error loading history: Failed to load" in captured.out


#################################################
##### Unit test for lines 120-121 of apps/calculator_repl.py

"""
Test that entering 'cancel' for the second number cancels the operation
and prints 'Operation cancelled'.
"""

def test_second_number_cancel():

    with patch('builtins.input', side_effect=['add', '5', 'cancel', 'exit']), \
         patch('sys.stdout', new_callable=StringIO) as mock_stdout:
        calculator_repl()
        output = mock_stdout.getvalue()

        # Check that "Operation cancelled" appears in the output
        assert "Operation cancelled" in output

        # Check that the REPL eventually exits
        assert "Goodbye!" in output


#################################################
##### Unit test for lines 94-99 of apps/calculator_repl.py

"""
Test that the 'save' command calls save_history and prints success message.
"""


def test_save_command_success():
    with patch('builtins.input', side_effect=['save', 'exit']), \
         patch('sys.stdout', new_callable=StringIO) as mock_stdout:

        # Patch Calculator inside the module to return a single instance
        with patch('app.calculator_repl.Calculator') as MockCalculator:
            mock_calc = MockCalculator.return_value
            # Reset call count for save_history
            mock_calc.save_history.reset_mock()

            calculator_repl()

            # Assert save_history was called at least once
            assert mock_calc.save_history.call_count >= 1
            output = mock_stdout.getvalue()
            assert "History saved successfully" in output

"""
Test that if save_history raises an exception, the error message is printed.
"""

def test_save_command_exception():
    with patch('builtins.input', side_effect=['save', 'exit']), \
         patch('sys.stdout', new_callable=StringIO) as mock_stdout, \
         patch('app.calculator_repl.Calculator.save_history', side_effect=Exception("disk full")) as mock_save:
        
        calculator_repl()
        
        # Ensure save_history was called at least once
        assert mock_save.call_count >= 1
        
        output = mock_stdout.getvalue()
        assert "Error saving history: disk full" in output


#################################################
##### Unit test for lines 86-90 of apps/calculator_repl.py

"""
Test that 'redo' prints 'Operation redone' when redo() returns True.
"""

def test_redo_success():

    with patch('builtins.input', side_effect=['redo', 'exit']), \
         patch('sys.stdout', new_callable=StringIO) as mock_stdout, \
         patch('app.calculator_repl.Calculator.redo', return_value=True) as mock_redo:
        
        calculator_repl()
        
        output = mock_stdout.getvalue()
        # Check that redo() was called
        assert mock_redo.call_count >= 1
        # Check correct message
        assert "Operation redone" in output


"""
Test that 'redo' prints 'Nothing to redo' when redo() returns False.
"""

def test_redo_nothing_to_redo():

    with patch('builtins.input', side_effect=['redo', 'exit']), \
         patch('sys.stdout', new_callable=StringIO) as mock_stdout, \
         patch('app.calculator_repl.Calculator.redo', return_value=False) as mock_redo:
        
        calculator_repl()
        
        output = mock_stdout.getvalue()
        # Check that redo() was called
        assert mock_redo.call_count >= 1
        # Check correct message
        assert "Nothing to redo" in output


#################################################
##### Unit test for lines 78-82 of apps/calculator_repl.py

"""
Test that 'undo' prints 'Operation undone' when undo() returns True.
"""

def test_undo_success():

    with patch('builtins.input', side_effect=['undo', 'exit']), \
         patch('sys.stdout', new_callable=StringIO) as mock_stdout, \
         patch('app.calculator_repl.Calculator.undo', return_value=True) as mock_undo:
        
        calculator_repl()
        
        output = mock_stdout.getvalue()
        # Ensure undo() was called at least once
        assert mock_undo.call_count >= 1
        # Check that correct message was printed
        assert "Operation undone" in output


"""
Test that 'undo' prints 'Nothing to undo' when undo() returns False.
"""

def test_undo_nothing_to_undo():

    with patch('builtins.input', side_effect=['undo', 'exit']), \
         patch('sys.stdout', new_callable=StringIO) as mock_stdout, \
         patch('app.calculator_repl.Calculator.undo', return_value=False) as mock_undo:
        
        calculator_repl()
        
        output = mock_stdout.getvalue()
        # Ensure undo() was called at least once
        assert mock_undo.call_count >= 1
        # Check that correct message was printed
        assert "Nothing to undo" in output

#################################################
##### Unit test for lines 72-74 of apps/calculator_repl.py


"""
Test that the 'clear' command calls clear_history() and prints 'History cleared'.
"""

def test_clear_history():

    with patch('builtins.input', side_effect=['clear', 'exit']), \
         patch('sys.stdout', new_callable=StringIO) as mock_stdout, \
         patch('app.calculator_repl.Calculator.clear_history') as mock_clear:
        
        calculator_repl()
        
        # Ensure clear_history was called at least once
        assert mock_clear.call_count >= 1
        
        output = mock_stdout.getvalue()
        # Check that the correct message was printed
        assert "History cleared" in output


#################################################
##### Unit test for lines 116-117 of apps/calculator_repl.py

"""
Test that entering 'cancel' for the first number aborts the operation
and prints 'Operation cancelled'.
"""

def test_first_number_cancel():

    with patch('builtins.input', side_effect=['add', 'cancel', 'exit']), \
         patch('sys.stdout', new_callable=StringIO) as mock_stdout:
        
        calculator_repl()
        
        output = mock_stdout.getvalue()
        # Check that "Operation cancelled" was printed
        assert "Operation cancelled" in output
        # Ensure the REPL continued and exited
        assert "Goodbye!" in output