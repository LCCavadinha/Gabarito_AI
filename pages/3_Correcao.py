import streamlit as st
from PIL import Image
import io
from database import init_db, get_session, Prova, Aluno, Questao
from services.qr_service import ler_qr_code
from services.gemini_service import configurar_gemini, extrair_respostas_da_imagem
from services.correction_service import corrigir_prova, salvar_nota, buscar_gabarito_e_pesos

st.set_page_config(page_title="Correção | Gabarito IA", page_icon="🤖", layout="wide")
init_db()

st.title("🤖 Correção Automática")

# Verifica API Key
if not st.session_state.get("gemini_api_key"):
    st.error("Configure a chave API Gemini na página inicial antes de corrigir.")
    st.stop()

configurar_gemini(st.session_state.gemini_api_key)

# ── SELEÇÃO DA PROVA ─────────────────────────────────────────────
# CORREÇÃO: todos os dados extraídos para dicts DENTRO da sessão
session = get_session()
provas_completas = []
for p in session.query(Prova).all():
    soma = sum(q.peso for q in p.questoes)
    if abs(soma - 10.0) < 0.01:
        provas_completas.append({
            "id": p.id,
            "titulo": p.titulo,
            "turma": p.turma.nome,
            "num_questoes": len(p.questoes),
        })
session.close()

if not provas_completas:
    st.warning("Nenhuma prova com gabarito completo. Cadastre as questões e o gabarito na página 'Provas'.")
    st.stop()

prova_options = {f"{p['titulo']} ({p['turma']})": p["id"] for p in provas_completas}
prova_sel_label = st.selectbox("Selecione a Prova para Corrigir", list(prova_options.keys()))
prova_id = prova_options[prova_sel_label]

num_questoes = next(p["num_questoes"] for p in provas_completas if p["id"] == prova_id)

st.info(f"Prova com **{num_questoes}** questões. Faça upload das fotos dos gabaritos preenchidos pelos alunos.")

# ── UPLOAD DAS FOTOS ─────────────────────────────────────────────
fotos = st.file_uploader(
    "Selecione as fotos dos gabaritos (JPG, PNG)",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True,
    help="Você pode selecionar múltiplas fotos de uma vez (Ctrl+clique ou Shift+clique)"
)

if not fotos:
    st.info("Aguardando upload das fotos...")
    st.stop()

st.write(f"**{len(fotos)} foto(s) carregada(s)**")

if st.button("Corrigir Todos os Gabaritos", type="primary", use_container_width=True):
    gabarito, pesos = buscar_gabarito_e_pesos(prova_id)
    resultados = []
    erros = []

    barra = st.progress(0, text="Iniciando correção...")

    for i, foto in enumerate(fotos):
        barra.progress((i + 1) / len(fotos), text=f"Processando {foto.name}... ({i+1}/{len(fotos)})")

        try:
            imagem_pil = Image.open(io.BytesIO(foto.read()))

            # Passo 1: Ler QR Code
            dados_qr = ler_qr_code(imagem_pil)
            if not dados_qr:
                erros.append({
                    "arquivo": foto.name,
                    "erro": "QR Code não encontrado. Verifique se a foto está nítida e o QR Code visível."
                })
                continue

            qr_prova_id = dados_qr.get("prova_id")
            if qr_prova_id != prova_id:
                erros.append({
                    "arquivo": foto.name,
                    "erro": f"Esta folha pertence à prova ID {qr_prova_id}, não à prova selecionada."
                })
                continue

            aluno_id = dados_qr.get("aluno_id")

            # CORREÇÃO: extrai dados do aluno dentro da sessão
            session = get_session()
            aluno_obj = session.query(Aluno).filter_by(id=aluno_id).first()
            if aluno_obj:
                aluno_dados = {"id": aluno_obj.id, "nome": aluno_obj.nome, "matricula": aluno_obj.matricula}
            else:
                aluno_dados = None
            session.close()

            if not aluno_dados:
                erros.append({
                    "arquivo": foto.name,
                    "erro": f"Aluno ID {aluno_id} não encontrado no banco de dados."
                })
                continue

            # Passo 2: Gemini lê as bolhas
            respostas_aluno = extrair_respostas_da_imagem(imagem_pil, num_questoes)

            # Passo 3: Corrigir e salvar
            nota, detalhes = corrigir_prova(respostas_aluno, gabarito, pesos)
            salvar_nota(aluno_dados["id"], prova_id, nota, detalhes)

            acertos = sum(1 for d in detalhes.values() if d["acertou"])
            nulas = [str(q) for q, v in respostas_aluno.items() if v is None]
            resultados.append({
                "arquivo": foto.name,
                "aluno": aluno_dados["nome"],
                "matricula": aluno_dados["matricula"],
                "acertos": f"{acertos}/{num_questoes}",
                "nota": nota,
                "sem_marcacao": f"Q{', Q'.join(nulas)}" if nulas else "Nenhuma",
            })

        except Exception as e:
            erros.append({"arquivo": foto.name, "erro": str(e)})

    barra.progress(1.0, text="Correção concluída!")
    st.session_state["resultados_correcao"] = resultados
    st.session_state["erros_correcao"] = erros

# ── RESULTADOS ───────────────────────────────────────────────────
if "resultados_correcao" in st.session_state:
    resultados = st.session_state["resultados_correcao"]
    erros = st.session_state.get("erros_correcao", [])

    if resultados:
        st.divider()
        st.subheader(f"Resultado: {len(resultados)} gabarito(s) corrigido(s)")

        import pandas as pd
        df = pd.DataFrame(resultados, columns=["arquivo", "aluno", "matricula", "acertos", "nota", "sem_marcacao"])
        df.columns = ["Arquivo", "Aluno", "Matrícula", "Acertos", "Nota", "Sem Marcação"]
        df = df.sort_values("Nota", ascending=False)

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Nota": st.column_config.NumberColumn(format="%.2f"),
            }
        )

        media = df["Nota"].mean()
        col1, col2, col3 = st.columns(3)
        col1.metric("Média da Turma", f"{media:.2f}")
        col2.metric("Maior Nota", f"{df['Nota'].max():.2f}")
        col3.metric("Menor Nota", f"{df['Nota'].min():.2f}")

    if erros:
        st.divider()
        st.subheader(f"Erros: {len(erros)} foto(s) não processada(s)")
        for e in erros:
            st.error(f"**{e['arquivo']}**: {e['erro']}")

    st.info("As notas foram salvas no banco. Acesse a página 'Relatório' para exportar o Excel.")
