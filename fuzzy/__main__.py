import os

import crescent
import hikari

bot = hikari.GatewayBot(os.environ["TOKEN"])
client = crescent.Client(bot)
client.plugins.load_folder("fuzzy.plugins")


if __name__ == "__main__":
    if os.name != "nt":
        import asyncio

        import uvloop

        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    bot.run(
        activity=hikari.Activity(
            name="you!",
            type=hikari.ActivityType.WATCHING,
        )
    )
