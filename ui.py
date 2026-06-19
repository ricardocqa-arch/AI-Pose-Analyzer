import sqlite3
import pandas as pd
import os
import tkinter as tk
from tkinter import filedialog
import gradio as gr

from paths import resource_path
from styles import IDR_THEME_CSS, COLORS
from database import load_portfolio, save_portfolio, init_db
from recommendation import recomendar_exoesqueletos
from analysis import analisar_video
from config import TAGS_OFICIAIS, NIVEL_CHOICES, DB_PATH


def escolher_pasta_interativo():
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    pasta = filedialog.askdirectory(title="Selecione a pasta onde guardar os resultados")
    root.destroy()
    return pasta if pasta else "Nenhuma pasta selecionada"


def get_model_choices():
    try:
        df = load_portfolio()
        return sorted(df["nome"].tolist()) if not df.empty else []
    except:
        return []


def atualizar_dropdowns():
    """Atualiza todos os dropdowns após alterações no portfólio"""
    choices = get_model_choices()
    return (
        gr.update(choices=choices),
        gr.update(choices=choices),
        gr.update(choices=choices)
    )


# ===================== FUNÇÕES DE GESTÃO =====================

def adicionar_exo(nome, protecoes, nivel, forca_newton, peso_eq, descricao, indicado_para):
    if not nome or not nome.strip():
        return load_portfolio(), *atualizar_dropdowns()[0:2], "❌ Nome é obrigatório!"

    protecao_str = ", ".join(protecoes) if isinstance(protecoes, list) and protecoes else ""

    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO exos 
            (nome, protecao, nivel_assistencia, forca_assistida_newton, 
             peso_equipamento, descricao, indicado_para)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (nome.strip(), protecao_str, nivel, forca_newton, peso_eq, descricao, indicado_para))
        conn.commit()

        new_df = load_portfolio()
        return new_df, *atualizar_dropdowns()[0:2], f"✅ Exoesqueleto '{nome}' adicionado com sucesso!"
    except sqlite3.Error as e:
        conn.rollback()
        return load_portfolio(), *atualizar_dropdowns()[0:2], f"❌ Erro: {str(e)}"
    finally:
        conn.close()


def carregar_para_edicao(nome_selecionado):
    if not nome_selecionado:
        return None, [], None, 0.0, 0.0, None, None, None

    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql_query("SELECT * FROM exos WHERE nome = ?", conn, params=(nome_selecionado,))
    finally:
        conn.close()

    if df.empty:
        return None, [], None, 0.0, 0.0, None, None, None

    row = df.iloc[0]
    def safe_float(val):
        try: return float(val)
        except: return 0.0

    protecoes_list = [t.strip() for t in str(row.get("protecao", "")).split(",") if t.strip()]

    return (
        row.get("nome"), protecoes_list, row.get("nivel_assistencia"),
        safe_float(row.get("forca_assistida_newton")), safe_float(row.get("peso_equipamento")),
        row.get("descricao"), row.get("indicado_para"), nome_selecionado
    )


def guardar_edicao(nome_novo, protecoes, nivel, forca_newton, peso_eq, descricao, indicado_para, nome_original):
    def safe_float(val):
        try: return float(val)
        except: return 0.0

    forca_newton = safe_float(forca_newton)
    peso_eq = safe_float(peso_eq)

    if not nome_novo or not nome_original:
        return load_portfolio(), *atualizar_dropdowns()[0:2], "❌ Nome inválido!"

    protecao_str = ", ".join(protecoes) if isinstance(protecoes, list) and protecoes else ""

    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE exos SET nome = ?, protecao = ?, nivel_assistencia = ?,
                            forca_assistida_newton = ?, peso_equipamento = ?,
                            descricao = ?, indicado_para = ?
            WHERE nome = ?
        """, (nome_novo, protecao_str, nivel, forca_newton, peso_eq, descricao, indicado_para, nome_original))
        conn.commit()

        new_df = load_portfolio()
        return new_df, *atualizar_dropdowns()[0:2], "✅ Alterações guardadas com sucesso!"
    except sqlite3.Error as e:
        conn.rollback()
        return load_portfolio(), *atualizar_dropdowns()[0:2], f"❌ Erro: {str(e)}"
    finally:
        conn.close()


def eliminar_exo(nome_selecionado):
    if not nome_selecionado:
        return load_portfolio(), *atualizar_dropdowns()[0:2], "❌ Selecione um modelo para eliminar."

    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM exos WHERE nome = ?", (nome_selecionado,))
        if cursor.fetchone() is None:
            return load_portfolio(), *atualizar_dropdowns()[0:2], f"❌ Modelo '{nome_selecionado}' não encontrado."

        cursor.execute("DELETE FROM exos WHERE nome = ?", (nome_selecionado,))
        conn.commit()

        new_df = load_portfolio()
        return new_df, *atualizar_dropdowns()[0:2], f"✅ Modelo '{nome_selecionado}' eliminado com sucesso!"

    except sqlite3.Error as e:
        conn.rollback()
        return load_portfolio(), *atualizar_dropdowns()[0:2], f"❌ Erro ao eliminar: {str(e)}"
    finally:
        conn.close()


def processar_video(uploaded, peso_carga, postura, pasta_destino):
    if uploaded is None:
        return None, None, "❌ Carrega um vídeo primeiro!", ""

    if not pasta_destino or "Nenhuma pasta" in str(pasta_destino):
        pasta_destino = os.getcwd()

    video_path = uploaded if isinstance(uploaded, str) else uploaded.name

    try:
        peso_carga = float(peso_carga) if peso_carga not in (None, "") else 0.0
    except:
        peso_carga = 0.0

    try:
        events, video_anotado, json_path = analisar_video(video_path, peso_carga, pasta_destino)

        if not events:
            texto_eventos = "✅ Nenhum movimento de risco detetado."
        else:
            texto_eventos = "EVENTOS DE RISCO DETETADOS:\n\n"
            for i, e in enumerate(events, 1):
                texto_eventos += f"{i}. {e['tipo']}\n   ⏰ {e['inicio']} → {e['fim']}  ({e['duracao_seg']} s)\n   Carga: {e.get('carga_kg', 'Não aplicável')}\n\n"

        recomendacao_texto = recomendar_exoesqueletos(events, postura)

        return video_anotado, json_path, texto_eventos, recomendacao_texto

    except Exception as err:
        import traceback
        return None, None, f"❌ Erro durante a análise:\n{str(err)}", ""


# ===================== INTERFACE GRADIO =====================

with gr.Blocks(title="AI Pose Analyzer - Ergonomia & Exoesqueletos") as demo:

    with gr.Row():
        with gr.Column(scale=4):
            gr.Markdown(f"""
                # <span style='color:{COLORS['primary']}'>AI</span> Pose Analyzer
                ### Sistema Inteligente de Análise Postural e Recomendação de Exoesqueletos
            """)
        with gr.Column(scale=1):
            # O logótipo antigo da empresa foi removido daqui para desvincular a marca
            pass


    with gr.Tabs():
        with gr.Tab("🔎 Análise de Vídeo"):

            with gr.Row():
                # Alterado de gr.Video para gr.File para evitar erros de renderização de codec
                video_in = gr.File(
                    label="📂 Selecionar Vídeo para Análise",
                    file_types=["video"],
                    file_count="single",
                    container=True
                )

            with gr.Row():
                output_folder_path = gr.Textbox(
                    label="📁 Pasta de Destino dos Resultados",
                    placeholder="Escolha onde salvar os vídeos e JSON...", scale=4)
                btn_folder = gr.Button("Procurar...", scale=1, elem_classes=["custom-secondary-btn"])

            with gr.Row():
                peso_carga_in = gr.Number(label="Peso da Carga (kg, opcional)", value=0, minimum=0)
                postura_in = gr.Radio(choices=["nenhum", "em_pe", "sentado"], value="nenhum", label="Postura da tarefa", elem_classes=["posture-radio"]
                )
            with gr.Row():
                btn_analisar = gr.Button("Analisar Vídeo", variant="primary", size="large")

            btn_folder.click(fn=escolher_pasta_interativo, outputs=output_folder_path)

            with gr.Row():
                with gr.Column(scale=2):
                    video_out = gr.Video(
                        label="📹 Vídeo Anotado",
                        height=620,
                        format="mp4",
                        interactive=False,
                        show_label=True,
                        container=True,
                        elem_id="video_anotado",
                        elem_classes=["output-box", "video-large"]
                    )
                    json_out = gr.File(label="Download JSON", elem_classes=["output-box"])

                with gr.Column(scale=1):
                    eventos_out = gr.Textbox(label="Eventos de Risco", lines=14)
                    recomendacao_out = gr.Textbox(label="Recomendação de Exoesqueletos", lines=14)



        with gr.Tab("🗂️ Gestão do Portfólio", elem_classes=["custom-tab"]):
            gr.Markdown("## 🗂️ Gestão do Portfólio de Exoesqueletos")

            df_portfolio = gr.Dataframe(
                value=load_portfolio(),
                interactive=False,
                headers=["ID", "Nome", "Proteção", "Nível Assist.", "Força Assistida (N)",
                         "Peso Equip. (kg)", "Descrição", "Indicado Para"],
                max_height=380,
                datatype=["number", "str", "str", "str", "number", "number", "str", "str"],
                elem_id="portfolio_table",
                elem_classes=["dark-table"]
            )


            gr.Markdown("---")

            # ==================== SECÇÃO 1 – ADICIONAR ====================
            with gr.Group(elem_classes=["dark-panel"]):
                gr.Markdown("### ➕ 1. Adicionar Novo Exoesqueleto")
                with gr.Row():
                    nome_add = gr.Textbox(label="Nome do modelo", scale=2)
                    protecao_add = gr.Dropdown(choices=TAGS_OFICIAIS, multiselect=True, max_choices=6, label="Proteção fornecida", elem_classes=["dark-dropdown"])
                    nivel_add = gr.Dropdown(choices=NIVEL_CHOICES, label="Nível de Assistência", elem_classes=["dark-dropdown"])
                    forca_add = gr.Number(label="Força Assistida (N)", minimum=0, value=100)
                    peso_add = gr.Number(label="Peso Equip. (kg)", minimum=0, value=2.5)

                with gr.Row():
                    desc_add = gr.Textbox(label="Descrição", lines=2, scale=3)
                    indicado_add = gr.Textbox(label="Indicado Para (opcional)", lines=2, scale=2)

                btn_adicionar = gr.Button("Adicionar ao Portfólio", variant="primary", size="large", scale=0)
                status_add = gr.Textbox(label="Estado", interactive=False)

            gr.Markdown("---")

            # ==================== SECÇÃO 2 – EDITAR ====================
            with gr.Group(elem_classes=["dark-panel"]):

                gr.Markdown("### ✏️ 2. Editar Exoesqueleto Existente")
                with gr.Row():
                    selector_edit = gr.Dropdown(label="Selecione o modelo para editar", choices=get_model_choices(), interactive=True, scale=2, elem_classes=["dark-dropdown"])
                    btn_carregar = gr.Button("Carregar Dados", variant="secondary", size="large", scale=0, elem_classes=["custom-secondary-btn"]
                    )

                with gr.Row():
                    nome_edit = gr.Textbox(label="Nome do modelo", scale=2)
                    protecao_edit = gr.Dropdown(choices=TAGS_OFICIAIS, multiselect=True, max_choices=6, label="Proteção fornecida", elem_classes=["dark-dropdown"])
                    nivel_edit = gr.Dropdown(choices=NIVEL_CHOICES, label="Nível de Assistência", elem_classes=["dark-dropdown"])
                    forca_edit = gr.Number(label="Força Assistida (N)", minimum=0)
                    peso_edit = gr.Number(label="Peso Equip. (kg)", minimum=0)

                with gr.Row():
                    desc_edit = gr.Textbox(label="Descrição", lines=2, scale=3)
                    indicado_edit = gr.Textbox(label="Indicado Para (opcional)", lines=2)

                btn_guardar = gr.Button("Guardar Alterações", variant="primary", size="large", scale=0)
                status_edit = gr.Textbox(label="Estado", interactive=False)

            gr.Markdown("---")

            # ==================== SECÇÃO 3 – ELIMINAR ====================
            with gr.Group(elem_classes=["dark-panel"]):
                gr.Markdown("### 🗑️ 3. Eliminar Exoesqueleto", elem_classes=["dark-panel"])
                with gr.Row():
                    selector_delete = gr.Dropdown(label="Selecione o modelo para eliminar", choices=get_model_choices(), interactive=True, scale=2, elem_classes=["dark-dropdown"])
                    btn_eliminar = gr.Button("Eliminar Selecionado", variant="stop", size="large", scale=0,
                                             elem_classes=["custom-delete-btn"])
                status_delete = gr.Textbox(label="Estado da Eliminação", interactive=False)

            # ===================== LIGAÇÕES DOS BOTÕES =====================
            btn_adicionar.click(
                fn=adicionar_exo,
                inputs=[nome_add, protecao_add, nivel_add, forca_add, peso_add, desc_add, indicado_add],
                outputs=[df_portfolio, selector_edit, selector_delete, status_add]
            )

            btn_carregar.click(
                fn=carregar_para_edicao,
                inputs=[selector_edit],
                outputs=[nome_edit, protecao_edit, nivel_edit, forca_edit, peso_edit, desc_edit, indicado_edit,
                         selector_edit]
            )

            btn_guardar.click(
                fn=guardar_edicao,
                inputs=[nome_edit, protecao_edit, nivel_edit, forca_edit, peso_edit, desc_edit, indicado_edit,
                        selector_edit],
                outputs=[df_portfolio, selector_edit, selector_delete, status_edit]
            )

            btn_eliminar.click(
                fn=eliminar_exo,
                inputs=[selector_delete],
                outputs=[df_portfolio, selector_edit, selector_delete, status_delete]
            )



    btn_analisar.click(
        fn=processar_video,
        inputs=[video_in, peso_carga_in, postura_in, output_folder_path],
        outputs=[video_out, json_out, eventos_out, recomendacao_out]
    )


demo = demo