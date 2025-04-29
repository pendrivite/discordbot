from discord.ext import commands
import discord
import asyncio

def setup_commands(bot):
    # Komenda: Ping
    @bot.command()
    async def ping(ctx):
        """Sprawdza opóźnienie bota."""
        await ctx.send(f'Pong! {round(bot.latency * 1000)}ms')

    # Komenda: Info o użytkowniku
    @bot.command()
    async def info(ctx, member: discord.Member = None):
        """Wyświetla informacje o użytkowniku (domyślnie o autorze)."""
        member = member or ctx.author
        embed = discord.Embed(title="Informacje o użytkowniku", color=discord.Color.blue())
        embed.add_field(name="Nazwa", value=member.name, inline=True)
        embed.add_field(name="ID", value=member.id, inline=True)
        embed.add_field(name="Dołączył", value=member.joined_at.strftime("%Y-%m-%d"), inline=True)
        embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
        await ctx.send(embed=embed)

    # Komenda: Czyszczenie wiadomości
    @bot.command()
    @commands.has_permissions(manage_messages=True)
    async def clear(ctx, amount: int):
        """Usuwa określoną liczbę wiadomości (tylko dla osób z uprawnieniami)."""
        await ctx.channel.purge(limit=amount + 1)
        await ctx.send(f'Usunięto {amount} wiadomości.', delete_after=5)

    # Komenda: Nadanie roli administratora
    @bot.command()
    @commands.has_permissions(administrator=True)
    async def makeadmin(ctx, member: discord.Member):
        """Nadaje użytkownikowi rolę Admin (tylko dla administratorów)."""
        admin_role = discord.utils.get(ctx.guild.roles, name="Admin")
        
        if not admin_role:
            await ctx.send("Rola 'Admin' nie istnieje na tym serwerze!")
            return
        
        if admin_role in member.roles:
            await ctx.send(f"{member.mention} już ma rolę Admin!")
            return
        
        try:
            await member.add_roles(admin_role)
            await ctx.send(f"{member.mention} otrzymał rolę Admin!")
        except discord.Forbidden:
            await ctx.send("Brak uprawnień do nadania roli! Upewnij się, że moja rola jest wyższa niż rola Admin.")
        except discord.HTTPException as e:
            await ctx.send(f"Wystąpił błąd: {e}")

    # Komenda: Wysłanie wiadomości (z opcją powtórek)
    @bot.command()
    async def write(ctx, *, message_count):
        """Wysyła podaną wiadomość określoną liczbę razy (np. !write Cześć 100)."""
        MAX_REPEATS = 100  # Maksymalna liczba powtórek
        
        # Rozdziel treść wiadomości i liczbę powtórek
        try:
            parts = message_count.rsplit(' ', 1)
            if len(parts) == 1:
                message = parts[0]
                count = 1
            else:
                message, count_str = parts
                count = int(count_str)
        except ValueError:
            await ctx.send("Liczba powtórek musi być liczbą całkowitą! (np. !write Cześć 100)")
            return

        # Sprawdzanie ograniczeń
        if count < 1:
            await ctx.send("Liczba powtórek musi być większa od 0!")
            return
        if count > MAX_REPEATS:
            await ctx.send(f"Za dużo powtórek! Maksymalnie można wysłać {MAX_REPEATS} wiadomości.")
            return

        try:
            for _ in range(count):
                await ctx.send(message)
                await asyncio.sleep(0.5)
        except discord.Forbidden:
            await ctx.send("Brak uprawnień do wysyłania wiadomości w tym kanale!")
        except discord.HTTPException as e:
            await ctx.send(f"Błąd podczas wysyłania wiadomości: {e}")

    # Komenda: Wysłanie wiadomości na serwer z DM
    @bot.command()
    async def writeserv(ctx, *, args):
        """Wysyła wiadomość na podany kanał i serwer z DM (np. !writeserv Cześć #ogólny MojSerwer)."""
        if not isinstance(ctx.channel, discord.DMChannel):
            await ctx.send("Tej komendy można używać tylko w prywatnych wiadomościach (DM)!")
            return

        # Rozdziel argumenty: wiadomość, kanał, serwer
        try:
            parts = args.rsplit(' ', 2)
            if len(parts) < 3:
                await ctx.send("Podaj wiadomość, kanał i serwer! (np. !writeserv Cześć #ogólny MojSerwer)")
                return
            message, channel_name, server_name = parts
            # Usuń '#' z nazwy kanału, jeśli podano
            channel_name = channel_name.lstrip('#')
        except ValueError:
            await ctx.send("Nieprawidłowy format! Użyj: !writeserv <wiadomość> <kanał> <serwer>")
            return

        # Znajdź serwer
        guild = discord.utils.get(bot.guilds, name=server_name)
        if not guild:
            await ctx.send(f"Nie znaleziono serwera o nazwie '{server_name}'!")
            return

        # Znajdź kanał
        channel = discord.utils.get(guild.text_channels, name=channel_name)
        if not channel:
            await ctx.send(f"Nie znaleziono kanału tekstowego o nazwie '{channel_name}' na serwerze '{server_name}'!")
            return

        # Sprawdź uprawnienia
        permissions = channel.permissions_for(guild.me)
        if not permissions.send_messages:
            await ctx.send(f"Brak uprawnień do wysyłania wiadomości na kanale '{channel_name}' na serwerze '{server_name}'!")
            return

        # Wyślij wiadomość
        try:
            await channel.send(message)
            await ctx.send(f"Wiadomość '{message}' została wysłana na kanał '{channel_name}' na serwerze '{server_name}'!")
        except discord.HTTPException as e:
            await ctx.send(f"Błąd podczas wysyłania wiadomości: {e}")

    # Obsługa błędów dla komendy clear
    @clear.error
    async def clear_error(ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Brak uprawnień do zarządzania wiadomościami!")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Podaj liczbę wiadomości do usunięcia!")

    # Obsługa błędów dla komendy makeadmin
    @makeadmin.error
    async def makeadmin_error(ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Tylko administratorzy mogą używać tej komendy!")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Podaj użytkownika, któremu chcesz nadać rolę Admin! (np. !makeadmin @użytkownik)")

    # Obsługa błędów dla komendy write
    @write.error
    async def write_error(ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Podaj wiadomość do wysłania! (np. !write Cześć 100)")

    # Obsługa błędów dla komendy writeserv
    @writeserv.error
    async def writeserv_error(ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Podaj wiadomość, kanał i serwer! (np. !writeserv Cześć #ogólny MojSerwer)")
