import streamlit as st
import pandas as pd
import json
from database import init_db, get_session, Prova, Nota, Aluno, Questao
from services.excel_service import exportar_notas_excel

st.set_page_config(page_title="Relatório | Gabarito IA", page_icon="📊", layout="wide")
init_db()

st.title("📊 Relatório de Notas")

session = get_session()
provas_com_notas = (
    session.query(Prova)
    .join(Nota, Prova.id == Nota.prova_id)
    .distinct()
    .all()
)
provas_lista = [{"id": p.id, "titulo": p.titulo, "turma": p.turma.nome} for p in provas_com_notas]
session.close()

if not provas_lista:
    st.info("Nenhuma nota registrada ainda.")
    st.stop()

prova_options = {f"{p['titulo']} ({p['turma']})": p['id'] for p in provas_lista}
prova_sel_label = st.selectbox("Selecione a Prova", list(prova_options.keys()))
prova_id = prova_options[prova_sel_label]

session = get_session()
notas_raw = (
    session.query(Nota.pontuacao, Nota.respostas_json, Aluno.matricula, Aluno.nome)
    .join(Aluno, Nota.aluno_id == Aluno.id)
    .filter(Nota.prova_id == prova_id)
    .all()
)
questoes_raw = (
    session.query(Questao.numero, Questao.alternativa_correta, Questao.peso)
    .filter(Questao.prova_id == prova_id)
    .order_by(Questao.numero)
    .all()
)
session.close()

if not notas_raw:
    st.info("Nenhuma nota encontrada para esta prova.")
    st.stop()

dados = [
    {
        "Matrícula": n.matricula,
        "Nome do Aluno": n.nome,
        "Nota": n.pontuacao,
        "Situação": "Aprovado" if n.pontuacao >= 6.0 else "Reprovado",
    }
    for n in notas_raw
]
df = pd.DataFrame(dados).sort_values("Nome do Aluno")

st.subheader(f"Notas: {len(df)} aluno(s)")
st.dataframe(df, use_container_width=True, hide_index=True)

st.divider()
col1, col2, col3, col4 = st.columns(4)
col1.metric("Média", f"{df['Nota'].mean():.2f}")
col2.metric("Maior Nota", f"{df['Nota'].max():.2f}")
col3.metric("Menor Nota", f"{df['Nota'].min():.2f}")
aprovados = len(df[df["Situação"] == "Aprovado"])
col4.metric("Aprovados", f"{aprovados}/{len(df)}")

st.divider()
st.subheader("Exportar")
try:
    excel_bytes = exportar_notas_excel(prova_id)
    st.download_button(
        label="Baixar Excel",
        data=excel_bytes,
        file_name=f"notas_prova_{prova_id}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )
except Exception as e:
    st.error(f"Erro ao gerar Excel: {e}")
