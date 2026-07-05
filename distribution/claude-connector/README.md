# Filingrail MCP connector — Claude Desktop, Claude Code, Cursor, Continue

Give any MCP-compatible AI client live SEC EDGAR data. Each user brings their own RapidAPI key, so every install funnels to a Filingrail subscription.

## 1. Install the server

```bash
pip install filingrail-mcp
```

(Requires Python 3.10+. This installs the `filingrail-mcp` command.)

## 2. Get a key

Free tier: **50 calls/day, no card**. Subscribe on RapidAPI, copy your `X-RapidAPI-Key`:

**https://rapidapi.com/hudson-enterprises-llc-hudson-enterprises-llc-default/api/filingrail**

## 3. Wire it into your client

### Claude Desktop

Edit the config file:
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

Add (or merge) the `filingrail` block — see `claude_desktop_config.json` in this folder:

```json
{
  "mcpServers": {
    "filingrail": {
      "command": "filingrail-mcp",
      "env": { "RAPIDAPI_KEY": "YOUR_RAPIDAPI_KEY_HERE" }
    }
  }
}
```

Restart Claude Desktop. The Filingrail tools appear in the tool picker (the 🔌/hammer icon). Then just ask a question.

### Claude Code (CLI)

```bash
claude mcp add filingrail --env RAPIDAPI_KEY=YOUR_RAPIDAPI_KEY_HERE -- filingrail-mcp
```

Or add the same `mcpServers` block to your `.mcp.json` / Claude Code MCP config.

### Cursor

Settings → **MCP** → Add new MCP server, or edit `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "filingrail": {
      "command": "filingrail-mcp",
      "env": { "RAPIDAPI_KEY": "YOUR_RAPIDAPI_KEY_HERE" }
    }
  }
}
```

### Continue (VS Code / JetBrains)

Add to your Continue MCP config (`~/.continue/config.yaml` under `mcpServers`, or the JSON equivalent):

```yaml
mcpServers:
  - name: filingrail
    command: filingrail-mcp
    env:
      RAPIDAPI_KEY: YOUR_RAPIDAPI_KEY_HERE
```

## 4. Try it

Ask your assistant:

- *"What was Apple's cash position last quarter? Link me the filing."*
- *"Show insider sells at NVIDIA in the last 30 days."*
- *"List Berkshire Hathaway's top 10 holdings as of the latest 13F."*

## Tools exposed

`search_companies`, `get_recent_filings`, `get_financials`, `get_financials_history`, `get_insider_trades`, `get_8k_events`, `get_13f_holdings`, `health` — all return normalized JSON, with a `source_filing_url` on every financials response.

## Troubleshooting

- **"RAPIDAPI_KEY env var required"** → the key isn't reaching the server. Confirm it's in the `env` block and you restarted the client.
- **`filingrail-mcp` not found** → the pip install went to a different Python. Use the full path to the installed script, or install into the interpreter your client uses.
- Questions: `support@hudsonenterprisesllc.com`
