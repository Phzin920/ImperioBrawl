🤖 Império Brawl Bot – Documentação Oficial
O Império Brawl Bot é o assistente definitivo para servidores de Brawl Stars. Desenvolvido em Python com discord.py, ele oferece moderação avançada, envio de mensagens personalizadas em embed, inteligência artificial (IA) com Groq, criação de formulários interativos, sistema completo de logs, filtro de palavrões, menus dropdown, botões, anúncios automáticos, advertências e muito mais. Tudo isso através de Slash Commands modernos e intuitivos.

🚀 Funcionalidades Principais
📢 Sistema de Anúncios e Embeds
Comando /falar – escolha o tipo (aviso, urgencia, atualizacao) e envie uma mensagem com cor e título personalizados.

Footer configurável com nome e ícone do servidor.

🛡️ Moderação Completa
/ban, /kick, /mute (com duração: 10s, 5m, 2h, 1d).

/add-advertencia – adiciona advertência a um usuário (armazenada em JSON).

/warn-dm – envia um aviso na DM do usuário com filtro automático de palavras impróprias.

Todos os comandos exigem permissão de staff (cargo específico ou ban_members).

📝 Formulários e Interatividade
/formulario-criar – cria um modal com perguntas personalizadas (separadas por ponto e vírgula).

/formulario-editar (em desenvolvimento, mas estrutura pronta).

/add-botao – adiciona um botão com link a qualquer mensagem existente.

/menu-dropdown – gera um menu suspenso com opções personalizadas.

🤖 Inteligência Artificial (Groq)
/chat-ia – converse com a IA (modelo Llama 3 70B) diretamente no Discord.

/anunciar – informe um tema e a IA gera um anúncio criativo, formatado e pronto para ser enviado em qualquer canal.

Filtro de linguagem ofensiva também aplicado na entrada do usuário.

⚙️ Utilidades Extras
/forum-criar – cria um novo canal de fórum no servidor (staff apenas).

Sistema de status rotativo (15 segundos) com mensagens dinâmicas.

📊 Sistema de Logs Avançado
Todas as ações de moderação (ban, kick, mute, advertência, warn DM, anúncio) são registradas em um canal específico (LOG_CHANNEL_ID).

Logs automáticos de mensagens deletadas e mensagens editadas (com conteúdo antes/depois).

Interface limpa com embeds coloridos por tipo de evento.

🔒 Filtro de Palavrões
Utiliza a biblioteca better-profanity para bloquear mensagens impróprias em /warn-dm e /chat-ia.

Expansível com palavras personalizadas.

📚 Painel de Ajuda Integrado
/painel-ajuda – exibe uma lista completa de todos os comandos do bot, organizados por categoria, com descrições claras.

📁 Estrutura do Projeto (Versão Avançada)
text
ImperioBrawlBOT/
│
├── bot.py                     # Arquivo principal (tudo em um só lugar)
├── .env                       # Variáveis de ambiente (token, chaves, IDs)
├── requirements.txt           # Dependências
├── warnings.json              # Armazenamento das advertências (criado automaticamente)
├── forms.json                 # Dados de formulários (futuro)
│
└── (opcional) cogs/           # Se quiser separar, mas no código único está tudo modularizado via Cogs internas
🔧 Tecnologias Utilizadas
Python 3.10+

discord.py 2.x (Slash Commands nativos)

Groq API (LLaMA 3 70B)

better-profanity (filtro de palavrões)

python-dotenv

JSON para armazenamento local

⚙️ Configuração e Instalação
1. Clone o repositório
bash
git clone https://github.com/Phzin920/imperio-brawl-bot.git
cd imperio-brawl-bot
2. Instale as dependências
bash
pip install -r requirements.txt
requirements.txt:

text
discord.py
python-dotenv
groq
better-profanity
3. Configure o arquivo .env
Crie um arquivo .env na raiz com o seguinte conteúdo:

env
DISCORD_TOKEN=SEU_TOKEN_AQUI
GROQ_API_KEY=SUA_CHAVE_GROQ_AQUI
LOG_CHANNEL_ID=ID_DO_CANAL_DE_LOGS
STAFF_ROLE_ID=ID_DO_CARGO_DE_STAFF (opcional)
IDs podem ser obtidos ativando o modo desenvolvedor no Discord (clique com botão direito no canal/cargo → "Copiar ID").

4. Execute o bot
bash
python bot.py
📌 Lista Completa de Slash Commands
Comando	Descrição	Permissão
/falar	Envia embed personalizado (aviso/urgência/atualização)	Staff
/ban	Bane um membro	Staff
/kick	Expulsa um membro	Staff
/mute	Silencia temporariamente (ex: 1h)	Staff
/add-advertencia	Adiciona uma advertência	Staff
/warn-dm	Envia aviso na DM (com filtro)	Staff
/formulario-criar	Cria formulário com perguntas	Gerenciar Mensagens
/formulario-editar	Edita formulário (placeholder)	Staff
/add-botao	Adiciona botão a uma mensagem	Staff
/menu-dropdown	Cria menu suspenso	Qualquer um
/chat-ia	Conversa com IA (Groq)	Qualquer um
/anunciar	Gera anúncio por IA baseado em tema	Staff
/forum-criar	Cria canal de fórum	Gerenciar Canais
/painel-ajuda	Exibe todos os comandos	Qualquer um
🧪 Exemplos de Uso
➕ Enviar um aviso
text
/falar tipo:aviso mensagem:O servidor entrará em modo de manutenção às 22h.
🔨 Banir um usuário
text
/ban membro:@Jogador123 motivo:Quebrou as regras repetidamente
🤖 Criar anúncio com IA
text
/anunciar tema:Novo evento de fim de semana com dobro de experiência
→ A IA gera um texto criativo e envia no canal atual.

📝 Formulário de entrada
text
/formulario-criar titulo:"Formulário de Recrutamento" perguntas:"Qual sua idade?; Qual seu rank?; Por que quer entrar?"
→ O bot abre um modal para o usuário preencher.

🔒 Segurança e Boas Práticas
O token do bot é carregado via .env – nunca commitar esse arquivo.

O .gitignore inclui:

text
.env
__pycache__/
*.pyc
warnings.json
forms.json
Comandos de moderação verificam permissões via cargo STAFF_ROLE_ID ou permissão ban_members.

Filtro de palavrões ativo em canais de texto e DMs de aviso.

🚀 Deploy Contínuo (Hospedagem)
Opções recomendadas:

Railway / Render (gratuito com limitação)

VPS (Linode, DigitalOcean, AWS)

Heroku (com dyno sempre ativo)

Configure as mesmas variáveis de ambiente do .env no painel da hospedagem.

Comando de inicialização:

bash
python bot.py
📈 Melhorias Planejadas (Futuras)
Dashboard web para gerenciar advertências e logs.

Banco de dados (SQLite/PostgreSQL) em vez de JSON.

Sistema de tickets.

Agendamento de mensagens.

Suporte a múltiplos servidores (sharding).

👑 Autor e Créditos
Enzo Pietrantonio
Desenvolvedor Python e Web. Projeto desenvolvido para a comunidade Império Brawl, sob a organização The Programmers Studio (TPS).

📄 Licença
Este projeto é de código aberto para fins educacionais e de uso comunitário. Sinta-se livre para adaptar e melhorar, mantendo os devidos créditos.

Império Brawl – Evolua com a comunidade, lidere com o bot. 🏆

