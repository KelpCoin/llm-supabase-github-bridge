# MCP Wiring (LLM Agents ↔ Supabase)

Use the official Supabase MCP server. Do not build a custom protocol.

## Hosted Supabase

1. In Supabase Dashboard → Project Settings → MCP (or AI Tools).
2. Generate / copy the MCP URL with the feature groups you need (database, functions, branching, debugging, docs).
3. Add to your client (Cursor, Claude Code, Codex, Copilot, Grok, etc.):

```json
{
  "mcpServers": {
    "supabase": {
      "type": "http",
      "url": "https://mcp.supabase.com/mcp?features=docs%2Caccount%2Cdatabase%2Cdebugging%2Cdevelopment%2Cfunctions%2Cbranching"
    }
  }
}
```

Or use the project-specific URL from the dashboard.

## Self-Hosted / Local

See Supabase docs for enabling the MCP server behind Envoy / SSH tunnel. Prefer local Postgres + CLI for pure air-gap work; MCP is the online bridge.

## Security

- Follow Supabase security best practices before connecting any LLM.
- Prefer read-only or tightly scoped service roles for experimental agents.
- RLS is your friend. Agents should only see the silos they are authorised for.
- Never give an LLM the Stripe secret key. Give it a controlled Edge Function that creates Checkout Sessions.

## GitHub Integration

Pair MCP with the official Supabase GitHub integration (now free-plan capable) so agents can push schema changes and Actions can verify them.
