import os
import discord
from dotenv import load_dotenv
from ChatDev.chatdev.chat_chain import ChatChain
from ChatDev.camel.typing import ModelType

# Load environment variables
load_dotenv()

# Bot setup
intents = discord.Intents.default()
bot = discord.Bot(command_prefix='!', intents=intents)

# Slash command for ChatDev functionality with environment variables
@discord.slash_command(name="chatdev", description="Run your ChatDev function with custom environment variables")
async def chatdev(ctx: discord.ApplicationContext, org: str, task: str, name: str, model: str, path: str, env_vars: str = None, run_args: str = None):
    # Parse environment variables
    env_dict = {}
    if env_vars:
        for var in env_vars.split(','):
            key, value = var.split('=')
            env_dict[key.strip()] = value.strip()

    # Parse run arguments
    run_arguments = run_args.split(' ') if run_args else []

    # Map model names to ModelType
    args2type = {
        'GPT_3_5_TURBO': ModelType.GPT_3_5_TURBO,
        'GPT_4': ModelType.GPT_4,
        'GPT_4_32K': ModelType.GPT_4_32k,
        'GPT_4_TURBO': ModelType.GPT_4_TURBO,
        'GPT_4_TURBO_V': ModelType.GPT_4_TURBO_V
    }

    # Create ChatChain instance
    chat_chain = ChatChain(
        task_prompt=task,
        project_name=name,
        org_name=org,
        model_type=args2type[model],
        code_path=path,
        env_vars=env_dict,
        run_args=run_arguments
    )

    # Execute the chat chain and capture the output
    output_messages = chat_chain.execute_chain_capture_output()

    # Send the result back to the Discord channel
    await ctx.respond(f"ChatDev execution completed with environment variables: {env_vars} and run arguments: {run_args}")

    # Send the output messages from the chat chain execution
    for message in output_messages:
        await ctx.send_followup(message)

# Event listener for when the bot has connected to Discord
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}!")
    # Sync the application commands with Discord
    # await bot.sync_commands()

# Run the bot
bot.run(os.getenv('DISCORD_TOKEN'))

