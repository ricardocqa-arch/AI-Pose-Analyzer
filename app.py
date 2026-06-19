import gradio as gr
from database import init_db
from styles import IDR_THEME_CSS


print("🔧 Inicializando base de dados...")
init_db()
print("✅ Base de dados pronta!\n")


from ui import demo

if __name__ == "__main__":
    print("🚀 Iniciando aplicação Gradio...")

    # Tenta várias portas automaticamente
    ports = [7860, 7861, 7862, 7863, 7864, 7865]

    launched = False
    for port in ports:
        try:
            print(f"🔌 Tentando iniciar na porta {port}...")
            demo.launch(
                inbrowser=True,
                theme=gr.themes.Soft(),
                css=IDR_THEME_CSS,
                share=False,
                server_name="127.0.0.1",
                server_port=port,
                show_error=True,
                debug=False
            )
            launched = True
            break
        except OSError:
            print(f"⚠️ Porta {port} ocupada. Tentando próxima...")
            continue

    if not launched:
        print("❌ Não foi possível encontrar uma porta disponível.")