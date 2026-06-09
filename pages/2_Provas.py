import streamlit as st
import zipfile
import io
from database import init_db, get_session, Turma, Prova, Questao, Aluno
from services.pdf_service import gerar_todos_pdfs

st.set_page_config(page_title="Provas | Gabarito IA", page_icon="📋", layout="wide")
init_db()

st.title("📋 Provas")

tab1, tab2, tab3 = st.tabs(["Criar Prova", "Questões e Gabarito", "Gerar Folhas PDF"])

# ── TAB 1: CRIAR PROVA ───────────────────────────────────────────
with tab1:
    session = get_session()
    turmas_data = [{"id": t.id, "nome": t.nome} for t in session.query(Turma).all()]
    session.close()

    if not turmas_data:
        st.warning("Cadastre turmas e alunos antes de criar provas.")
    else:
        col_form, col_lista = st.columns([1, 1])

        with col_form:
            st.subheader("Nova Prova")
            with st.form("form_prova", clear_on_submit=True):
                titulo_prova = st.text_input("Título da Prova")
                turma_options = {t["nome"]: t["id"] for t in turmas_data}
                turma_sel = st.selectbox("Turma", list(turma_options.keys()))
                submitted = st.form_submit_button("Criar Prova", use_container_width=True)

                if submitted:
                    if not titulo_prova:
                        st.error("Informe o título da prova.")
                    else:
                        session = get_session()
                        try:
                            prova = Prova(titulo=titulo_prova, turma_id=turma_options[turma_sel])
                            session.add(prova)
                            session.commit()
                            st.success(f"Prova '{titulo_prova}' criada! Agora cadastre as questões na aba 'Questões e Gabarito'.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro: {e}")
                        finally:
                            session.close()

        with col_lista:
            st.subheader("Provas Criadas")
            session = get_session()
            provas_data = []
            for p in session.query(Prova).all():
                num_q = len(p.questoes)
                soma_pesos = sum(q.peso for q in p.questoes)
                provas_data.append({
                    "titulo": p.titulo,
                    "turma": p.turma.nome,
                    "num_q": num_q,
                    "soma_pesos": soma_pesos,
                    "completo": abs(soma_pesos - 10.0) < 0.01 and num_q > 0
                })
            session.close()

            if provas_data:
                for p in provas_data:
                    status = "Gabarito completo" if p["completo"] else "Sem gabarito definido"
                    st.markdown(f"**{p['titulo']}** | Turma: {p['turma']} | {p['num_q']} questão(ões) | {status}")
            else:
                st.info("Nenhuma prova criada ainda.")

# ── TAB 2: QUESTÕES E GABARITO ───────────────────────────────────
with tab2:
    session = get_session()
    provas_data = [{"id": p.id, "titulo": p.titulo, "turma": p.turma.nome} for p in session.query(Prova).all()]
    session.close()

    if not provas_data:
        st.warning("Crie uma prova primeiro.")
    else:
        prova_options = {f"{p['titulo']} ({p['turma']})": p['id'] for p in provas_data}
        prova_sel_label = st.selectbox("Selecione a Prova", list(prova_options.keys()), key="prova_questoes")
        prova_id = prova_options[prova_sel_label]

        session = get_session()
        prova = session.query(Prova).filter_by(id=prova_id).first()
        questoes_existentes = []
        soma_atual = 0.0
        if prova:
            questoes_existentes = [{
                "numero": q.numero,
                "peso": q.peso,
                "alternativa_correta": q.alternativa_correta
            } for q in prova.questoes]
            soma_atual = sum(q.peso for q in prova.questoes)
        session.close()

        st.info(f"Questões cadastradas: **{len(questoes_existentes)}** | Soma dos pesos: **{soma_atual:.2f}/10.00**")

        if abs(soma_atual - 10.0) < 0.01 and len(questoes_existentes) > 0:
            st.success("Gabarito completo! A soma dos pesos é exatamente 10.")

        st.divider()
        col_form, col_gabarito = st.columns([1, 1])

        with col_form:
            st.subheader("Adicionar Questão")
            with st.form("form_questao", clear_on_submit=True):
                num_questao = st.number_input(
                    "Número da questão",
                    min_value=1, max_value=20, step=1,
                    value=len(questoes_existentes) + 1
                )
                peso_questao = st.number_input(
                    "Peso da questão (pontos)",
                    min_value=0.1, max_value=10.0, step=0.1, value=1.0,
                    help=f"Restam {max(0, 10.0 - soma_atual):.2f} pontos para distribuir"
                )
                alternativa = st.selectbox("Alternativa correta", ["A", "B", "C", "D", "E"])
                submitted = st.form_submit_button("Adicionar Questão", use_container_width=True)

                if submitted:
                    if soma_atual + peso_questao > 10.01:
                        st.error(f"Peso excede o limite! Restam apenas {10.0 - soma_atual:.2f} pontos.")
                    else:
                        session = get_session()
                        try:
                            existente = session.query(Questao).filter_by(
                                prova_id=prova_id, numero=num_questao
                            ).first()
                            if existente:
                                existente.peso = peso_questao
                                existente.alternativa_correta = alternativa
                                session.commit()
                                st.success(f"Questão {num_questao} atualizada!")
                            else:
                                q = Questao(
                                    numero=int(num_questao),
                                    peso=peso_questao,
                                    alternativa_correta=alternativa,
                                    prova_id=prova_id,
                                )
                                session.add(q)
                                session.commit()
                                st.success(f"Questão {num_questao} ({alternativa}) adicionada!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro: {e}")
                        finally:
                            session.close()

        with col_gabarito:
            st.subheader("Gabarito Atual")
            session = get_session()
            prova_atual = session.query(Prova).filter_by(id=prova_id).first()
            questoes_data = []
            if prova_atual:
                questoes_data = [{"numero": q.numero, "alternativa_correta": q.alternativa_correta, "peso": q.peso}
                                 for q in prova_atual.questoes]
            session.close()

            if questoes_data:
                for q in questoes_data:
                    st.markdown(f"Q{q['numero']:02d} | **{q['alternativa_correta']}** | {q['peso']:.1f}pt")
            else:
                st.info("Nenhuma questão cadastrada ainda.")

# ── TAB 3: GERAR PDFs ────────────────────────────────────────────
with tab3:
    session = get_session()
    provas_data = []
    for p in session.query(Prova).all():
        soma = sum(q.peso for q in p.questoes)
        if abs(soma - 10.0) < 0.01:
            provas_data.append({
                "id": p.id,
                "titulo": p.titulo,
                "turma": p.turma.nome,
                "turma_id": p.turma_id,
                "questoes": [q for q in p.questoes]
            })
    session.close()

    if not provas_data:
        st.warning("Nenhuma prova com gabarito completo (soma = 10). Cadastre as questões primeiro.")
    else:
        prova_options = {f"{p['titulo']} ({p['turma']})": p for p in provas_data}
        prova_sel_label = st.selectbox("Selecione a Prova", list(prova_options.keys()), key="prova_pdf")
        prova_selecionada = prova_options[prova_sel_label]

        session = get_session()
        alunos_turma = session.query(Aluno).filter_by(turma_id=prova_selecionada["turma_id"]).all()
        alunos_data = [{"id": a.id, "matricula": a.matricula, "nome": a.nome} for a in alunos_turma]
        questoes = prova_selecionada["questoes"]
        session.close()

        if not alunos_data:
            st.warning("A turma não possui alunos cadastrados.")
        else:
            st.info(f"Serão geradas **{len(alunos_data)}** folhas de gabarito para a turma **{prova_selecionada['turma']}**.")

            if st.button("Gerar PDFs de todos os alunos", use_container_width=True):
                with st.spinner("Gerando folhas de gabarito..."):
                    try:
                        # Get fresh session to pass ORM objects to gerar_todos_pdfs
                        session_pdf = get_session()
                        alunos_for_pdf = session_pdf.query(Aluno).filter_by(turma_id=prova_selecionada["turma_id"]).all()
                        prova_for_pdf = session_pdf.query(Prova).filter_by(id=prova_selecionada["id"]).first()
                        questoes_for_pdf = [q for q in prova_for_pdf.questoes] if prova_for_pdf else []
                        
                        pdfs = gerar_todos_pdfs(alunos_for_pdf, prova_for_pdf, questoes_for_pdf)
                        session_pdf.close()

                        # Agrupa todos em um ZIP para download único
                        zip_buffer = io.BytesIO()
                        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                            for matricula, pdf_bytes in pdfs.items():
                                nome_arquivo = f"gabarito_{matricula}.pdf"
                                zf.writestr(nome_arquivo, pdf_bytes)
                        zip_buffer.seek(0)

                        st.success(f"{len(pdfs)} folhas geradas com sucesso!")
                        st.download_button(
                            label="Baixar todos os PDFs (ZIP)",
                            data=zip_buffer.read(),
                            file_name=f"gabaritos_{prova_selecionada['titulo']}.zip",
                            mime="application/zip",
                            use_container_width=True,
                        )
                    except Exception as e:
                        st.error(f"Erro ao gerar PDFs: {e}")
