import datetime as dt
import logging
from collections import defaultdict

import crescent
import hikari

from fuzzy.db import cxn

_log = logging.getLogger(__name__)

plugin = crescent.Plugin[hikari.GatewayBot, None]()


@plugin.include
@crescent.command(name="userinfo", description="Fetches a user's information")
class User:
    user = crescent.option(
        hikari.User,
        "The user to fetch information for.",
        default=None,
    )

    async def callback(self, ctx: crescent.Context) -> None:
        guild = plugin.app.cache.get_guild(453229374691344394)
        if not guild:
            await ctx.respond("Guild not found.", ephemeral=True)
            return

        member = guild.get_member(
            self.user or ctx.user
        ) or await plugin.app.rest.fetch_member(
            guild.id,
            self.user or ctx.user,
        )
        if not member:
            await ctx.respond("User not found.", ephemeral=True)
            return

        roles = sorted(
            member.get_roles() or await member.fetch_roles(),
            key=lambda role: role.position,
            reverse=True,
        )

        await ctx.respond(
            embed=hikari.Embed(
                title=f"User Information - {member.display_name}",
                colour=(
                    colours[0]
                    if (colours := [role.color for role in roles if role.color])
                    else None
                ),
            )
            .set_thumbnail(member.user.make_avatar_url(size=1024))
            .set_author(name="Information")
            .set_footer(
                text=f"Invoked by {ctx.user.display_name}",
                icon=ctx.user.make_avatar_url(size=1024),
            )
            .add_field(name="User ID", value=str(member.user.id))
            .add_field(
                name="Admin?",
                value=(
                    "Yes"
                    if roles[0].permissions & hikari.Permissions.ADMINISTRATOR
                    else "No"
                ),
                inline=True,
            )
            .add_field(
                name="Bot?",
                value="Yes" if member.is_bot else "No",
                inline=True,
            )
            .add_field(
                name="Boosting?",
                value="Yes" if member.premium_since else "No",
                inline=True,
            )
            .add_field(
                name="Created on",
                value=(
                    member.user.created_at.strftime("%d %b %Y")
                    if member.user.created_at
                    else "Unknown"
                ),
                inline=True,
            )
            .add_field(
                name="Joined on",
                value=(
                    member.joined_at.strftime("%d %b %Y")
                    if member.joined_at
                    else "Unknown"
                ),
                inline=True,
            )
            .add_field("No. of roles", f"{len(roles):,}", inline=True)
            .add_field(
                "Existed for",
                f"{(dt.datetime.now(dt.UTC) - member.user.created_at).days:,} days",
                inline=True,
            )
            .add_field(
                "Member for",
                (
                    f"{(dt.datetime.now(dt.UTC) - member.joined_at).days:,} days"
                    if member.joined_at
                    else "Unknown"
                ),
                inline=True,
            )
            .add_field(name="Top role", value=roles[0].mention, inline=True)
        )
