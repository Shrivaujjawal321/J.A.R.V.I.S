# Future MCP Servers — Setup Recipes

> Pulled out of `.mcp.json` because they need OAuth credentials or API keys before they can run.
> When ready, copy the relevant block back into `.mcp.json` under `mcpServers`.

---

## Gmail

**Status:** Boss already has Gmail MCP connected at the **user level** (globally). Project-level not needed.

If you want to add it project-scoped instead, recipe:

```json
"gmail": {
  "command": "npx",
  "args": ["-y", "@gongrzhe/server-gmail-autoauth"],
  "env": {
    "GMAIL_OAUTH_PATH": "/home/ujjwal/Documents/J.A.R.V.I.S./credentials.json",
    "GMAIL_CREDENTIALS_PATH": "/home/ujjwal/Documents/J.A.R.V.I.S./data/gmail_token.json"
  }
}
```

**Setup steps:**
1. Get OAuth credentials from https://console.cloud.google.com
2. Save as `credentials.json` in project root
3. Run the server once to do auth flow → produces `data/gmail_token.json`

---

## Google Calendar

```json
"gcal": {
  "command": "npx",
  "args": ["-y", "@cocal/google-calendar-mcp"],
  "env": {
    "GOOGLE_OAUTH_CREDENTIALS": "/home/ujjwal/Documents/J.A.R.V.I.S./credentials.json"
  }
}
```

**Setup:** Same Google Cloud OAuth flow as Gmail. Both can share `credentials.json`.

---

## Notion

```json
"notion": {
  "command": "npx",
  "args": ["-y", "@notionhq/notion-mcp-server"],
  "env": {
    "NOTION_API_KEY": "your_notion_integration_token_here"
  }
}
```

**Setup:**
1. Create integration at https://notion.so/my-integrations
2. Copy the integration token
3. **Important:** Share each Notion page you want Jarvis to access *with* the integration (Notion's permission model)

---

## Brave Search

```json
"brave-search": {
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-brave-search"],
  "env": {
    "BRAVE_API_KEY": "your_brave_api_key_here"
  }
}
```

**Setup:** Get API key from https://brave.com/search/api/
**Alternative:** Built-in WebSearch tool already works — Brave only needed for higher rate limits or specific search features.

---

## Puppeteer (Browser Automation)

```json
"puppeteer": {
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-puppeteer"]
}
```

**Setup:** No credentials needed. Just enable when needed.
**Note:** Boss already has chrome-devtools MCP at user level which covers most browser automation.
