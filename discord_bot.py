import os
from discord import app_commands, Intents
from discord.ext import commands
from dotenv import load_dotenv
from ChatDev.chatdev.chat_chain import ChatChain
from ChatDev.camel.typing import ModelType

# Load environment variables
load_dotenv()

# Bot setup
intents = Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Register an instance of the Tree with the bot
tree = app_commands.CommandTree(bot)

# Helper function to get configuration paths
def get_config(company):
    """
    return configuration json files for ChatChain
    user can customize only parts of configuration json files, other files will be left for default
    Args:
        company: customized configuration name under CompanyConfig/

    Returns:
        path to three configuration jsons: [config_path, config_phase_path, config_role_path]
    """
    config_dir = os.path.join("CompanyConfig", company)
    default_config_dir = os.path.join("CompanyConfig", "Default")

    config_files = [
        "ChatChainConfig.json",
        "PhaseConfig.json",
        "RoleConfig.json"
    ]

    config_paths = []

    for config_file in config_files:
        company_config_path = os.path.join(config_dir, config_file)
        default_config_path = os.path.join(default_config_dir, config_file)

        if os.path.exists(company_config_path):
            config_paths.append(company_config_path)
        else:
            config_paths.append(default_config_path)

    return tuple(config_paths)

# Slash command for ChatDev functionality with environment variables
@tree.command(name="chatdev", description="Run your ChatDev function with custom environment variables")
@app_commands.describe(
    config="Name of config, which is used to load configuration under CompanyConfig/",
    org="Name of organization, your software will be generated in WareHouse/name_org_timestamp",
    task="Prompt of software",
    name="Name of software, your software will be generated in WareHouse/name_org_timestamp",
    model="GPT Model, choose from {'GPT_3_5_TURBO','GPT_4','GPT_4_32K', 'GPT_4_TURBO'}",
    path="Your file directory, ChatDev will build upon your software in the Incremental mode",
    env_vars="Environment variables to set for the initial run, in the format KEY=VALUE separated by commas",
    run_args="Arguments to pass to the software upon initial run, separated by spaces"
)
async def chat_dev_function(interaction: discord.Interaction, config: str, org: str, task: str, name: str, model: str, path: str, env_vars: str = None, run_args: str = None):
    # Parse environment variables
    env_dict = {}
    if env_vars:
        for var in env_vars.split(','):
            key, value = var.split('=')
            env_dict[key.strip()] = value.strip()

    # Parse run arguments
    run_arguments = run_args.split(' ') if run_args else []

    # Get configuration paths
    config_path, config_phase_path, config_role_path = get_config(config)

    # Map model names to ModelType
    args2type = {'GPT_3_5_TURBO': ModelType.GPT_3_5_TURBO,
                 'GPT_4': ModelType.GPT_4,
                 'GPT_4_32K': ModelType.GPT_4_32k,
                 'GPT_4_TURBO': ModelType.GPT_4_TURBO,
                 'GPT_4_TURBO_V': ModelType.GPT_4_TURBO_V
                 }

    # Create ChatChain instance
    chat_chain = ChatChain(config_path=config_path,
                           config_phase_path=config_phase_path,
                           config_role_path=config_role_path,
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
    await interaction.response.send_message(f"ChatDev execution completed with environment variables: {env_vars} and run arguments: {run_args}")

    # Send the output messages from the chat chain execution
    for message in output_messages:
        await interaction.followup.send(message)

# Sync the command tree to ensure the commands are registered
bot.tree.sync()

# Run the bot
bot.run(os.getenv('DISCORD_TOKEN'))

