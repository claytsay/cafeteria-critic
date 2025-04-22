"""Implements interfaces to various LLM backends."""

from abc import ABC, abstractmethod
import logging
from openai import OpenAI
import os
import requests
from shutil import which
import subprocess

from cafeteriacritic.menu import MenuCollection


class LLM(ABC):
    """Abstract class for all LLM interfaces."""

    @abstractmethod
    def send_prompt(self, prompt: str) -> str:
        """Sends a prompt to the model and returns the response.

        Args:
          prompt: Text to send to the model.

        Returns:
          The response from the model.
        """
        pass


class OllamaLLM(LLM):
    """Interface to a local Ollama instance.

    An Ollama backend server must be running on localhost for this to work.
    """

    def __init__(self, model: str, port: int = 11434) -> None:
        """Constructs an OllamaLLM.

        Args:
          model: Choice of Ollama model to use; must be installed
          port: Port on localhost in which the Ollama server is being
            hosted. Defaults to 11434.
        """
        super().__init__()
        if not which("ollama"):
            raise ValueError("ollama is not installed")
        output = subprocess.run(["ollama", "list"], capture_output=True)
        models_available = set(output.stdout.decode("ascii").split()[4::7])
        if ":latest" not in model:
            model += ":latest"
        if model not in models_available:
            raise ValueError(f"Invalid model: {model}")
        if not isinstance(port, int) or port < 0:
            raise ValueError(f"Invalid port: {port}")
        self._model = model
        self._port = port

    def send_prompt(self, prompt: str) -> str:
        data = {"model": self._model, "prompt": prompt, "stream": False}
        response = requests.post(
            f"http://localhost:{self._port}/api/generate", json=data
        )
        if response.status_code != 200:
            raise RuntimeError(f'Error with ollama backend: {response.json()["error"]}')
        else:
            return response.json()["response"]


class OpenAILLM(LLM):
    """Interface to the OpenAI LLM API."""

    _SYSTEM_PROMPT = (
        "You are a food critic assistant, skilled in evaluating "
        "how good a restaurant or cafeteria is from the dishes "
        "it serves."
    )

    def __init__(self, model: str = "gpt-3.5-turbo", api_key: str = None) -> None:
        """Constructs an OpenAILLM.

        Args:
          api_key: OpenAI API key; must be 51 characters and start with 'sk-'.
            If an api_key is not provided, it will be read from the
            OPENAI_API_KEY environment variable.
          model: OpenAI model to use. Not checked at runtime. Defaults to
            'gpt-3.5-turbo'.
        """
        super().__init__()

        if not api_key:
            logging.warning("No API key provided; reading from environment")
            api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("Invalid API key: no key provided")
        if len(api_key) != 51:
            raise ValueError(
                (
                    f"Invalid API key: length is incorrect "
                    f"expected: 51; actual: {len(api_key)}"
                )
            )
        if api_key[0:3] != "sk-":
            raise ValueError(
                (
                    f"Invalid API key: first 3 characters are incorrect "
                    f'(expected: "sk-"; actual: "{api_key[0:3]}")'
                )
            )

        self._api_key = api_key
        self._client = OpenAI(api_key=self._api_key)
        self._model = model

    def send_prompt(self, prompt: str) -> str:
        completion = self._client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": OpenAILLM._SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        )
        return completion.choices[0].message.content


def menu_collection_to_prompt(menu_collection: MenuCollection) -> str:
    """Converts a collection of menus into a prompt.

    Stringifies each menu and prompts the LLM into choosing which one is the
    best one and providing its reasons as to why.

    Args:
      menu_collection: The collection of menus to convert into a prompt.

    Returns:
      A string prompting a LLM to make a decision about which menu is the most
      appealing.
    """
    prompt = (
        "Below is a list of restaurants/cafeterias and their menus "
        "for one particular day. Considering the variety of dishes "
        "available, the price of each dish, and the quality of each "
        "dish, determine which restaurant/cafeteria is the best and "
        "write a one-paragraph summary explaining your reasoning. Make"
        "sure to draw specific points of evidence from the menu to "
        "support your reasoning. The menus are as follows: \n\n"
    )
    prompt += "\n\n".join(m.__str__() for m in menu_collection.menus)
    return prompt
