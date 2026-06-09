import pandas as pd
import io
from database import get_session, Nota, Aluno, Prova, Questao
import json


def exportar_notas_excel(prova_id: int) -> bytes:
    """
    Gera um arquivo Excel com as notas dos alunos de uma prova.
    Retorna bytes prontos para download.
    """
    session = get_session()
    try:
        prova = session.query(Prova).filter_by(id=prova_id).first()
        notas = (
            session.query(Nota, Aluno)
            .join(Aluno, Nota.aluno_id == Aluno.id)
            .filter(Nota.prova_id == prova_id)
            .all()
        )
        questoes = (
            session.query(Questao)
            .filter_by(prova_id=prova_id)
            .order_by(Questao.numero)
            .all()
        )

        # Planilha principal: resumo de notas
        dados_resumo = []
        for nota, aluno in notas:
            dados_resumo.append({
                "Matrícula": aluno.matricula,
                "Nome do Aluno": aluno.nome,
                "Nota Final": nota.pontuacao,
                "Situação": "Aprovado" if nota.pontuacao >= 6.0 else "Reprovado",
            })

        df_resumo = pd.DataFrame(dados_resumo).sort_values("Nome do Aluno")

        # Planilha de detalhes: resposta por questão
        dados_detalhe = []
        for nota, aluno in notas:
            linha = {"Matrícula": aluno.matricula, "Nome": aluno.nome}
            respostas = json.loads(nota.respostas_json) if nota.respostas_json else {}
            for q in questoes:
                detalhe = respostas.get(str(q.numero), {})
                if isinstance(detalhe, dict):
                    resp = detalhe.get("resposta_aluno", "-")
                    acertou = detalhe.get("acertou", False)
                    linha[f"Q{q.numero:02d}"] = f"{resp or '-'} {'✓' if acertou else '✗'}"
                else:
                    linha[f"Q{q.numero:02d}"] = str(detalhe) if detalhe else "-"
            linha["Nota"] = nota.pontuacao
            dados_detalhe.append(linha)

        df_detalhe = pd.DataFrame(dados_detalhe).sort_values("Nome")

        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df_resumo.to_excel(writer, index=False, sheet_name="Notas Finais")
            df_detalhe.to_excel(writer, index=False, sheet_name="Detalhes por Questão")

            # Auto-ajuste das colunas
            for sheet_name in writer.sheets:
                ws = writer.sheets[sheet_name]
                for col in ws.columns:
                    max_len = max(len(str(cell.value or "")) for cell in col)
                    ws.column_dimensions[col[0].column_letter].width = min(max_len + 4, 40)

        buffer.seek(0)
        return buffer.read()
    finally:
        session.close()
