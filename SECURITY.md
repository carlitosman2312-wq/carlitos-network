# Security Policy

## Project status and supported releases

Carlitos Network (CRLTS) is an experimental Bitcoin Core-derived project. No production mainnet release or public testnet deployment is currently supported. Do not use real funds or treat a successful build/test run as a security audit.

Until a production release series is explicitly published, there are no supported production versions. The validated development branch and its CI status are documented in [TEST_STATUS.md](TEST_STATUS.md).

## Reporting a vulnerability

**Do not send Carlitos vulnerability reports to Bitcoin Core's security contacts.** Carlitos is an independent project; the upstream Bitcoin Core security email address and PGP keys are not Carlitos disclosure contacts.

This repository does not currently document a dedicated encrypted security contact or a verified private disclosure channel. Do not post exploit details, private keys, wallet seeds, or a weaponized proof of concept in a public GitHub issue or pull request.

Before accepting sensitive vulnerability reports, the maintainers must establish and verify a private channel, preferably by enabling GitHub Private Vulnerability Reporting for this repository or publishing a dedicated security email address and its verified encryption key. Until that channel is confirmed, use a public GitHub issue only to ask the maintainers to arrange a private disclosure route; include no vulnerability details.

## Coordinated disclosure

Once a private channel is available, reporters and maintainers should agree on a remediation and disclosure timeline. Avoid publishing details that could expose users or node operators before a fix and mitigation guidance are available.
