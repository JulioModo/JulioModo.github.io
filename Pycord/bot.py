import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions
from datetime import datetime, timedelta, timezone
import os
import json
from asyncio import create_task, sleep

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)


# ============================================================
#                     SYSTEME DE LOGS
# ============================================================

async def log_action(guild, action_type, member, moderator, reason=None, extra_info=None):
    log_channel = discord.utils.get(guild.text_channels, name="logs-modération")
    if log_channel is None:
        return

    desc = f"👤 Membre : {member.mention if isinstance(member, discord.Member) else member}\n"
    desc += f"👮 Par : {moderator.mention}\n"

    if reason:
        desc += f"📝 Raison : {reason}\n"
    if extra_info:
        desc += f"ℹ️ Info : {extra_info}\n"

    embed = discord.Embed(
        title=f"🔔 {action_type}",
        description=desc,
        color=0xff0000
    )
    embed.timestamp = discord.utils.utcnow()

    await log_channel.send(embed=embed)


# ============================================================
#                    COMMANDES DE MODÉRATION
# ============================================================

# !kick <membre>
@bot.command()
@has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="Aucune raison donnée"):
    if not ctx.guild.me.guild_permissions.kick_members:
        return await ctx.send("❌ Je n'ai pas la permission de kick !")

    if member.top_role >= ctx.guild.me.top_role:
        return await ctx.send("❌ Je peux pas kick ce mec, il est trop haut placé pour moi.")

    if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
        return await ctx.send("❌ Il est au-dessus de toi, tu peux pas.")

    try:
        await member.send(f"🚪 Kick de **{ctx.guild.name}**.\nRaison : {reason}")
    except:
        pass

    await member.kick(reason=reason)
    await ctx.send(f"👢 {member.mention} a été kick. (`{reason}`)")
    await log_action(ctx.guild, "KICK", member, ctx.author, reason)

# !ban <membre>
@bot.command()
@has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="Aucune raison donnée"):
    try:
        await member.send(f"🔨 Bannissement de **{ctx.guild.name}** : {reason}")
    except:
        pass

    await member.ban(reason=reason)
    await ctx.send(f"🔨 {member.mention} banni. (`{reason}`)")
    await log_action(ctx.guild, "BAN", member, ctx.author, reason)

# !warn <membre> <motif>
@bot.command()
@has_permissions(manage_messages=True)
async def warn(ctx, member: discord.Member, *, reason="Aucune raison donnée"):
    try:
        await member.send(f"⚠️ Avertissement sur **{ctx.guild.name}** : {reason}")
    except:
        pass

    await ctx.send(f"⚠️ {member.mention} averti (`{reason}`).")
    await log_action(ctx.guild, "WARN", member, ctx.author, reason)


@bot.command()
@has_permissions(ban_members=True)
async def deban(ctx, user_id: int):
    user = await bot.fetch_user(user_id)
    try:
        await ctx.guild.unban(user)
        await ctx.send(f"✅ {user} débanni.")

        try:
            await user.send(f"Tu as été débanni de **{ctx.guild.name}**.")
        except:
            pass

        await log_action(ctx.guild, "DEBAN", user, ctx.author)

    except discord.NotFound:
        await ctx.send("❌ Cet utilisateur n'est pas banni.")
    except Exception as e:
        await ctx.send(f"❌ Erreur : {e}")

# !clear <time> <unité>
@bot.command()
@has_permissions(manage_messages=True)
async def clear(ctx, amount: int, unit: str):
    try:
        now = datetime.now(timezone.utc)

        if unit.lower() == "s":
            limit = now - timedelta(seconds=amount)
        elif unit.lower() == "m":
            limit = now - timedelta(minutes=amount)
        elif unit.lower() == "h":
            limit = now - timedelta(hours=amount)
        else:
            return await ctx.send("⛔ Unité invalide (s/m/h).")

        deleted = []
        async for msg in ctx.channel.history(limit=1000):
            if msg.created_at >= limit:
                deleted.append(msg)

        if not deleted:
            return await ctx.send("⛔ Aucun message trouvé.")

        await ctx.channel.delete_messages(deleted)
        await ctx.send(
            f"🧹 {len(deleted)} messages supprimés (sur {amount}{unit})",
            delete_after=5
        )
        await log_action(ctx.guild, "CLEAR", ctx.author, ctx.author,
                         extra_info=f"{len(deleted)} messages supprimés ({amount}{unit})")

    except Exception as e:
        await ctx.send(f"❌ Erreur : {e}")

# !lock
@bot.command()
@has_permissions(manage_channels=True)
async def lock(ctx):
    overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
    overwrite.send_messages = False
    await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)

    await ctx.send("🔒 Salon verrouillé.")
    await log_action(ctx.guild, "LOCK", ctx.author, ctx.author,
                     extra_info=f"Salon {ctx.channel.mention} verrouillé")

# !unlock
@bot.command()
@has_permissions(manage_channels=True)
async def unlock(ctx):
    overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
    overwrite.send_messages = True
    await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)

    await ctx.send("🔓 Salon déverrouillé.")
    await log_action(ctx.guild, "UNLOCK", ctx.author, ctx.author,
                     extra_info=f"Salon {ctx.channel.mention} déverrouillé")


# ============================================================
#                      AUTO-ROLE
# ============================================================

AUTO_ROLES = {}

@bot.event
async def on_member_join(member):
    if member.guild.id in AUTO_ROLES:
        role_id = AUTO_ROLES[member.guild.id]
        role = member.guild.get_role(role_id)
        if role:
            try:
                await member.add_roles(role)
                await log_action(member.guild, "AUTO-ROLE", member, bot.user,
                                 extra_info=f"Rôle {role.name} assigné")
            except:
                pass


@bot.command()
@has_permissions(administrator=True)
async def setup_autorole(ctx, role_id: int):
    role = ctx.guild.get_role(role_id)
    if not role:
        return await ctx.send("❌ Rôle introuvable.")

    AUTO_ROLES[ctx.guild.id] = role_id
    await ctx.send(f"✅ Auto-role configuré : {role.mention}")


# ============================================================
#                     SETUP DES LOGS
# ============================================================

@bot.command()
@has_permissions(administrator=True)
async def setup_logs(ctx, role_id: int):
    role = ctx.guild.get_role(role_id)
    if not role:
        return await ctx.send("❌ Rôle introuvable.")

    existing = discord.utils.get(ctx.guild.text_channels, name="logs-modération")
    if existing:
        return await ctx.send("ℹ️ Le salon existe déjà.")

    overwrites = {
        ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
        role: discord.PermissionOverwrite(read_messages=True),
        ctx.guild.me: discord.PermissionOverwrite(read_messages=True)
    }

    channel = await ctx.guild.create_text_channel("logs-modération", overwrites=overwrites)
    await ctx.send(f"✅ Salon de logs créé : {channel.mention}")


# ============================================================
#                    AUTO-POST & KILLSWITCH
# ============================================================

AUTOPOST_TASK = None
AUTOPOST_DATA = {}
KILLSWITCH_ACTIVE = False


async def autopost_loop(guild_id):
    global AUTOPOST_TASK

    data = AUTOPOST_DATA[guild_id]
    channel = bot.get_channel(data["channel"])
    interval = data["interval"]
    message = data["message"]

    if not channel:
        print(f"[AUTOPOST] Channel introuvable pour {guild_id}")
        AUTOPOST_TASK = None
        return

    while True:
        if KILLSWITCH_ACTIVE:
            print("[KILLSWITCH] AutoPost annulé.")
            return

        try:
            await channel.send(message)
        except Exception as e:
            print(f"[AUTOPOST ERROR] {e}")

        await sleep(interval * 60)


@bot.command()
@has_permissions(administrator=True)
async def autopost(ctx, action=None, channel_id: int = None, interval: int = None, *, message=None):
    global AUTOPOST_TASK

    if action == "set":
        if not channel_id or not interval or not message:
            return await ctx.send("❌ Syntaxe : `!autopost set <channel_id> <interval_min> <message>`")

        AUTOPOST_DATA[ctx.guild.id] = {
            "channel": channel_id,
            "interval": interval,
            "message": message
        }

        if AUTOPOST_TASK:
            AUTOPOST_TASK.cancel()

        AUTOPOST_TASK = create_task(autopost_loop(ctx.guild.id))

        await ctx.send(f"✅ AutoPost configuré : toutes les **{interval} min** → <#{channel_id}>")

    elif action == "stop":
        if AUTOPOST_TASK:
            AUTOPOST_TASK.cancel()
            AUTOPOST_TASK = None
            AUTOPOST_DATA.pop(ctx.guild.id, None)
            await ctx.send("🛑 AutoPost arrêté.")
        else:
            await ctx.send("ℹ️ Aucun AutoPost actif.")

    else:
        await ctx.send("❌ Utilise `!autopost set` ou `!autopost stop`")


@bot.command()
@has_permissions(administrator=True)
async def killbot(ctx):
    global KILLSWITCH_ACTIVE
    KILLSWITCH_ACTIVE = True

    await ctx.send("🧨 **KILLSWITCH ACTIVÉ — arrêt complet.**")
    await bot.close()


# ============================================================
#                      GESTION DES ERREURS
# ============================================================

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, MissingPermissions):
        return await ctx.send("🙂‍↔️ Perms insuffisantes.")
    if isinstance(error, commands.MissingRequiredArgument):
        return await ctx.send("❗ Argument manquant.")
    if isinstance(error, commands.MemberNotFound):
        return await ctx.send("🔍 Membre introuvable.")
    raise error


# ============================================================
#                        LANCEMENT
# ============================================================

if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("❌ TOKEN MANQUANT DANS LES VARIABLES D'ENVIRONNEMENT.")
    else:
        bot.run(token)
