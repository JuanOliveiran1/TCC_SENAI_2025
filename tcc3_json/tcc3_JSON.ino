// --- Pinos ---
const int ledPin = 8;      // LED indicador
const int buzzerPin = 7;
const int relePin = 6;     // Relé → Lâmpada

// --- Limites ---
const float limiteTempLED = 100.0;
const float tempMaxFaixa = 180.0; 
const float tempMinFaixa = 175.0; 
const float tempMin = 25.0;

// --- Variáveis ---
float tempCelsius = 25.0;
bool subindo = true;
bool cicloCompleto = false;
bool releLigado = true;
int ciclosManutencao = 0;          
const int maxCiclosManutencao = 2;

void setup() {
  Serial.begin(9600);

  pinMode(ledPin, OUTPUT);
  pinMode(buzzerPin, OUTPUT);
  pinMode(relePin, OUTPUT);

  digitalWrite(relePin, HIGH);
  releLigado = true;

  enviarJSON("STARTUP", "Sistema iniciado");
  delay(300);
}

void loop() {

  if (!cicloCompleto) {

    // --- Aquecimento rápido inicial ---
    if (subindo && ciclosManutencao == 0 && tempCelsius < tempMaxFaixa) {
      tempCelsius += 12;

      if (tempCelsius >= tempMaxFaixa) {
        tempCelsius = tempMaxFaixa;
        releLigado = false;
        digitalWrite(relePin, LOW);
        subindo = false;
      }
    }

    // --- Oscilação 175 ↔ 180 ---
    else {
      if (subindo) {
        tempCelsius += 2;
        if (tempCelsius >= tempMaxFaixa) {
          tempCelsius = tempMaxFaixa;
          releLigado = false;
          digitalWrite(relePin, LOW);
          subindo = false;
        }
      } else {
        tempCelsius -= 2;

        if (tempCelsius <= tempMinFaixa) {
          tempCelsius = tempMinFaixa;
          ciclosManutencao++;

          if (ciclosManutencao < maxCiclosManutencao) {
            releLigado = true;
            digitalWrite(relePin, HIGH);
            subindo = true;
          } else {
            releLigado = true;
            digitalWrite(relePin, HIGH);
            subindo = false;
            cicloCompleto = true;
            enviarJSON("EVENTO", "Ciclo de manutencao concluido");
          }
        }
      }
      delay(50);
    }
  }

  // -----------------------------------
  //        RESFRIAMENTO FINAL
  // -----------------------------------
  else {
    enviarJSON("EVENTO", "CICLO_COMPLETO");

    for (float t = tempCelsius; t > tempMin; t -= 50.0) {
      tempCelsius = t;

      enviarJSONEstado("RESFRIANDO");

      digitalWrite(ledPin, LOW);
      digitalWrite(relePin, LOW);
      delay(100);
    }

    enviarJSON("EVENTO", "RESFRIAMENTO_CONCLUIDO");

    // --- Alerta final ---
    for (int i = 0; i < 5; i++) {
      digitalWrite(buzzerPin, HIGH);
      digitalWrite(relePin, HIGH);
      digitalWrite(ledPin, HIGH);
      delay(300);
      digitalWrite(buzzerPin, LOW);
      digitalWrite(relePin, LOW);
      digitalWrite(ledPin, LOW);
      delay(300);
    }

    enviarJSON("EVENTO", "PROCESSO_FINALIZADO");

    while (true);
  }

  // --- LED indicador ---
  digitalWrite(ledPin, tempCelsius >= limiteTempLED ? HIGH : LOW);

  // --- JSON contínuo durante o processo ---
  enviarJSONEstado(subindo ? "AQUECENDO" : "OSCILACAO");

  delay(150);
}



// --------------------------------------------------------------
//              Funções auxiliares para gerar JSON
// --------------------------------------------------------------

void enviarJSON(const char* tipo, const char* mensagem) {
  Serial.print("{\"tipo\":\"");
  Serial.print(tipo);
  Serial.print("\",\"msg\":\"");
  Serial.print(mensagem);
  Serial.println("\"}");
}

void enviarJSONEstado(const char* estado) {
  Serial.print("{");
  Serial.print("\"temperatura\":");
  Serial.print(tempCelsius, 1);
  Serial.print(",\"rele\":\"");
  Serial.print(releLigado ? "ON" : "OFF");
  Serial.print("\",\"estado\":\"");
  Serial.print(estado);
  Serial.println("\"}");
}
