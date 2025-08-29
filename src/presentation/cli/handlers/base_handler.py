"""
Base Handler for CLI Operations

Provides common functionality and interface for all CLI menu handlers.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict

from src.presentation.config.dependency_injection import DIContainer


class BaseHandler(ABC):
    """
    Base class for all CLI menu handlers.

    Provides common functionality and ensures consistent interface
    across all menu operations.
    """

    def __init__(self, container: DIContainer):
        """
        Initialize the handler with dependency injection container.

        Args:
            container: DI container with all required dependencies
        """
        self.container = container

    @abstractmethod
    def handle(self, *args, **kwargs) -> None:
        """
        Handle the specific menu operation.

        This method should be implemented by each concrete handler
        to provide the specific functionality for that menu option.
        """
        pass

    @abstractmethod
    def get_description(self) -> str:
        """
        Get a description of what this handler does.

        Returns:
            Description string for the handler
        """
        pass

    def _display_header(self, title: str) -> None:
        """Display a formatted header for the operation."""
        print(f"\n{'='*50}")
        print(f" {title}")
        print(f"{'='*50}")

    def _display_result(self, result: Dict[str, Any]) -> None:
        """Display operation results in a formatted way."""
        print(f"\n{'='*50}")
        print(" RESULTADO DA OPERAÇÃO")
        print(f"{'='*50}")

        for key, value in result.items():
            if isinstance(value, float):
                print(f"{key}: {value:.2f}")
            else:
                print(f"{key}: {value}")

        print(f"{'='*50}")

    def _wait_for_user(self) -> None:
        """Wait for user input to continue."""
        input("\nPressione Enter para continuar...")

    def _get_user_input(self, prompt: str, default: str = "") -> str:
        """
        Get user input with optional default value.

        Args:
            prompt: Input prompt
            default: Default value if user presses enter

        Returns:
            User input or default value
        """
        if default:
            user_input = input(f"{prompt} [{default}]: ").strip()
            return user_input if user_input else default
        else:
            return input(f"{prompt}: ").strip()

    def _confirm_action(self, message: str) -> bool:
        """
        Ask user to confirm an action.

        Args:
            message: Confirmation message

        Returns:
            True if user confirms, False otherwise
        """
        response = input(f"{message} (s/N): ").strip().lower()
        return response == 's' or response == 'sim'