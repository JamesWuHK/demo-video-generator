# Contributing to Demo Video Generator

Thank you for your interest in contributing to Demo Video Generator! This document provides guidelines for contributing to the project.

## Code of Conduct

Be respectful and inclusive. We want to maintain a welcoming environment for all contributors.

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue with:
- A clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Your environment (OS, Python version, etc.)

### Suggesting Features

Feature suggestions are welcome! Please open an issue describing:
- The feature you'd like to see
- Why it would be useful
- How it might work

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests if available
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/demo-video-generator.git
cd demo-video-generator

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Install Playwright browsers
playwright install chromium
```

### Code Style

- Follow PEP 8 guidelines
- Use type hints where possible
- Write docstrings for functions and classes
- Keep functions focused and concise

### Testing

Before submitting a PR:
- Test your changes manually
- Ensure existing functionality still works
- Add tests for new features if possible

## Project Structure

```
demo-video-generator/
├── src/demo_video_generator/
│   ├── core/          # Core functionality
│   ├── cli/           # CLI interface
│   └── api/           # API service
├── examples/          # Example scripts
├── tests/             # Test files
└── docs/              # Documentation
```

## Questions?

Feel free to open an issue for any questions about contributing!
