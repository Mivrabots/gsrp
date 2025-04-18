import discord
from discord.ext import commands
import sqlite3
import os
from keep_alive import keep_alive  # Import the keep-alive function

# Set up the bot
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

# Connect to SQLite database
conn = sqlite3.connect("applications.db")
cursor = conn.cursor()

# Create the applications table with an application type
cursor.execute('''CREATE TABLE IF NOT EXISTS applications (
                  id INTEGER PRIMARY KEY,
                  user_id INTEGER,
                  application_type TEXT,
                  status TEXT,
                  answers TEXT)''')
conn.commit()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    # Sync commands when the bot is ready
    await bot.tree.sync()

# Slash command to accept an application (Admin-only)
@bot.tree.command(name="accept", description="Accept an application for a specific type")
async def accept(interaction: discord.Interaction, user: discord.Member, app_type: str):
    """Accept an application for a specific type"""
    if not any(role.name == "Staff Reviewer" for role in interaction.user.roles):
        await interaction.response.send_message("You don't have permission to accept applications.", ephemeral=True)
        return

    if app_type not in ["staff", "game_dev", "dev_app"]:
        await interaction.response.send_message("Invalid application type. Use 'staff', 'game_dev', or 'dev_app'.", ephemeral=True)
        return

    cursor.execute("UPDATE applications SET status = 'Accepted' WHERE user_id = ? AND application_type = ?",
                   (user.id, app_type))
    conn.commit()

    # Send a congratulatory DM to the user
    embed = discord.Embed(
        title="✅ Congratulations!",
        description=f"Your {app_type.capitalize()} application has been accepted.\n\n"
                    "A member of the management team will reach out to you with onboarding information.\n\n"
                    "Thank you for your interest in supporting Georgia State Roleplay!",
        color=discord.Color.green()
    )
    await user.send(embed=embed)
    
    await interaction.response.send_message(f"{user.mention}'s {app_type} application has been accepted!")

# Slash command to deny an application (Admin-only)
@bot.tree.command(name="deny", description="Deny an application for a specific type")
async def deny(interaction: discord.Interaction, user: discord.Member, app_type: str):
    """Deny an application for a specific type"""
    if not any(role.name == "Staff Reviewer" for role in interaction.user.roles):
        await interaction.response.send_message("You don't have permission to deny applications.", ephemeral=True)
        return

    if app_type not in ["staff", "game_dev", "dev_app"]:
        await interaction.response.send_message("Invalid application type. Use 'staff', 'game_dev', or 'dev_app'.", ephemeral=True)
        return

    cursor.execute("UPDATE applications SET status = 'Denied' WHERE user_id = ? AND application_type = ?",
                   (user.id, app_type))
    conn.commit()

    # Send a denial DM to the user
    embed = discord.Embed(
        title="❌ Your application has been denied",
        description=f"Unfortunately, your {app_type.capitalize()} application has been denied.\n\n"
                    "Thank you for your interest in Georgia State Roleplay. Please feel free to apply again in the future.",
        color=discord.Color.red()
    )
    await user.send(embed=embed)

    await interaction.response.send_message(f"{user.mention}'s {app_type} application has been denied!")

# Run the keep-alive function
keep_alive()

# Get the bot token from environment variables
bot_token = os.getenv("TOKEN")

# Run the bot
if bot_token:
    bot.run(bot_token)
else:
    print("Error: Bot token not found. Please set the DISCORD_BOT_TOKEN environment variable.")
