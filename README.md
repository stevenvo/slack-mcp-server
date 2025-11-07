# Slack MCP Server

<!-- mcp-name: io.github.stevenvo/slack-mcp-server -->

[![PyPI](https://img.shields.io/pypi/v/slack-mcp-server-v2)](https://pypi.org/project/slack-mcp-server-v2/)
[![Python Version](https://img.shields.io/pypi/pyversions/slack-mcp-server-v2)](https://pypi.org/project/slack-mcp-server-v2/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Model Context Protocol (MCP) server that provides programmatic access to Slack conversations, threads, and workspace information. Designed for AI assistants like Claude to interact with your Slack workspace through a standardized interface.

## What is MCP?

The [Model Context Protocol](https://modelcontextprotocol.io) is an open standard that enables AI assistants to securely access external data sources and tools. This server implements MCP to give Claude direct access to your Slack workspace.

## Features

### 📨 Message Operations
- **Read Channel Messages**: Fetch recent messages from any channel with flexible time-based filtering
- **Read Thread Messages**: Access complete conversation threads including all replies
- **Get Message Permalinks**: Generate permanent, shareable links to specific messages

### 🔍 Discovery & Search
- **List Your Channels**: Enumerate all channels you're a member of (public, private, DMs, group DMs)
- **Search Conversations**: Find messages where you're mentioned or involved using Slack's search

### 📊 Metadata & Context
- **Get Channel Info**: View channel details, topics, purposes, member counts, and settings
- **Get User Info**: Look up user profiles, emails, titles, timezones, and status information

## Quick Start

### Option 1: Install from PyPI (Recommended)

The easiest way to use this MCP server is to install it directly from PyPI:

```bash
# Install via pip
pip install slack-mcp-server-v2

# Or install via uvx (recommended for MCP servers)
uvx slack-mcp-server-v2
```

### Option 2: Install from Source

```bash
# Clone the repository
git clone https://github.com/stevenvo/slack-mcp-server.git
cd slack-mcp-server

# Install dependencies
pip install -r requirements.txt
```

After installation, you'll need to set up authentication (see below).

## Authentication

### Option 1: User Token (Recommended)

A User Token uses your personal Slack permissions and can access all channels you're a member of.

1. Go to https://api.slack.com/apps
2. Create a new app (or use existing)
3. Navigate to "OAuth & Permissions"
4. Add the following **User Token Scopes**:
   - `channels:history` - View messages in public channels
   - `channels:read` - View basic channel info
   - `groups:history` - View messages in private channels
   - `groups:read` - View basic private channel info
   - `im:history` - View messages in direct messages
   - `im:read` - View basic DM info
   - `mpim:history` - View messages in group DMs
   - `mpim:read` - View basic group DM info
   - `users:read` - View user information
   - `search:read` - Search messages
5. Install the app to your workspace
6. Copy the "User OAuth Token" (starts with `xoxp-`)

### Option 2: Bot Token

A Bot Token is more limited but easier to set up for team-wide access.

1. Follow steps 1-2 above
2. Add **Bot Token Scopes** instead (same list but in bot section)
3. Install the app
4. Copy the "Bot User OAuth Token" (starts with `xoxb-`)
5. Invite the bot to channels you want to read: `/invite @YourBotName`

### Configure Environment

Create a `.env` file:

```bash
cp .env.example .env
```

Edit `.env` and add your token:

```bash
# Use one of these:
SLACK_USER_TOKEN=xoxp-your-user-token-here
# OR
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
```

## Configuration for Claude Code

Add this server to Claude Code by editing your `~/.claude.json` file:

### Using PyPI Package (Recommended)

```json
{
  "mcpServers": {
    "slack": {
      "command": "uvx",
      "args": ["slack-mcp-server-v2"],
      "env": {
        "SLACK_USER_TOKEN": "xoxp-your-user-token-here",
        "SLACK_WORKSPACE_URL": "https://your-workspace.slack.com"
      }
    }
  }
}
```

### Using Local Installation

If you installed from source:

```json
{
  "mcpServers": {
    "slack": {
      "command": "python",
      "args": ["/path/to/slack-mcp-server/server.py"],
      "env": {
        "SLACK_USER_TOKEN": "xoxp-your-user-token-here",
        "SLACK_WORKSPACE_URL": "https://your-workspace.slack.com"
      }
    }
  }
}
```

### Using Bot Token

If you prefer to use a bot token instead of a user token:

```json
{
  "mcpServers": {
    "slack": {
      "command": "uvx",
      "args": ["slack-mcp-server-v2"],
      "env": {
        "SLACK_BOT_TOKEN": "xoxb-your-bot-token-here",
        "SLACK_WORKSPACE_URL": "https://your-workspace.slack.com"
      }
    }
  }
}
```

**Note**: Remember to invite your bot to channels: `/invite @YourBotName`

### Verify Installation

Restart Claude Code and verify the server is running:

```bash
claude mcp list
```

You should see `slack` in the list of active MCP servers.

## Available Tools

This server provides 7 MCP tools for interacting with Slack:

### 📬 `read_channel_messages`

Retrieve recent messages from any Slack channel with flexible time filtering.

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `channel_id` | string | ✅ | - | Slack channel ID (e.g., `C1234567890`) |
| `lookback_hours` | number | ❌ | 24 | Hours to look back from now |
| `limit` | number | ❌ | 100 | Max messages to retrieve (max: 1000) |

**Natural Language Examples:**
- "Show me messages from the #general channel in the last 24 hours"
- "Read the last 48 hours of messages from channel C1234567890"
- "Get the most recent 50 messages from C070PDRHQS1"

**Returns:** Formatted messages with timestamps, user mentions, thread indicators, reactions, and permalinks.

---

### 💬 `read_thread_messages`

Read all messages in a conversation thread, including the parent message and all replies.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `channel_id` | string | ✅ | Channel ID where the thread exists |
| `thread_ts` | string | ✅ | Thread timestamp (the `ts` field of the parent message) |

**Natural Language Examples:**
- "Read the full thread with timestamp 1699564800.123456 in channel C1234567890"
- "Show me all replies to message ts 1699564800.123456"

**Returns:** Complete thread with parent message and all replies, formatted with timestamps and reactions.

---

### 📋 `get_channel_info`

Get detailed metadata about a Slack channel.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `channel_id` | string | ✅ | Slack channel ID |

**Natural Language Examples:**
- "Get info about channel C1234567890"
- "Show me details for the #engineering channel"

**Returns:** Channel name, ID, creation date, member count, privacy status, topic, and purpose.

---

### 👤 `get_user_info`

Look up detailed profile information for any Slack user.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `user_id` | string | ✅ | Slack user ID (e.g., `U1234567`) |

**Natural Language Examples:**
- "Get info about user U1234567"
- "Show me details for @john.doe"

**Returns:** User's real name, display name, email, title, status, timezone, and admin/bot flags.

---

### 📑 `list_my_channels`

List all channels you're a member of, with support for different channel types.

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `types` | string | ❌ | `public_channel,private_channel` | Comma-separated channel types |

**Supported Types:**
- `public_channel` - Public channels
- `private_channel` - Private channels
- `mpim` - Group direct messages
- `im` - Direct messages

**Natural Language Examples:**
- "List all my channels"
- "Show me all private channels I'm in"
- "List all my DMs"

**Returns:** Channel names, IDs, member counts, and privacy indicators.

---

### 🔍 `search_my_conversations`

Search for messages across all conversations where you're mentioned or involved.

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `query` | string | ✅ | - | Search terms |
| `count` | number | ❌ | 20 | Number of results (max: 100) |

**Natural Language Examples:**
- "Search my conversations for 'deployment'"
- "Find messages mentioning 'bug fix' in the last week"
- "Search for messages about 'Q4 planning'"

**Returns:** Matching messages with channel names, user info, timestamps, and permalinks.

---

### 🔗 `get_message_permalink`

Generate a permanent, shareable link to a specific Slack message.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `channel_id` | string | ✅ | Channel ID |
| `message_ts` | string | ✅ | Message timestamp |

**Natural Language Examples:**
- "Get permalink for message 1699564800.123456 in channel C1234567890"
- "Generate a link to this message"

**Returns:** Permanent URL that works even if the workspace's URL changes.

## Usage Examples

Once configured in Claude Code, you can interact with your Slack workspace using natural language. Here are some example queries:

### Reading Messages
```
👤 "Show me the latest messages from #engineering"
🤖 [Claude fetches and displays recent messages with timestamps, users, and links]

👤 "What were the last 100 messages in the #product-updates channel from the past week?"
🤖 [Claude retrieves messages from the last 168 hours with limit of 100]
```

### Following Threads
```
👤 "Read the full thread that starts at timestamp 1699564800.123456 in channel C1234567890"
🤖 [Claude displays the entire conversation thread with all replies]
```

### Discovery & Search
```
👤 "List all channels I'm a member of"
🤖 [Claude shows all your public and private channels with member counts]

👤 "Search my Slack conversations for 'quarterly review'"
🤖 [Claude searches across all your messages and shows matches with context]

👤 "Find mentions of 'production deployment' in my conversations"
🤖 [Claude uses Slack search to find relevant messages]
```

### Getting Context
```
👤 "Get info about channel C1234567890"
🤖 [Claude shows channel name, topic, member count, etc.]

👤 "Who is user U1234567?"
🤖 [Claude displays user profile with email, title, timezone]

👤 "Get me a permanent link to message 1699564800.123456 in #general"
🤖 [Claude generates a shareable permalink]
```

### Practical Workflows

**Catch up on a project:**
```
👤 "Show me all messages from #project-alpha in the last 3 days"
```

**Find that important decision:**
```
👤 "Search for messages about 'API migration decision'"
```

**Get onboarding context:**
```
👤 "List all channels I'm in and show me the purpose of each"
```

## Finding Channel IDs

### Method 1: From Slack URL
When you're in a channel, the URL looks like:
```
https://your-workspace.slack.com/archives/C1234567890/p1234567890
```
The part after `/archives/` is the channel ID: `C1234567890`

### Method 2: Using the MCP Server
Ask Claude:
```
List all my channels
```

### Method 3: Right-click in Slack
1. Right-click on the channel name
2. Click "Copy link"
3. Extract the channel ID from the URL

## Requirements

- **Python**: 3.10 or higher
- **Slack Workspace**: Admin access to create and configure a Slack app
- **Claude Code**: Latest version with MCP support
- **Operating System**: macOS, Linux, or Windows with WSL

## Troubleshooting

### "Missing required scopes" Error

Your Slack app needs the proper OAuth scopes configured.

**Solution:**
1. Go to https://api.slack.com/apps and select your app
2. Navigate to "OAuth & Permissions"
3. Ensure you've added all required scopes listed in the Authentication section
4. Reinstall the app to your workspace
5. Copy the new token

### "Channel not found" Error

**For Bot Tokens:**
```bash
# Invite the bot to the channel first
/invite @YourBotName
```

**For User Tokens:**
- Verify you're a member of the channel
- Check the channel ID is correct (see "Finding Channel IDs" section)

### "Not authenticated" Error

**Check your configuration:**
```bash
# Verify token is set correctly (check ~/.claude.json)
cat ~/.claude.json | grep -A 5 "slack"

# Ensure no extra whitespace
echo "$SLACK_USER_TOKEN" | wc -c
```

**Common issues:**
- Token has expired or been revoked
- Extra spaces or newlines in the token string
- Wrong token type (user vs bot)
- Token not properly quoted in JSON

### MCP Server Not Running

**Verify server is loaded:**
```bash
# List all MCP servers
claude mcp list

# Check if slack server is running
claude mcp list | grep slack
```

**Check logs for errors:**
```bash
# View recent MCP server logs
tail -f ~/.claude/debug/*.log

# Filter for slack-related errors
tail -f ~/.claude/debug/*.log | grep -i slack
```

**Common solutions:**
1. Restart Claude Code completely
2. Check `~/.claude.json` syntax is valid JSON
3. Verify Python version: `python --version` (must be 3.10+)
4. Test the server manually: `python server.py` (if installed from source)

### SSL Certificate Errors

If you're behind a corporate proxy (like Zscaler):

```bash
# Set SSL certificate environment variable
export SSL_CERT_FILE=/path/to/your/ca-bundle.pem
export REQUESTS_CA_BUNDLE=/path/to/your/ca-bundle.pem

# Then reinstall
pip install slack-mcp-server-v2
```

### Rate Limiting

Slack API has rate limits. If you hit them:
- Reduce the `limit` parameter in `read_channel_messages`
- Increase `lookback_hours` to fetch fewer messages
- Wait a few minutes before retrying

**Rate limit indicators:**
```
Error: ratelimited
```

**Solution:** The server will automatically handle rate limits, but you may need to wait.

## Security & Privacy

### Token Security

- **Never commit tokens to version control** - The `.env` file is gitignored by default
- **Revoke compromised tokens immediately** at https://api.slack.com/apps
- **Use environment variables** in production, never hardcode tokens
- **Rotate tokens periodically** as part of security best practices

### Data Access

**User Tokens:**
- Have access to everything you can see in Slack
- Use your personal permissions
- See all channels you're a member of
- More convenient for personal use

**Bot Tokens:**
- Limited to channels where the bot is invited
- Separate from personal identity
- Better for team/shared setups
- More granular control

### Corporate Environments

If you're using this in a corporate environment:
- Check with your IT/Security team before creating Slack apps
- Be aware of data retention and compliance policies
- Consider using bot tokens for audit trails
- SSL certificate configuration may be required (see Troubleshooting)

## Limitations

- **Read-only**: This server only reads data, it cannot post messages or modify content
- **Rate limits**: Subject to Slack's API rate limits (Tier 3: ~50 requests per minute)
- **Token scope**: Can only access channels/conversations the token has permission to see
- **Message history**: Limited to Slack workspace's message retention policy

## Contributing

Contributions are welcome! Here's how you can help:

### Reporting Issues

Found a bug or have a feature request?
1. Check existing issues at https://github.com/stevenvo/slack-mcp-server/issues
2. Create a new issue with:
   - Clear description of the problem/feature
   - Steps to reproduce (for bugs)
   - Expected vs actual behavior
   - Your environment (Python version, OS, Claude Code version)

### Pull Requests

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Test thoroughly
5. Commit with clear messages: `git commit -m "Add amazing feature"`
6. Push to your fork: `git push origin feature/amazing-feature`
7. Open a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/slack-mcp-server.git
cd slack-mcp-server

# Install in development mode
pip install -e .

# Make changes and test
python server.py
```

## Changelog

### v0.1.0 (2025-01-06)
- Initial release
- 7 core tools for reading Slack conversations
- Support for user and bot tokens
- Published to PyPI and MCP registry
- Comprehensive documentation

## Roadmap

Potential future enhancements:
- [ ] Support for Slack Enterprise Grid
- [ ] Message filtering by user or reactions
- [ ] Export conversations to different formats
- [ ] Support for Slack Connect channels
- [ ] Caching to reduce API calls
- [ ] Webhook support for real-time updates

Suggestions welcome in [GitHub Issues](https://github.com/stevenvo/slack-mcp-server/issues)!

## Related Projects

- [Model Context Protocol](https://modelcontextprotocol.io) - The MCP specification
- [MCP Registry](https://registry.modelcontextprotocol.io) - Browse more MCP servers
- [Slack SDK for Python](https://github.com/slackapi/python-slack-sdk) - The underlying library
- [Claude Code](https://claude.com/claude-code) - AI assistant with MCP support

## Support

- **Documentation**: You're reading it!
- **Issues**: https://github.com/stevenvo/slack-mcp-server/issues
- **Discussions**: https://github.com/stevenvo/slack-mcp-server/discussions
- **Slack API Docs**: https://api.slack.com/docs

## License

MIT License - see [LICENSE](LICENSE) file for details.

Copyright (c) 2025 Steven Vo

---

**Made with ❤️ for the MCP community**

If you find this useful, please ⭐ star the repository on GitHub!
