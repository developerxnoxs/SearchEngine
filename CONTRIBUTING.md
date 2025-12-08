# Contributing to Multi Search Engine

First off, thanks for taking the time to contribute!

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible using the bug report template.

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. Create an issue and provide:

- A clear and descriptive title
- A detailed description of the proposed enhancement
- Explain why this enhancement would be useful
- List any similar features in other libraries if applicable

### Adding New Search Engines

We welcome contributions for new search engines! Here's how:

1. Create a new file in `multi_search_engine/engines/`
2. Inherit from `SearchEngine` base class
3. Implement `_build_search_url()` and `_parse_results()` methods
4. Add tests for the new engine
5. Update documentation

Example structure:

```python
from multi_search_engine.base import SearchEngine, SearchResult
from typing import List, Optional

class NewSearchEngine(SearchEngine):
    ENGINE_NAME = "newengine"
    BASE_URL = "https://www.example.com/search"
    
    def _build_search_url(
        self,
        query: str,
        page: int = 1,
        num_results: int = 10,
        language: Optional[str] = None,
        country: Optional[str] = None,
        safe_search: bool = True
    ) -> str:
        # Build and return the search URL
        pass
    
    def _parse_results(self, html: str) -> List[SearchResult]:
        # Parse HTML and return list of SearchResult
        pass
```

### Pull Requests

1. Fork the repo and create your branch from `main`
2. If you've added code that should be tested, add tests
3. If you've changed APIs, update the documentation
4. Ensure the test suite passes
5. Make sure your code follows the existing style
6. Issue that pull request!

## Development Setup

```bash
# Clone your fork
git clone https://github.com/your-username/multi-search-engine.git
cd multi-search-engine

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Run linting
flake8 multi_search_engine
mypy multi_search_engine
```

## Style Guide

- Follow PEP 8
- Use type hints for all function parameters and return values
- Write docstrings for all public methods
- Keep functions focused and small
- Use meaningful variable names

## Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests liberally after the first line

## Testing

- Write tests for all new features
- Ensure all tests pass before submitting a PR
- Aim for high code coverage
- Use mocking for external HTTP requests

## Documentation

- Update README.md if needed
- Add docstrings to new functions/classes
- Update API documentation
- Add examples for new features

## Questions?

Feel free to open an issue with your question or reach out to the maintainers.

Thank you for contributing!
