
# Welcome to your CDK Python project!

Despliegue en AWS (AWS CDK)
Esta implementación despliega la infraestructura serverless en tu cuenta de AWS.
Prerrequisitos
AWS CLI configurada (aws configure)
Node.js y npm
AWS CDK (npm install -g aws-cdk)
Python 3.10+
Pasos
Mover al directorio de CDK:
cd cdk-interactions-api


Instalar dependencias y activar entorno virtual:
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt


Bootstrap (Solo la primera vez):
cdk bootstrap


Desplegar el Stack:
cdk deploy


Cargar Datos de Prueba:
Una vez desplegado, ve a la consola de AWS -> DynamoDB -> Tablas -> Interactions.
Crea manualmente los elementos de prueba (ver load_data.py como referencia).
Probar la API Desplegada:
Obtén la URL de la API de la salida de cdk deploy.
API_URL="<pega_tu_url_de_api_gateway_aqui>"

curl -X GET "$API_URL/interactions/123456789"




## Architecture Diagram

```mermaid
graph TB
    A["Developer"] -->|Code| B["GitHub<br/>Repository"]
    B -->|Trigger| C["AWS CDK<br/>Stack"]
    C -->|Deploy| D["CloudFormation<br/>Stack"]
    
    D -->|Create| E["API Gateway<br/>REST API"]
    D -->|Create| F["Lambda<br/>Functions"]
    D -->|Create| G["DynamoDB<br/>Table"]
    
    E -->|Invoke| F
    F -->|Read/Write| G
    
    H["Client"] -->|HTTP Request| E
    E -->|Response| H
    
    F -->|Log| I["CloudWatch<br/>Logs"]
    
    style A fill:#e1f5ff
    style B fill:#f3e5f5
    style C fill:#fff9c4
    style D fill:#ffe0b2
    style E fill:#c8e6c9
    style F fill:#c8e6c9
    style G fill:#c8e6c9
    style H fill:#e1f5ff
    style I fill:#fce4ec
```
