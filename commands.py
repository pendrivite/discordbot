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
            # Dzielimy input na słowa, bierzemy ostatnie jako potencjalną liczbę
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

        # Wysyłanie wiadomości
        try:
            for _ in range(count):
                await ctx.send(message)
                await asyncio.sleep(0.5)  # Opóźnienie 0.5s, aby uniknąć rate limitów
        except discord.Forbidden:
            await ctx.send("Brak uprawnień do wysyłania wiadomości w tym kanale!")
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