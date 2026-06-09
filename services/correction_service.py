import json
from database import get_session, Nota, Questao


def corrigir_prova(
    respostas_aluno: dict,
    gabarito: dict[str, str],
    pesos: dict[str, float]
) -> tuple[float, dict]:
    """
    Compara as respostas do aluno com o gabarito oficial.
    Retorna (nota_final, detalhes_por_questao).

    respostas_aluno: {"1": "A", "2": "C", ...}  (pode ter None para não marcadas)
    gabarito:        {"1": "B", "2": "C", ...}
    pesos:           {"1": 0.5, "2": 1.0, ...}
    """
    nota = 0.0
    detalhes = {}

    for num_str, correta in gabarito.items():
        resposta = respostas_aluno.get(num_str)
        peso = pesos.get(num_str, 0.0)
        acertou = resposta is not None and resposta.upper() == correta.upper()

        if acertou:
            nota += peso

        detalhes[num_str] = {
            "resposta_aluno": resposta,
            "alternativa_correta": correta,
            "acertou": acertou,
            "peso": peso,
            "pontos_obtidos": peso if acertou else 0.0,
        }

    return round(nota, 2), detalhes


def salvar_nota(aluno_id: int, prova_id: int, pontuacao: float, respostas: dict):
    """Salva ou atualiza a nota do aluno no banco de dados."""
    session = get_session()
    try:
        nota_existente = session.query(Nota).filter_by(
            aluno_id=aluno_id, prova_id=prova_id
        ).first()

        if nota_existente:
            nota_existente.pontuacao = pontuacao
            nota_existente.respostas_json = json.dumps(respostas)
        else:
            nova_nota = Nota(
                aluno_id=aluno_id,
                prova_id=prova_id,
                pontuacao=pontuacao,
                respostas_json=json.dumps(respostas),
            )
            session.add(nova_nota)

        session.commit()
    finally:
        session.close()


def buscar_gabarito_e_pesos(prova_id: int) -> tuple[dict, dict]:
    """Retorna (gabarito, pesos) como dicionários com chaves string."""
    session = get_session()
    try:
        questoes = session.query(Questao).filter_by(prova_id=prova_id).order_by(Questao.numero).all()
        gabarito = {str(q.numero): q.alternativa_correta for q in questoes}
        pesos = {str(q.numero): q.peso for q in questoes}
        return gabarito, pesos
    finally:
        session.close()
