import google.generativeai as genai
from PIL import Image
import json
import re


def configurar_gemini(api_key: str):
    genai.configure(api_key=api_key)


def extrair_respostas_da_imagem(imagem_pil: Image.Image, num_questoes: int) -> dict:
    """
    Envia a imagem do gabarito para o Gemini e retorna as respostas identificadas.
    Retorna um dict como: {"1": "A", "2": "C", "3": null, ...}
    """
    model = genai.GenerativeModel("gemini-3-flash-preview")

    prompt = f"""Você está analisando uma folha de gabarito de prova escolar.
A prova tem {num_questoes} questões numeradas de 1 a {num_questoes}.
Cada questão tem 5 alternativas: A, B, C, D, E representadas por círculos/bolhas.
O aluno marcou (preencheu ou assinalou com X) apenas um círculo por questão.

Sua tarefa:
1. Identifique o número de cada questão
2. Identifique qual alternativa está marcada (preenchida/assinalada) em cada questão

Regras obrigatórias de resposta:
- Retorne APENAS um JSON válido, sem texto antes ou depois
- Sem markdown, sem backticks, sem explicações
- Formato exato: {{"1": "A", "2": "C", "3": "B"}}
- Se uma questão não tiver marcação clara ou tiver mais de uma marcação: use null
- As chaves devem ser strings com o número da questão
- Os valores devem ser letras maiúsculas: "A", "B", "C", "D" ou "E"
- Inclua todas as questões de 1 a {num_questoes}"""

    try:
        resposta = model.generate_content([prompt, imagem_pil])
        return _parse_seguro(resposta.text, num_questoes)
    except Exception as e:
        raise RuntimeError(f"Erro ao chamar Gemini: {str(e)}")


def _parse_seguro(texto: str, num_questoes: int) -> dict:
    """Extrai o JSON da resposta mesmo que venha com texto ao redor."""
    match = re.search(r'\{.*?\}', texto, re.DOTALL)
    if not match:
        raise ValueError(f"Gemini não retornou JSON válido. Resposta recebida: {texto[:200]}")

    dados = json.loads(match.group())

    # Garante que todas as questões estão presentes
    for i in range(1, num_questoes + 1):
        if str(i) not in dados:
            dados[str(i)] = None

    return dados
