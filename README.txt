  Smart Boutique - Nalú Modas 4.0 🛍️🤖

Sistema de monitoramento e automação IoT integrado a um dashboard web em Flask para gestão ambiental e de fluxo de pessoas na loja Nalú Modas.


    📌 Visão Geral do Projeto

O Smart Boutique é um sistema completo que combina firmware embarcado em um ESP32 com uma aplicação web hospedada no PythonAnywhere. 

O hardware coleta dados de temperatura, umidade e presença (movimento) no ambiente da loja, salvando a contagem de acessos na memória não volátil (Flash) do microcontrolador. Os dados são transmitidos simultaneamente para:
1. Plataforma Blynk Cloud: para monitoramento e alertas em tempo real em dispositivos móveis.
2. Servidor Web Flask (PythonAnywhere): via API HTTP/JSON, alimentando um banco de dados SQLite para exibição em dashboard e análises históricas.


    🛠️ Tecnologias e Ferramentas Utilizadas

    Hardware & Firmware (ESP32)
- Linguagem: C++ / C (Arduino Framework)
- Microcontrolador: ESP32
- Sensores:
  - DHT22 (Pino GPIO 14): Leitura de Temperatura e Umidade.
  - PIR (Pino GPIO 13): Detecção de Presença / Movimento.
- Bibliotecas: WiFi.h, HTTPClient.h, BlynkSimpleEsp32.h, DHT.h, Preferences.h.

    Backend & Web Service
- Linguagem: Python 3
- Framework Web: Flask
- Banco de Dados: SQLite3 (`database.db`)
- Hospedagem Web: PythonAnywhere


    📐 Arquitetura do Sistema

           ┌────────────────────────┐
           │ ESP32 Microcontroller  │
           │ (DHT22 + Sensor PIR)   │
           └───────────┬────────────┘
                       │
         ┌─────────────┴────────────┐
         │                          │
  (HTTP POST / JSON)         (Blynk Protocol)
         │                          │
         ▼                          ▼
┌──────────────────┐         ┌───────────────┐
│ PythonAnywhere   │         │  Blynk Cloud  │
│ (Flask + SQLite) │         │  App Mobile   │
│web site + Mobile │         └───────────────┘
└──────────────────┘



Conexões do Hardware (ESP32)
GPIO 13: Sinal do Sensor PIR (Presença)
GPIO 14: Sinal do Sensor DHT22 (Clima)


    📡 Mapeamento de Pinos e Portas Virtuais (Blynk)
Pin out Virtual - Blynk App
V1: LED/Indicador de Movimento (0 = Sem movimento, 255 = Movimento)
V2: Display / Contagem acumulada de presença
V3: Display de Temperatura (°C)
V4: Display de Umidade (%)

    🚀 Como Rodar o Código do ESP32 (Arduino IDE / PlatformIO)
Abra o arquivo Código_ESP32 no seu ambiente de desenvolvimento (Arduino IDE ou VS Code com PlatformIO).

Instale as dependências necessárias pelas bibliotecas do gerenciador:

Blynk
DHT sensor library
Adafruit Unified Sensor

Atualize as credenciais de rede no código:

C++
char ssid[] = "SUA_REDE_WIFI";
char pass[] = "SUA_SENHA_WIFI";
Se necessário, ajuste os tokens da Blynk Cloud (BLYNK_TEMPLATE_ID, BLYNK_AUTH_TOKEN).

Conecte o ESP32 via USB e selecione a placa ESP32 Dev Module.

Compile e faça o upload para a placa.

    🔐 Segurança das Credenciais
Atenção: Lembre-se de nunca subir dados sensíveis de produção (senhas de Wi-Fi pessoais ou tokens privados) em repositórios públicos. 
Use marcadores genéricos ou variáveis de ambiente para preservar a segurança das redes.

    👨‍💻 Autores
Desenvolvido por:

Alunos da faculdade UNIVESP-EAD de engenharia de computação, em desenvolvimento ao Projeto Integrador 6: 2°semestre de 2026
Turma de 2022 - T22 - Grupo 16

Alunos:  
        Adaumir A. Dos Santos
        Ana Paula Ap. Pedroso
        Anderson Fco Da Silva
        Brenda N. S. Machado
        Daniel dos S. Lopes
        Gabriela De M. Saqui
        Marcelo S. Pereira
        Wainer De P. Dias


Sob orientação da coordenadora Aline Santos, a quem somos imensamente gratos pela paciência e pela atenção com o grupo.
