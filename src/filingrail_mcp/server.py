"""Filingrail MCP server — expose the 7 v1 SEC EDGAR endpoints as MCP tools.

Run:
    pip install filingrail-mcp
    RAPIDAPI_KEY=... filingrail-mcp        # stdio (for Claude Desktop, Cursor, Continue)

Or with explicit stdio:
    python -m filingrail_mcp

Add to Claude Desktop's claude_desktop_config.json:
    {
      "mcpServers": {
        "filingrail": {
          "command": "filingrail-mcp",
          "env": { "RAPIDAPI_KEY": "..." }
        }
      }
    }
"""

from __future__ import annotations

import os
from typing import Any, Optional

from mcp.server.fastmcp import FastMCP
from filingrail import FilingrailClient, FilingrailError


mcp = FastMCP("filingrail")


def _client() -> FilingrailClient:
    key = os.environ.get("RAPIDAPI_KEY") or os.environ.get("X_RAPIDAPI_KEY")
    if not key:
        raise RuntimeError(
            "RAPIDAPI_KEY env var required. Subscribe at "
            "https://rapidapi.com/hudson-enterprises-llc-hudson-enterprises-llc-default/api/filingrail"
        )
    return FilingrailClient(api_key=key)


@mcp.tool()
def search_companies(q: str, limit: int = 10) -> list[dict]:
    """Search SEC-registered companies by ticker, CIK, or name fragment.

    Args:
        q: search term (e.g. "AAPL", "Apple", "320193")
        limit: max results (1-100, default 10)

    Returns: list of {cik, ticker, name, ...}
    """
    with _client() as c:
        return [c.__dict__ for c in c.search_companies(q, limit=limit)]


@mcp.tool()
def get_recent_filings(form_type: Optional[str] = None, cik: Optional[int] = None, limit: int = 25) -> list[dict]:
    """Get recent SEC filings, optionally filtered by form type or CIK.

    Args:
        form_type: filter by form (e.g. "10-K", "10-Q", "8-K", "4", "13F-HR")
        cik: filter by company CIK
        limit: max results (1-500, default 25)

    Returns: list of filings, newest first
    """
    with _client() as c:
        return [{
            "accession_number": f.accession_number,
            "cik": f.cik,
            "form_type": f.form_type,
            "filing_date": str(f.filing_date) if f.filing_date else None,
            "filing_url": f.filing_url,
        } for f in c.get_recent_filings(form_type=form_type, cik=cik, limit=limit)]


@mcp.tool()
def get_financials(ticker_or_cik: str, limit: int = 4) -> dict:
    """Get latest XBRL-normalized financial statements (balance sheet, income, cash flow).

    Args:
        ticker_or_cik: company ticker (e.g. "AAPL") or CIK (e.g. "320193")
        limit: number of statements to return (1-50, default 4)

    Returns: {statements: [{statement_type, period_end, line_items: {total_assets, revenue, ...}}], source_filing_url}
    """
    with _client() as c:
        statements = c.get_financials(ticker_or_cik, limit=limit)
        return {
            "ticker_or_cik": ticker_or_cik,
            "statements": [{
                "statement_type": s.statement_type,
                "period_start": str(s.period_start) if s.period_start else None,
                "period_end": str(s.period_end) if s.period_end else None,
                "period_type": s.period_type,
                "currency": s.currency,
                "line_items": s.line_items,
            } for s in statements],
            "source_filing_url": statements[0].source_filing_url if statements else None,
        }


@mcp.tool()
def get_financials_history(
    ticker_or_cik: str, period: str = "Q", limit: int = 12,
    statement_type: Optional[str] = None, line_item: Optional[str] = None,
) -> list[dict]:
    """Get historical quarterly or annual financial-statement series.

    Args:
        ticker_or_cik: company ticker or CIK
        period: "Q" (quarterly) or "A" (annual), default Q
        limit: max periods (1-100, default 12)
        statement_type: filter to one of "balance_sheet" / "income_statement" / "cash_flow"
        line_item: filter to a single line-item key (e.g. "revenue", "total_assets")

    Returns: list of statements oldest-to-newest
    """
    with _client() as c:
        return [{
            "statement_type": s.statement_type,
            "period_end": str(s.period_end) if s.period_end else None,
            "period_type": s.period_type,
            "line_items": s.line_items,
        } for s in c.get_financials_history(
            ticker_or_cik, period=period, limit=limit,
            statement_type=statement_type, line_item=line_item,
        )]


@mcp.tool()
def get_insider_trades(ticker_or_cik: str, since: Optional[str] = None, limit: int = 25) -> list[dict]:
    """Get insider transactions (Form 4) for a company.

    Args:
        ticker_or_cik: company ticker or CIK
        since: ISO date (YYYY-MM-DD) — only trades on or after this date
        limit: max trades (1-500, default 25)

    Returns: list of trades — insider_name, transaction_date, code, shares, price, USD value
    """
    with _client() as c:
        return [{
            "insider_name": t.insider_name,
            "officer_title": t.insider_relationship.officer_title,
            "is_director": t.insider_relationship.is_director,
            "is_officer": t.insider_relationship.is_officer,
            "transaction_date": str(t.transaction_date) if t.transaction_date else None,
            "transaction_code": t.transaction_code,
            "shares": t.shares,
            "price_per_share": t.price_per_share,
            "total_value_usd": t.total_value_usd,
            "shares_owned_after": t.shares_owned_after,
        } for t in c.get_insider_trades(ticker_or_cik, since=since, limit=limit)]


@mcp.tool()
def get_8k_events(ticker_or_cik: str, since: Optional[str] = None, limit: int = 10) -> list[dict]:
    """Get 8-K material events with SEC item codes for a company.

    Args:
        ticker_or_cik: company ticker or CIK
        since: ISO date — only events on or after this date
        limit: max events (1-200, default 10)

    Returns: list of events — event_date, item_codes (e.g. ["5.02", "9.01"]), descriptions
    """
    with _client() as c:
        return [{
            "event_date": str(e.event_date) if e.event_date else None,
            "item_codes": e.item_codes,
            "item_descriptions": e.item_descriptions,
            "summary": e.summary,
            "has_financial_exhibits": e.has_financial_exhibits,
        } for e in c.get_8k_events(ticker_or_cik, since=since, limit=limit)]


@mcp.tool()
def get_13f_holdings(institution_cik: int, quarter: Optional[str] = None, limit: int = 100) -> list[dict]:
    """Get 13F-HR institutional holdings for an investment manager.

    Args:
        institution_cik: institution's CIK (e.g. 1067983 for Berkshire Hathaway)
        quarter: YYYY-Qn format (e.g. "2026-Q1"), default latest
        limit: max holdings (1-5000, default 100)

    Returns: list of holdings — issuer_name, CUSIP, value_usd, shares
    """
    with _client() as c:
        return [{
            "issuer_cusip": h.issuer_cusip,
            "issuer_name": h.issuer_name,
            "issuer_ticker": h.issuer_ticker,
            "title_of_class": h.title_of_class,
            "value_usd": h.value_usd,
            "shares": h.shares,
            "investment_discretion": h.investment_discretion,
        } for h in c.get_13f_holdings(institution_cik, quarter=quarter, limit=limit)]


@mcp.tool()
def health() -> dict:
    """Check Filingrail API health. Returns {status: 'ok'} if live."""
    with _client() as c:
        return c.health()


def main():
    """Entry point for `filingrail-mcp` command."""
    mcp.run()


if __name__ == "__main__":
    main()
