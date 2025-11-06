#!/usr/bin/env python3
"""
Slack MCP Server - Read conversations and threads you're involved in.

Provides tools to:
- Read channel messages
- Read thread messages
- Get channel info
- Get user info
- Search for your conversations
"""

import os
import ssl
import logging
from datetime import datetime, timedelta
from typing import Any, Optional
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from mcp.server import Server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
import mcp.server.stdio

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("slack-mcp")

# Initialize Slack client
SLACK_TOKEN = os.getenv("SLACK_USER_TOKEN", os.getenv("SLACK_BOT_TOKEN", ""))
if not SLACK_TOKEN:
    logger.error("No SLACK_USER_TOKEN or SLACK_BOT_TOKEN found in environment")
    raise ValueError("SLACK_USER_TOKEN or SLACK_BOT_TOKEN environment variable is required")

# Create SSL context for Zscaler proxy compatibility
ssl_context = ssl.create_default_context()

# Check for custom CA bundle (Zscaler)
ca_bundle = os.getenv("SSL_CERT_FILE") or os.getenv("REQUESTS_CA_BUNDLE")
if ca_bundle and os.path.exists(ca_bundle):
    logger.info(f"Using custom CA bundle: {ca_bundle}")
    ssl_context.load_verify_locations(ca_bundle)

slack_client = WebClient(token=SLACK_TOKEN, ssl=ssl_context)

# Create MCP server
app = Server("slack-mcp")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available Slack tools."""
    return [
        Tool(
            name="read_channel_messages",
            description="Read messages from a Slack channel. Supports filtering by time range.",
            inputSchema={
                "type": "object",
                "properties": {
                    "channel_id": {
                        "type": "string",
                        "description": "Slack channel ID (e.g., C1234567890)"
                    },
                    "lookback_hours": {
                        "type": "number",
                        "description": "Hours to look back (default: 24)",
                        "default": 24
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum messages to retrieve (default: 100, max: 1000)",
                        "default": 100
                    }
                },
                "required": ["channel_id"]
            }
        ),
        Tool(
            name="read_thread_messages",
            description="Read all messages in a specific thread.",
            inputSchema={
                "type": "object",
                "properties": {
                    "channel_id": {
                        "type": "string",
                        "description": "Slack channel ID where the thread exists"
                    },
                    "thread_ts": {
                        "type": "string",
                        "description": "Thread timestamp (ts of the parent message)"
                    }
                },
                "required": ["channel_id", "thread_ts"]
            }
        ),
        Tool(
            name="get_channel_info",
            description="Get information about a Slack channel.",
            inputSchema={
                "type": "object",
                "properties": {
                    "channel_id": {
                        "type": "string",
                        "description": "Slack channel ID"
                    }
                },
                "required": ["channel_id"]
            }
        ),
        Tool(
            name="get_user_info",
            description="Get information about a Slack user.",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "Slack user ID"
                    }
                },
                "required": ["user_id"]
            }
        ),
        Tool(
            name="list_my_channels",
            description="List all channels you're a member of.",
            inputSchema={
                "type": "object",
                "properties": {
                    "types": {
                        "type": "string",
                        "description": "Channel types (comma-separated: public_channel, private_channel, mpim, im)",
                        "default": "public_channel,private_channel"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="search_my_conversations",
            description="Search for messages where you're mentioned or involved in conversations.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (automatically includes your mentions)"
                    },
                    "count": {
                        "type": "number",
                        "description": "Number of results (default: 20, max: 100)",
                        "default": 20
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_message_permalink",
            description="Get a permanent link to a specific message.",
            inputSchema={
                "type": "object",
                "properties": {
                    "channel_id": {
                        "type": "string",
                        "description": "Slack channel ID"
                    },
                    "message_ts": {
                        "type": "string",
                        "description": "Message timestamp"
                    }
                },
                "required": ["channel_id", "message_ts"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls."""
    try:
        if name == "read_channel_messages":
            return await read_channel_messages(
                arguments["channel_id"],
                arguments.get("lookback_hours", 24),
                arguments.get("limit", 100)
            )

        elif name == "read_thread_messages":
            return await read_thread_messages(
                arguments["channel_id"],
                arguments["thread_ts"]
            )

        elif name == "get_channel_info":
            return await get_channel_info(arguments["channel_id"])

        elif name == "get_user_info":
            return await get_user_info(arguments["user_id"])

        elif name == "list_my_channels":
            return await list_my_channels(
                arguments.get("types", "public_channel,private_channel")
            )

        elif name == "search_my_conversations":
            return await search_my_conversations(
                arguments["query"],
                arguments.get("count", 20)
            )

        elif name == "get_message_permalink":
            return await get_message_permalink(
                arguments["channel_id"],
                arguments["message_ts"]
            )

        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

    except SlackApiError as e:
        error_msg = f"Slack API error: {e.response['error']}"
        logger.error(error_msg)
        return [TextContent(type="text", text=error_msg)]

    except Exception as e:
        error_msg = f"Error: {str(e)}"
        logger.error(error_msg)
        return [TextContent(type="text", text=error_msg)]


async def read_channel_messages(
    channel_id: str,
    lookback_hours: float,
    limit: int
) -> list[TextContent]:
    """Read messages from a channel."""
    # Calculate timestamp
    since_dt = datetime.utcnow() - timedelta(hours=lookback_hours)
    oldest_ts = str(since_dt.timestamp())

    # Get channel info
    channel_info = slack_client.conversations_info(channel=channel_id)
    channel_name = channel_info["channel"]["name"]

    # Fetch messages
    result = slack_client.conversations_history(
        channel=channel_id,
        oldest=oldest_ts,
        limit=min(limit, 1000)
    )

    messages = []
    for msg in result["messages"]:
        # Skip bot messages and system messages
        if msg.get("subtype") in ["bot_message", "channel_join", "channel_leave"]:
            continue

        user_id = msg.get("user", "unknown")
        ts = msg.get("ts", "")
        text = msg.get("text", "")

        # Format timestamp
        msg_time = datetime.fromtimestamp(float(ts)).strftime("%Y-%m-%d %H:%M:%S UTC")

        # Build message URL (requires SLACK_WORKSPACE_URL env var)
        workspace_url = os.getenv("SLACK_WORKSPACE_URL", "https://your-workspace.slack.com")
        ts_clean = ts.replace(".", "")
        msg_url = f"{workspace_url}/archives/{channel_id}/p{ts_clean}"

        # Format message
        formatted = f"**Time:** {msg_time}\n"
        formatted += f"**User:** <@{user_id}>\n"
        formatted += f"**Link:** {msg_url}\n"

        if msg.get("thread_ts"):
            formatted += f"**Thread:** Yes (replies: {msg.get('reply_count', 0)})\n"

        formatted += f"**Message:**\n{text}\n"

        # Add reactions if any
        if msg.get("reactions"):
            reactions = ", ".join([f":{r['name']}: ({r['count']})" for r in msg["reactions"]])
            formatted += f"**Reactions:** {reactions}\n"

        formatted += "\n---\n"
        messages.append(formatted)

    summary = f"# Messages from #{channel_name}\n"
    summary += f"Found {len(messages)} messages from the last {lookback_hours} hours\n\n"
    summary += "".join(messages)

    return [TextContent(type="text", text=summary)]


async def read_thread_messages(channel_id: str, thread_ts: str) -> list[TextContent]:
    """Read all messages in a thread."""
    result = slack_client.conversations_replies(
        channel=channel_id,
        ts=thread_ts
    )

    messages = []
    for idx, msg in enumerate(result["messages"]):
        user_id = msg.get("user", "unknown")
        ts = msg.get("ts", "")
        text = msg.get("text", "")

        msg_time = datetime.fromtimestamp(float(ts)).strftime("%Y-%m-%d %H:%M:%S UTC")

        prefix = "**[PARENT]**" if idx == 0 else f"**[REPLY {idx}]**"

        formatted = f"{prefix}\n"
        formatted += f"**Time:** {msg_time}\n"
        formatted += f"**User:** <@{user_id}>\n"
        formatted += f"**Message:**\n{text}\n"

        if msg.get("reactions"):
            reactions = ", ".join([f":{r['name']}: ({r['count']})" for r in msg["reactions"]])
            formatted += f"**Reactions:** {reactions}\n"

        formatted += "\n---\n"
        messages.append(formatted)

    workspace_url = os.getenv("SLACK_WORKSPACE_URL", "https://your-workspace.slack.com")
    thread_url = f"{workspace_url}/archives/{channel_id}/p{thread_ts.replace('.', '')}"
    summary = f"# Thread Messages\n"
    summary += f"**Link:** {thread_url}\n"
    summary += f"**Total messages:** {len(messages)}\n\n"
    summary += "".join(messages)

    return [TextContent(type="text", text=summary)]


async def get_channel_info(channel_id: str) -> list[TextContent]:
    """Get channel information."""
    result = slack_client.conversations_info(channel=channel_id)
    channel = result["channel"]

    info = f"# Channel Information\n\n"
    info += f"**Name:** #{channel.get('name')}\n"
    info += f"**ID:** {channel.get('id')}\n"
    info += f"**Created:** {datetime.fromtimestamp(channel.get('created', 0)).strftime('%Y-%m-%d')}\n"
    info += f"**Members:** {channel.get('num_members', 'N/A')}\n"
    info += f"**Is Private:** {channel.get('is_private', False)}\n"
    info += f"**Is Archived:** {channel.get('is_archived', False)}\n"

    if channel.get("topic", {}).get("value"):
        info += f"**Topic:** {channel['topic']['value']}\n"

    if channel.get("purpose", {}).get("value"):
        info += f"**Purpose:** {channel['purpose']['value']}\n"

    return [TextContent(type="text", text=info)]


async def get_user_info(user_id: str) -> list[TextContent]:
    """Get user information."""
    result = slack_client.users_info(user=user_id)
    user = result["user"]
    profile = user.get("profile", {})

    info = f"# User Information\n\n"
    info += f"**Name:** {user.get('real_name', user.get('name'))}\n"
    info += f"**ID:** {user.get('id')}\n"
    info += f"**Display Name:** @{user.get('name')}\n"
    info += f"**Email:** {profile.get('email', 'N/A')}\n"
    info += f"**Title:** {profile.get('title', 'N/A')}\n"
    info += f"**Status:** {profile.get('status_text', 'N/A')}\n"
    info += f"**Timezone:** {user.get('tz_label', 'N/A')}\n"
    info += f"**Is Admin:** {user.get('is_admin', False)}\n"
    info += f"**Is Bot:** {user.get('is_bot', False)}\n"

    return [TextContent(type="text", text=info)]


async def list_my_channels(types: str) -> list[TextContent]:
    """List channels the user is a member of."""
    result = slack_client.conversations_list(
        types=types,
        exclude_archived=True,
        limit=1000
    )

    channels = []
    for channel in result["channels"]:
        if channel.get("is_member"):
            name = channel.get("name", "unknown")
            channel_id = channel.get("id")
            members = channel.get("num_members", 0)
            is_private = "🔒" if channel.get("is_private") else "🌐"

            channels.append(f"- {is_private} **#{name}** (`{channel_id}`) - {members} members")

    summary = f"# Your Channels\n"
    summary += f"Found {len(channels)} channels you're a member of:\n\n"
    summary += "\n".join(channels)

    return [TextContent(type="text", text=summary)]


async def search_my_conversations(query: str, count: int) -> list[TextContent]:
    """Search for messages mentioning the user or matching query."""
    # Get current user ID
    auth_result = slack_client.auth_test()
    user_id = auth_result["user_id"]

    # Add user mention to query
    search_query = f"{query} <@{user_id}>"

    result = slack_client.search_messages(
        query=search_query,
        count=min(count, 100)
    )

    messages = []
    for match in result["messages"]["matches"]:
        channel_name = match.get("channel", {}).get("name", "unknown")
        user = match.get("user", "unknown")
        text = match.get("text", "")
        ts = match.get("ts", "")
        permalink = match.get("permalink", "")

        msg_time = datetime.fromtimestamp(float(ts)).strftime("%Y-%m-%d %H:%M:%S UTC")

        formatted = f"**Channel:** #{channel_name}\n"
        formatted += f"**User:** <@{user}>\n"
        formatted += f"**Time:** {msg_time}\n"
        formatted += f"**Link:** {permalink}\n"
        formatted += f"**Message:**\n{text}\n"
        formatted += "\n---\n"

        messages.append(formatted)

    total = result["messages"]["total"]
    summary = f"# Search Results\n"
    summary += f"Query: '{query}' (including mentions of you)\n"
    summary += f"Found {total} total matches, showing {len(messages)} results:\n\n"
    summary += "".join(messages)

    return [TextContent(type="text", text=summary)]


async def get_message_permalink(channel_id: str, message_ts: str) -> list[TextContent]:
    """Get a permanent link to a message."""
    result = slack_client.chat_getPermalink(
        channel=channel_id,
        message_ts=message_ts
    )

    permalink = result["permalink"]
    info = f"# Message Permalink\n\n**Link:** {permalink}"

    return [TextContent(type="text", text=info)]


async def main():
    """Run the MCP server."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
