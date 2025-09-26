# Security Policy

## Supported Versions

| Version | Supported          |
|---------|-------------------|
| 1.0.x   | ✅ Yes            |
| < 1.0   | ❌ No             |

## Reporting a Vulnerability

We take the security of GitLab Ping seriously. If you believe you've found a security vulnerability, please follow these steps:

### 1. **Do Not Disclose Publicly**
Please do not report security vulnerabilities through public GitHub issues, discussions, or other public channels.

### 2. **Report Privately**
Report security vulnerabilities by sending an email to:
- **Email**: `vladimir.nosov.security@gmail.com`
- **Subject**: `[GitLab Ping Security] - Vulnerability Report`

### 3. **Include in Your Report**
Please include as much of the following information as possible to help us better understand and resolve the issue:
- Type of vulnerability (e.g., XSS, SQL injection, RCE, etc.)
- Full paths and URLs of affected resources
- Steps to reproduce the vulnerability
- Proof-of-concept or exploit code (if available)
- Impact of the vulnerability
- Your environment (OS, Python version, etc.)

### 4. **What to Expect**
- We will acknowledge receipt of your report within 48 hours
- We will provide a more detailed response within 5 business days indicating the next steps
- We will keep you informed of the progress towards a fix and announcement
- Once the vulnerability is resolved, we will publicly credit you (unless you prefer to remain anonymous)

### 5. **Safe Harbor**
Security researchers who follow this policy will:
- Not be subject to legal action
- Be considered to be acting in good faith
- Receive credit for their discovery

## Security Best Practices

### For Users
- Keep your GitLab Ping installation updated
- Use strong authentication for your GitLab account
- Monitor your GitLab instance for unusual activity
- Regularly review your notification settings

### For Developers
- Follow secure coding practices
- Keep dependencies updated
- Use environment variables for sensitive data
- Implement proper input validation
- Use HTTPS for all network communications

## Dependency Security

We regularly scan our dependencies for known vulnerabilities using:
- GitHub Dependabot
- Safety (Python package security checker)
- Manual security reviews

If you discover a vulnerable dependency, please report it following the vulnerability reporting process above.

## Contact

For general security questions or concerns, please contact us at:
- **Email**: `vladimir.nosov.security@gmail.com`
- **GitHub**: [@CoOre](https://github.com/CoOre)

---

*This security policy is based on industry best practices and may be updated as needed.*