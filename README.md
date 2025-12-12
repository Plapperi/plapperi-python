# Plapperi Python SDK

[![PyPI version](https://img.shields.io/pypi/v/plapperi.svg)](https://pypi.org/project/plapperi/)
[![Python support](https://img.shields.io/pypi/pyversions/plapperi.svg)](https://pypi.org/project/plapperi/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

The official Python library for the [Plapperi.ch](https://plapperi.ch/) API. Translate text to Swiss German dialects and synthesize natural-sounding speech.

## Features

- **Dialect Translation**: Translate High German to various Swiss German dialects
- **Speech Synthesis**: Generate natural-sounding audio from Swiss German text
- **Async Support**: Both synchronous and asynchronous operations
- **Batch Processing**: Efficient handling of multiple translation jobs
- **Type Safety**: Full type hints with Pydantic models
- **Context Manager Support**: Clean resource management

## Installation

Install the package using pip:

```bash
pip install plapperi
```

## Requirements

- Python 3.9 or higher
- An API key from [Plapperi.ch](https://plapperi.ch/)

## Quick Start

### Setting up Authentication

Set your API key as an environment variable:

```bash
export PLAPPERI_API_KEY="your-api-key-here"
```

Or pass it directly when initializing the client:

```python
from plapperi import Plapperi

client = Plapperi(api_key="your-api-key-here")
```

### Basic Translation

Translate text to a Swiss German dialect:

```python
from plapperi import Plapperi

client = Plapperi()

# Translate to Valais dialect
result = client.translation.translate(
    text="Die Bevölkerung hat genug von den vielen Touristen.",
    dialect="vs",
)

print(result)
# Output: "D'Bevölkrig het gnüeg va de viele Touristu."
```

### Supported Dialects

The following Swiss German dialects are currently supported:

| Dialect Code | Region | Example Usage |
|--------------|--------|---------------|
| `vs` | Valais (Wallis) | `dialect="vs"` |
| `bs` | Basel-Stadt | `dialect="bs"` |
| `ag` | Aargau | `dialect="ag"` |
| `be` | Bern | `dialect="be"` |
| `zh` | Zürich | `dialect="zh"` |
| `lu` | Luzern | `dialect="lu"` |
| `gr` | Graubünden | `dialect="gr"` |
| `sg` | St. Gallen | `dialect="sg"` |

### Basic Speech Synthetization

Synthesize speech:

```python
from plapperi import Plapperi

client = Plapperi()

# Synthesize with voice aragon
result = client.synthetization.synth(
    text="D Bevölkerig het gnueg vode vellne Touriste.",
    voice="aragon",
)
```

## Advanced Usage

### Custom Configuration

Configure the client with custom timeout and base URL:

```python
from plapperi import Plapperi

client = Plapperi(
    api_key="your-api-key-here",
    base_url="https://api.plapperi.ch",
    timeout=60.0,  # seconds
)
```

### Translation with Beam Search

Control the translation quality using beam search:

```python
result = client.translation.translate(
    text="Guten Morgen, wie geht es Ihnen?",
    dialect="be",
    beam_size=8,  # Higher values = better quality but slower (default=4)
)
```

### Manual Job Control (Translation)

For more control over the translation process, you can manage jobs manually:

```python
from plapperi import Plapperi

client = Plapperi()

# Start a translation job
job = client.translation.start(
    text="Das Wetter ist heute sehr schön.",
    dialect="zh",
    beam_size=4,
)

print(f"Job ID: {job.job_id}")
print(f"Status: {job.status}")

# Poll for completion
import time
while True:
    status = client.translation.status(job.job_id)
    
    if status.is_completed:
        print(f"Translation: {status.result.translation}")
        break
    elif status.is_failed:
        print(f"Job failed: {status.error}")
        break
    elif status.is_processing:
        print("Still processing...")
    
    time.sleep(1.0)
```

### Batch Translation

Process multiple texts efficiently by managing jobs manually:

```python
from plapperi import Plapperi
import time

client = Plapperi()

texts = [
    "Guten Morgen!",
    "Wie geht es dir?",
    "Das Wetter ist schön.",
    "Ich mag Schweizer Schokolade.",
    "Bis bald!",
]

# Start all jobs
jobs = []
for text in texts:
    job = client.translation.start(text=text, dialect="be")
    jobs.append((text, job.job_id))
    print(f"Started job {job.job_id} for: {text}")

# Poll all jobs until complete
results = []
pending_jobs = dict(jobs)

while pending_jobs:
    for original_text, job_id in list(pending_jobs.items()):
        status = client.translation.status(job_id)
        
        if status.is_completed:
            results.append({
                "original": original_text,
                "translation": status.result.translation,
                "dialect": "be",
            })
            del pending_jobs[original_text]
            print(f"✓ Completed: {original_text}")
        elif status.is_failed:
            print(f"✗ Failed: {original_text} - {status.error}")
            del pending_jobs[original_text]
    
    if pending_jobs:
        time.sleep(0.5)  # Poll every 500ms

# Display results
for result in results:
    print(f"{result['original']} -> {result['translation']}")
```

### Optimized Batch Processing with Concurrent Polling

For better performance with large batches, use concurrent polling:

```python
from plapperi import Plapperi
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

client = Plapperi()

def process_translation(text, dialect="be", beam_size=4):
    """Start and wait for a single translation job."""
    job = client.translation.start(
        text=text,
        dialect=dialect,
        beam_size=beam_size,
    )
    
    # Poll until complete
    while True:
        status = client.translation.status(job.job_id)
        
        if status.is_completed:
            return {
                "original": text,
                "translation": status.result.translation,
                "job_id": job.job_id,
            }
        elif status.is_failed:
            return {
                "original": text,
                "error": status.error,
                "job_id": job.job_id,
            }
        
        time.sleep(0.5)

texts = [
    "Guten Morgen!",
    "Wie geht es dir?",
    "Das Wetter ist schön.",
    "Ich mag Schweizer Schokolade.",
    "Bis bald!",
]

# Process all translations concurrently
with ThreadPoolExecutor(max_workers=5) as executor:
    # Submit all jobs
    future_to_text = {
        executor.submit(process_translation, text): text 
        for text in texts
    }
    
    # Collect results as they complete
    for future in as_completed(future_to_text):
        result = future.result()
        if "error" in result:
            print(f"✗ {result['original']}: {result['error']}")
        else:
            print(f"✓ {result['original']} -> {result['translation']}")
```

### Context Manager Usage

Use the client as a context manager for automatic cleanup:

```python
from plapperi import Plapperi

with Plapperi() as client:
    result = client.translation.translate(
        text="Herzlichen Glückwunsch!",
        dialect="zh",
    )
    print(result)
# Client is automatically closed
```

### Error Handling

Handle API errors gracefully:

```python
from plapperi import Plapperi
from plapperi.errors.api_error import ApiError
from plapperi.errors.timeout_error import PlapperiTimeoutError

client = Plapperi()

try:
    result = client.translation.translate(
        text="Ein sehr langer Text...",
        dialect="vs",
        timeout=30.0,
    )
    print(result)
    
except PlapperiTimeoutError as e:
    print(f"Translation timed out: {e}")
    
except ApiError as e:
    print(f"API error: {e.status_code} - {e.body}")
    
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Speech Synthesis (Coming Soon)

The synthetization API is currently under development:

```python
# Future API (not yet implemented)
audio = client.synthetization.synth(
    text="Grüezi mitenand!",
    voice="swiss-german-female",
)
```

## API Reference

### Client

#### `Plapperi(api_key=None, base_url="https://api.plapperi.ch", timeout=30.0)`

Initialize the Plapperi client.

**Parameters:**
- `api_key` (str, optional): Your API key. If not provided, reads from `PLAPPERI_API_KEY` environment variable.
- `base_url` (str): Base URL for the API. Default: `https://api.plapperi.ch`
- `timeout` (float): Request timeout in seconds. Default: `30.0`

**Methods:**
- `close()`: Close the HTTP client
- Can be used as a context manager with `with` statement

### Translation

#### `client.translation.translate(text, dialect, beam_size=4, poll_interval=1.0, timeout=60.0)`

Translate text and wait for completion.

**Parameters:**
- `text` (str): Text to translate to Swiss German
- `dialect` (str): Dialect code (e.g., 'vs', 'be', 'zh')
- `beam_size` (int): Beam size for translation quality (1-8). Default: `4`
- `poll_interval` (float): Seconds between status checks. Default: `1.0`
- `timeout` (float): Maximum seconds to wait. Default: `60.0`

**Returns:** `str` - The translated text

**Raises:**
- `PlapperiTimeoutError`: If job doesn't complete within timeout
- `ApiError`: If job fails or API error occurs

#### `client.translation.start(text, dialect, beam_size=4)`

Start a translation job without waiting.

**Parameters:**
- `text` (str): Text to translate
- `dialect` (str): Dialect code
- `beam_size` (int): Beam size (1-8). Default: `4`

**Returns:** `Job` - Job information with `job_id` and `status`

#### `client.translation.status(job_id)`

Check the status of a translation job.

**Parameters:**
- `job_id` (str): The job ID from `start()`

**Returns:** `TranslationStatus` - Status object with:
- `job_id` (str): The job identifier
- `status` (JobStatus): Current status (PENDING, PROCESSING, COMPLETED, FAILED)
- `result` (TranslationResult | None): Translation result if completed
- `error` (str | None): Error message if failed
- Properties: `is_completed`, `is_failed`, `is_pending`, `is_processing`

## Type Definitions

### Job Status Values

```python
from plapperi.types.job import JobStatus

JobStatus.PENDING      # Job is queued
JobStatus.PROCESSING   # Job is being processed
JobStatus.COMPLETED    # Job completed successfully
JobStatus.FAILED       # Job failed with error
```

### Dialect Enum

```python
from plapperi.types.dialect import Dialect

Dialect.VALAIS      # "vs"
Dialect.BASEL       # "bs"
Dialect.AARGAU      # "ag"
Dialect.BERN        # "be"
Dialect.ZURICH      # "zh"
Dialect.LUCERNE     # "lu"
Dialect.GRAUBUNDEN  # "gr"
Dialect.ST_GALLEN   # "sg"
```

## Best Practices

### Batch Processing Strategy

When processing multiple translations, consider these strategies:

1. **Sequential with Manual Control** (Simple, predictable):
   - Start all jobs first
   - Poll until all complete
   - Good for small batches (<10 texts)

2. **Concurrent Polling** (Fast, efficient):
   - Use ThreadPoolExecutor
   - Each thread manages one translation
   - Good for medium batches (10-100 texts)

3. **Chunked Processing** (Scalable):
   - Process in chunks of 10-20
   - Avoids overwhelming the API
   - Good for large batches (100+ texts)

### Performance Tips

- **Batch Size**: Start 10-20 jobs, then poll
- **Poll Interval**: Use 0.5-1.0 seconds between checks
- **Beam Size**: Use 4 for balanced quality/speed, 6-8 for best quality
- **Timeout**: Set based on text length (30-60s typical)
- **Error Recovery**: Implement retry logic for failed jobs

### Example: Production-Ready Batch Processor

```python
from plapperi import Plapperi
from plapperi.errors.api_error import ApiError
import time
from typing import List, Dict

def batch_translate(
    texts: List[str],
    dialect: str = "be",
    beam_size: int = 4,
    max_concurrent: int = 10,
    poll_interval: float = 0.5,
    max_retries: int = 3,
) -> List[Dict]:
    """
    Translate multiple texts with automatic retry and error handling.
    
    Args:
        texts: List of texts to translate
        dialect: Target dialect
        beam_size: Quality parameter (1-8)
        max_concurrent: Maximum concurrent jobs
        poll_interval: Seconds between status checks
        max_retries: Retries for failed jobs
        
    Returns:
        List of dictionaries with 'original', 'translation', and 'status'
    """
    client = Plapperi()
    results = []
    
    # Process in chunks
    for i in range(0, len(texts), max_concurrent):
        chunk = texts[i:i + max_concurrent]
        chunk_results = []
        
        # Start all jobs in chunk
        jobs = []
        for text in chunk:
            try:
                job = client.translation.start(
                    text=text,
                    dialect=dialect,
                    beam_size=beam_size,
                )
                jobs.append({
                    "text": text,
                    "job_id": job.job_id,
                    "retries": 0,
                })
            except ApiError as e:
                chunk_results.append({
                    "original": text,
                    "translation": None,
                    "status": "error",
                    "error": str(e),
                })
        
        # Poll until all complete
        pending = jobs.copy()
        while pending:
            for job_info in pending[:]:
                try:
                    status = client.translation.status(job_info["job_id"])
                    
                    if status.is_completed:
                        chunk_results.append({
                            "original": job_info["text"],
                            "translation": status.result.translation,
                            "status": "success",
                        })
                        pending.remove(job_info)
                        
                    elif status.is_failed:
                        if job_info["retries"] < max_retries:
                            # Retry failed job
                            new_job = client.translation.start(
                                text=job_info["text"],
                                dialect=dialect,
                                beam_size=beam_size,
                            )
                            job_info["job_id"] = new_job.job_id
                            job_info["retries"] += 1
                        else:
                            chunk_results.append({
                                "original": job_info["text"],
                                "translation": None,
                                "status": "failed",
                                "error": status.error,
                            })
                            pending.remove(job_info)
                            
                except ApiError as e:
                    print(f"Error checking status: {e}")
            
            if pending:
                time.sleep(poll_interval)
        
        results.extend(chunk_results)
        print(f"Completed chunk {i//max_concurrent + 1}/{(len(texts)-1)//max_concurrent + 1}")
    
    client.close()
    return results

# Usage
texts = ["Guten Tag"] * 50
results = batch_translate(texts, dialect="zh", max_concurrent=10)

for r in results:
    if r["status"] == "success":
        print(f"✓ {r['original']} -> {r['translation']}")
    else:
        print(f"✗ {r['original']}: {r.get('error', 'Unknown error')}")
```

## Support

- **Documentation**: [https://plapperi.ch/docs](https://plapperi.ch/docs)
- **Issues**: [GitHub Issues](https://github.com/Plapperi/plapperi-python/issues)
- **Email**: info@noxenum.io

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Changelog

### 0.0.2

- Synthetization API support (TTS)

### 0.0.1 (Current)

- Initial release
- Translation API support with multiple Swiss German dialects
- Synchronous operations
- Manual job control for batch processing
- Type-safe Pydantic models
- Context manager support

### Upcoming Features

- Streaming responses
- WebSocket support for real-time translation

## Acknowledgments

Built with ❤️ by [Noxenum](https://noxenum.io) for the Swiss German community.