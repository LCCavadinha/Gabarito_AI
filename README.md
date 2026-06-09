# Gabarito IA

Sistema de correção automática de provas escolares com múltipla escolha usando Inteligência Artificial (Google Gemini Vision) e QR Code para identificação de alunos.

---

## Sumário

1. [Visão Geral](#visão-geral)
2. [Fluxo Completo](#fluxo-completo)
3. [Pré-requisitos](#pré-requisitos)
4. [Instalação passo a passo](#instalação-passo-a-passo)
5. [Como obter a API Key do Gemini](#como-obter-a-api-key-do-gemini)
6. [Configuração do arquivo .env](#configuração-do-arquivo-env)
7. [Como rodar](#como-rodar)
8. [Estrutura de arquivos](#estrutura-de-arquivos)
9. [Bibliotecas utilizadas](#bibliotecas-utilizadas)
10. [Banco de dados](#banco-de-dados)
11. [Como o ZIP de PDFs é gerado](#como-o-zip-de-pdfs-é-gerado)
12. [Solução de problemas comuns](#solução-de-problemas-comuns)

---

## Visão Geral

O Gabarito IA automatiza o processo de correção de provas escolares de múltipla escolha (A a E). O professor cadastra o gabarito correto, o sistema gera folhas de resposta personalizadas para cada aluno com QR Code único, e após a prova, fotografa as folhas preenchidas e faz o upload. O sistema identifica o aluno pelo QR Code, lê as bolhas marcadas com IA e calcula a nota automaticamente, exportando um relatório em Excel.

> **Importante:** a IA não corrige a prova. Ela faz apenas uma tarefa: ler visualmente quais bolhas estão marcadas na foto. A correção em si é lógica Python pura (comparação de respostas com o gabarito).

---

## Fluxo Completo

```
1. Professor cadastra turma e alunos
         ↓
2. Professor cria a prova, define questões com pesos (soma = 10) e o gabarito correto
         ↓
3. Sistema gera um PDF por aluno com QR Code único (contém ID do aluno e da prova)
         ↓
4. Professor imprime e distribui as folhas antes da prova
         ↓
5. Aluno preenche as bolhas e assina a folha
         ↓
6. Professor fotografa as folhas preenchidas e faz upload em lote
         ↓
7. Sistema processa cada foto:
   → Lê o QR Code (identifica o aluno)
   → Envia a imagem para o Gemini Vision (lê as bolhas)
   → Compara com o gabarito cadastrado
   → Calcula a nota ponderada pelos pesos
   → Salva no banco de dados
         ↓
8. Professor visualiza o relatório e exporta o Excel com matrícula e nota de cada aluno
```

---

## Pré-requisitos

- **Python 3.10 ou superior**
- **pip** (gerenciador de pacotes Python)
- **Git** (opcional, para clonar o projeto)
- **Dependência de sistema para leitura de QR Code:**

### Linux / Ubuntu
```bash
sudo apt-get update
sudo apt-get install libzbar0
```

### macOS
```bash
brew install zbar
```

### Windows
Não é necessária instalação adicional. O projeto usa `cv2.QRCodeDetector` do OpenCV, que funciona nativamente no Windows sem DLL externa.

---

## Instalação passo a passo

### 1. Acesse a pasta do projeto
```bash
cd gabarito_ia
```

### 2. Crie um ambiente virtual
```bash
# Linux / macOS
python -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

> Você saberá que o ambiente virtual está ativo quando o terminal exibir `(venv)` no início da linha.

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Crie o arquivo `.env` a partir do exemplo
```bash
# Linux / macOS
cp .env_example .env

# Windows
copy .env_example .env
```

Abra o arquivo `.env` e substitua `your_api_key_here` pela sua chave real:
```
GEMINI_API_KEY=AIzaSuaChaveAqui
```

### 5. Confirme que o `.gitignore` está correto

O projeto já inclui um `.gitignore`. Confirme que ele contém no mínimo:
```
.env
venv/
__pycache__/
*.pyc
gabarito.db
```

---

## Como obter a API Key do Gemini

A API Key do Gemini é **gratuita** para uso em desenvolvimento, com limite de 1.500 requisições por dia.

### Passo a passo

1. Acesse [aistudio.google.com](https://aistudio.google.com)
2. Faça login com sua conta Google
3. No menu superior, clique em **"Get API key"**
4. Clique em **"Create API key in new project"**
   > ⚠️ Sempre escolha **"in new project"**. Criar em projeto existente pode resultar em cota zerada.
5. Copie a chave gerada (começa com `AIza...`)
6. Cole no arquivo `.env`:
   ```
   GEMINI_API_KEY=AIzaSuaChaveAqui
   ```

### Erros comuns relacionados à API Key

| Erro | Causa | Solução |
|------|-------|---------|
| `400 API key expired` | Chave inválida ou deletada | Gerar nova chave no AI Studio |
| `429 quota exceeded (limit: 0)` | Projeto sem cota gratuita habilitada | Criar nova chave em **novo projeto** no AI Studio |
| `429 quota exceeded` | Limite de 15 req/min atingido | Aguardar 1 minuto e tentar novamente |
| `404 model not found` | Nome do modelo desatualizado | Verificar se está usando `gemini-1.5-flash-latest` |

### Monitorar uso
Acesse [ai.dev/rate-limit](https://ai.dev/rate-limit) para verificar quantas requisições você já usou no dia.

---

## Configuração do arquivo .env

O arquivo `.env` deve ficar na raiz do projeto, no mesmo nível do `app.py`:

```
gabarito_ia/
├── .env          ← aqui (não vai para o GitHub)
├── .env_example  ← template público (vai para o GitHub)
├── app.py
├── database.py
└── ...
```

Conteúdo do `.env`:
```env
GEMINI_API_KEY=AIzaSuaChaveAqui
```

> O arquivo `.env` **nunca deve ser enviado para o GitHub**. O `.env_example` é o template público que vai para o repositório no lugar dele.

---

## Como rodar

Com o ambiente virtual ativado e o `.env` configurado:

```bash
streamlit run app.py
```

O navegador abrirá automaticamente em `http://localhost:8501`.

Se não abrir automaticamente, acesse manualmente no navegador.

### Para parar o servidor
```bash
Ctrl + C
```

### Rodando em uma porta diferente
```bash
streamlit run app.py --server.port 8502
```

---

## Estrutura de arquivos

```
gabarito_ia/
├── app.py                        # Página inicial: carrega .env, inicializa banco, exibe chave API
├── database.py                   # Modelos do banco de dados (SQLAlchemy + SQLite)
├── requirements.txt              # Dependências Python
├── .env                          # Chave API Gemini (não enviar para o GitHub)
├── .env_example                  # Template público da configuração (vai para o GitHub)
├── .gitignore                    # Arquivos ignorados pelo Git
├── gabarito.db                   # Banco de dados SQLite (criado automaticamente)
│
├── services/
│   ├── __init__.py               # Arquivo vazio (necessário para o Python reconhecer como módulo)
│   ├── gemini_service.py         # Comunicação com a API Gemini Vision
│   ├── qr_service.py             # Geração e leitura de QR Code
│   ├── pdf_service.py            # Geração da folha de gabarito em PDF (design IAvalia)
│   ├── correction_service.py     # Lógica de correção e persistência de notas
│   └── excel_service.py          # Exportação do relatório em Excel
│
└── pages/
    ├── 1_Cadastros.py            # Cadastro de professores, turmas e alunos
    ├── 2_Provas.py               # Criar provas, questões, gabarito e gerar PDFs
    ├── 3_Correcao.py             # Upload de fotos e correção automática
    └── 4_Relatorio.py            # Visualização de notas e exportação Excel
```

---

## Bibliotecas utilizadas

### `streamlit >= 1.32.0`
**O que faz:** framework Python para criar interfaces web interativas sem HTML, CSS ou JavaScript.

**Por que foi escolhida:** o objetivo era ter um protótipo funcional rapidamente, com formulários, tabelas, upload de arquivos e download de relatórios, tudo em Python puro. O Streamlit elimina a necessidade de um backend separado e um frontend separado.

**Onde é usado:** em todos os arquivos `app.py` e `pages/`.

---

### `sqlalchemy >= 2.0.0`
**O que faz:** ORM (Object-Relational Mapper) que permite trabalhar com banco de dados usando classes Python em vez de SQL puro.

**Por que foi escolhida:** torna o código mais legível, protege contra SQL injection e permite definir as tabelas como classes Python com relacionamentos declarativos.

**Onde é usado:** `database.py` (definição dos modelos), e em todos os arquivos de página para queries.

> **Atenção:** o SQLAlchemy usa lazy loading por padrão. Isso significa que relacionamentos (`turma.alunos`, `prova.questoes`) só são carregados quando acessados. Se a sessão já foi fechada nesse momento, ocorre `DetachedInstanceError`. A solução é sempre extrair os dados necessários para dicionários **antes** de fechar a sessão.

---

### `reportlab >= 4.0.0`
**O que faz:** biblioteca para geração programática de PDFs. Permite desenhar textos, formas, imagens e tabelas em coordenadas precisas.

**Por que foi escolhida:** o sistema precisa gerar folhas de gabarito padronizadas com layout preciso: QR Code posicionado no canto, grid de bolhas A-E, dados do aluno pré-impressos e design baseado na identidade visual da IAvalia.

**Onde é usado:** `services/pdf_service.py`.

---

### `qrcode[pil] >= 7.4.0`
**O que faz:** gera imagens de QR Code a partir de dados estruturados.

**Por que foi escolhida:** cada folha de gabarito precisa ter um QR Code único por aluno por prova. O QR Code contém um JSON com `aluno_id`, `matricula` e `prova_id`, permitindo identificação automática sem depender de leitura de texto manuscrito.

**Onde é usado:** `services/qr_service.py` e `services/pdf_service.py`.

```python
# Dados que ficam gravados no QR Code
{"aluno_id": 42, "matricula": "20231045", "prova_id": 7}
```

---

### `opencv-python-headless >= 4.8.0`
**O que faz:** biblioteca de visão computacional. Processa imagens, converte formatos, aplica filtros e detecta/decodifica QR Codes.

**Por que foi escolhida (headless):** a versão `headless` não depende de interface gráfica (sem janelas), adequada para servidores e ambientes sem display. Substituiu o `pyzbar` que exigia uma DLL externa (`libzbar-64.dll`) no Windows.

**O que faz no projeto:** tenta ler o QR Code da foto com 5 estratégias progressivas: imagem original, escala de cinza, upscaling 2x, binarização por threshold de Otsu, e recorte ampliado do canto onde o QR Code fica.

**Onde é usado:** `services/qr_service.py`.

---

### `google-generativeai >= 0.5.0`
**O que faz:** SDK oficial do Google para acessar os modelos Gemini via API. O Gemini Vision recebe imagens e responde perguntas sobre elas.

**Por que foi escolhida:** ler bolhas preenchidas em fotos com iluminação irregular, ângulos variados e qualidade de câmera imprevisível seria extremamente difícil com algoritmos clássicos de visão computacional. O Gemini Vision analisa a imagem e retorna um JSON com as alternativas marcadas.

**Modelo utilizado:** `gemini-1.5-flash-latest` (plano gratuito: 1.500 requisições/dia).

**Onde é usado:** `services/gemini_service.py`.

```python
# O que o Gemini retorna para cada foto
{"1": "A", "2": "C", "3": "B", "4": null, ...}
# null = questão sem marcação clara ou com marcação dupla
```

---

### `pandas >= 2.0.0`
**O que faz:** biblioteca padrão de manipulação de dados em Python. Cria DataFrames, ordena, filtra e exporta dados tabulares.

**Por que foi escolhida:** transforma a lista de notas em um DataFrame organizado e exporta diretamente para `.xlsx` com duas abas (resumo e detalhes por questão) com auto-ajuste de colunas.

**Onde é usado:** `services/excel_service.py` e `pages/3_Correcao.py`, `pages/4_Relatorio.py`.

---

### `openpyxl >= 3.1.0`
**O que faz:** motor que o Pandas usa para ler e escrever arquivos `.xlsx` (Excel moderno).

**Por que foi escolhida:** é a engine padrão e mais estável do Pandas para arquivos Excel. Permite auto-ajuste de largura de colunas.

**Onde é usado:** indiretamente via Pandas em `services/excel_service.py`.

---

### `pillow >= 10.0.0`
**O que faz:** biblioteca de manipulação de imagens em Python. Abre, converte e transforma imagens em múltiplos formatos.

**Por que foi escolhida:** o Streamlit entrega arquivos de upload como bytes. O Gemini precisa de imagem PIL. O OpenCV precisa de array numpy. O Pillow faz a ponte entre todos esses formatos.

**Onde é usado:** `pages/3_Correcao.py` (abre o upload), `services/qr_service.py` (converte para OpenCV), `services/gemini_service.py` (envia para o Gemini).

---

### `python-dotenv >= 1.0.0`
**O que faz:** carrega variáveis de ambiente de um arquivo `.env` para o processo Python.

**Por que foi escolhida:** a API Key do Gemini não pode ficar hardcoded no código nem ser enviada ao GitHub. O `.env` mantém a chave fora do controle de versão e o `python-dotenv` a carrega automaticamente na inicialização.

**Onde é usado:** `app.py`.

```python
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY", "")
```

---

### `numpy >= 1.24.0`
**O que faz:** biblioteca de computação numérica. Oferece arrays multidimensionais de alta performance.

**Por que foi escolhida:** o OpenCV trabalha com arrays NumPy (formato BGR). A conversão de imagem PIL para formato OpenCV exige `numpy.array()`.

**Onde é usado:** `services/qr_service.py`.

```python
img_array = np.array(imagem_pil.convert("RGB"))
img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
```

---

### `zipfile` (biblioteca padrão do Python)
**O que faz:** cria e manipula arquivos ZIP. Faz parte da biblioteca padrão do Python, ou seja, **não precisa ser instalada** e não aparece no `requirements.txt`.

**Por que foi escolhida:** o professor precisa baixar um PDF por aluno de uma só vez. Em vez de fazer N downloads separados, o sistema empacota todos os PDFs em um único arquivo ZIP para download único.

**Onde é usado:** `pages/2_Provas.py`.

---

## Banco de dados

O banco de dados é um arquivo SQLite criado automaticamente em `gabarito.db` na primeira execução. Não é necessária nenhuma configuração adicional.

### Modelos

| Tabela | Campos | Relacionamento |
|--------|--------|----------------|
| `professores` | id, nome, email (único) | 1 professor → N turmas |
| `turmas` | id, nome, professor_id | 1 turma → N alunos, N provas |
| `alunos` | id, nome, matricula (única), turma_id | 1 aluno → N notas |
| `provas` | id, titulo, turma_id | 1 prova → N questões, N notas |
| `questoes` | id, numero, peso, alternativa_correta, prova_id | Único: (prova_id, numero) |
| `notas` | id, pontuacao, respostas_json, aluno_id, prova_id | Único: (aluno_id, prova_id) |

### Regra de negócio importante
A soma dos pesos de todas as questões de uma prova **deve ser exatamente 10**. O sistema valida isso na interface de cadastro e só permite gerar os PDFs quando a soma estiver correta.

---

## Como o ZIP de PDFs é gerado

Quando o professor clica em **"Gerar PDFs de todos os alunos"** na página de Provas, o sistema gera um arquivo ZIP contendo um PDF por aluno. Todo o processo acontece **em memória RAM**, sem salvar nenhum arquivo temporário no disco.

### O que acontece internamente

```python
import zipfile
import io

# 1. Gera os bytes de cada PDF individualmente
pdfs = gerar_todos_pdfs(alunos, prova, questoes)
# pdfs = {"456": b"...bytes do PDF da Sheila...", "778": b"...bytes do PDF da Sandy...", ...}

# 2. Cria um buffer em memória para o ZIP (sem salvar no disco)
zip_buffer = io.BytesIO()

# 3. Abre o buffer como um arquivo ZIP com compressão DEFLATED
with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
    for matricula, pdf_bytes in pdfs.items():
        # 4. Adiciona cada PDF ao ZIP com nome baseado na matrícula
        zf.writestr(f"gabarito_{matricula}.pdf", pdf_bytes)

# 5. Volta o cursor para o início do buffer para leitura
zip_buffer.seek(0)

# 6. Streamlit serve o buffer diretamente para download no navegador
st.download_button(
    label="Baixar todos os PDFs (ZIP)",
    data=zip_buffer.read(),
    file_name=f"gabaritos_{prova.titulo}.zip",
    mime="application/zip",
)
```

### Por que tudo fica em memória

O uso de `io.BytesIO()` cria um buffer em memória que se comporta como um arquivo, mas nunca toca o disco. Isso tem três vantagens:

- **Sem arquivos temporários:** nada é gravado no servidor, evitando acúmulo de arquivos
- **Mais rápido:** operações em RAM são muito mais rápidas que I/O em disco
- **Mais limpo:** ao finalizar o processo, a memória é liberada automaticamente pelo Python

### Estrutura do ZIP gerado

```
gabaritos_Redes_de_Computadores.zip
├── gabarito_456.pdf    ← folha da Sheila (matrícula 456)
├── gabarito_556.pdf    ← folha do Vytor (matrícula 556)
└── gabarito_778.pdf    ← folha da Sandy (matrícula 778)
```

Cada PDF contém o nome, matrícula, QR Code único e o grid de bolhas para aquele aluno específico.

---

## Solução de problemas comuns

### `DetachedInstanceError` ao acessar uma página
**Causa:** sessão do SQLAlchemy fechada antes de acessar relacionamentos.

**Solução:** extraia todos os dados necessários para dicionários dentro da sessão antes de fechá-la:
```python
# ERRADO
session = get_session()
turmas = session.query(Turma).all()
session.close()
for t in turmas:
    print(t.alunos)  # erro aqui

# CORRETO
session = get_session()
turmas_data = [{"nome": t.nome, "alunos": len(t.alunos)} for t in session.query(Turma).all()]
session.close()
for t in turmas_data:
    print(t["alunos"])  # seguro
```

---

### QR Code não encontrado
**Causas possíveis:**
- Foto desfocada ou com iluminação ruim
- QR Code cortado ou dobrado
- Foto tirada de muito longe

**Soluções:**
- Fotografar com boa iluminação, sem reflexo
- O QR Code deve ocupar pelo menos 15% da imagem
- Fotografar em orientação retrato (vertical), com a folha preenchendo o quadro

---

### `libzbar-64.dll not found` (Windows)
**Causa:** versão antiga do projeto usava `pyzbar`, que exige DLL nativa no Windows.

**Solução:** certifique-se de que o arquivo `services/qr_service.py` usa `cv2.QRCodeDetector` em vez de `pyzbar`. Se ainda estiver usando `pyzbar`, substitua pela implementação com OpenCV.

---

### `400 API key expired` ou `429 quota exceeded`
Veja a seção [Erros comuns relacionados à API Key](#erros-comuns-relacionados-à-api-key).

---

### Excel não aparece para download
**Causa:** o padrão `st.button` + `st.spinner` + `st.download_button` no Streamlit faz o botão de download sumir após re-renderização.

**Solução:** em `pages/4_Relatorio.py`, o `st.download_button` deve estar diretamente na página, sem um `st.button` intermediário:
```python
excel_bytes = exportar_notas_excel(prova_id)
st.download_button(
    label="Baixar Excel",
    data=excel_bytes,
    file_name="notas.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)
```

---

### Streamlit não recarrega o `.env` após alterar a chave
**Solução:** pare o servidor (`Ctrl+C`) e reinicie:
```bash
streamlit run app.py
```
O `.env` é carregado apenas na inicialização do processo.

---

## Observações finais

- O banco de dados `gabarito.db` é criado automaticamente na primeira execução
- Para reiniciar o banco do zero, delete o arquivo `gabarito.db` e reinicie o servidor
- O sistema suporta provas com 10 a 20 questões e pesos variáveis, desde que a soma seja 10
- Fotos em JPEG e PNG são aceitas no upload
- O relatório Excel gerado contém duas abas: **Notas Finais** (resumo) e **Detalhes por Questão** (resposta de cada aluno por questão)