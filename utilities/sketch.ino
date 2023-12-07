/*
Entrega final e projeto extensionista da disciplina de Internet das Coisa. 2023/2
Professor: Rodolfo Stoffel
Grupo:  Guilherme dos Santos Francisco
        Jorge Jr.
        Julian Casali
        Lucas Heim
        Yasmin Moraes da Silva

Comentários e outras informações ao fim do código
*/
#include "HX711.h"
#include <PubSubClient.h>
#include <WiFi.h>

#define DATA_IN_D 1
#define DATA_IN_E 3
#define BOTAO 4
#define SCK 2
#define TOPIC "IOT/MEDE_CARGA"
#define ID_MQTT "esp32_mqtt" // id mqtt (para identificação de sessão)

// variaveis globais
// iniciando o sensor
HX711 balanca_direita, balanca_esquerda;
// pesagem
float fator_conversao = 420.0; // obtido empiricamente: valor adc/peso escolhido na interface.
float peso_direita = 0.0;
float peso_esquerda = 0.0;
// transmissão de dados
const char *SSID = "Wokwi-GUEST";              // SSID / nome da rede WI-FI que deseja se conectar
const char *PASSWORD = "";                     // Senha da rede WI-FI que deseja se conectar
const char *BROKER_MQTT = "broker.hivemq.com"; // URL do broker MQTT que se deseja utilizar
int BROKER_PORT = 1883;                        // Porta do Broker MQTT
char msg_full[16] = {0};                       // payload
WiFiClient espClient;                          // Cria o objeto espClient
PubSubClient MQTT(espClient);                  // Instancia o Cliente MQTT passando o objeto espClient

// funções extra
/* Inicializa e conecta-se na rede WI-FI desejada */
void initWiFi(void)
{
  delay(10);
  Serial.println("------Conexao WI-FI------");
  Serial.print("Conectando-se na rede: ");
  Serial.println(SSID);
  Serial.println("Aguarde");

  reconnectWiFi();
}

/* Inicializa os parâmetros de conexão MQTT(endereço do broker, porta) */
void initMQTT(void)
{
  MQTT.setServer(BROKER_MQTT, BROKER_PORT); // Informa qual broker e porta deve ser conectado
  // caso necessário, o set da função de callback entra aqui
}

/* Reconecta-se ao broker MQTT*/
void reconnectMQTT(void)
{
  while (!MQTT.connected())
  {
    Serial.print("* Tentando se conectar ao Broker MQTT: ");
    Serial.println(BROKER_MQTT);
    if (MQTT.connect(ID_MQTT))
    {
      Serial.println("Conectado com sucesso ao broker MQTT!");
    }
    else
    {
      Serial.println("Falha ao reconectar no broker.");
      Serial.println("Nova tentativa de conexao em 2 segundos.");
      delay(2000);
    }
  }
}

/* Verifica o estado das conexões WiFI e ao broker MQTT.
  Em caso de desconexão (qualquer uma das duas), a conexão é refeita. */
void checkWiFIAndMQTT(void)
{
  if (!MQTT.connected())
    reconnectMQTT(); // se não há conexão com o Broker, a conexão é refeita

  reconnectWiFi(); // se não há conexão com o WiFI, a conexão é refeita
}

void reconnectWiFi(void)
{
  // se já está conectado a rede WI-FI, nada é feito.
  // Caso contrário, são efetuadas tentativas de conexão
  if (WiFi.status() == WL_CONNECTED)
    return;

  WiFi.begin(SSID, PASSWORD); // Conecta na rede WI-FI

  while (WiFi.status() != WL_CONNECTED)
  {
    delay(100);
    Serial.print(".");
  }

  Serial.println();
  Serial.print("Conectado com sucesso na rede ");
  Serial.print(SSID);
  Serial.println("IP obtido: ");
  Serial.println(WiFi.localIP());
}

void setup()
{
  // put your setup code here, to run once:
  Serial.begin(115200);
  balanca_direita.begin(DATA_IN_D, SCK);
  balanca_esquerda.begin(DATA_IN_E, SCK);
  pinMode(BOTAO, INPUT);
  // Inicializa a conexao Wi-Fi
  initWiFi();
  // Inicializa a conexao ao broker MQTT
  initMQTT();
}

void loop()
{
  // put your main code here, to run repeatedly:
  Serial.print("Aguardando nova medição...\n");
  checkWiFIAndMQTT();
  peso_direita = balanca_direita.read() / fator_conversao;
  peso_esquerda = balanca_esquerda.read() / fator_conversao;
  if (peso_direita <= 0)
  {
    Serial.println("Falha na balança direita!");
  }
  else if (peso_esquerda <= 0)
  {
    Serial.println("Falha na balança esquerda!");
  }
  else
  {
    sprintf(msg_full, "D;%.2f;E;%.2f\0", peso_direita, peso_esquerda);
    MQTT.publish(TOPIC, msg_full);
    MQTT.loop();
    Serial.println("Dados adquiridos e enviados!");
  }

  delay(3500); // this speeds up the simulation
}

/*
Fontes:
https://www.youtube.com/watch?v=GE13ovG3omw
https://www.youtube.com/watch?v=7eweZU6JTbw
https://www.youtube.com/watch?v=0YAz9q42uzE
https://www.youtube.com/watch?v=Ehk7Zh043Cw
https://www.youtube.com/watch?v=0btGnLHdv8I
https://cdn.sparkfun.com/datasheets/Sensors/ForceFlex/hx711_english.pdf

E materiais de aula!

Este protótipo possui uma série de abstrações em relação a um cenário real.
É preciso fazer a calibração do sensor e a tara da balança. Para tal, novas funções precisam ser desenvolvidas.
Para maior precisão, é possível implementar um clock externo ao HX711, assim como aumentar a sua velocidade de aquisição.
Ambos são intervenções de hardware, que fogem a capacidade de simulação.
Também é preciso implementar um filtro em software. Mas como a relação de dados da simulação é ideal - linear - este foi abstraido.
Por segurança, considere células de carga com capacidade superior a 50kg.
Para medição de carga específica em pontos diferentes nos pés, é preciso implementar vários HX711 ou um multiplexador de dados para as células de carga.
Ou alguma espécie de chaveamento entre elas.
Auto teste e leds indicativos de status podem ser adicionados para aprimorar a interface com o usuário final.

*/
