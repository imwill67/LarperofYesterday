import discord
from discord import app_commands
import os
import json

from dotenv import load_dotenv


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

GUILD_ID = 1537916356559765545

SETTINGS_FILE = "settings.json"


# ============================================================
# DISCORD SETUP
# ============================================================

intents = discord.Intents.default()

client = discord.Client(
    intents=intents
)

tree = app_commands.CommandTree(
    client
)

GUILD = discord.Object(
    id=GUILD_ID
)


# ============================================================
# SETTINGS
# ============================================================

def load_settings():

    if not os.path.exists(SETTINGS_FILE):
        return {}

    with open(
        SETTINGS_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def save_settings(settings):

    with open(
        SETTINGS_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            settings,
            file,
            indent=4
        )


settings = load_settings()


# ============================================================
# ADMIN CHECK
# ============================================================

def administrator_only():

    async def predicate(
        interaction: discord.Interaction
    ):

        if interaction.guild is None:
            return False

        return interaction.user.guild_permissions.administrator

    return app_commands.check(predicate)


# ============================================================
# BOT READY
# ============================================================

@client.event
async def on_ready():

    await tree.sync(
        guild=GUILD
    )

    print(
        f"Logged in as {client.user}!"
    )

    print(
        "Larper of Yesterday is online."
    )

    print(
        "Slash commands synced."
    )


# ============================================================
# /ping
# ============================================================

@tree.command(
    name="ping",
    description="Check if Larper of Yesterday is working.",
    guild=GUILD
)
@administrator_only()
async def ping(
    interaction: discord.Interaction
):

    await interaction.response.send_message(
        "Pong! 🏓",
        ephemeral=True
    )


# ============================================================
# /setrole
# ============================================================

@tree.command(
    name="setrole",
    description="Set the role used when someone is ripped.",
    guild=GUILD
)
@app_commands.describe(
    role="The role that will be given to dead users."
)
@administrator_only()
async def setrole(
    interaction: discord.Interaction,
    role: discord.Role
):

    bot_member = interaction.guild.me

    if bot_member is None:

        await interaction.response.send_message(
            "❌ I couldn't determine my role in this server.",
            ephemeral=True
        )

        return

    if role >= bot_member.top_role:

        await interaction.response.send_message(
            "❌ I can't use that role because it's higher than or equal to my highest role.",
            ephemeral=True
        )

        return

    settings[str(interaction.guild.id)] = {
        "death_role_id": role.id
    }

    save_settings(settings)

    await interaction.response.send_message(
        f"✅ Death role set to {role.mention}.",
        ephemeral=True
    )


# ============================================================
# /rip
# ============================================================

@tree.command(
    name="rip",
    description="Rip a user in half. ☠️",
    guild=GUILD
)
@app_commands.describe(
    user="The user you want to rip."
)
@administrator_only()
async def rip(
    interaction: discord.Interaction,
    user: discord.Member
):

    guild_id = str(interaction.guild.id)

    # Check if a death role has been configured
    if guild_id not in settings:

        await interaction.response.send_message(
            "❌ No death role has been configured yet. Use /setrole first.",
            ephemeral=True
        )

        return

    death_role_id = settings[guild_id].get(
        "death_role_id"
    )

    if not death_role_id:

        await interaction.response.send_message(
            "❌ No death role has been configured yet. Use /setrole first.",
            ephemeral=True
        )

        return

    death_role = interaction.guild.get_role(
        death_role_id
    )

    if death_role is None:

        await interaction.response.send_message(
            "❌ The configured death role no longer exists.",
            ephemeral=True
        )

        return

    # Already dead?
    if death_role in user.roles:

        await interaction.response.send_message(
            f"❌ {user.mention} is already dead. You can't rip them again. 😭",
            ephemeral=True
        )

        return

    bot_member = interaction.guild.me

    if bot_member is None:

        await interaction.response.send_message(
            "❌ I couldn't determine my role in this server.",
            ephemeral=True
        )

        return

    # Check target's highest role against bot's highest role
    if user.top_role >= bot_member.top_role:

        await interaction.response.send_message(
            "❌ I can't rip this user because their highest role is higher than or equal to mine.",
            ephemeral=True
        )

        return

    # Check the death role itself
    if death_role >= bot_member.top_role:

        await interaction.response.send_message(
            "❌ I can't give the RIP role because it's higher than or equal to my highest role.",
            ephemeral=True
        )

        return

    try:

        await user.add_roles(
            death_role,
            reason=f"Ripped by {interaction.user}"
        )

    except discord.Forbidden:

        await interaction.response.send_message(
            "❌ I don't have permission to give the RIP role to this user.",
            ephemeral=True
        )

        return

    # Public announcement
    await interaction.response.send_message(
        f"💀 {user.mention} has been ripped in half."
    )


# ============================================================
# /revive
# ============================================================

@tree.command(
    name="revive",
    description="Bring a dead user back to life. ❤️",
    guild=GUILD
)
@app_commands.describe(
    user="The user you want to revive."
)
@administrator_only()
async def revive(
    interaction: discord.Interaction,
    user: discord.Member
):

    guild_id = str(interaction.guild.id)

    # Check if a death role has been configured
    if guild_id not in settings:

        await interaction.response.send_message(
            "❌ No death role has been configured yet. Use /setrole first.",
            ephemeral=True
        )

        return

    death_role_id = settings[guild_id].get(
        "death_role_id"
    )

    if not death_role_id:

        await interaction.response.send_message(
            "❌ No death role has been configured yet. Use /setrole first.",
            ephemeral=True
        )

        return

    death_role = interaction.guild.get_role(
        death_role_id
    )

    if death_role is None:

        await interaction.response.send_message(
            "❌ The configured death role no longer exists.",
            ephemeral=True
        )

        return

    # Already alive?
    if death_role not in user.roles:

        await interaction.response.send_message(
            f"❌ {user.mention} is already alive. What are you reviving? 😭",
            ephemeral=True
        )

        return

    bot_member = interaction.guild.me

    if bot_member is None:

        await interaction.response.send_message(
            "❌ I couldn't determine my role in this server.",
            ephemeral=True
        )

        return

    if death_role >= bot_member.top_role:

        await interaction.response.send_message(
            "❌ I can't remove the RIP role because it's higher than or equal to my highest role.",
            ephemeral=True
        )

        return

    try:

        await user.remove_roles(
            death_role,
            reason=f"Revived by {interaction.user}"
        )

    except discord.Forbidden:

        await interaction.response.send_message(
            "❌ I don't have permission to remove the RIP role from this user.",
            ephemeral=True
        )

        return

    # Public announcement
    await interaction.response.send_message(
        f"❤️ {user.mention} has been revived."
    )


# ============================================================
# /help
# ============================================================

@tree.command(
    name="help",
    description="Show the Larper of Yesterday command list.",
    guild=GUILD
)
@administrator_only()
async def help_command(
    interaction: discord.Interaction
):

    embed = discord.Embed(
        title="☠️ Larper of Yesterday",
        description="Command list",
        color=discord.Color.red()
    )

    embed.add_field(
        name="/ping",
        value="Check if the bot is working. 🏓",
        inline=False
    )

    embed.add_field(
        name="/rip @user",
        value="Rips a user in half. ☠️",
        inline=False
    )

    embed.add_field(
        name="/revive @user",
        value="Brings a dead user back to life. ❤️",
        inline=False
    )

    embed.add_field(
        name="/setrole @role",
        value="Sets the role used for dead users. 🔧",
        inline=False
    )

    embed.add_field(
        name="/help",
        value="Shows this command list. 📖",
        inline=False
    )

    await interaction.response.send_message(
        embed=embed,
        ephemeral=True
    )


# ============================================================
# GLOBAL APP COMMAND ERROR HANDLER
# ============================================================

@tree.error
async def on_app_command_error(
    interaction: discord.Interaction,
    error: app_commands.AppCommandError
):

    if isinstance(
        error,
        app_commands.CheckFailure
    ):

        message = (
            "❌ You need Administrator permissions "
            "to use Larper of Yesterday commands."
        )

        if interaction.response.is_done():

            await interaction.followup.send(
                message,
                ephemeral=True
            )

        else:

            await interaction.response.send_message(
                message,
                ephemeral=True
            )

        return

    # Print unexpected errors to console
    print(
        f"Command error: {error}"
    )

    if interaction.response.is_done():

        await interaction.followup.send(
            "❌ Something went wrong while executing that command.",
            ephemeral=True
        )

    else:

        await interaction.response.send_message(
            "❌ Something went wrong while executing that command.",
            ephemeral=True
        )


# ============================================================
# START BOT
# ============================================================

if not TOKEN:

    raise RuntimeError(
        "DISCORD_TOKEN was not found "
        "in the .env file."
    )


client.run(TOKEN)
