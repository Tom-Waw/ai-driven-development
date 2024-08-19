import logging

from lpu.agent import Agent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    developer = Agent("Developer")

    logger.info("Prompting Developer")
    developer.prompt(
        "You are a well trained professional software developer (python)."
        + "Respond in JSON format with a random 'email' and 'phone' number."
    )


if __name__ == "__main__":
    main()
