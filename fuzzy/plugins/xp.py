import datetime as dt
import logging
from collections import defaultdict

import crescent
import hikari

from fuzzy.db import cxn

_log = logging.getLogger(__name__)

plugin = crescent.Plugin[hikari.GatewayBot, None]()

CHANNEL_IDS = {
    453353894857146368,
    453566750395596810,
}


def level(xp: int) -> int:
    return int((xp + 1) ** 0.5)


@plugin.include
@crescent.event
async def apply_missed_xp(event: hikari.StartedEvent) -> None:
    cursor = cxn.cursor()
    cursor.execute("SELECT last_message FROM users ORDER BY last_message DESC LIMIT 1")
    last_message = res[0] if (res := cursor.fetchone()) else 0

    _log.info("Applying missed XP (from %s)", last_message)

    xp_mapping: dict[int, int] = defaultdict(int)
    msg_mapping: dict[int, float] = defaultdict(lambda: 0)

    for channel_id in CHANNEL_IDS:
        messages = plugin.app.rest.fetch_messages(
            channel_id,
            after=dt.datetime.fromtimestamp(last_message),
        )

        async for message in messages:
            if (ts := message.timestamp.timestamp()) - msg_mapping[
                message.author.id
            ] > 60:
                xp_mapping[message.author.id] += 1
                msg_mapping[message.author.id] = ts

    cursor.executemany(
        """
        INSERT INTO users (id, xp, last_message) VALUES (:author_id, :xp, :ts)
        ON CONFLICT (id) DO UPDATE SET xp = xp + :xp, last_message = :ts
        """,
        (
            {
                "author_id": user_id,
                "xp": xp,
                "ts": dt.datetime.now(dt.UTC).timestamp(),
            }
            for user_id, xp in xp_mapping.items()
        ),
    )
    cxn.commit()

    _log.info("Applied missed XP!")


@plugin.include
@crescent.event
async def add_xp(event: hikari.MessageCreateEvent) -> None:
    if not event.is_human or event.channel_id not in CHANNEL_IDS:
        return

    cursor = cxn.cursor()

    cursor.execute(
        "SELECT last_message FROM users WHERE id = ?",
        (event.author_id,),
    )
    last_message = res[0] if (res := cursor.fetchone()) else 0

    if (ts := event.message.timestamp.timestamp()) - last_message < 60:
        _log.info("Not enough time passed since last message")
        return

    _log.info("Adding XP to %s", event.author_id)

    cursor.execute(
        """
        INSERT INTO users (id, xp, last_message) VALUES (:author_id, 1, :ts)
        ON CONFLICT (id) DO UPDATE SET xp = xp + 1, last_message = :ts
        """,
        {
            "author_id": event.author_id,
            "ts": ts,
        },
    )
    cxn.commit()


@plugin.include
@crescent.command(name="xp", description="Fetches a user's XP and level")
class XP:
    user = crescent.option(
        hikari.User,
        "The user to fetch the level for.",
        default=None,
    )

    async def callback(self, ctx: crescent.Context) -> None:
        user = self.user or ctx.user
        cursor = cxn.cursor()
        cursor.execute("SELECT xp FROM users WHERE id = ?", (user.id,))
        xp = res[0] if (res := cursor.fetchone()) else 0
        await ctx.respond(
            f"{user.mention} has **{xp:,}** XP (level **{level(xp):,}**).",
        )


@plugin.include
@crescent.command(name="leaderboard", description="Fetches the leaderboard.")
class Leaderboard:
    async def callback(self, ctx: crescent.Context) -> None:
        cursor = cxn.cursor()
        cursor.execute("SELECT id, xp FROM users ORDER BY xp DESC LIMIT 10")
        leaderboard = cursor.fetchall()
        await ctx.respond(
            "\n".join(
                f"{i + 1}. <@{user_id}> - **{xp:,}** XP (level **{level(xp):,}**)."
                for i, (user_id, xp) in enumerate(leaderboard)
            ),
        )


@plugin.include
@crescent.command(name="nextlevel", description="Fetches a user's next level.")
class NextLevel:
    user = crescent.option(
        hikari.User,
        "The user to fetch the next level for.",
        default=None,
    )

    async def callback(self, ctx: crescent.Context) -> None:
        user = self.user or ctx.user
        cursor = cxn.cursor()
        cursor.execute("SELECT xp FROM users WHERE id = ?", (user.id,))
        xp = res[0] if (res := cursor.fetchone()) else 0
        lvl = level(xp)
        remaining_xp = (lvl + 1) ** 2 - xp
        await ctx.respond(
            f"{user.mention} needs **{remaining_xp:,}** XP to reach level **{lvl + 1:,}**.",
        )
