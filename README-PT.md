![Badge com o tempo gasto](https://img.shields.io/endpoint?url=https%3A%2F%2Fgist.githubusercontent.com%2FRealiserad%2Fd3ec7fdeecc35aeeb315b4efba493326%2Fraw%2Ffish-ai-git-estimate.json)
![Badge de popularidade](https://img.shields.io/endpoint?url=https%3A%2F%2Fgist.githubusercontent.com%2FRealiserad%2Fd3ec7fdeecc35aeeb315b4efba493326%2Fraw%2Fpopularity.json)
[![Doar XMR](https://img.shields.io/badge/Donate_XMR-grey?style=for-the-badge&logo=monero)](https://github.com/user-attachments/assets/07a2947f-6e5a-480f-990a-77204933411f)

Ler em [Português 🇧🇷](README-PT.md) ou [English 🇺🇸](README.md).

# Sobre

O `fish-ai` adiciona funcionalidade de IA ao [Fish](https://fishshell.com).
É incrível! Eu o criei para facilitar a minha vida e espero que torne a
sua mais fácil também. Aqui está o argumento de venda completo:

- Ele pode transformar um comentário em um comando de shell e vice-versa, o que significa
menos tempo gasto
lendo manpages, pesquisando no Google e copiando e colando do Stack Overflow. Ótimo
ao trabalhar com `git`, `kubectl`, `curl` e outras ferramentas com muitos
parâmetros e opções.
- Cometeu um erro de digitação? Ele também pode corrigir um comando que falhou (semelhante ao
[`thefuck`](https://github.com/nvbn/thefuck)).
- Não tem certeza do que digitar em seguida ou apenas com preguiça? Deixe a LLM autocompletar
seus comandos com um localizador fuzzy integrado.
- Tudo é feito usando dois atalhos de teclado (configuráveis), sem necessidade de mouse!
- Pode ser conectado à LLM de sua escolha (mesmo uma auto-hospedada!).
- Tudo é de código aberto, razoavelmente fácil de ler e tem
cerca de 2000 linhas de código, o que significa que você mesmo pode auditar o código
em uma tarde.
- Instale e atualize com facilidade usando [`fisher`](https://github.com/jorgebucaran/fisher).
- Testado tanto no macOS quanto nas distribuições Linux mais comuns.
- Não interfere com [`fzf.fish`](https://github.com/PatrickF1/fzf.fish),
[`tide`](https://github.com/IlanCosman/tide) ou qualquer um dos outros plugins
que você já está usando!
- Não envolve o seu shell, instala telemetria ou força você a mudar
para um emulador de terminal proprietário.

Este plugin foi originalmente baseado no [repositório `fish.codex` de Tom Dörr](https://github.com/tom-doerr/codex.fish).
Sem o Tom, este repositório não existiria!

Se você gostar, por favor, adicione uma ⭐.

Correções de bugs são bem-vindas! Considero este projeto amplamente completo em termos de recursos.
Antes de abrir um PR para uma solicitação de recurso, considere abrir uma issue onde
você explica o que deseja adicionar e por quê, e podemos conversar sobre isso primeiro.

## 🎥 Demonstração

![Demonstração](https://github.com/user-attachments/assets/86b61223-e568-4152-9e5e-d572b2b1385b)

## 👨‍🔧 Como instalar

### Instalar o `fish-ai`

Certifique-se de que o `git` e o [`uv`](https://github.com/astral-sh/uv), ou
[uma versão suportada do Python](https://github.com/Realiserad/fish-ai/blob/main/.github/workflows/python-tests.yaml)
junto com o `pip` e `venv` estejam instalados. Em seguida, obtenha o plugin usando
o [`fisher`](https://github.com/jorgebucaran/fisher):

```shell
fisher install realiserad/fish-ai
```

### Criar uma configuração

Crie um arquivo de configuração `$XDG_CONFIG_HOME/fish-ai.ini` (use
`~/.config/fish-ai.ini` se `$XDG_CONFIG_HOME` não estiver definido) onde
você especifica com qual LLM o `fish-ai` deve se comunicar.

#### Anthropic

Para usar a [Anthropic](https://www.anthropic.com):

```ini
[anthropic]
provider = anthropic
api_key = <sua chave de API>
model = claude-sonnet-4-6
```

#### Azure OpenAI

Para usar o [Azure OpenAI](https://azure.microsoft.com/en-us/products/ai-services/openai-service):

```ini
[fish-ai]
configuration = azure

[azure]
provider = azure
server = https://<sua instância>.openai.azure.com
model = <nome do seu deployment>
api_key = <sua chave de API>
```

#### Bedrock

O [AWS Bedrock](https://aws.amazon.com/bedrock) fornece LLMs hospedadas pela AWS. Elas
podem ser acessadas através do gateway Mantle ou da API Converse.

Se nenhuma `api_key` for configurada, um token de curto prazo é gerado
automaticamente a partir das suas
[credenciais da AWS](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-authentication.html).
Você também pode especificar uma `api_key` diretamente se preferir usar uma
[chave de API do Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/api-keys.html).

Use `aws_profile` para selecionar um perfil nomeado da sua configuração da AWS. Se omitido,
a cadeia de credenciais padrão é usada.

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

Isso requer a permissão `bedrock:InvokeModel`.

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

Isso requer a permissão `bedrock-mantle:CreateInference`.

#### Cohere

Para usar a [Cohere](https://cohere.com):

```ini
[cohere]
provider = cohere
api_key = <sua chave de API>
model = command-a-03-2025
```

#### DeepSeek

Para usar o [DeepSeek](https://www.deepseek.com):

```ini
[deepseek]
provider = deepseek
api_key = <sua chave de API>
model = deepseek-chat
```

Você pode criar um token de acesso pessoal (PAT) [aqui](https://github.com/settings/tokens).
O PAT não requer nenhuma permissão.

#### Google

Para usar o [Gemini](https://ai.google.com) do Google:

```ini
[google]
provider = google
api_key = <sua chave de API>
model = gemini-3.1-pro-preview
```

#### Groq

Para usar o [Groq](https://groq.com):

```ini
[groq]
provider = groq
api_key = <sua chave de API>
```

#### OpenAI

Para usar a [OpenAI](https://platform.openai.com):

```ini
[fish-ai]
configuration = openai

[openai]
provider = openai
model = gpt-4o
api_key = <sua chave de API>
organization = <sua organização>
```

#### OpenRouter

Para usar o [OpenRouter](https://openrouter.ai):

```ini
[fish-ai]
configuration = openrouter

[openrouter]
provider = self-hosted
server = https://openrouter.ai/api/v1
model = google/gemini-3-flash-preview
api_key = <sua chave de API>
extra_body = {"reasoning": {"effort": "minimal", "exclude": true}}
```

#### Auto-hospedado

Para usar uma LLM auto-hospedada (atrás de uma API compatível com OpenAI):

```ini
[fish-ai]
configuration = self-hosted

[self-hosted]
provider = self-hosted
server = https://<seu servidor>:<porta>/v1
model = <seu modelo>
api_key = <sua chave de API>
```

Se você estiver auto-hospedando, minha recomendação é usar o
[Ollama](https://github.com/ollama/ollama) com o
[Llama 3.3 70B](https://ollama.com/library/llama3.3). Uma configuração padrão
rodando em `localhost` pode ficar parecida
com isto:

```ini
[fish-ai]
configuration = local-llama

[local-llama]
provider = self-hosted
model = llama3.3
server = http://localhost:11434/v1
```

Os modelos disponíveis estão listados [aqui](https://openrouter.ai/models).

### Colocar a chave de API no seu chaveiro (keyring)

Em vez de colocar a chave de API no arquivo de configuração, você pode permitir que o
`fish-ai` a carregue do seu chaveiro. Para salvar uma nova chave de API ou transferir
uma chave de API existente para o seu chaveiro, execute `fish_ai_put_api_key`.

## 🙉 Como usar

### Transformar comentários em comandos e vice-versa

Digite um comentário (qualquer coisa que comece com `#`) e pressione **Ctrl + P** para transformá-lo
em um comando de shell! Observe que se o seu comentário for muito breve ou vago, a LLM
pode decidir melhorar o comentário em vez de fornecer um comando de shell. Você
precisará pressionar **Ctrl + P** novamente.

Você também pode executar o processo inverso. Digite um comando e pressione **Ctrl + P** para transformá-lo
em um comentário explicando o que o comando faz.

### Autocompletar comandos

Comece a digitar seu comando ou comentário e pressione **Ctrl + Space** para exibir uma lista
de complementos no [`fzf`](https://github.com/junegunn/fzf) (ele vem empacotado
com o plugin, sem necessidade de instalá-lo separadamente).

Para refinar os resultados, digite algumas instruções e pressione **Ctrl + P**
dentro do `fzf`.

### Sugerir correções

Se um comando falhar, você pode pressionar imediatamente **Ctrl + Space** no prompt de comando
para permitir que o `fish-ai` sugira uma correção!

## 🤸 Opções adicionais

Você pode ajustar o comportamento do `fish-ai` adicionando opções extras ao seu
arquivo de configuração `fish-ai.ini`.

### Alterar os atalhos de teclado padrão

Por padrão, o `fish-ai` se associa a **Ctrl + P** e **Ctrl + Space**. Você
pode querer alterar isso se houver interferência com algum atalho de teclado
existente no seu sistema.

Para alterar os atalhos de teclado, defina `keymap_1` (o padrão é **Ctrl + P**)
e `keymap_2` (o padrão é **Ctrl + Space**) para a sequência de escape
do atalho de teclado que você deseja usar.

Para obter a sequência de escape correta do atalho de teclado, use
[`fish_key_reader`](https://fishshell.com/docs/current/cmds/fish_key_reader.html).

Por exemplo, se você obtiver a seguinte saída do `fish_key_reader`:

```shell
$ fish_key_reader
Press a key:
bind ctrl-p 'do something'
$ fish_key_reader
Press a key:
bind ctrl-space 'do something'
```

Em seguida, coloque o seguinte no seu arquivo de configuração:

```ini
[fish-ai]
keymap_1 = 'ctrl-p'
keymap_2 = 'ctrl-space'
```

Reinicie o shell para que as alterações entrem em vigor.

### Explicar em um idioma diferente

Para explicar comandos de shell em um idioma diferente, defina a opção `language`
para o nome do idioma. Por exemplo:

```ini
[fish-ai]
language = Portuguese
```

Isso só funcionará bem se a LLM que você está usando tiver sido treinada em um conjunto de dados
com o idioma escolhido.

### Número de complementos

Para alterar o número de complementos sugeridos pela LLM ao pressionar
**Ctrl + Space**, defina a opção `completions`. O valor padrão é `5`.

Aqui está um exemplo de como você pode aumentar o número de complementos para `10`:

```ini
[fish-ai]
completions = 10
```

Para alterar o número de complementos refinados sugeridos pela LLM ao pressionar
**Ctrl + P** no `fzf`, defina a opção `refined_completions`. O valor padrão
é `3`.

```ini
[fish-ai]
refined_completions = 5
```

### Personalizar complementos usando o histórico de comandos

Você pode personalizar os complementos sugeridos pela LLM enviando
um trecho do seu histórico de comandos.

Para ativá-lo, especifique o número máximo de comandos do histórico
a serem enviados para a LLM usando a opção `history_size`. O valor padrão
é `0` (não enviar nenhum histórico de comandos).

```ini
[fish-ai]
history_size = 5
```

Se você ativar esta opção, considere o uso de [`sponge`](https://github.com/meaningful-ooo/sponge)
para remover automaticamente comandos quebrados do seu histórico de comandos.

### Visualizar pipes (redirecionamentos)

Para enviar a saída de um pipe para a LLM ao completar um comando, use a
opção `preview_pipe`.

```ini
[fish-ai]
preview_pipe = True
```

Isso enviará a saída do pipe consecutivo mais longo após o último
parêntese não fechado antes do cursor. Por exemplo, se você autocompletar
`az vm list | jq`, a saída de `az vm list` será enviada para a LLM.

Este comportamento é desativado por padrão, pois pode desacelerar o processo
de conclusão e fazer com que os comandos sejam executados duas vezes.

### Configurar o indicador de progresso

Você pode alterar o indicador de progresso (o padrão é ⏳) exibido quando o
plugin está aguardando uma resposta da LLM.

Para alterar o padrão, defina a opção `progress_indicator` para zero ou
mais caracteres.

```ini
[fish-ai]
progress_indicator = wait...
```

### Usar cabeçalhos personalizados

Você pode enviar cabeçalhos HTTP personalizados usando a opção `headers`. Especifique um
ou mais cabeçalhos usando pares `Key: Value` separados por vírgula. Por exemplo:

```ini
[fish-ai]
headers = Header-1: value1, Header-2: value2
```

## 🎭 Alternar entre contextos

Você pode alternar entre diferentes seções na configuração usando o
comando `fish_ai_switch_context`.

## 🐾 Privacidade de dados

Ao usar o plugin, o `fish-ai` envia o nome do seu sistema operacional e o
buffer de linha de comando para a LLM.

Quando você codifica ou completa um comando, ele também envia o conteúdo de quaisquer
arquivos mencionados (desde que o arquivo seja legível), e quando você explica
ou completa um comando, a saída de `<command> --help` é fornecida à
LLM para referência.

O `fish-ai` também pode enviar um trecho do seu histórico de comandos
ao completar um comando. Isso é desativado por padrão.

Finalmente, para corrigir o comando anterior, o buffer da linha de comando anterior,
juntamente com qualquer saída de terminal e o código de saída correspondente, é enviado
para a LLM.

Se você se preocupa com a privacidade dos dados, deve usar uma LLM
auto-hospedada. Quando hospedada localmente, nenhum dado sai da sua máquina.

### Ocultação de informações sensíveis (Redaction)

O plugin tenta ocultar informações sensíveis do prompt
antes de enviá-lo para a LLM. Informações sensíveis são substituídas pelo
espaço reservado `<REDACTED>`.

As seguintes informações são ocultadas:

- Senhas e chaves de API fornecidas como argumentos de linha de comando
- Chaves privadas codificadas em PEM armazenadas em arquivos
- Tokens Bearer, fornecidos por exemplo ao cURL

Se você confia no provedor da LLM (por exemplo, porque está hospedando localmente),
você pode desativar a ocultação usando a opção `redact = False`.