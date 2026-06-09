import streamlit as st
from database import init_db, get_session, Professor, Turma, Aluno

st.set_page_config(page_title="Cadastros | Gabarito IA", page_icon="👥", layout="wide")
init_db()

st.title("👥 Cadastros")

tab1, tab2, tab3 = st.tabs(["Professores", "Turmas", "Alunos"])

# ── TAB 1: PROFESSORES ───────────────────────────────────────────
with tab1:
    col_form, col_lista = st.columns([1, 1])

    with col_form:
        st.subheader("Novo Professor")
        with st.form("form_professor", clear_on_submit=True):
            nome_prof = st.text_input("Nome completo")
            email_prof = st.text_input("E-mail")
            submitted = st.form_submit_button("Cadastrar Professor", use_container_width=True)

            if submitted:
                if not nome_prof or not email_prof:
                    st.error("Preencha todos os campos.")
                else:
                    session = get_session()
                    try:
                        existente = session.query(Professor).filter_by(email=email_prof).first()
                        if existente:
                            st.error("E-mail já cadastrado.")
                        else:
                            prof = Professor(nome=nome_prof, email=email_prof)
                            session.add(prof)
                            session.commit()
                            st.success(f"Professor '{nome_prof}' cadastrado com sucesso!")
                            st.rerun()
                    except Exception as e:
                        st.error(f"Erro: {e}")
                    finally:
                        session.close()

    with col_lista:
        st.subheader("Professores Cadastrados")
        session = get_session()
        professores = session.query(Professor).all()
        professores_data = [
            {"id": p.id, "nome": p.nome, "email": p.email}
            for p in professores
        ]
        session.close()

        if professores_data:
            for p in professores_data:
                st.markdown(f"**{p['nome']}** | {p['email']}")
        else:
            st.info("Nenhum professor cadastrado ainda.")

# ── TAB 2: TURMAS ────────────────────────────────────────────────
with tab2:
    session = get_session()
    professores = session.query(Professor).all()
    professores_data = [{"id": p.id, "nome": p.nome, "email": p.email} for p in professores]
    session.close()

    if not professores:
        st.warning("Cadastre um professor antes de criar turmas.")
    else:
        col_form, col_lista = st.columns([1, 1])

        with col_form:
            st.subheader("Nova Turma")
            with st.form("form_turma", clear_on_submit=True):
                nome_turma = st.text_input("Nome da Turma")
                prof_options = {f"{p['nome']} ({p['email']})": p['id'] for p in professores_data}
                prof_sel = st.selectbox("Professor Responsável", list(prof_options.keys()))
                submitted = st.form_submit_button("Cadastrar Turma", use_container_width=True)

                if submitted:
                    if not nome_turma:
                        st.error("Informe o nome da turma.")
                    else:
                        session = get_session()
                        try:
                            turma = Turma(nome=nome_turma, professor_id=prof_options[prof_sel])
                            session.add(turma)
                            session.commit()
                            st.success(f"Turma '{nome_turma}' cadastrada!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro: {e}")
                        finally:
                            session.close()

        with col_lista:
            st.subheader("Turmas Cadastradas")
            session = get_session()
            turmas = session.query(Turma).all()
            turmas_data = [
                {
                    "id": t.id,
                    "nome": t.nome,
                    "professor_nome": t.professor.nome if t.professor else None,
                    "num_alunos": len(t.alunos),
                }
                for t in turmas
            ]
            session.close()

            if turmas_data:
                for t in turmas_data:
                    st.markdown(f"**{t['nome']}** | Prof. {t['professor_nome']} | {t['num_alunos']} aluno(s)")
            else:
                st.info("Nenhuma turma cadastrada ainda.")

# ── TAB 3: ALUNOS ────────────────────────────────────────────────
with tab3:
    session = get_session()
    turmas = session.query(Turma).all()
    turmas_data = [{"id": t.id, "nome": t.nome} for t in turmas]
    session.close()

    if not turmas:
        st.warning("Cadastre uma turma antes de adicionar alunos.")
    else:
        col_form, col_lista = st.columns([1, 1])

        with col_form:
            st.subheader("Novo Aluno")
            with st.form("form_aluno", clear_on_submit=True):
                nome_aluno = st.text_input("Nome completo do aluno")
                matricula = st.text_input("Matrícula")
                turma_options = {t['nome']: t['id'] for t in turmas_data}
                turma_sel = st.selectbox("Turma", list(turma_options.keys()))
                submitted = st.form_submit_button("Cadastrar Aluno", use_container_width=True)

                if submitted:
                    if not nome_aluno or not matricula:
                        st.error("Preencha todos os campos.")
                    else:
                        session = get_session()
                        try:
                            existente = session.query(Aluno).filter_by(matricula=matricula).first()
                            if existente:
                                st.error(f"Matrícula '{matricula}' já cadastrada para {existente.nome}.")
                            else:
                                aluno = Aluno(
                                    nome=nome_aluno,
                                    matricula=matricula,
                                    turma_id=turma_options[turma_sel],
                                )
                                session.add(aluno)
                                session.commit()
                                st.success(f"Aluno '{nome_aluno}' cadastrado!")
                                st.rerun()
                        except Exception as e:
                            st.error(f"Erro: {e}")
                        finally:
                            session.close()

        with col_lista:
            st.subheader("Alunos Cadastrados")
            turma_filtro = st.selectbox("Filtrar por turma", ["Todas"] + [t['nome'] for t in turmas_data])

            session = get_session()
            alunos_data = []
            if turma_filtro == "Todas":
                alunos = session.query(Aluno).all()
                alunos_data = [{"nome": a.nome, "matricula": a.matricula, "id": a.id} for a in alunos]
            else:
                turma_obj = session.query(Turma).filter_by(nome=turma_filtro).first()
                if turma_obj:
                    alunos_data = [{"nome": a.nome, "matricula": a.matricula, "id": a.id} for a in turma_obj.alunos]

            session.close()

            if alunos_data:
                for a in alunos_data:
                    st.markdown(f"**{a['nome']}** | Matrícula: `{a['matricula']}`")
            else:
                st.info("Nenhum aluno encontrado.")
