#!/usr/bin/env python3
"""Post-generation hook: print next steps after scaffold creation."""

AGENT_NAME = "{{ cookiecutter.agent_name }}"

print(
    f"""
{AGENT_NAME} scaffold generated successfully.

Next steps:
  cd {AGENT_NAME}
  cp .env.example .env
  make setup
  make check && make test
  python -m src.main

Mount edge-agent-rules @ v0.2.0 as a git submodule at .cursor/rules (see README).
"""
)
