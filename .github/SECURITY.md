# Security Policy

The ATBClone team takes the security of our application and users seriously. We appreciate the efforts of security researchers and community members who responsibly disclose security vulnerabilities.

---

## Supported Versions

Only the latest active release branch receives security updates. We strongly encourage all users to stay on the most recent release.

| Version | Supported          | Notes                              |
| :------ | :----------------- | :--------------------------------- |
| 1.5.x   | :white_check_mark: | Current active release branch      |
| < 1.5.0 | :x:                | Unsupported; please upgrade        |

---

## Reporting a Vulnerability

**Please DO NOT report security vulnerabilities through public GitHub issues, discussions, or pull requests.**

If you believe you have discovered a vulnerability in ATBClone, please report it through one of the following channels:

### 1. GitHub Private Vulnerability Reporting (Preferred)
You can report vulnerabilities privately using GitHub's advisory system:
* Navigate to the [Security Advisories](https://github.com/aitobox/ATBClone/security/advisories) tab of the repository.
* Click **"Report a vulnerability"** (or use direct link: [New Advisory](https://github.com/aitobox/ATBClone/security/advisories/new)).
* Provide detailed information about the vulnerability.

### 2. Email Contact (Alternative)
If you cannot use GitHub's private vulnerability reporting, you can reach out via email:
* **Security Contact**: [clone@outlook.com](mailto:clone@outlook.com)
* **Subject Line**: `[SECURITY] ATBClone Vulnerability Report: <Brief Description>`

---

## What to Include in Your Report

To help us investigate and resolve the issue efficiently, please include as much of the following details as possible:

1. **Vulnerability Summary**: A clear description of the potential vulnerability and its impact.
2. **Affected Components**: Engine, CLI, GUI, configuration parser, sandbox entitlements, or specific scripts.
3. **Environment**:
   * macOS version and architecture (Apple Silicon / Intel)
   * ATBClone version
   * Python runtime environment
4. **Steps to Reproduce**: A minimal, step-by-step reproduction guide or Proof of Concept (PoC) code/recipe.
5. **Mitigation Suggestions** (optional): Any remediation steps or code suggestions you may have.

---

## Response & Disclosure Process

* **Acknowledgment**: We will acknowledge receipt of your vulnerability report within **48 hours**.
* **Triage & Assessment**: Within **5 business days**, we will evaluate the severity, verify the report, and communicate the expected resolution plan.
* **Fix & Release**: We will work on a patch in a private fork/branch and release a security fix as promptly as possible.
* **Coordinated Disclosure**: We follow responsible/coordinated vulnerability disclosure principles. We kindly ask that you keep the report confidential until a fix has been published and users have had reasonable time to update.
* **Credit**: With your permission, we will publicly credit your contribution in the security advisory and release notes.

---

## Scope

### In-Scope
* ATBClone core engine logic (`src/atbclone/core/`)
* Application cloning, permission handling, and sandbox entitlement management
* ATBClone CLI commands and options parsing
* ATBClone GUI interactions and configuration management

### Out-of-Scope
* Vulnerabilities in upstream/third-party dependencies unless a practical exploit path exists through ATBClone
* Social engineering or physical attacks requiring unauthorized physical access to the device
* Issues requiring rooted/jailbroken environments or disabling macOS System Integrity Protection (SIP) without privilege escalation
* Denial of Service (DoS) attacks on the local machine that do not result in privilege escalation or data tampering
