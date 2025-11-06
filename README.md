# Slack MCP Server

MCP server for reading Slack conversations and threads you're involved in. Built specifically for use with Claude Code.

## Features

- **Read Channel Messages**: Get recent messages from any channel with time-based filtering
- **Read Thread Messages**: Read entire conversation threads
- **Get Channel Info**: View channel details and metadata
- **Get User Info**: Look up user profiles and information
- **List Your Channels**: See all channels you're a member of
- **Search Conversations**: Find messages where you're mentioned or involved
- **Get Message Links**: Generate permanent links to specific messages

## Installation

1. Clone or download this directory
2. Install dependencies:

```bash
cd slack-mcp-server
pip install -r requirements.txt
```

3. Set up your Slack token (see Authentication section below)

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

## Add to Claude Code

Add this to your `~/.claude.json` file in the `mcpServers` section:

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

Or if using uvx:

```json
{
  "mcpServers": {
    "slack": {
      "command": "uvx",
      "args": ["--from", "/path/to/slack-mcp-server", "slack-mcp"],
      "env": {
        "SLACK_USER_TOKEN": "xoxp-your-user-token-here",
        "SLACK_WORKSPACE_URL": "https://your-workspace.slack.com"
      }
    }
  }
}
```

Restart Claude Code and verify with:

```bash
claude mcp list
```

## Available Tools

### 1. `read_channel_messages`

Read recent messages from a channel.

**Parameters:**
- `channel_id` (required): Slack channel ID (e.g., `C1234567890`)
- `lookback_hours` (optional): Hours to look back (default: 24)
- `limit` (optional): Max messages to retrieve (default: 100, max: 1000)

**Example:**
```
Read the last 48 hours of messages from channel C1234567890
```

### 2. `read_thread_messages`

Read all messages in a thread.

**Parameters:**
- `channel_id` (required): Channel ID where thread exists
- `thread_ts` (required): Thread timestamp (from parent message)

**Example:**
```
Read the full thread with timestamp 1699564800.123456 in channel C1234567890
```

### 3. `get_channel_info`

Get channel metadata.

**Parameters:**
- `channel_id` (required): Channel ID

**Example:**
```
Get info about channel C1234567890
```

### 4. `get_user_info`

Get user profile information.

**Parameters:**
- `user_id` (required): User ID (e.g., `U1234567`)

**Example:**
```
Get info about user U1234567
```

### 5. `list_my_channels`

List all channels you're a member of.

**Parameters:**
- `types` (optional): Comma-separated types (default: `public_channel,private_channel`)
  - Options: `public_channel`, `private_channel`, `mpim`, `im`

**Example:**
```
List all my channels
```

### 6. `search_my_conversations`

Search for messages where you're mentioned or involved.

**Parameters:**
- `query` (required): Search terms
- `count` (optional): Number of results (default: 20, max: 100)

**Example:**
```
Search my conversations for "deployment" in the last week
```

### 7. `get_message_permalink`

Get a permanent link to a specific message.

**Parameters:**
- `channel_id` (required): Channel ID
- `message_ts` (required): Message timestamp

**Example:**
```
Get permalink for message 1699564800.123456 in channel C1234567890
```

## Usage with Claude Code

Once configured, you can ask Claude to:

- "Show me messages from the #general channel in the last 24 hours"
- "Read the thread starting at timestamp 1699564800.123456 in channel C1234567890"
- "Search my Slack conversations for mentions of 'deployment'"
- "List all channels I'm in"
- "Get info about user U1234567"

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

## Troubleshooting

### "Missing required scopes"
Make sure you've added all the required scopes in your Slack app configuration.

### "Channel not found"
- Verify the channel ID is correct
- If using a bot token, make sure the bot is invited to the channel (`/invite @BotName`)
- If using a user token, make sure you're a member of the channel

### "Not authenticated"
- Check that your `SLACK_USER_TOKEN` or `SLACK_BOT_TOKEN` is set correctly
- Verify the token hasn't expired
- Make sure there are no extra spaces in the `.env` file

### MCP Server Not Showing Up
```bash
# Check MCP server status
claude mcp list

# Check logs
tail -f ~/.claude/debug/*.log
```

## Security Notes

- Never commit your `.env` file or expose your Slack tokens
- User tokens have access to everything you can see in Slack - use with care
- Consider using bot tokens for shared/team setups
- Tokens can be revoked at https://api.slack.com/apps

## License

MIT
