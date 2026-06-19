from config import TAGS_OFICIAIS, MAPEAMENTO_RISCO_SUPORTE
from database import load_portfolio
import sqlite3
import pandas as pd

from paths import resource_path



def normalize_tag(tag):
    if not tag:
        return ""
    return tag.strip().lower().replace(" ", "_").replace("-", "_")


def recomendar_exoesqueletos(eventos, postura="nenhum"):
    if not eventos:
        return "Nenhum risco detetado → sem recomendação necessária."

    # 1. Recolher todas as necessidades (tags) dos riscos detetados

    necessidades = set()
    risco_frequencia = {}

    for ev in eventos:
        tipo = ev["tipo"]
        duracao = ev.get("duracao_seg", 0)
        if tipo in MAPEAMENTO_RISCO_SUPORTE:
            for tag_original in MAPEAMENTO_RISCO_SUPORTE[tipo]:
                tag_norm = normalize_tag(tag_original)
                if tag_norm:
                    necessidades.add(tag_norm)

            # Regista frequência/duração do risco
            risco_frequencia[tipo] = risco_frequencia.get(tipo, 0) + duracao

    if not necessidades:
        return "Riscos detetados, mas sem mapeamento conhecido."

    # 2. Carregar portfólio
    conn = sqlite3.connect("exoskeletons.db")
    df = pd.read_sql_query("""
        SELECT nome, protecao, nivel_assistencia, forca_assistida_newton, 
               peso_equipamento, descricao, indicado_para
        FROM exos
    """, conn)
    conn.close()

    if df.empty:
        return "Não existem exoesqueletos registados na base de dados."

    # 3. Calcular pontuação para cada exoesqueleto
    recomendados = []

    for _, row in df.iterrows():
        suportes_str = row.get("protecao", "") or ""
        suportes = set(normalize_tag(tag) for tag in suportes_str.split(",") if normalize_tag(tag))


        compatibilidade = len(suportes & necessidades)

        if compatibilidade == 0:
            continue

        # Pontuação extra baseada em força e nível
        forca = row.get("forca_assistida_newton", 0) or 0
        nivel = row.get("nivel_assistencia", "baixo")

        nivel_score = {"baixo": 1, "médio": 2, "médio-alto": 3, "alto": 4}.get(nivel, 1)

        # Pontuação final
        score = (compatibilidade * 10) + (forca / 10) + (nivel_score * 5)

        # ===================== AJUSTE POR POSTURA =====================
        if postura != "nenhum":
            if postura in suportes:
                score += 15  #  BONUS
            else:
                score -= 20  # PENALIZAÇÃO

        justificativa = f"Cobre {compatibilidade} necessidades: {', '.join(sorted(suportes & necessidades))}. "
        if forca > 0:
            justificativa += f"Força assistida: {forca:.0f} N. "

        recomendados.append({
            "Modelo": row["nome"],
            "Nível": nivel,
            "Força (N)": round(forca, 1),
            "Peso (kg)": row.get("peso_equipamento", "?"),
            "Compatibilidade": compatibilidade,
            "Score": round(score, 1),
            "Justificativa": justificativa + (row.get("descricao") or "")
        })

    # 4. Ordenar por Score (melhor primeiro)
    recomendados = sorted(recomendados, key=lambda x: x["Score"], reverse=True)

    # 5. Construir texto final
    if not recomendados:
        return (f"Principais necessidades: {', '.join(sorted(necessidades))}\n\n"
                f"Nenhum exoesqueleto compatível encontrado.")

    texto = f"**Análise de Riscos:** {len(eventos)} eventos detetados\n"
    texto += f"**Necessidades identificadas:** {', '.join(sorted(necessidades))}\n\n"
    texto += "**Recomendações Mais Adequadas:**\n\n"

    for r in recomendados[:5]:
        texto += f"• **{r['Modelo']}**  ({r['Nível']}, {r['Força (N)']} N, {r['Peso (kg)']} kg)\n"
        texto += f"  {r['Justificativa']}\n\n"

    if len(recomendados) > 5:
        texto += f"*... e mais {len(recomendados) - 5} modelos compatíveis.*\n"

    return texto