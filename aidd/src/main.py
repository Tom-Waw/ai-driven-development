import traceback

import ram
from prompts.chains.planning import run_planning_chain

client_request = """
Create a mini game that allows the user to create a character.
The user can change the appearance of the character and give it a name.
There are three character  types: warrior, mage, and rogue.
One can pick the character type and the character will have different stats based on the type.
Also each character type has unique weapons and armor to choose from.

The game should have a simple UI that allows the user to interact with the game.
Also the user should be able to save the character to a file and load it later or delete it.
"""


def main():
    project = run_planning_chain(client_request)
    

    print(project.model_dump_json(indent=2))


if __name__ == "__main__":
    while True:
        try:
            ram.reset()
            prompt = input("Press Enter to start the conversation... [exit to quit]\n")
            if prompt == "exit":
                break

            main()
        except Exception as e:
            print(traceback.format_exc())
