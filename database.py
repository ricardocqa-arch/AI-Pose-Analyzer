
from paths import resource_path
from config import DB_PATH, TAGS_OFICIAIS

import sqlite3
import pandas as pd
import os
import shutil  # <-- Adicionado para permitir copiar o ficheiro real
from paths import resource_path
from config import DB_PATH, TAGS_OFICIAIS


# ===================== SQLITE - PORTFÓLIO EXOESQUELETOS =====================

def init_db():
    # 1. Descobrir onde está o executável real no PC do utilizador
    # Se correr no PyInstaller, o ficheiro final deve ficar ao lado do .exe
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Se o ficheiro .db não existir fisicamente ao lado do .exe, vamos criá-lo a partir do original
    if not os.path.exists(DB_PATH):
        print("🔧 Primeira execução detectada ou base de dados em falta...")
        try:
            # Encontra o caminho do ficheiro embutido dentro do pacote PyInstaller
            db_original_empacotado = resource_path('exoskeletons.db')

            if os.path.exists(db_original_empacotado):
                # Copia o ficheiro cheio de dados para a pasta onde o utilizador pode escrever
                shutil.copy2(db_original_empacotado, DB_PATH)
                print("✅ Base de dados com registos importada com sucesso!")
        except Exception as e:
            print("⚠️ Não foi possível copiar a base de dados preenchida, criando uma nova:", e)

    # 2. Agora liga-se normalmente ao caminho de escrita correto
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # ===================== GARANTIR QUE A TABELA EXISTE =====================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS exos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                protecao TEXT,
                nivel_assistencia TEXT,
                forca_assistida_newton REAL,
                peso_equipamento REAL,
                descricao TEXT,
                indicado_para TEXT
            )
        """)
        conn.commit()

        # ===================== VERIFICAR SE A TABELA TEM DADOS =====================
        try:
            cursor.execute("SELECT COUNT(*) FROM exos")
            result = cursor.fetchone()
            count = result[0] if result else 0
        except Exception as e:
            print("⚠️ Erro ao contar registos:", e)
            count = 0

        # ===================== INSERIR DADOS INICIAIS APENAS SE TUDO FALHAR =====================
        if count == 0:
            print("📊 Tabela vazia de segurança. Inserindo dados mínimos...")

            dados_iniciais = [
                ("JAPET.W+", "lombar,costas,levantamento", "alto", 250, 3.0,
                 "Exoesqueleto motorizado que protege a região lombar, reduz impacto na coluna e auxilia levantamento de cargas.",
                 "Flexão Excessiva de Tronco"),

                ("Muscle Suit Soft Power", "lombar,costas", "médio", 35, 0.43,
                 "Exoesqueleto têxtil ultra leve que reduz tensão lombar e distribui esforço corporal.",
                 "Flexão Excessiva de Tronco"),

                ("Muscle Suit Every", "lombar,costas,levantamento", "alto", 250, 3.8,
                 "Exoesqueleto pneumático potente para levantamento até 25kg, ideal para uso intensivo.",
                 "Flexão Excessiva de Tronco")
            ]

            cursor.executemany("""
                INSERT INTO exos 
                (nome, protecao, nivel_assistencia, forca_assistida_newton, peso_equipamento, descricao, indicado_para)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, dados_iniciais)

            conn.commit()
            print(f"✅ {len(dados_iniciais)} registos iniciais inseridos de emergência.")

        else:
            print(f"✅ Tabela mapeada com sucesso! Contém {count} registos válidos.")

    except sqlite3.Error as e:
        print("❌ Erro crítico na base de dados:", e)

    finally:
        conn.close()

def load_portfolio():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM exos", conn)
    conn.close()
    return df


def save_portfolio(df):
    """Atualiza apenas a normalização das tags. Não recria a tabela."""
    if df is None or df.empty:
        return df

    df = validar_e_normalizar_protecao(df)

    conn = sqlite3.connect(DB_PATH)

    df.to_sql("exos", conn, if_exists="replace", index=False)
    conn.close()

    print("Alterações guardadas (proteção normalizada).")
    return df


def validar_e_normalizar_protecao(df):
    if df is None or df.empty:
        return df

    def clean_tags(tags_str):
        if pd.isna(tags_str) or not tags_str:
            return ""
        tags = [t.strip().lower() for t in str(tags_str).split(",")]
        valid_tags = [t for t in tags if t in [tag.lower() for tag in TAGS_OFICIAIS]]
        return ", ".join(sorted(set(valid_tags)))

    df["protecao"] = df["protecao"].apply(clean_tags)
    return df