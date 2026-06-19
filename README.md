
# 🔎 AI Pose Analyzer (Ergonomics & Computer Vision)

O **AI Pose Analyzer** é uma ferramenta de visão computacional desenvolvida em Python que automatiza a análise ergonómica de posturas em ambiente laboral, sugerindo soluções de exoesqueletos com base em riscos detetados.

## 🚀 Funcionalidades Principais
* **Deteção Postural 3D:** Rastreamento de 33 marcos anatómicos corporais em tempo real através do pipeline BlazePose da Google (MediaPipe).
* **Análise de Riscos Ergonómicos:** Monitorização contínua de ângulos críticos de flexão de tronco, ombros, joelhos e pescoço com regras de sensibilidade customizáveis.
* **Motor de Recomendação:** Filtra e sugere modelos ideais de exoesqueletos recorrendo a algoritmos baseados em cruzamento de dados de bases SQLite relacionais.
* **Painel de Gestão:** Interface desktop dinâmica nativa em Gradio com CRUD completo para gerir o portfólio de equipamentos disponíveis.

## 🛠️ Tecnologias Utilizadas
* **Linguagem:** Python 3.11
* **Visão Computacional:** MediaPipe & OpenCV
* **Interface Gráfica:** Gradio
* **Base de Dados:** SQLite & Pandas
* **Compilação:** PyInstaller (Criação de executáveis portáveis de ambiente local)

## 📦 Como Executar
1. Instale as dependências: `pip install -r requirements.txt`
2. Execute a aplicação: `python app.py`
