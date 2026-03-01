import discord
from discord.ext import commands
import os
import asyncio
import random
from datetime import timedelta

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="+", intents=intents)

say_task = None


# =========================
#        MODERATION
# =========================

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="Aucune raison"):
    await member.kick(reason=reason)
    await ctx.send(f"{member} a été kick. Raison: {reason}")


@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="Aucune raison"):
    await member.ban(reason=reason)
    await ctx.send(f"{member} a été ban. Raison: {reason}")


@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, user_id: int):
    user = await bot.fetch_user(user_id)
    await ctx.guild.unban(user)
    await ctx.send(f"{user} a été unban.")


@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"{amount} messages supprimés.", delete_after=5)


@bot.command()
@commands.has_permissions(manage_channels=True)
async def lock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send("Salon verrouillé.")


@bot.command()
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.send("Salon déverrouillé.")


@bot.command()
@commands.has_permissions(moderate_members=True)
async def mute(ctx, member: discord.Member, minutes: int, *, reason="Aucune raison"):
    duration = timedelta(minutes=minutes)
    await member.timeout(duration, reason=reason)
    await ctx.send(f"{member.mention} est mute pour {minutes} minutes.")


# =========================
#        SAY RANDOM
# =========================

@bot.command()
@commands.has_permissions(administrator=True)
async def say(ctx, *, message):
    global say_task

    if say_task is not None:
        await ctx.send("Un say est déjà actif.")
        return

    async def random_say_loop():
        while True:
            wait_time = random.randint(21600, 86400)  # 6h à 24h
            await asyncio.sleep(wait_time)
            await ctx.send(message)

    say_task = bot.loop.create_task(random_say_loop())
    await ctx.send("Say random activé (min 6h).")


@bot.command()
@commands.has_permissions(administrator=True)
async def saystop(ctx):
    global say_task

    if say_task is None:
        await ctx.send("Aucun say actif.")
        return

    say_task.cancel()
    say_task = None
    await ctx.send("Say arrêté.")


# =========================
#        KILLBOT
# =========================

@bot.command()
@commands.has_permissions(administrator=True)
async def killbot(ctx):
    await ctx.send("Extinction du bot...")
    await bot.close()


# =========================
#        LANCEMENT
# =========================

if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("TOKEN MANQUANT")
    else:
        bot.run(token)