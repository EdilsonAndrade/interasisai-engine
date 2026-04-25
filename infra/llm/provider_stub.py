from domain.interfaces import ILLMProvider


class LLMProviderStub(ILLMProvider):
    async def generate(self, prompt: str) -> str:
        return f"stub:{prompt}"
