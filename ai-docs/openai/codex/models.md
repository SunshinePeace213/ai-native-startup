---
source: https://learn.chatgpt.com/docs/models
fetched: 2026-07-21
---
> **In here:** GPT-5.6 variants (Sol, Terra, Luna) · Reasoning levels and effort modes · Configuration and CLI usage

# Models - Codex Documentation

## Overview

Codex offers multiple AI models optimized for different work types. The platform provides three GPT-5.6 variants (Sol, Terra, Luna), previous-generation GPT-5.5, and specialized models. Users select models via desktop app, web interface, CLI, or IDE extension.

## Primary Model Options

### GPT-5.6 Family

#### GPT-5.6 Sol

- "Flagship GPT-5.6 model with the strongest capability for complex coding, computer use, research, and cybersecurity"
- Best for: ambiguous, difficult, high-value tasks requiring analysis and polish
- CLI: `codex -m gpt-5.6-sol`
- Available across all platforms with ChatGPT credentials

#### GPT-5.6 Terra

- "Balanced GPT-5.6 model for everyday work, with performance competitive with GPT-5.5 at a lower cost"
- Best for: routine work requiring strong reasoning without Sol's full depth
- CLI: `codex -m gpt-5.6-terra`

#### GPT-5.6 Luna

- "Fast and affordable GPT-5.6 model that delivers strong capability at the lowest cost"
- Best for: specific, repeatable tasks with clear success criteria
- CLI: `codex -m gpt-5.6-luna`

### Legacy Models

#### GPT-5.5

- Previous frontier model for complex workflows
- CLI: `codex -m gpt-5.5`

#### GPT-5.3 Codex Spark

- Text-only research preview optimized for real-time coding
- Restricted to ChatGPT Pro users

## Reasoning Levels

Users can adjust reasoning effort from Low to Ultra:

- **Low/Light**: Quick, well-scoped tasks
- **Medium**: Balanced speed and depth
- **High/Extra High**: Multi-step, complex work
- **Max**: Maximum depth for hardest problems
- **Ultra**: Parallel subagent processing for divisible tasks

## Configuration

Set default model in `config.toml`:

```toml
model = "gpt-5.6"
```

Or via CLI flag:

```shell
codex --model gpt-5.6-sol
```

Codex cloud chats currently don't support model selection changes.
