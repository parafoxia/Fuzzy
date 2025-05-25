import crescent
import hikari

plugin = crescent.Plugin[hikari.GatewayBot, None]()


@plugin.include
@crescent.command(
    description="Shuts Fuzzy down.",
    default_member_permissions=hikari.Permissions.ADMINISTRATOR,
)
async def shutdown(ctx: crescent.Context):
    await ctx.respond("Shutting down. See you soon!", ephemeral=True)
    await plugin.app.close()
