#define BLYNK_TEMPLATE_ID           "TMPL21IHddvV3"
#define BLYNK_TEMPLATE_NAME         "Sensor de Presença"
#define BLYNK_AUTH_TOKEN            "jZHL-64e662LXQDgyQ0ZH5WPAdcdCp3l"

#define BLYNK_PRINT Serial

#include <WiFi.h>
#include <WiFiClient.h>
#include <BlynkSimpleEsp32.h>
#include <HTTPClient.h>
#include <DHT.h>
#include <Preferences.h> // Biblioteca para salvar dados na Flash

// --- CONFIGURAÇÃO DE WIFI ---
char ssid[] = "SUA_REDE_WIFI"; 
char pass[] = "SUA_SENHA_WIFI"; 

// --- PINOS E SENSORES ---
#define PIR_PIN 13        // Pino de dados PIR Presenca
#define DHTPIN 14        // Pino de dados do DHT22 TEMP e UMID
#define DHTTYPE DHT22    

DHT dht(DHTPIN, DHTTYPE);
Preferences preferences;

// Variáveis de controle de Presença
int contadorPresenca = 0;
bool movimentoDetectado = false;

// URL da API no PythonAnywhere
const char* serverName = "http://nalumodas.pythonanywhere.com/api/dados";

BlynkTimer timer;

// Função para ler o DHT22, enviar ao Blynk e também ao Servidor Web (PythonAnywhere)
void enviarClima() {
  float h = dht.readHumidity();
  float t = dht.readTemperature();

  if (isnan(h) || isnan(t)) {
    Serial.println("Falha ao ler o sensor DHT22!");
    return;
  }

  // 1. Envia para os pinos virtuais V3 (Temp) e V4 (Umi) do Blynk
  Blynk.virtualWrite(V3, t);
  Blynk.virtualWrite(V4, h);
  
  Serial.printf("Temp: %.1f°C | Umi: %.1f%%\n", t, h);

  // 2. Envia os dados via HTTP POST para o PythonAnywhere
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverName);
    http.addHeader("Content-Type", "application/json");

    String httpRequestData = "{\"temperatura\":" + String(t) + ",\"umidade\":" + String(h) + "}";

    int codigoResposta = http.POST(httpRequestData);

    if (codigoResposta > 0) {
      Serial.print("Dados enviados ao PythonAnywhere. Código HTTP: ");
      Serial.println(codigoResposta);
    } else {
      Serial.print("Erro no envio web. Código: ");
      Serial.println(codigoResposta);
    }
    
    http.end();
  } else {
    Serial.println("WiFi desconectado!");
  }
}

// Função para verificar o Sensor de Presença PIR
void verificarSensor() {
  int leitura = digitalRead(PIR_PIN);

  if (leitura == HIGH && !movimentoDetectado) {
    Serial.println("ALERTA: Movimento detectado!");
    
    contadorPresenca++; 
    
    // Salva o novo valor do contador na memória Flash
    preferences.putInt("contador", contadorPresenca);
    
    Blynk.virtualWrite(V1, 255);        
    Blynk.virtualWrite(V2, contadorPresenca); 
    
    movimentoDetectado = true; 
  } 
  else if (leitura == LOW && movimentoDetectado) {
    Serial.println("Status: Movimento encerrado.");
    Blynk.virtualWrite(V1, 0); 
    movimentoDetectado = false; 
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(PIR_PIN, INPUT);
  dht.begin();

  // Inicia a memória Flash no modo leitura/escrita (false)
  preferences.begin("projeto", false);

  // Recupera o valor salvo. Se não existir, assume 0.
  contadorPresenca = preferences.getInt("contador", 0);

  Serial.println("\n--- Iniciando Sistema IoT Unificado ---");
  Serial.print("Contador recuperado: ");
  Serial.println(contadorPresenca);
  
  // Inicializa o Blynk (que já cuida da conexão WiFi de forma integrada)
  Blynk.begin(BLYNK_AUTH_TOKEN, ssid, pass);

  // Sincroniza o valor do contador com o App assim que conecta
  Blynk.virtualWrite(V2, contadorPresenca);

  // Timers: Presença (200ms) e Clima/PythonAnywhere (a cada 10 segundo)
  timer.setInterval(200L, verificarSensor);
  timer.setInterval(10000L, enviarClima);
}

void loop() {
  Blynk.run();
  timer.run();
}