# TCC_SENAI_2025

<img src="https://github.com/JuanOliveiran1/TCC_SENAI_2025/blob/main/TCC_v1.gif" width="600" height="400" />

# **(Passo a passo de instalação e execução)**

Vou fornecer o passo a passo aqui (coloque em README.md):

Requisitos

Python 3.9+ (recomendado 3.11)

Arduino conectado e enviando JSON na Serial (baud 9600)

pip

Passo a passo (Linux / macOS / Windows WSL)

Clone / copie o projeto:

git clone <seu-repo> arduino-dashboard
cd arduino-dashboard


Crie e ative um ambiente virtual:

Linux / macOS:

python3 -m venv .venv
source .venv/bin/activate


Windows (cmd):

python -m venv .venv
.venv\Scripts\activate


Instale dependências:

pip install --upgrade pip
pip install -r requirements.txt


Configurar porta serial (opcional):

Edite streamlit_app.py ou informe a porta pela sidebar do app.

Em Linux portas típicas: /dev/ttyUSB0 ou /dev/ttyACM0

Em Windows: COM3, COM4, etc.

Rodar o painel (Streamlit):

streamlit run streamlit_app.py


O browser abrirá automaticamente (geralmente http://localhost:8501).

Teste:

Abra o Serial Monitor (IDE do Arduino) desligado (a porta não pode ser usada por dois programas ao mesmo tempo) e verifique se o Arduino envia JSONs como nas respostas anteriores.

Se estiver com problemas, use um programa serial (PuTTY, minicom) para ver o que chega.

Exemplo de JSON enviado pelo Arduino (recap)
{"temperatura":180.0,"rele":"ON","estado":"OSCILACAO"}
{"tipo":"EVENTO","msg":"CICLO_COMPLETO"}

Sugestões e melhorias futuras

Adicionar timestamps no Arduino (ex.: "ts": 1700000000) para maior precisão.

Salvar histórico em arquivo CSV para posterior análise.

Exportar como serviço (systemd / Docker) para produção.

Usar MQTT em vez de Serial se o Arduino for ESP32/ESP8266 com Wi-Fi.


Implementar controles remotos (botões no Streamlit que enviam comandos de volta via Serial).
