import os

import crescent
import hikari

from fuzzy.db import init_db

bot = hikari.GatewayBot(os.environ["TOKEN"])
client = crescent.Client(bot, default_guild=453229374691344394)
client.plugins.load_folder("fuzzy.plugins")

if __name__ == "__main__":
    if os.name != "nt":
        import asyncio

        import uvloop

        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    init_db()
    bot.run(
        activity=hikari.Activity(
            name="you!",
            type=hikari.ActivityType.WATCHING,
        )
    )
