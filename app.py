import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import asyncio
import io
import os
import json
from typing import Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot configuration
TOKEN = 'DISCORD-TOKEN'  # Replace with your bot token
API_CONFIG = {
    "endpoints": [
        {
            "name": "API-1",
            "url": "http://167.235.229.108/m/{appid}",
            "success_code": 200,
            "unavailable_code": 404,
            "enabled": True,
            "priority": 1
        },
        {
            "name": "API-2",
            "url": "http://167.235.229.108/{appid}",
            "success_code": 200,
            "unavailable_code": 404,
            "enabled": True,
            "priority": 2
        },
        {
            "name": "API-3",
            "url": "http://masss.pythonanywhere.com/storage?auth=IEOIJE54esfsipoE56GE4&appid={appid}",
            "success_code": 200,
            "unavailable_code": 404,
            "enabled": True,
            "priority": 3
        },
        {
            "name": "API-4",
            "url": "https://raw.githubusercontent.com/sushi-dev55-alt/sushitools-games-repo-alt/refs/heads/main/{appid}.zip",
            "success_code": 200,
            "unavailable_code": 404,
            "enabled": True,
            "priority": 4
        }
    ],
    "game_names": {
        "730": "Counter-Strike: Global Offensive",
        "570": "Dota 2",
        "440": "Team Fortress 2",
        "620": "Portal 2",
        "292030": "The Witcher 3",
        "3240220": "Game Files",
        "3249229": "Game Data"
    }
}

# Discord bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

class SteamFileDownloader:
    def __init__(self, api_config):
        self.api_config = api_config
        self.endpoints = sorted(api_config["endpoints"], key=lambda x: x["priority"])
        self.game_names = api_config["game_names"]
        self.session = None
        
    async def get_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close_session(self):
        if self.session and not self.session.closed:
            await self.session.close()
    
    def get_game_name(self, appid):
        """Get the game name for a given App ID"""
        return self.game_names.get(appid, f"Game (AppID: {appid})")
    
    async def download_file(self, appid):
        """Try to download file from APIs in priority order"""
        endpoints = [e for e in self.endpoints if e["enabled"]]
        
        for endpoint in endpoints:
            try:
                url = endpoint["url"].format(appid=appid)
                logger.info(f"Trying {endpoint['name']}: {url}")
                
                session = await self.get_session()
                async with session.get(url, timeout=30) as response:
                    if response.status == endpoint["success_code"]:
                        content = await response.read()
                        if content:
                            filename = f"{appid}_{self.get_game_name(appid).replace(':', '').replace(' ', '_')}.zip"
                            return filename, content
                    elif response.status == endpoint["unavailable_code"]:
                        logger.info(f"File not found on {endpoint['name']}")
                        continue
                    else:
                        logger.warning(f"Unexpected status {response.status} from {endpoint['name']}")
            except Exception as e:
                logger.error(f"Error with {endpoint['name']}: {str(e)}")
                continue
        
        return None, None
    
    async def get_game_logo(self, appid):
        """Get game logo from Steam API"""
        try:
            url = f"https://cdn.cloudflare.steamstatic.com/steam/apps/{appid}/header.jpg"
            session = await self.get_session()
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    return await response.read()
        except:
            pass
        return None

@bot.event
async def on_ready():
    logger.info(f'Bot is ready as {bot.user}')
    try:
        synced = await bot.tree.sync()
        logger.info(f"Synced {len(synced)} command(s)")
    except Exception as e:
        logger.error(f"Failed to sync commands: {e}")

@bot.tree.command(name="download", description="Download game files by App ID")
@app_commands.describe(
    appid="Steam App ID (e.g., 730 for CS:GO)",
    show_logo="Whether to show game logo (default: True)"
)
async def download_command(interaction: discord.Interaction, appid: str, show_logo: bool = True):
    """Download game files using Steam App ID"""
    await interaction.response.defer()
    
    downloader = SteamFileDownloader(API_CONFIG)
    
    # Get game name
    game_name = downloader.get_game_name(appid)
    
    # Create initial embed
    embed = discord.Embed(
        title=f"📥 Downloading: {game_name}",
        description=f"AppID: `{appid}`\nSearching for files...",
        color=discord.Color.blue()
    )
    await interaction.followup.send(embed=embed)
    
    # Get game logo if requested
    logo_data = None
    if show_logo:
        logo_data = await downloader.get_game_logo(appid)
    
    # Try to download file
    embed.color = discord.Color.yellow()
    embed.description = "🔍 Searching through available sources..."
    await interaction.edit_original_response(embed=embed)
    
    filename, file_content = await downloader.download_file(appid)
    
    if file_content:
        # Success - send file
        embed.color = discord.Color.green()
        embed.title = f"✅ Download Complete: {game_name}"
        embed.description = f"Successfully downloaded {game_name}!\nFile size: {len(file_content):,} bytes"
        
        # Add logo to embed if available
        if logo_data:
            embed.set_thumbnail(url="attachment://logo.jpg")
            logo_file = discord.File(io.BytesIO(logo_data), filename="logo.jpg")
        else:
            logo_file = None
        
        # Create file object
        file_obj = discord.File(io.BytesIO(file_content), filename=filename)
        
        # Send files and embed
        files_to_send = [file_obj]
        if logo_file:
            files_to_send.append(logo_file)
        
        await interaction.edit_original_response(
            embed=embed,
            attachments=files_to_send
        )
    else:
        # Failure
        embed.color = discord.Color.red()
        embed.title = f"❌ Download Failed: {game_name}"
        embed.description = f"Could not find files for {game_name} (AppID: {appid})\n\nAvailable games:\n" + "\n".join([f"• `{app}`: {name}" for app, name in API_CONFIG["game_names"].items()])
        
        await interaction.edit_original_response(embed=embed)
    
    await downloader.close_session()

@bot.tree.command(name="list_games", description="List all available games")
async def list_games_command(interaction: discord.Interaction):
    """List all available games in the database"""
    embed = discord.Embed(
        title="🎮 Available Games",
        description="Here are all the games you can download:",
        color=discord.Color.purple()
    )
    
    for appid, name in API_CONFIG["game_names"].items():
        embed.add_field(
            name=f"AppID: {appid}",
            value=name,
            inline=False
        )
    
    embed.set_footer(text="Use /download [appid] to download game files")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="api_status", description="Check status of all APIs")
async def api_status_command(interaction: discord.Interaction):
    """Check the status of all configured APIs"""
    await interaction.response.defer()
    
    downloader = SteamFileDownloader(API_CONFIG)
    embed = discord.Embed(
        title="🔧 API Status",
        description="Checking API endpoints...",
        color=discord.Color.blue()
    )
    
    results = []
    for endpoint in downloader.endpoints:
        if not endpoint["enabled"]:
            results.append(f"❌ **{endpoint['name']}**: Disabled")
            continue
            
        try:
            # Test with a known working appid
            test_url = endpoint["url"].format(appid="730")
            session = await downloader.get_session()
            async with session.head(test_url, timeout=5) as response:
                if response.status in [200, 404]:  # Both are expected responses
                    results.append(f"✅ **{endpoint['name']}**: Online (Priority: {endpoint['priority']})")
                else:
                    results.append(f"⚠️ **{endpoint['name']}**: Unexpected status {response.status}")
        except Exception as e:
            results.append(f"❌ **{endpoint['name']}**: Offline - {str(e)}")
    
    embed.description = "\n".join(results)
    embed.color = discord.Color.green() if all("✅" in r or "⚠️" in r for r in results) else discord.Color.orange()
    
    await downloader.close_session()
    await interaction.followup.send(embed=embed)

@bot.command(name="help_bot")
async def help_command(ctx):
    """Show help information"""
    embed = discord.Embed(
        title="🤖 Steam File Downloader Bot Help",
        description="A bot to download game files using Steam App IDs",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="Slash Commands",
        value="""`/download [appid] [show_logo]` - Download game files
`/list_games` - List all available games
`/api_status` - Check API endpoint status""",
        inline=False
    )
    
    embed.add_field(
        name="Example",
        value="`/download 730` - Downloads CS:GO files",
        inline=False
    )
    
    embed.add_field(
        name="Available Games",
        value="\n".join([f"• `{app}`: {name}" for app, name in API_CONFIG["game_names"].items()]),
        inline=False
    )
    
    embed.set_footer(text="Bot created with Steam DB API integration")
    await ctx.send(embed=embed)

# Error handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Command not found. Use `/download`, `/list_games`, or `/api_status`")
    else:
        logger.error(f"Command error: {error}")
        await ctx.send(f"An error occurred: {str(error)}")

# Run the bot
if __name__ == "__main__":
    bot.run(TOKEN)