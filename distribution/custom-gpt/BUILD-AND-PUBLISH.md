# SEC Filing Analyst — Custom GPT: build & publish guide

**Status:** ready-to-paste config. Publishing needs an **OpenAI account with ChatGPT Plus/Team/Enterprise** (GPT builder access) → **FLAGGED FOR OPERATOR**. Everything below is complete; the operator just pastes and clicks.

Every install of this GPT funnels the user to subscribe to Filingrail on RapidAPI (they bring their own key), so the GPT is a demand funnel into a paid API subscription.

## Files in this folder

- `system-instructions.md` — paste into the GPT builder's **Instructions** field.
- `openapi-actions-schema.yaml` — paste into the Action's **Schema** field.
- `gpt-profile.md` — name, description, conversation starters, category.

## Step-by-step (operator, ~10 min)

1. Go to **chatgpt.com** → left sidebar **GPTs** → **+ Create** → **Configure** tab.
2. **Name:** `SEC Filing Analyst`
3. **Description:** (from `gpt-profile.md`)
4. **Instructions:** paste the full body of `system-instructions.md`.
5. **Conversation starters:** paste the four from `gpt-profile.md`.
6. **Capabilities:** turn OFF Web Browsing, DALL-E, Code Interpreter (not needed; keeps it fast and on-task). Leave them off unless you want browsing as a fallback.
7. **Actions → Create new action:**
   - **Authentication:** `API Key` → **Auth Type:** `API Key`, **Custom Header Name:** `X-RapidAPI-Key`. Paste a **RapidAPI key** here (see "Whose key?" below).
   - **Schema:** paste the full contents of `openapi-actions-schema.yaml`.
   - **Privacy policy URL:** `https://hudsonenterprisesllc.com/legal/privacy`
8. **Test** in the right-hand preview: try *"What was Apple's revenue last quarter?"* — it should call `getFinancials` and return numbers + a `sec.gov` link.
9. **Save → Publish.** Visibility:
   - **"Anyone with the link"** — recommended for distribution (share the link in the dev.to post / socials).
   - **"GPT Store"** — for maximum discovery. Requires a verified builder profile (name or verified domain). Category: **Research & Analysis**.

## Whose key? (the funnel mechanics)

GPT Actions send **one** API key that the *builder* configures — end users of a published GPT do **not** each paste their own key into the Action. So there are two viable models:

- **Model A — shared builder key (simplest, funnel via the prompt).** Put a Filingrail **Free-tier** key in the Action auth. All users share its 50 calls/day quota. When it's exhausted the GPT tells users to get their own key + install the SDK/MCP (the instructions already do this). Cheapest way to ship; the funnel is the in-chat CTA to RapidAPI. Watch the shared quota.
- **Model B — Pro key you fund (better UX, still a funnel).** Put a Filingrail **Pro ($9/mo)** key in the Action so the GPT "just works" for everyone, and let the system-prompt CTA drive users who want their own higher limits / the MCP server / the SDK to subscribe. Treat the $9 as demand-gen spend.

Either way the GPT's job in the portfolio is **awareness → RapidAPI subscription**, not per-user metering (that's what the MCP server + SDK are for, where each user genuinely brings their own key).

## Known gotcha — the X-RapidAPI-Host header

RapidAPI requires **two** headers: `X-RapidAPI-Key` (the API-key auth) and `X-RapidAPI-Host: filingrail.p.rapidapi.com`. GPT Actions inject only the key. The schema declares `X-RapidAPI-Host` as a **header parameter with a constant `default`** on every operation, which the Actions runtime sends automatically. If a test call returns a RapidAPI "host not specified" error, the fallback is to host a thin proxy (a Cloudflare Worker that adds the Host header) and point `servers.url` at it — but test the direct path first; the default-parameter approach works in current GPT Actions.

## Firewall / guardrail check

- Brand: Hudson Enterprises LLC. Support: `support@hudsonenterprisesllc.com`. Privacy: `hudsonenterprisesllc.com/legal/privacy`.
- No income/earnings claims. No investment advice (the system prompt forbids it).
- Uses only the public RapidAPI gateway `filingrail.p.rapidapi.com` — no origin secrets, no Superior Ag anything.
