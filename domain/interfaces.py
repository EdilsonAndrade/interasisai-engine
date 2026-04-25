from abc import ABC, abstractmethod
from typing import Protocol

from domain.models import ChatInput, ChatResult


class ISecretValidator(Protocol):
    def is_valid(self, provided_secret: str | None) -> bool:
        ...


class ILogger(Protocol):
    def info(self, message: str) -> None:
        ...

    def warning(self, message: str) -> None:
        ...

    def error(self, message: str) -> None:
        ...


class ILLMProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str) -> str:
        """Generate a model response for a prompt."""


class IChatUseCase(ABC):
    @abstractmethod
    async def execute(self, chat_input: ChatInput) -> ChatResult:
        """Process a chat input and return a structured chat result."""
