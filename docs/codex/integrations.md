# Integrations

This page covers the small set of integrations worth standardizing for ongoing development work. It intentionally separates what is usable now from what is recommended later.

## Status Model
- `available_now`: usable immediately in this environment
- `recommended_later`: officially supported and worth adding, but not assumed to be installed here
- `blocked_or_misconfigured`: present or intended, but not currently usable

## `openai_docs`
- Kind: MCP
- Status: `recommended_later`
- Purpose: query official OpenAI documentation during SDK, API, and migration work.
- Official add command:

```bash
codex mcp add openaiDeveloperDocs --url https://developers.openai.com/mcp
```

- Why it matters here: this repo still has OpenAI modernization ahead, and primary-source docs reduce guesswork.
- Current environment note: no MCP servers are visible in-session right now, so this is recommended but not currently verified as active here.
- Official reference: https://platform.openai.com/docs/docs-mcp

## `github_cli`
- Kind: command-line integration
- Status: `blocked_or_misconfigured`
- Purpose: local GitHub operations such as PR lookup, issue inspection, and workflow checks.
- Check command:

```bash
gh auth status
```

- Current environment note: `gh` is installed, but the active auth token is invalid in this session.
- Official reference: https://cli.github.com/

## `github_mcp`
- Kind: MCP
- Status: `recommended_later`
- Purpose: provide structured GitHub repository context and operations through an MCP server.
- Prerequisites:
  - valid GitHub token
  - remote-server or Docker-based setup path
- Current environment note: no MCP servers are visible in-session right now, and this repo does not assume GitHub MCP is already installed.
- Official references:
  - https://docs.github.com/en/copilot/how-tos/provide-context/use-mcp/use-the-github-mcp-server
  - https://github.com/github/github-mcp-server

## Deferred Integrations
- cloud, database, and browser-oriented MCPs are intentionally deferred
- they may become useful later for CI/CD, cloud deployment, or persistent storage work
- they are not standardized yet because the current repo workflow does not depend on them
