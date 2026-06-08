    import discord
    from discord.ext import commands, tasks
    from discord import app_commands
    import os
    import json
    import asyncio
    from datetime import datetime, timedelta
    from dotenv import load_dotenv
    from better_profanity import profanity
    import groq

    load_dotenv()

    TOKEN = os.getenv("DISCORD_TOKEN")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    LOG_CHANNEL_ID = int(os.getenv("1512877642234466444", 0))
    STAFF_ROLE_ID = int(os.getenv("1444651305443266724", 0))

    # Configuração do filtro de palavrões (adicione mais palavras se quiser)
    profanity.load_censor_words()

    # Inicializa cliente Groq
    groq_client = groq.Groq(api_key=GROQ_API_KEY)

    # ======================== CONFIGURAÇÕES DOS EMBEDS ========================
    FOOTER_TEXT = "Bot de Moderação e Anúncios"
    FOOTER_ICON = None  # Coloque uma URL se quiser

    EMBEDS = {
        'aviso': {'titulo': '📢 Aviso', 'cor': 0x3498DB},
        'urgencia': {'titulo': '🚨 Urgência', 'cor': 0xE74C3C},
        'atualizacao': {'titulo': '📢 Atualização', 'cor': 0x2ECC71}
    }

    def criar_embed(tipo: str, mensagem: str):
        config = EMBEDS[tipo]
        embed = discord.Embed(title=config['titulo'], description=mensagem, color=config['cor'])
        if FOOTER_ICON:
            embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_ICON)
        else:
            embed.set_footer(text=FOOTER_TEXT)
        return embed

    # ======================== SISTEMA DE LOGS ========================
    async def enviar_log(interaction_or_ctx, acao: str, detalhes: str, cor=0x2ECC71):
        canal = bot.get_channel(LOG_CHANNEL_ID)
        if not canal:
            return
        embed = discord.Embed(title=f"📝 {acao}", description=detalhes, color=cor, timestamp=datetime.utcnow())
        embed.set_footer(text=f"ID do usuário: {interaction_or_ctx.user.id if hasattr(interaction_or_ctx, 'user') else 'Sistema'}")
        await canal.send(embed=embed)

    # ======================== ARMAZENAMENTO SIMPLES (JSON) ========================
    # Arquivos: warnings.json, forms.json
    def carregar_json(nome):
        try:
            with open(nome, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def salvar_json(nome, dados):
        with open(nome, 'w') as f:
            json.dump(dados, f, indent=4)

    # ======================== COG DE MODERAÇÃO ========================
    class ModeracaoCog(commands.Cog):
        def __init__(self, bot):
            self.bot = bot

        # Verificação de permissão (cargo staff ou permissão de banir)
        async def has_staff_perms(self, interaction: discord.Interaction):
            if STAFF_ROLE_ID and interaction.user.get_role(STAFF_ROLE_ID):
                return True
            return interaction.user.guild_permissions.ban_members

        @app_commands.command(name="ban", description="Bane um usuário do servidor")
        async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = "Sem motivo"):
            if not await self.has_staff_perms(interaction):
                await interaction.response.send_message("❌ Você não tem permissão para usar este comando.", ephemeral=True)
                return
            await member.ban(reason=reason)
            embed = criar_embed("urgencia", f"**{member}** foi banido.\nMotivo: {reason}")
            await interaction.response.send_message(embed=embed)
            await enviar_log(interaction, "BAN", f"**Staff:** {interaction.user}\n**Alvo:** {member}\n**Motivo:** {reason}", 0xE74C3C)

        @app_commands.command(name="kick", description="Expulsa um usuário do servidor")
        async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = "Sem motivo"):
            if not await self.has_staff_perms(interaction):
                await interaction.response.send_message("❌ Sem permissão.", ephemeral=True)
                return
            await member.kick(reason=reason)
            embed = criar_embed("aviso", f"**{member}** foi expulso.\nMotivo: {reason}")
            await interaction.response.send_message(embed=embed)
            await enviar_log(interaction, "KICK", f"**Staff:** {interaction.user}\n**Alvo:** {member}\n**Motivo:** {reason}", 0xE67E22)

        @app_commands.command(name="mute", description="Silencia um usuário por um tempo")
        async def mute(self, interaction: discord.Interaction, member: discord.Member, duracao: str, reason: str = "Sem motivo"):
            if not await self.has_staff_perms(interaction):
                await interaction.response.send_message("❌ Sem permissão.", ephemeral=True)
                return
            # duracao formato: "10s", "5m", "1h", "1d"
            try:
                if duracao.endswith('s'):
                    segundos = int(duracao[:-1])
                elif duracao.endswith('m'):
                    segundos = int(duracao[:-1]) * 60
                elif duracao.endswith('h'):
                    segundos = int(duracao[:-1]) * 3600
                elif duracao.endswith('d'):
                    segundos = int(duracao[:-1]) * 86400
                else:
                    raise ValueError
                timeout = timedelta(seconds=segundos)
                await member.timeout(timeout, reason=reason)
                embed = criar_embed("aviso", f"**{member}** foi silenciado por {duracao}.\nMotivo: {reason}")
                await interaction.response.send_message(embed=embed)
                await enviar_log(interaction, "MUTE", f"**Staff:** {interaction.user}\n**Alvo:** {member}\n**Duração:** {duracao}\n**Motivo:** {reason}", 0xF1C40F)
            except:
                await interaction.response.send_message("Formato inválido. Use `10s`, `5m`, `2h` ou `1d`.", ephemeral=True)

        @app_commands.command(name="add-advertencia", description="Adiciona uma advertência a um usuário")
        async def add_warning(self, interaction: discord.Interaction, member: discord.Member, motivo: str):
            if not await self.has_staff_perms(interaction):
                await interaction.response.send_message("❌ Sem permissão.", ephemeral=True)
                return
            warnings = carregar_json("warnings.json")
            user_id = str(member.id)
            if user_id not in warnings:
                warnings[user_id] = []
            warnings[user_id].append({"staff": interaction.user.name, "motivo": motivo, "data": str(datetime.now())})
            salvar_json("warnings.json", warnings)
            embed = criar_embed("aviso", f"⚠️ Advertência adicionada a {member.mention}\nMotivo: {motivo}")
            await interaction.response.send_message(embed=embed)
            await enviar_log(interaction, "ADVERTÊNCIA", f"**Staff:** {interaction.user}\n**Alvo:** {member}\n**Motivo:** {motivo}", 0xE67E22)

        @app_commands.command(name="warn-dm", description="Envia um aviso na DM de um usuário (com filtro de palavrões)")
        async def warn_dm(self, interaction: discord.Interaction, member: discord.Member, mensagem: str):
            if not await self.has_staff_perms(interaction):
                await interaction.response.send_message("❌ Sem permissão.", ephemeral=True)
                return
            if profanity.contains_profanity(mensagem):
                await interaction.response.send_message("❌ A mensagem contém palavras inapropriadas e foi bloqueada.", ephemeral=True)
                return
            try:
                embed = discord.Embed(title="🚨 Aviso da Moderação", description=mensagem, color=0xE74C3C)
                await member.send(embed=embed)
                await interaction.response.send_message(f"✅ Aviso enviado para {member.mention}.", ephemeral=True)
                await enviar_log(interaction, "WARN DM", f"**Staff:** {interaction.user}\n**Alvo:** {member}\n**Conteúdo:** {mensagem}", 0x3498DB)
            except:
                await interaction.response.send_message("❌ Não foi possível enviar DM para o usuário.", ephemeral=True)

    # ======================== COG DE FORMULÁRIOS ========================
    class FormularioCog(commands.Cog):
        def __init__(self, bot):
            self.bot = bot
            self.forms = carregar_json("forms.json")

        class FormModal(discord.ui.Modal):
            def __init__(self, title, perguntas):
                super().__init__(title=title)
                self.perguntas = perguntas
                for i, p in enumerate(perguntas):
                    item = discord.ui.TextInput(label=p, style=discord.TextStyle.long, required=True, custom_id=f"q{i}")
                    self.add_item(item)

            async def on_submit(self, interaction: discord.Interaction):
                respostas = "\n".join([f"**{self.perguntas[i]}:** {item.value}" for i, item in enumerate(self.children)])
                embed = discord.Embed(title="📝 Novo Formulário Enviado", description=respostas, color=0x2ECC71)
                # Envia para um canal específico (pode mudar)
                canal = interaction.guild.get_channel(LOG_CHANNEL_ID) or interaction.channel
                await canal.send(embed=embed)
                await interaction.response.send_message("✅ Formulário enviado com sucesso!", ephemeral=True)

        @app_commands.command(name="formulario-criar", description="Cria um formulário com perguntas personalizadas")
        async def criar_form(self, interaction: discord.Interaction, titulo: str, perguntas: str):
            if not interaction.user.guild_permissions.manage_messages:
                await interaction.response.send_message("❌ Permissão insuficiente.", ephemeral=True)
                return
            lista_perguntas = [p.strip() for p in perguntas.split(";") if p.strip()]
            if not lista_perguntas:
                await interaction.response.send_message("❌ Informe pelo menos uma pergunta (separadas por ponto e vírgula).", ephemeral=True)
                return
            modal = self.FormModal(titulo, lista_perguntas)
            await interaction.response.send_modal(modal)

        @app_commands.command(name="formulario-editar", description="Edita um formulário existente (apenas título e perguntas)")
        async def editar_form(self, interaction: discord.Interaction, id_form: str, novo_titulo: str, novas_perguntas: str):
            # Simplificado: só armazena em memória, mas você pode salvar em JSON
            await interaction.response.send_message("⚠️ Funcionalidade de edição em desenvolvimento. Use /formulario-criar novamente.", ephemeral=True)

        @app_commands.command(name="add-botao", description="Adiciona um botão a uma mensagem atual")
        async def add_botao(self, interaction: discord.Interaction, mensagem_id: str, label: str, url: str):
            try:
                msg = await interaction.channel.fetch_message(int(mensagem_id))
                view = discord.ui.View()
                view.add_item(discord.ui.Button(label=label, url=url))
                await msg.edit(view=view)
                await interaction.response.send_message("✅ Botão adicionado!", ephemeral=True)
            except:
                await interaction.response.send_message("❌ Erro ao encontrar mensagem ou adicionar botão.", ephemeral=True)

        @app_commands.command(name="menu-dropdown", description="Cria uma mensagem com um menu dropdown personalizado")
        async def menu_dropdown(self, interaction: discord.Interaction, titulo: str, opcoes: str):
            # opcoes: "op1,desc1;op2,desc2"
            itens = []
            for item in opcoes.split(";"):
                parts = item.split(",")
                if len(parts) >= 2:
                    itens.append(discord.SelectOption(label=parts[0], description=parts[1], value=parts[0]))
            if not itens:
                await interaction.response.send_message("❌ Formato inválido. Use: `Opção1,Descrição1;Opção2,Descrição2`", ephemeral=True)
                return
            select = discord.ui.Select(placeholder=titulo, options=itens)

            async def callback(interact):
                await interact.response.send_message(f"Você selecionou: {interact.data['values'][0]}", ephemeral=True)
            select.callback = callback

            view = discord.ui.View()
            view.add_item(select)
            await interaction.response.send_message("📋 Menu criado:", view=view)

    # ======================== COG DE IA E ANÚNCIOS ========================
    class IACog(commands.Cog):
        def __init__(self, bot):
            self.bot = bot

        @app_commands.command(name="chat-ia", description="Converse com a IA (Groq)")
        async def chat_ia(self, interaction: discord.Interaction, mensagem: str):
            if profanity.contains_profanity(mensagem):
                await interaction.response.send_message("❌ Sua mensagem contém palavras inapropriadas.", ephemeral=True)
                return
            await interaction.response.defer()
            try:
                resposta = groq_client.chat.completions.create(
                    model="llama3-70b-8192",
                    messages=[
                        {"role": "system", "content": "Você é um assistente útil em um servidor Discord de Brawl Stars."},
                        {"role": "user", "content": mensagem}
                    ]
                )
                texto = resposta.choices[0].message.content
                if len(texto) > 2000:
                    texto = texto[:1997] + "..."
                embed = discord.Embed(title="🤖 IA Responde", description=texto, color=0x9B59B6)
                embed.set_footer(text=f"Comando usado por {interaction.user}")
                await interaction.followup.send(embed=embed)
            except Exception as e:
                await interaction.followup.send(f"❌ Erro na IA: {str(e)}")

        @app_commands.command(name="anunciar", description="Gera um anúncio automaticamente com IA baseado em um tema")
        async def anunciar(self, interaction: discord.Interaction, tema: str, canal: discord.TextChannel = None):
            if not interaction.user.guild_permissions.manage_messages:
                await interaction.response.send_message("❌ Permissão insuficiente.", ephemeral=True)
                return
            await interaction.response.defer()
            prompt = f"Crie um anúncio formal e atrativo para um servidor de Brawl Stars sobre o seguinte tema: {tema}. Use emojis, seja claro e empolgado. Máximo 400 caracteres."
            try:
                resposta = groq_client.chat.completions.create(
                    model="llama3-70b-8192",
                    messages=[{"role": "user", "content": prompt}]
                )
                texto = resposta.choices[0].message.content
                embed = criar_embed("atualizacao", texto)
                canal_destino = canal or interaction.channel
                await canal_destino.send(embed=embed)
                await interaction.followup.send(f"✅ Anúncio enviado em {canal_destino.mention}", ephemeral=True)
                await enviar_log(interaction, "ANÚNCIO IA", f"**Staff:** {interaction.user}\n**Tema:** {tema}\n**Canal:** {canal_destino.mention}\n**Conteúdo:** {texto}", 0x2ECC71)
            except Exception as e:
                await interaction.followup.send(f"❌ Erro ao gerar anúncio: {e}")

    # ======================== COG DE UTILIDADES EXTRAS ========================
    class UtilidadesCog(commands.Cog):
        def __init__(self, bot):
            self.bot = bot

        @app_commands.command(name="forum-criar", description="Cria um novo fórum no servidor")
        async def criar_forum(self, interaction: discord.Interaction, nome: str, categoria: discord.CategoryChannel = None):
            if not interaction.user.guild_permissions.manage_channels:
                await interaction.response.send_message("❌ Permissão insuficiente.", ephemeral=True)
                return
            try:
                forum = await interaction.guild.create_forum_channel(name=nome, category=categoria)
                embed = discord.Embed(title="✅ Fórum criado", description=f"{forum.mention} foi criado com sucesso.", color=0x2ECC71)
                await interaction.response.send_message(embed=embed)
                await enviar_log(interaction, "CRIAR FÓRUM", f"**Staff:** {interaction.user}\n**Nome:** {nome}\n**Categoria:** {categoria.name if categoria else 'Nenhuma'}", 0x3498DB)
            except Exception as e:
                await interaction.response.send_message(f"❌ Erro: {e}", ephemeral=True)

    # ======================== COG DE AJUDA ========================
    class AjudaCog(commands.Cog):
        def __init__(self, bot):
            self.bot = bot

        @app_commands.command(name="painel-ajuda", description="Mostra todos os comandos disponíveis e suas funções")
        async def painel_ajuda(self, interaction: discord.Interaction):
            embed = discord.Embed(title="📖 Central de Ajuda - Comandos do Bot", color=0xF1C40F)
            embed.set_thumbnail(url=bot.user.display_avatar.url)

            comandos = {
                "🛡️ Moderação": [
                    "`/ban` - Bane um usuário",
                    "`/kick` - Expulsa um usuário",
                    "`/mute` - Silencia temporariamente",
                    "`/add-advertencia` - Adiciona uma advertência",
                    "`/warn-dm` - Envia aviso na DM (com filtro)"
                ],
                "📝 Formulários": [
                    "`/formulario-criar` - Cria um formulário interativo",
                    "`/formulario-editar` - Edita um formulário",
                    "`/add-botao` - Adiciona botão a uma mensagem",
                    "`/menu-dropdown` - Cria menu suspenso"
                ],
                "🤖 IA e Anúncios": [
                    "`/chat-ia` - Converse com inteligência artificial",
                    "`/anunciar` - Gera anúncio automático por IA"
                ],
                "⚙️ Utilidades": [
                    "`/forum-criar` - Cria um canal de fórum",
                    "`/painel-ajuda` - Exibe este painel"
                ]
            }

            for categoria, cmds in comandos.items():
                embed.add_field(name=categoria, value="\n".join(cmds), inline=False)

            embed.set_footer(text="Sistema de moderação com logs avançados e filtro de palavrões")
            await interaction.response.send_message(embed=embed)

    # ======================== COG ORIGINAL "FALAR" (ADAPTADO) ========================
    class FalarCog(commands.Cog):
        def __init__(self, bot):
            self.bot = bot

        @app_commands.command(name="falar", description="Envia uma mensagem em embed (pode ser aviso, urgência ou atualização)")
        async def falar(self, interaction: discord.Interaction, tipo: str, mensagem: str):
            tipos_validos = ["aviso", "urgencia", "atualizacao"]
            if tipo not in tipos_validos:
                await interaction.response.send_message(f"Tipo inválido. Use: {', '.join(tipos_validos)}", ephemeral=True)
                return
            embed = criar_embed(tipo, mensagem)
            await interaction.response.send_message(embed=embed)

    # ======================== CONFIGURAÇÃO PRINCIPAL DO BOT ========================
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True

    class MeuBot(commands.Bot):
        async def setup_hook(self):
            await self.add_cog(ModeracaoCog(self))
            await self.add_cog(FormularioCog(self))
            await self.add_cog(IACog(self))
            await self.add_cog(UtilidadesCog(self))
            await self.add_cog(AjudaCog(self))
            await self.add_cog(FalarCog(self))
            await self.tree.sync()

    bot = MeuBot(command_prefix="!", intents=intents)

    # Rotação de status
    STATUS_LIST = [
        "/falar para enviar anúncios",
        "/falar para enviar atualizações",
        "👑 Império Brawl",
        "🏆 Comunidade de Brawl Stars",
        "🚨 Sistema de Avisos"
    ]
    status_index = 0

    @tasks.loop(seconds=15)
    async def rotate_status():
        global status_index
        await bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=STATUS_LIST[status_index]
            )
        )
        status_index = (status_index + 1) % len(STATUS_LIST)

    @bot.event
    async def on_ready():
        if not rotate_status.is_running():
            rotate_status.start()
        print(f"✅ Logged in as {bot.user}")
        # Carregar arquivos de dados
        if not os.path.exists("warnings.json"):
            salvar_json("warnings.json", {})
        if not os.path.exists("forms.json"):
            salvar_json("forms.json", {})

    # Logs de mensagens deletadas/editadas (opcional, avançado)
    @bot.event
    async def on_message_delete(message):
        if LOG_CHANNEL_ID and not message.author.bot:
            canal_log = bot.get_channel(LOG_CHANNEL_ID)
            if canal_log:
                embed = discord.Embed(title="🗑️ Mensagem deletada", description=f"**Autor:** {message.author}\n**Canal:** {message.channel.mention}\n**Conteúdo:** {message.content[:1000]}", color=0xE74C3C, timestamp=datetime.utcnow())
                await canal_log.send(embed=embed)

    @bot.event
    async def on_message_edit(before, after):
        if LOG_CHANNEL_ID and not before.author.bot and before.content != after.content:
            canal_log = bot.get_channel(LOG_CHANNEL_ID)
            if canal_log:
                embed = discord.Embed(title="✏️ Mensagem editada", description=f"**Autor:** {before.author}\n**Canal:** {before.channel.mention}\n**Antes:** {before.content[:500]}\n**Depois:** {after.content[:500]}", color=0x3498DB, timestamp=datetime.utcnow())
                await canal_log.send(embed=embed)

    # Inicialização
    if __name__ == "__main__":
        bot.run("TOKEN")
