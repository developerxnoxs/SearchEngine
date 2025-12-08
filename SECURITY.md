# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability, please report it responsibly.

### How to Report

1. **Do NOT** open a public GitHub issue for security vulnerabilities
2. Send an email to the maintainers with details about the vulnerability
3. Include steps to reproduce the issue
4. Allow reasonable time for a fix before public disclosure

### What to Include

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Any suggested fixes (optional)

### Response Timeline

- **Acknowledgment**: Within 48 hours
- **Initial Assessment**: Within 1 week
- **Fix Timeline**: Depends on severity
  - Critical: 24-48 hours
  - High: 1 week
  - Medium: 2 weeks
  - Low: Next release

## Security Best Practices

When using this library:

1. **Never commit API keys** - Use environment variables
2. **Use ScraperAPI responsibly** - Follow their terms of service
3. **Rate limiting** - Always use rate limiting to avoid being blocked
4. **Proxy credentials** - Never hardcode proxy credentials
5. **Cache sensitive data carefully** - Be mindful of what gets cached

## Known Security Considerations

- This library makes HTTP requests to external search engines
- HTML content from search engines is parsed - ensure you trust the source
- Cached data should be stored securely if it contains sensitive information
