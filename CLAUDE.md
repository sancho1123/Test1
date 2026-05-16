# CLAUDE.md

This file provides guidance for AI assistants (Claude, etc.) working in this repository.

## Repository Overview

- **Name**: Test1
- **Owner**: sancho1123
- **Remote**: `origin` hosted on GitHub (`sancho1123/Test1`)
- **Status**: Newly initialized repository

## Project Structure

```
Test1/
├── CLAUDE.md                          # AI assistant guidance (this file)
├── .github/
│   └── workflows/
│       └── daily-ukraine-brief.yml    # GitHub Actions: runs at 5 AM ET daily
├── scripts/
│   ├── generate_brief.py              # Calls Claude API to generate the daily brief
│   ├── send_email.py                  # Sends brief via Gmail SMTP
│   └── README.md                      # Setup instructions and secret configuration
├── reports/
│   ├── latest_brief.md               # Most recent brief (overwritten daily)
│   └── YYYY-MM-DD_Ukraine-Russia_*   # Dated archive of each brief
└── .git/                              # Git repository metadata
```

## Daily Brief Automation

This repository generates a daily Ukraine–Russia War Analyst Brief for OUSW Comptroller P/B analysts.

- **Schedule**: 5:00 AM Eastern Time (configured via GitHub Actions cron)
- **Output**: Markdown report saved to `reports/` and emailed to ericjsanchez23@gmail.com
- **Required GitHub Secrets**: `ANTHROPIC_API_KEY`, `GMAIL_USER`, `GMAIL_APP_PASSWORD`
- **Manual trigger**: GitHub Actions → "Daily Ukraine–Russia War Analyst Brief" → Run workflow

See `scripts/README.md` for full setup instructions.

## Development Workflow

### Branching

- Feature branches should follow the pattern: `claude/<description>-<id>` or `feature/<description>`
- Always branch from the latest `main` (or default branch) before starting work
- Push with: `git push -u origin <branch-name>`

### Commits

- Write clear, descriptive commit messages
- Use imperative mood in commit subjects (e.g., "Add feature" not "Added feature")
- Keep commits focused — one logical change per commit

### Pull Requests

- Provide a summary of changes and a test plan
- Link related issues when applicable

## Code Conventions

> Update this section as the project adopts languages, frameworks, and tooling.

- Prefer clarity and simplicity over cleverness
- Follow the conventions of whatever language/framework is adopted
- Keep functions small and focused
- Add comments only where the logic isn't self-evident

## Testing

> Update this section once a test framework is configured.

- All new features should include tests
- Run the full test suite before pushing changes

## Linting & Formatting

> Update this section once linters/formatters are configured.

## Dependencies

> Update this section once a package manager is in use.

## Key Notes for AI Assistants

1. **Read before writing** — Always read existing files before modifying them
2. **Minimal changes** — Only make changes that are directly requested or clearly necessary
3. **No over-engineering** — Avoid adding abstractions, utilities, or features beyond what is asked
4. **Security first** — Never introduce vulnerabilities (injection, XSS, etc.)
5. **Don't guess** — If something is unclear, ask the user rather than assuming
6. **Update this file** — When significant project structure, tooling, or conventions change, update CLAUDE.md to keep it current
