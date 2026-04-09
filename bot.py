import os
import discord
from discord.ext import commands
import wavelink

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True  # Importante para música!

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# ================== CONEXÃO COM LAVALINK ==================
@bot.event
async def on_ready():
    print(f'✅ Bot conectado como {bot.user}')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="!play"))

    # Conectar ao Lavalink
    nodes = [
        wavelink.Node(
            identifier="MainNode",
            uri="http://127.0.0.1:2333",      # Mude se estiver em outro lugar
            password="youshallnotpass"
        )
    ]
    await wavelink.Pool.connect(nodes=nodes, client=bot)
    print("🔗 Conectado ao Lavalink!")

# ================== COG DE MÚSICA ==================
class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def play(self, ctx, *, search: str):
        """Toca uma música ou adiciona na fila"""
        if not ctx.author.voice:
            return await ctx.send("❌ Você precisa estar em um canal de voz!")

        channel = ctx.author.voice.channel
        player: wavelink.Player = channel.guild.voice_client or await channel.connect(cls=wavelink.Player)

        tracks = await wavelink.Playable.search(search)
        
        if not tracks:
            return await ctx.send("❌ Não encontrei essa música.")

        if isinstance(tracks, wavelink.Playlist):
            added = await player.queue.put_wait(tracks)
            await ctx.send(f"✅ Adicionada playlist **{tracks.name}** com {len(tracks)} músicas!")
        else:
            track = tracks[0]
            await player.queue.put_wait(track)
            await ctx.send(f"✅ Adicionado: **{track.title}**")

        if not player.playing:
            await player.play(player.queue.get())

    @commands.command()
    async def skip(self, ctx):
        """Pula a música atual"""
        player: wavelink.Player = ctx.voice_client
        if player and player.playing:
            await player.skip()
            await ctx.send("⏭️ Música pulada!")
        else:
            await ctx.send("❌ Não tem música tocando.")

    @commands.command()
    async def pause(self, ctx):
        player: wavelink.Player = ctx.voice_client
        if player and player.playing:
            await player.pause()
            await ctx.send("⏸️ Pausado.")

    @commands.command()
    async def resume(self, ctx):
        player: wavelink.Player = ctx.voice_client
        if player and player.paused:
            await player.resume()
            await ctx.send("▶️ Voltando...")

    @commands.command()
    async def stop(self, ctx):
        player: wavelink.Player = ctx.voice_client
        if player:
            await player.disconnect()
            await ctx.send("⏹️ Parei e saí do canal.")

    @commands.command()
    async def queue(self, ctx):
        player: wavelink.Player = ctx.voice_client
        if not player or not player.queue:
            return await ctx.send("Fila vazia.")
        
        q = "\n".join([f"{i+1}. {track.title}" for i, track in enumerate(player.queue)])
        await ctx.send(f"**Fila atual:**\n{q}")

# ================== COMANDOS ANTIGOS ==================
@bot.command()
async def ola(ctx):
    await ctx.send(f"Fala dev! 🚀 {ctx.author.mention}")

@bot.command()
async def ajuda(ctx):
    embed = discord.Embed(title="🚀 Comandos Disponíveis", color=0x7289da)
    embed.add_field(name="Música", value="!play <música>\n!skip\n!pause\n!resume\n!stop\n!queue", inline=False)
    embed.add_field(name="Outros", value="!ola\n!projeto", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def projeto(ctx):
    await ctx.send("💡 Ideia: Crie uma lista de tarefas com Python!")

# Adicionar o Cog
async def setup_hook():
    await bot.add_cog(Music(bot))

bot.setup_hook = setup_hook

bot.run(os.getenv("MTQ5MTkwNzIwNjYwNDUyMTU5Ng.GqHnDK.obi0UNP9oioliOJXuGSRfR0TSR0wGD8Uv7qayo"))



