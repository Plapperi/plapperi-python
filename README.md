# Plapperi Python API library

The official Python SDK for [Plapperi.ch](https://plapperi.ch/).

## Install

```bash
pip install plapperi
```

## Usage

### Translation
```py
from plapperi.client import Plapperi

client = Plapperi(api_key="YOUR_API_KEY")

result = client.translation.translate(
    text="Ich bin ein Text in hochdeutscher Sprache.",
    dialect="vs",
)

print(result)
```