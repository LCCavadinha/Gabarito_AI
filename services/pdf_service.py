from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
import io
from PIL import Image as PILImage
from services.qr_service import gerar_qr_code


def gerar_folha_gabarito(aluno, prova, questoes: list) -> bytes:
    """
    Gera a folha de gabarito em PDF para um aluno específico.
    Inclui QR Code, dados do aluno, linha de assinatura e grid de bolhas.
    Retorna bytes do PDF.
    """
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    W, H = A4
    margin = 1.5 * cm

    # ── QR CODE ──────────────────────────────────────────────────
    qr_pil = gerar_qr_code(aluno.id, aluno.matricula, prova.id)
    qr_buffer = io.BytesIO()
    qr_pil.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)
    qr_size = 3.2 * cm
    qr_x = W - margin - qr_size
    qr_y = H - margin - qr_size
    c.drawImage(ImageReader(qr_buffer), qr_x, qr_y, width=qr_size, height=qr_size)

    # ── CABEÇALHO ────────────────────────────────────────────────
    c.setFont("Helvetica-Bold", 15)
    c.drawString(margin, H - margin - 0.6 * cm, "FOLHA DE GABARITO")

    c.setFont("Helvetica-Bold", 10)
    c.drawString(margin, H - margin - 1.4 * cm, f"Prova: {prova.titulo}")

    c.setFont("Helvetica", 10)
    c.drawString(margin, H - margin - 2.1 * cm, f"Aluno(a): {aluno.nome}")
    c.drawString(margin, H - margin - 2.7 * cm, f"Matrícula: {aluno.matricula}")

    # Linha de assinatura
    sig_y = H - margin - 3.5 * cm
    c.setFont("Helvetica", 10)
    c.drawString(margin, sig_y, "Assinatura: ")
    c.line(margin + 2.8 * cm, sig_y, W - margin - qr_size - 0.5 * cm, sig_y)

    # Instrução
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(
        margin,
        H - margin - 4.3 * cm,
        "Instruções: Preencha completamente o círculo da alternativa correta. Não rasure e não marque mais de uma alternativa por questão."
    )

    # Linha separadora
    sep_y = H - margin - 4.8 * cm
    c.setStrokeColorRGB(0.3, 0.3, 0.3)
    c.setLineWidth(0.5)
    c.line(margin, sep_y, W - margin, sep_y)

    # ── GRID DE BOLHAS ───────────────────────────────────────────
    grid_top = sep_y - 0.8 * cm
    alt_labels = ["A", "B", "C", "D", "E"]
    bubble_r = 0.27 * cm
    row_h = 1.05 * cm
    alt_spacing = 0.85 * cm
    num_label_w = 2.3 * cm
    col_width = W / 2 - margin

    num_q = len(questoes)
    split = (num_q + 1) // 2

    for col_idx in range(2):
        x_base = margin + col_idx * (W / 2)
        alt_start_x = x_base + num_label_w

        # Cabeçalho das alternativas
        c.setFont("Helvetica-Bold", 9)
        for j, alt in enumerate(alt_labels):
            c.drawCentredString(alt_start_x + j * alt_spacing, grid_top + 0.3 * cm, alt)

        # Linha divisória do cabeçalho
        c.setLineWidth(0.5)
        c.line(x_base, grid_top + 0.05 * cm,
               alt_start_x + 4 * alt_spacing + bubble_r, grid_top + 0.05 * cm)

        q_start = col_idx * split
        q_end = min(q_start + split, num_q)

        for i, q_i in enumerate(range(q_start, q_end)):
            q = questoes[q_i]
            y = grid_top - (i + 1) * row_h + 0.2 * cm

            # Número e peso da questão
            c.setFont("Helvetica-Bold", 9)
            c.drawString(x_base, y + 0.2 * cm, f"Q{q.numero:02d}")
            c.setFont("Helvetica", 7)
            c.drawString(x_base, y - 0.22 * cm, f"({q.peso:.1f}pt)")

            # Bolhas A B C D E
            c.setLineWidth(0.8)
            for j in range(5):
                bx = alt_start_x + j * alt_spacing
                c.circle(bx, y + 0.05 * cm, bubble_r, stroke=1, fill=0)

    c.save()
    buffer.seek(0)
    return buffer.read()


def gerar_todos_pdfs(alunos: list, prova, questoes: list) -> dict[str, bytes]:
    """Gera um PDF por aluno e retorna um dicionário {matricula: bytes_pdf}."""
    pdfs = {}
    for aluno in alunos:
        pdfs[aluno.matricula] = gerar_folha_gabarito(aluno, prova, questoes)
    return pdfs
