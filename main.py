from opencc import OpenCC
import threading
import logging
import aiohttp

cc = OpenCC('s2twp')

import discord

bot = discord.Bot()

@bot.event
async def on_ready():
    logging.info(f'Logged in as {bot.user.name} ({bot.user.id})')

@bot.command(name="佳句", description="每日一句佳句，讓你更有文學氣息")
async def get_quote(ctx):
    # http://v3.wufazhuce.com:8000/api/channel/one/0/0 的API
    async with aiohttp.ClientSession() as session:
        async with session.get('http://v3.wufazhuce.com:8000/api/channel/one/0/0') as resp:
            data = await resp.json()
            quote = data['data']['content_list'][0]['forward']
            quote = cc.convert(quote)
            await ctx.send(quote)

@bot.command(name="伺服器資訊", description="取得這個 Discord 伺服器的資訊")
async def send_server_info(ctx):
    guild = ctx.guild
    embed = discord.Embed(title=guild.name, description="", color=0x00ff00)
    embed.add_field(name="伺服器名稱", value=guild.name, inline=True)
    embed.add_field(name="伺服器人數", value=guild.member_count, inline=True)
    embed.add_field(name="伺服器擁有者", value=guild.owner, inline=True)
    embed.add_field(name="伺服器位置", value=guild.region, inline=True)
    embed.add_field(name="伺服器ID", value=guild.id, inline=True)
    embed.set_thumbnail(url=guild.icon_url)
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label='🖼 看看圖示', url=guild.icon_url))
    await ctx.send(embed=embed, view=view)

@bot.command(name="頻道資訊", description="取得這個頻道的資訊")
async def get_channel_info(ctx):
    channel = ctx.channel
    embed = discord.Embed(title=channel.name, description="", color=0x00ff00)
    embed.add_field(name="頻道名稱", value=channel.name, inline=True)
    embed.add_field(name="頻道類型", value=channel.type, inline=True)
    embed.add_field(name="頻道ID", value=channel.id, inline=True)
    await ctx.send(embed=embed)

@bot.command(name="使用者資訊", description="取得這個使用者的資訊")
async def get_user_info(ctx, user: discord.User):
    if user is None:
        user = ctx.author
    embed = discord.Embed(title=user.name, description="", color=0x00ff00)
    embed.add_field(name="使用者名稱", value=user.name, inline=True)
    embed.add_field(name="使用者ID", value=user.id, inline=True)
    roles = [role.name for role in user.roles if role.name != "@everyone"]
    embed.add_field(name="身分組", value=roles, inline=True)
    embed.add_field(name="使用者狀態", value=user.status, inline=True)
    embed.add_field(name="使用者創建時間", value=user.created_at, inline=True)
    embed.set_thumbnail(url=user.avatar_url)
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label='🖼 看看頭像', url=user.avatar_url))
    await ctx.send(embed=embed, view=view)

@bot.command(name="清除", description="清除一定數量訊息，可指定要清除的數量與發送者")
async def clear(ctx, amount: int, user: discord.User = None):
    # 檢查使用者是否有管理訊息的權限
    if not ctx.author.permissions_in(ctx.channel).manage_messages:
        embed = discord.Embed(title="權限不足", description="你沒有足夠的權限來清除訊息", color=0xff0000)
        await ctx.send(embed=embed, ephermeral=True)
        return
    
    if not ctx.guild.me.permissions_in(ctx.channel).manage_messages:
        embed = discord.Embed(title="權限不足", description="我沒有足夠的權限來清除訊息", color=0xff0000)
        await ctx.send(embed=embed, ephermeral=True)
        return

    # purge: 清除訊息
    if user:
        await ctx.channel.purge(limit=amount, check=lambda m: m.author == user)
        embed = discord.Embed(title="成功清除訊息", description=f"清除了 {amount} 則 {user.name} 的訊息", color=0x00ff00)
        await ctx.send(embed=embed, ephermeral=True)
        return
    else:
        await ctx.channel.purge(limit=amount)
        embed = discord.Embed(title="成功清除訊息", description=f"清除了 {amount} 則訊息", color=0x00ff00)
        await ctx.send(embed=embed, ephermeral=True)
        return

@bot.command(name="說", description="讓機器人說話")
async def say(ctx, *, message):
    await ctx.send(message)

@bot.command(name="WHOIS 資訊", description="取得指定網站的 WHOIS 資訊")
async def whois(ctx, domain):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://api.hackertarget.com/whois/?q={domain}') as resp:
            data = await resp.text()
            await ctx.send(f'```{data}```')