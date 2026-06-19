![Distintivo com tempo gasto](https://img.shields.io/endpoint?url=https%3A%2F%2Fgist.githubusercontent.com%2FRealiserad%2Fd3ec7fdeecc35aeeb315b4efba493326%2Fraw%2Ffish-ai-git-estimate.json)
![Distintivo de popularidade](https://img.shields.io/endpoint?url=https%3A%2F%2Fgist.githubusercontent.com%2FRealiserad%2Fd3ec7fdeecc35aeeb315b4efba493326%2Fraw%2Fpopularity.json)
[![Doe XMR](https://img.shields.io/badge/Donate_XMR-grey?style=for-the-badge&logo=monero)](https://github.com/user-attachments/assets/07a2947f-6e5a-480f-990a-77204933411f)

Leia em [Português 🇧🇷](README-PT.md) ou [Inglês 🇺🇸](README.md).

# Sobre

`fish-ai` adiciona funcionalidades de IA ao [Fish](https://fishshell.com).
É incrível! Eu o construí para facilitar minha vida e espero que ele facilite a sua também. Aqui está a apresentação completa:

- Ele pode transformar um comentário em um comando de shell e vice-versa, o que significa menos tempo gasto lendo manpages, buscando no Google e copiando e colando do Stack Overflow. Excelente quando trabalhando com `git`, `kubectl`, `curl` e outras ferramentas com muitos parâmetros e opções.
- Cometeu um erro de digitação? Ele também pode corrigir um comando quebrado (semelhante ao [`thefuck`](https://github.com/nvbn/thefuck)).
- Não sabe o que digitar a seguir ou apenas está com preguiça? Deixe que o LLM complete seus comandos com um buscador difuso embutido.
- Tudo é feito usando dois (configuráveis) atalhos de teclado, sem necessidade de mouse!
- Pode ser conectado ao LLM de sua escolha (mesmo um auto-hospedado!).
- O projeto é totalmente open source, espero que seja relativamente fácil de ler e tem cerca de 2000 linhas de código, o que significa que você pode auditar o código você mesmo em uma tarde.
- Instale e atualize facilmente usando [`fisher`](https://github.com/jorgebucaran/fisher).
- Testado tanto em macOS quanto nas distribuições Linux mais comuns.
- Não interfere com [`fzf.fish`](https://github.com/PatrickF1/fzf.fish), [`tide`](https://github.com/IlanCosman/tide) ou qualquer outro plugin que você já esteja usando!
- Não envolve seu shell, instala telemetria ou força você a mudar para um emulador de terminal proprietário.

Este plugin foi originalmente baseado no repositório `fish.codex` do [Tom Dörr](https://github.com/tom-doerr/codex.fish). Sem o Tom, este repositório não existiria!

Se você gostou, por favor adicione uma ⭐.

Correções de bugs são bem-vindas! Considero este projeto em grande parte completo em termos de recursos. Antes de abrir um PR para um pedido de recurso, considere abrir uma issue onde você explica o que deseja adicionar e por quê, e podemos conversar sobre isso primeiro.

## 🎥 Demonstração

![Demonstração](https://github.com/user-attachments/assets/86b61223-e568-4152-9e5e-d572b2b1385b)

## 👨‍🔧 Como instalar

### Instalar `fish-ai`

Certifique-se de que `git` e ou [`uv`](https://github.com/astral-sh/uv), ou uma versão suportada do Python junto com `pip` e `venv` esteja instalada. Em seguida, pegue o plugin usando [`fisher`](https://github.com/jorgebucaran/fisher):

```shell
fisher install realiserad/fish-ai
```

### Criar uma configuração

Crie um arquivo de configuração `$XDG_CONFIG_HOME/fish-ai.ini` (use `~/.config/fish-ai.ini` se `$XDG_CONFIG_HOME` não estiver definido) onde você especifica qual LLM `fish-ai` deve usar. Se você não tiver certeza, use os Modelos do GitHub.

#### Anthropic

Para usar [Anthropic](https://www.anthropic.com):

```ini
[anthropic]
provider = anthropic
api_key = <sua chave API>
model = claude-sonnet-4-6
```

#### Azure OpenAI

Para usar [Azure OpenAI](https://azure.microsoft.com/en-us/products/ai-services/openai-service):

```ini
[fish-ai]
configuration = azure

[azure]
provider = azure
server = https://<sua instância>.openai.azure.com
model = <seu nome de implementação>
api_key = <sua chave API>
```

#### Bedrock

[AWS Bedrock](https://aws.amazon.com/bedrock) fornece LLMs hospedados pela AWS. Eles podem ser acessados através do gateway Mantle ou da API Converse.

Se nenhuma `api_key` estiver configurada, um token de curto prazo é gerado automaticamente a partir de suas [credenciais da AWS](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-authentication.html). Você também pode especificar uma `api_key` diretamente se preferir usar uma [chave API Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/api-keys.html).

Use `aws_profile` para selecionar um perfil nomeado de sua configuração AWS. Se omitido, a cadeia de credenciais padrão é utilizada.

Os IDs de modelo disponíveis estão listados na [documentação do Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/model-cards.html).

##### API Converse

Para usar a [API Converse](https://docs.aws.amazon.com/bedrock/latest/userguide/converse-api.html):

```ini
[fish-ai]
configuration = aws-converse

[aws-converse]
provider = bedrock
bedrock_api = converse
model = anthropic.claude-haiku-4-5-20251001-v1:0
aws_region = us-east-1
aws_profile = default
```

É necessária a permissão `bedrock:InvokeModel`.

##### Gateway Mantle

Para usar o [gateway Mantle](https://docs.aws.amazon.com/bedrock/latest/userguide/bedrock-mantle.html):

```ini
[fish-ai]
configuration = aws-mantle

[aws-mantle]
provider = bedrock
model = anthropic.claude-haiku-4-5
aws_region = us-east-1
aws_profile = default
```

É necessária a permissão `bedrock-mantle:CreateInference`.

#### Cohere

Para usar [Cohere](https://cohere.com):

```ini
[cohere]
provider = cohere
api_key = <sua chave API>
model = command-a-03-2025
```

#### DeepSeek

Para usar [DeepSeek](https://www.deepseek.com):

```ini
[deepseek]
provider = deepseek
api_key = <sua chave API>
model = deepseek-chat
```

#### Modelos do GitHub

Para usar [Modelos do GitHub](https://github.com/marketplace/models):

```ini
[fish-ai]
configuration = github

[github]
provider = self-hosted
server = https://models.github.ai/inference
api_key = <cole aqui seu PAT do GitHub>
model = gpt-4o-mini
```

Você pode criar um token de acesso pessoal (PAT) [aqui](https://github.com/settings/tokens). O PAT não requer permissões.

#### Google

Para usar [Gemini](https://ai.google.com) do Google:

```ini
[google]
provider = google
api_key = <sua chave API>
model = gemini-3.1-pro-preview
```

#### Groq

Para usar [Groq](https://groq.com):

```ini
[groq]
provider = groq
api_key = <sua chave API>
```

#### OpenAI

Para usar [OpenAI](https://platform.openai.com):

```ini
[fish-ai]
configuration = openai

[openai]
provider = openai
model = gpt-4o
api_key = <sua chave API>
organization = <sua organização>
```

#### OpenRouter

Para usar [OpenRouter](https://openrouter.ai):

```ini
[fish-ai]
configuration = openrouter

[openrouter]
provider = self-hosted
server = https://openrouter.ai/api/v1
model = google/gemini-3-flash-preview
api_key = <sua chave API>
extra_body = {"reasoning": {"effort": "minimal", "exclude": true}}
```

#### Auto-hospedado

Para usar um LLM auto-hospedado (atrás de uma API compatível com OpenAI):

```ini
[fish-ai]
configuration = self-hosted

[self-hosted]
provider = self-hosted
server = https://<seu servidor>:<porta>/v1
model = <seu modelo>
api_key = <sua chave API>
```

Se você estiver auto-hospedando, minha recomendação é usar [Ollama](https://github.com/ollama/ollama) com [Llama 3.3 70B](https://ollama.com/library/llama3.3). Uma configuração prática rodando em `localhost` poderia então ter a seguinte aparência:

```ini
[fish-ai]
configuration = local-llama

[local-llama]
provider = self-hosted
model = llama3.3
server = http://localhost:11434/v1
```

Modelos disponíveis estão listados [aqui](https://openrouter.ai/models).

### Coloque a chave API no seu cofre de senhas

Em vez de colocar a chave API no arquivo de configuração, você pode deixar o `fish-ai` carregá-la do seu cofre de senhas. Para salvar uma nova chave API ou transferir uma chave API existente para o seu cofre de senhas, execute `fish_ai_put_api_key`.

## 🙉 Como usar

### Transformar comentários em comandos e vice-versa

Digite um comentário (qualquer coisa que comece com `#`) e pressione **Ctrl + P** para transformá-lo em um comando de shell! Note que se seu comentário for muito breve ou vago, o LLM pode decidir melhorar o comentário ao invés de fornecer um comando de shell. Você precisará pressionar **Ctrl + P** novamente.

Você também pode executar na reversa. Digite um comando e pressione **Ctrl + P** para transformá-lo em um comentário explicando o que o comando faz.

### Autocompletar comandos

Comece a digitar seu comando ou comentário e pressione **Ctrl + Space** para exibir uma lista de autocompletes em [`fzf`](https://github.com/junegunn/fzf) (ele está embutido no plugin, não é necessário instalá-lo separadamente).

Para refiná-los, digite algumas instruções e pressione **Ctrl + P** dentro do `fzf`.

### Sugerir correções

Se um comando falhar, você pode imediatamente pressionar **Ctrl + Space** no prompt de comando para deixar que o `fish-ai` sugira uma correção!

## 🤸 Opções adicionais

Você pode ajustar o comportamento do `fish-ai` colocando opções adicionais no seu arquivo de configuração `fish-ai.ini`.

### Alterar os mapeamentos de teclas padrão

Por padrão, o `fish-ai` é vinculado a **Ctrl + P** e **Ctrl + Space**. Você pode querer mudar isso se houver interferência com quaisquer mapeamentos de teclas existentes no seu sistema.

Para mudar os mapeamentos de teclas, defina `keymap_1` (padrão é **Ctrl + P**) e `keymap_2` (padrão é **Ctrl + Space**) para a sequência de escape do mapeamento de tecla que você deseja usar.

Para obter a sequência de escape correta do mapeamento de teclas, use [`fish_key_reader`](https://fishshell.com/docs/current/cmds/fish_key_reader.html).

Por exemplo, se você tiver a seguinte saída do `fish_key_reader`:

```shell
$ fish_key_reader
Pressione uma tecla:
bind ctrl-p 'faça algo'
$ fish_key_reader
Pressione uma tecla:
bind ctrl-space 'faça algo'
```

Então coloque o seguinte no seu arquivo de configuração:

```ini
[fish-ai]
keymap_1 = 'ctrl-p'
keymap_2 = 'ctrl-space'
```

Reinicie o shell para as mudanças terem efeito.

### Explicar em uma linguagem diferente

Para explicar comandos de shell em uma linguagem diferente, defina a opção `language` para o nome da linguagem. Por exemplo:

```ini
[fish-ai]
language = Sueco
```

Isso só funcionará bem se o LLM que você está usando foi treinado em um conjunto de dados com a linguagem escolhida.

### Número de autocompletes

Para mudar o número de autocompletes sugeridos pelo LLM ao pressionar **Ctrl + Space**, defina a opção `completions`. O valor padrão é `5`.

Aqui está um exemplo de como você pode aumentar o número de autocompletes para `10`:

```ini
[fish-ai]
completions = 10
```

Para mudar o número de autocompletes refinados sugeridos pelo LLM ao pressionar **Ctrl + P** no `fzf`, defina a opção `refined_completions`. O valor padrão é `3`.

```ini
[fish-ai]
refined_completions = 5
```

### Personalizar autocompletes usando o histórico de comandos

Você pode personalizar os autocompletes sugeridos pelo LLM enviando um trecho do seu histórico de comandos.

Para habilitá-lo, especifique o número máximo de comandos do histórico a serem enviados ao LLM usando a opção `history_size`. O valor padrão é `0` (não envia nenhum histórico de comandos).

```ini
[fish-ai]
history_size = 5
```

Se você habilitar esta opção, considere o uso de [`sponge`](https://github.com/meaningful-ooo/sponge) para remover automaticamente comandos quebrados do seu histórico de comandos.

### Visualizar pipes

Para enviar a saída de um pipe ao LLM ao completar um comando, use a opção `preview_pipe`.

```ini
[fish-ai]
preview_pipe = True
```

Isso enviará a saída do pipe mais longo consecutivo após o último parêntese não finalizado antes do cursor. Por exemplo, se você autocompletar `az vm list | jq`, a saída de `az vm list` será enviada ao LLM.

Esse comportamento está desabilitado por padrão, pois pode desacelerar o processo de autocompletar e levar a comandos sendo executados duas vezes.

### Configurar o indicador de progresso

Você pode mudar o indicador de progresso (o padrão é ⏳) mostrado quando o plugin está esperando por uma resposta do LLM.

Para mudar o padrão, defina a opção `progress_indicator` para zero ou mais caracteres.

```ini
[fish-ai]
progress_indicator = wait...
```

### Usar cabeçalhos personalizados

Você pode enviar cabeçalhos HTTP personalizados usando a opção `headers`. Especifique um ou mais cabeçalhos usando pares `Chave: Valor` separados por vírgula. Por exemplo:

```ini
[fish-ai]
headers = Header-1: value1, Header-2: value2
```

## 🎭 Alternar entre contextos

Você pode alternar entre diferentes seções na configuração usando o comando `fish_ai_switch_context`.

## 🐾 Privacidade de dados

Ao usar o plugin, o `fish-ai` envia o nome do seu sistema operacional e o buffer de comando para o LLM.

Quando você codifica ou completa um comando, ele também envia o conteúdo de quaisquer arquivos que você mencionar (desde que o arquivo seja legível), e quando você explica ou completa um comando, a saída de `<comando> --help` é fornecida ao LLM como referência.

`fish-ai` também pode enviar um trecho do seu histórico de comandos quando completa um comando. Isso está desabilitado por padrão.

Finalmente, para corrigir o comando anterior, o buffer de comandos anterior, juntamente com qualquer saída do terminal e o código de saída correspondente, é enviado ao LLM.

Se você está preocupado com a privacidade dos dados, deve usar um LLM auto-hospedado. Quando hospedado localmente, nenhum dado sai da sua máquina.

### Redação de informações sensíveis

O plugin tenta redigir informações sensíveis do prompt antes de enviá-lo ao LLM. Informações sensíveis são substituídas pelo marcador `<REDACTED>`.

As seguintes informações são redigidas:

- Senhas e chaves API fornecidas como argumentos de linha de comando
- Chaves privadas codificadas PEM armazenadas em arquivos
- Tokens Bearer, fornecidos para, por exemplo, cURL

Se você confia no provedor do LLM (por exemplo, porque está hospedando localmente), pode desabilitar a redação usando a opção `redact = False`.
