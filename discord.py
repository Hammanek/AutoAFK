import requests
from textwrap import dedent
from AutoAFK import config

class Discord(object):

    def __init__(self, channel_id: str, token: str):
        self.discord_api = f"https://discord.com/api/webhooks/{channel_id}/{token}"

    def send(self, message: str) -> None:
        response = requests.post(
            url=self.discord_api,
            json={ 
                "content": dedent(message) 
            }
        )

        return {
            "status_code": response.status_code,
            "response": response.text
        }

if config.has_section('DISCORD') and config.getboolean('DISCORD', 'enable'):

    # Initialize the Discord object
    discord = Discord(channel_id=config.get("DISCORD","channel_id"), token=config.get("DISCORD","token"))

    # Custom print function that duplicates output to console and Discord
    def print_and_send_to_discord(*args, **kwargs):
        # Convert all arguments to strings and join them
        message = ' '.join(map(str, args))

        # Print to console
        built_in_print(*args, **kwargs)

        # Check if message is empty
        if message.strip():
            # List of prefixes to check
            prefixes = ['ERR', 'WAR', 'GRE', 'BLU', 'PUR']
            
            # Check if the message starts with any of the prefixes
            if any(message.startswith(prefix) for prefix in prefixes):
                # Start from the fourth character
                processed_message = message[3:]
                # Send processed message to Discord
                response = discord.send(processed_message)
            else:
                # Send the original message to Discord
                response = discord.send(message)

    # Save the built-in print function to avoid infinite recursion
    built_in_print = print

    # Replace the built-in print function with our custom function
    print = print_and_send_to_discord