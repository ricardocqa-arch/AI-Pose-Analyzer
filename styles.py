# styles.py
# Tema visual oficial da aplicação iDR Exoesqueletos

COLORS = {
    "background": "#0a0a0a",      # Preto quase absoluto (mais elegante)
    "card_bg": "#161b22",         # Cinzento escuro para cards e inputs
    "text_main": "#f0f0f0",       # Branco suave (melhor para leitura)
    "text_muted": "#8b949e",      # Cinza para textos secundários
    "primary": "#00d1ff",         # Ciano vibrante da marca iDR
    "primary_dark": "#00a8cc",    # Versão mais escura para hover
    "border": "#30363d",          # Bordas sutis
    "success": "#39d353",         # Verde para mensagens de sucesso
    "danger": "#f85149",          # Vermelho para erros/eliminar
    "warning": "#f0b030",         # Amarelo para alertas
}

IDR_THEME_CSS = f"""
/* ===================== TEMA GLOBAL ===================== */
:root, .gradio-container, .main, body, html {{
    background-color: {COLORS['background']} !important;
    color: {COLORS['text_main']} !important;
    font-family: 'Segoe UI', system-ui, sans-serif;
}}

/* Títulos e textos principais */
.prose h1, .prose h2, .prose h3, h1, h2, h3, label, .label span {{
    color: {COLORS['text_main']} !important;
}}

/* ===================== CARDS E INPUTS ===================== */
.gr-box, .gr-input, .gr-text-input, input, textarea, select, 
.block, .gr-block, .upload-container, .gr-file, .gr-video {{
    background-color: {COLORS['card_bg']} !important;
    border: 3px solid {COLORS['border']} !important;
    border-radius: 10px !important;
    color: {COLORS['text_main']} !important;
}}

/* Dataframe */
.dataframe {{
    background-color: {COLORS['card_bg']} !important;
    border: 1px solid {COLORS['border']} !important;
}}
.dataframe th {{
    background-color: #21262d !important;
    color: {COLORS['primary']} !important;
}}

/* ===================== BOTÕES ===================== */
.gr-button-primary {{
    background-color: {COLORS['primary']} !important;
    color: #000000 !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 8px !important;
    transition: all 0.2s ease;
}}

.gr-button-primary:hover {{
    background-color: {COLORS['primary_dark']} !important;
    transform: translateY(-1px);
}}

.gr-button-secondary {{
    background-color: transparent !important;
    color: {COLORS['text_main']} !important;
    border: 1px solid {COLORS['primary']} !important;
    border-radius: 8px !important;
}}

.gr-button-stop {{
    background-color: {COLORS['danger']} !important;
    color: white !important;
}}

/* ===================== TABS COM EMOJIS ===================== */
.tab-nav button {{
    color: #b8c0cc !important;
    font-size: 16px !important;
    font-weight: 500 !important;
    padding: 14px 24px !important;
}}

.tab-nav button:hover {{
    color: #e0e8f0 !important;
}}

.tab-nav button.selected,
.tab-nav button[aria-selected="true"] {{
    color: #00d1ff !important;
    font-weight: 700 !important;
    border-bottom: 4px solid #00d1ff !important;
}}

/* ===================== ALERTAS E STATUS ===================== */
.gr-textbox[style*="success"], .success {{
    border-color: {COLORS['success']} !important;
}}

.gr-textbox[style*="error"], .error {{
    border-color: {COLORS['danger']} !important;
}}

/* ===================== OUTROS ===================== */
.markdown {{
    color: {COLORS['text_main']} !important;
}}

.footer {{
    color: {COLORS['text_muted']} !important;
}}

/* ===================== TABELA ESPECÍFICA - MAIS FORTE ===================== */
#portfolio_table, .dark-table, .gr-dataframe {{
    background-color: #1f252e !important;
    border: 1px solid #30363d !important;
}}

#portfolio_table th, .dark-table th, .gr-dataframe th {{
    background-color: #2d333b !important;
    color: #00d1ff !important;
    font-weight: 600 !important;
}}

#portfolio_table td, .dark-table td, .gr-dataframe td {{
    background-color: #1f252e !important;
    color: #e6edf3 !important;
    border-bottom: 1px solid #30363d !important;
}}

#portfolio_table tr:hover td, .dark-table tr:hover td {{
    background-color: #2a2f38 !important;
}}

/* ===================== BOTÕES PERSONALIZADOS ===================== */

/* Botões secundários (Carregar, Procurar...) */
.custom-secondary-btn, .gr-button-secondary {{
    background-color: #21262d !important;
    color: #e6edf3 !important;
    border: 1px solid #00d1ff !important;
    font-weight: 500 !important;
}}

.custom-secondary-btn:hover {{
    background-color: #30363d !important;
    border-color: #00d1ff !important;
}}

/* Botões primários (Adicionar, Guardar) */
.custom-primary-btn, .gr-button-primary {{
    background-color: #00d1ff !important;
    color: #000000 !important;
    font-weight: 700 !important;
}}

.custom-primary-btn:hover {{
    background-color: #00b8e0 !important;
}}

/* Botão Eliminar (vermelho escuro) */
.custom-delete-btn, .gr-button-stop {{
    background-color: #f85149 !important;
    color: #ffffff !important;
    font-weight: 600 !important;
}}

.custom-delete-btn:hover {{
    background-color: #e03e3e !important;
}}

/* ===================== FUNDO BRANCO REMOVIDO - CORREÇÕES ESPECÍFICAS ===================== */

/* Botão "Carregar Dados" e outros botões secundários */
.custom-secondary-btn,
.gr-button-secondary {{
    background-color: #21262d !important;
    color: #e6edf3 !important;
    border: 1px solid #00d1ff !important;
}}

.custom-secondary-btn:hover,
.gr-button-secondary:hover {{
    background-color: #30363d !important;
}}

/* Remover fundos brancos em dropdowns, inputs com foco e painéis */
.gr-dropdown, .gr-input:focus, .gr-text-input:focus, select:focus {{
    background-color: #161b22 !important;
    color: #e6edf3 !important;
    border-color: #00d1ff !important;
}}

/* Remover fundo branco em caixas de seleção e labels */
.token, .gr-chip, .gr-dropdown .wrap {{
    background-color: #21262d !important;
}}

/* Corrigir fundo branco que aparece em alguns painéis de edição */
.gr-box, .gr-form, .block {{
    background-color: #161b22 !important;
}}

/* ===================== CAIXAS / PANELS (GRUPOS) - FUNDO BRANCO ===================== */
.gr-group, .gr-box, .block, .gr-form, .gr-panel, .dark-panel {{
    background-color: #161b22 !important;
    border: 1px solid #30363d !important;
    border-radius: 10px !important;
    padding: 15px !important;
}}

/* Forçar em filhos diretos também */
.gr-group > div, .gr-box > div {{
    background-color: #161b22 !important;
}}

/* Cabeçalhos das secções (1. Adicionar, 2. Editar, etc.) */
.gr-markdown h3, .gr-group .gr-markdown {{
    color: #00d1ff !important;
    margin-bottom: 10px !important;
}}

/* ===================== DROPDOWNS - MELHORIA DE VISIBILIDADE ===================== */

/* Fundo geral do dropdown */
.dark-dropdown, .gr-dropdown {{
    background-color: #21262d !important;
}}

/* Caixa que envolve as tags (wrap) */
.dark-dropdown .wrap,
.gr-dropdown .wrap {{
    background-color: #21262d !important;
}}

/* As tags selecionadas (o principal problema) */
.dark-dropdown .token,
.gr-dropdown .token,
.gr-chip {{
    background-color: #2d333b !important;     /* Fundo das tags */
    color: #ffffff !important;                 /* Texto branco - MUDANÇA PRINCIPAL */
    border: 1px solid #00d1ff55 !important;
    font-weight: 500 !important;
}}

/* Hover nas tags */
.dark-dropdown .token:hover,
.gr-dropdown .token:hover {{
    background-color: #3d444f !important;
    color: #ffffff !important;
}}

/* Quando o dropdown está aberto ou com foco */
.dark-dropdown:focus-within,
.gr-dropdown:focus-within {{
    border-color: #00d1ff !important;
    box-shadow: 0 0 0 3px rgba(0, 209, 255, 0.25) !important;
}}

/* ===================== RADIO BUTTONS - POSTURA DA TAREFA ===================== */
.posture-radio .gr-radio-label,
.posture-radio label,
.posture-radio .radio-item,
.gr-radio .gr-radio-label {{
    background-color: #21262d !important;
    color: #ffffff !important;
    border: 2px solid #50586b !important;
    border-radius: 8px !important;
    padding: 12px 20px !important;
    font-size: 15px !important;
}}

/* Opção selecionada */
.posture-radio .gr-radio-label.selected,
.posture-radio input[type="radio"]:checked + label,
.posture-radio .radio-item.selected {{
    background-color: #00d1ff !important;
    color: #000000 !important;
    border-color: #00d1ff !important;
    font-weight: 700 !important;
}}

/* Hover */
.posture-radio .gr-radio-label:hover {{
    background-color: #2d333b !important;
    border-color: #00d1ff !important;
}}

/* ===================== LABELS DOS OUTPUTS - UNIFORMIDADE FORTE ===================== */
.output-box .label,
.output-box label,
.gr-video .label,
.gr-file .label,
.gr-textbox .label,
#video_anotado .label,
#video_anotado label,
#json_out .label,
#eventos_out .label,
#recomendacao_out .label {{
    background-color: #21262d !important;
    color: #f0f4fa !important;
    font-weight: 700 !important;
    padding: 10px 18px !important;
    border-radius: 8px !important;
    border: 2px solid #00d1ff88 !important;
    margin-bottom: 12px !important;
    display: inline-flex !important;
    align-items: center !important;
    gap: 8px !important;
    width: fit-content !important;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3) !important;
}}

/* Garantia extra para o label do vídeo */
#video_anotado .label,
.gr-video > label,
.gr-video .wrap > label {{
    background-color: #21262d !important;
    border: 2px solid #00d1ff88 !important;
    color: #f0f4fa !important;
    font-weight: 700 !important;
}}

/* ===================== TÍTULOS MANUAIS DOS OUTPUTS ===================== */
.output-title,
.output-title {{
    background-color: #21262d !important;
    color: #f0f4fa !important;
    font-weight: 600 !important;
    padding: 9px 16px !important;
    border-radius: 8px !important;
    border: 1px solid #00d1ff66 !important;
    margin-bottom: 10px !important;
    display: inline-block !important;
    width: fit-content !important;
}}

/* Reduzir tamanho das caixas */
.output-box {{
    max-height: 340px !important;
}}

#video_out {{
    max-height: 380px !important;
}}

.gr-textbox.output-box {{
    max-height: 280px !important;
}}

/* ===================== VÍDEO ANOTADO - MELHOR VISUAL ===================== */
#video_anotado, .video-responsive video {{
    max-height: 520px;
    width: auto !important;
    margin: 0 auto;
    display: block;
}}

#video_anotado .video-container,
#video_anotado video {{
    background-color: #0a0a0a !important;   /* Fundo escuro igual ao da página */
    margin: 0 auto;
    max-height: 480px;
    width: auto !important;
}}

/* Centralizar o player e remover fundo branco */
.gr-video, .video-container video {{
    background-color: #0a0a0a !important;
}}

/* Remover barra cinzenta ou branca por baixo do vídeo */
.gr-video .player {{
    background-color: #0a0a0a !important;
}}

.video-responsive video {{
    max-height: 520px;
    width: auto !important;
    margin: 0 auto;
    display: block;
}}

/* ===================== VÍDEO ALTO - FORÇADO ===================== */
#video_anotado,
.video-large {{
    height: 650px !important;           /* Altura fixa do container */
    min-height: 650px !important;
    max-height: 700px !important;
    width: 100% !important;
}}

#video_anotado video,
.video-large video,
.gr-video video {{
    height: 580px !important;           /* Altura real do player */
    max-height: 580px !important;
    width: auto !important;
    max-width: 100% !important;
    margin: 0 auto !important;
    background-color: #0a0a0a !important;
    object-fit: contain;                /* Mantém proporção sem cortar */
}}

/* Forçar o container interno */
#video_anotado > div,
#video_anotado .gr-video,
.gr-video {{
    height: 100% !important;
    min-height: 620px !important;
    background-color: #0a0a0a !important;
}}
"""

# Exporta para ser usado facilmente
__all__ = ["COLORS", "IDR_THEME_CSS"]