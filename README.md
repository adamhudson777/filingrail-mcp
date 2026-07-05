<!-- mcp-name: io.github.adamhudson777/filingrail-mcp -->

# filingrail-mcp — SEC EDGAR filings inside Claude, Cursor, and any MCP agent

Give your AI agent live SEC EDGAR data: company financials, insider trades, 8-K events, 13F holdings, and the raw filings stream — all normalized to clean JSON, every number traceable back to its `sec.gov` source filing.

One `pip install`, one API key, and your agent can answer *"What was Apple's cash position last quarter?"* or *"List Berkshire Hathaway's top 10 holdings as of 2026-Q1"* — against real filings, not its training data.

```bash
pip install filingrail-mcp
```

> **Live on PyPI:** [pypi.org/project/filingrail-mcp](https://pypi.org/project/filingrail-mcp/) · MIT licensed · Python 3.10+

## Why this exists

Every number a public company reports to the SEC is free and open on EDGAR. The bottleneck isn't access — it's the XBRL parser, the tag-drift normalizer, the rate-limit governor, and the dedup layer you'd have to write before you get the one figure you actually wanted. `filingrail-mcp` hands your agent the finished JSON instead.

- **Source-traceable.** Every financial response carries the originating `source_filing_url`. Click it, see the exact 10-K / 10-Q on sec.gov. No "trust us."
- **Normalized.** `revenue` is `revenue`, whether the filer tagged it `us-gaap:Revenues`, `SalesRevenueNet`, or `RevenueFromContractWithCustomerExcludingAssessedTax`. 1.8M+ XBRL rows back to 2006.
- **Zero plumbing.** No EDGAR User-Agent config, no local parser, no rate-limit governor. The API handles all of it.

## Get a key (free tier, no card)

Filingrail is a REST API on RapidAPI. The free tier is **50 calls/day, no credit card**:

**→ [Subscribe to Filingrail on RapidAPI](https://rapidapi.com/hudson-enterprises-llc-hudson-enterprises-llc-default/api/filingrail)** and copy your `X-RapidAPI-Key`.

The end user brings their own key — set it as `RAPIDAPI_KEY` in your MCP client config (below).

## Configure your agent

### Claude Desktop

Edit `%APPDATA%/Claude/claude_desktop_config.json` (Windows) or `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS):

```json
{
  "mcpServers": {
    "filingrail": {
      "command": "filingrail-mcp",
      "env": { "RAPIDAPI_KEY": "your-rapidapi-key-here" }
    }
  }
}
```

Restart Claude Desktop. The Filingrail tools (`search_companies`, `get_financials`, `get_insider_trades`, …) appear in the tool list. Then just ask a question in plain English.

### Cursor / Continue / any other MCP client

Point the client at `filingrail-mcp` as the stdio command and pass `RAPIDAPI_KEY` as an environment variable. Same shape as above.

If your client only accepts a raw command, use:

```json
{ "command": "filingrail-mcp", "env": { "RAPIDAPI_KEY": "your-rapidapi-key-here" } }
```

## Tools exposed

| Tool | What it does |
|---|---|
| `search_companies(q, limit)` | Resolve ticker / CIK / name fragment to a company (8,000+ SEC issuers, fuzzy match) |
| `get_recent_filings(form_type, cik, limit)` | Recent filings firehose — filter by form (`10-K`, `8-K`, `4`, `13F-HR`) or CIK |
| `get_financials(ticker_or_cik, limit)` | Latest 10-K / 10-Q normalized line items + `source_filing_url` |
| `get_financials_history(ticker_or_cik, period, limit, …)` | Historical quarterly or annual series |
| `get_insider_trades(ticker_or_cik, since, limit)` | Form 4 transactions — who bought/sold, when, how much |
| `get_8k_events(ticker_or_cik, since, limit)` | 8-K material events with SEC item codes (5.02, 2.01, …) |
| `get_13f_holdings(institution_cik, quarter, limit)` | Institutional holdings (e.g. Berkshire = CIK 1067983) |
| `health()` | API liveness check |

## Try it

After installing and configuring, ask your agent:

- *"What was Apple's revenue and operating income last quarter, and link me the filing."*
- *"Show me insider sells at NVIDIA in the last 30 days."*
- *"What 8-K events did Tesla file this month?"*
- *"List Berkshire Hathaway's 10 largest 13F positions for 2026-Q1."*

## What it is not

Honest caveats:

- **Not real-time.** New filings appear within ~24h of EDGAR acceptance (fair-access policy).
- **Not Bloomberg.** No intraday prices, options chains, non-US issuers, or analyst estimates.
- **Structured SEC data, traced to source** — that's the whole product.

## Pricing

| Tier | Price | Calls/month |
|---|---|---|
| Free | $0 | 1,500 (50/day) |
| Pro | $9/mo | 5,000 |
| Ultra | $49/mo | 50,000 |
| Mega | $199/mo | 500,000 |

Keys and billing are handled by RapidAPI. **[Get yours →](https://rapidapi.com/hudson-enterprises-llc-hudson-enterprises-llc-default/api/filingrail)**

## Links

- [Get an API key (RapidAPI listing)](https://rapidapi.com/hudson-enterprises-llc-hudson-enterprises-llc-default/api/filingrail)
- [Filingrail homepage](https://filingrail.hudsonenterprisesllc.com)
- [Python SDK (sync + async)](https://pypi.org/project/filingrail/) — `pip install filingrail`
- [API status page](https://status.hudsonenterprisesllc.com)
- Questions / issues: `support@hudsonenterprisesllc.com`

## License

MIT © Hudson Enterprises LLC
