from discord_slash import SlashCommand
from discord_slash.utils.manage_commands import create_option
from discord.ext import commands
import os
from dotenv import load_dotenv
from chatdev.chat_chain import ChatChain
from camel.typing import ModelType

# Load environment variables
load_dotenv()

# Bot setup
bot = commands.Bot(command_prefix="!", intents=discord.Intents.default())
slash = SlashCommand(bot, sync_commands=True)

# Slash command for ChatDev functionality with environment variables
@slash.slash(
    name="ChatDevFunction",
    description="Run your ChatDev function with custom environment variables",
    options=[
        create_option(
            name="config",
            description="Name of config, which is used to load configuration under CompanyConfig/",
            option_type=3,  # Type 3 is string
            required=True
        ),
        create_option(
            name="org",
            description="Name of organization, your software will be generated in WareHouse/name_org_timestamp",
            option_type=3,  # Type 3 is string
            required=True
        ),
        create_option(
            name="task",
            description="Prompt of software",
            option_type=3,  # Type 3 is string
            required=True
        ),
        create_option(
            name="name",
            description="Name of software, your software will be generated in WareHouse/name_org_timestamp",
            option_type=3,  # Type 3 is string
            required=True
        ),
        create_option(
            name="model",
            description="GPT Model, choose from {'GPT_3_5_TURBO','GPT_4','GPT_4_32K', 'GPT_4_TURBO'}",
            option_type=3,  # Type 3 is string
            required=True
        ),
        create_option(
            name="path",
            description="Your file directory, ChatDev will build upon your software in the Incremental mode",
            option_type=3,  # Type 3 is string
            required=True
        ),
        create_option(
            name="env_vars",
            description="Environment variables to set for the initial run, in the format KEY=VALUE separated by commas",
            option_type=3,  # Type 3 is string
            required=False
        ),
        create_option(
            name="run_args",
            description="Arguments to pass to the software upon initial run, separated by spaces",
            option_type=3,  # Type 3 is string
            required=False
        ),
        # Add more options as needed for your inputs
    ]
)
async def _chat_dev_function(ctx, config, org, task, name, model, path, env_vars=None, run_args=None):
    # Parse environment variables
    env_dict = {}
    if env_vars:
        for var in env_vars.split(','):
            key, value = var.split('=')
            env_dict[key.strip()] = value.strip()

    # Parse run arguments
    run_arguments = run_args.split(' ') if run_args else []

    # Call your ChatDev functionality with the provided inputs
    args2type = {'GPT_3_5_TURBO': ModelType.GPT_3_5_TURBO,
                 'GPT_4': ModelType.GPT_4,
                 'GPT_4_32K': ModelType.GPT_4_32k,
                 'GPT_4_TURBO': ModelType.GPT_4_TURBO,
                 'GPT_4_TURBO_V': ModelType.GPT_4_TURBO_V
                 }
    chat_chain = ChatChain(config_path=config,
                           config_phase_path=config,
                           config_role_path=config,
                           task_prompt=task,
                           project_name=name,
                           org_name=org,
                           model_type=args2type[model],
                           code_path=path,
                           env_vars=env_dict,
                           run_args=run_arguments)
    # Execute the chat chain and capture the output
    output_messages = chat_chain.execute_chain_capture_output()
    # Send the result back to the Discord channel
    await ctx.send(f"ChatDev execution completed with environment variables: {env_vars} and run arguments: {run_args}")
    # Send the output messages from the chat chain execution
    for message in output_messages:
        await ctx.send(message)

# Run the bot
bot.run(os.getenv('DISCORD_TOKEN'))
