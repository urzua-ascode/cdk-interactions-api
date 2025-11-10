import os
    import boto3
    import json
    import base64
    from boto3.dynamodb.conditions import Key
    
    # --- Configuración de DynamoDB ---
    
    # El nombre de la tabla se pasará como variable de entorno desde el CDK
    TABLE_NAME = os.environ.get("INTERACTIONS_TABLE_NAME", "Interactions")
    # Usamos el cliente de boto3 estándar (se conecta a AWS)
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(TABLE_NAME)
    
    # --- Formateadores de Respuesta ---
    
    def create_response(status_code, body):
        """Crea una respuesta HTTP para API Gateway."""
        if not isinstance(body, str):
            body = json.dumps(body)
            
        return {
            "statusCode": status_code,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*" # CORS (opcional)
            },
            "body": body
        }
    
    # --- Handler Principal de Lambda ---
    
    def handler(event, context):
        """
        Punto de entrada para la Lambda.
        Se activa por API Gateway.
        """
        print(f"Evento recibido: {event}")
    
        try:
            # --- Extracción de Parámetros ---
            
            # De pathParameters
            account_number = event.get('pathParameters', {}).get('account_number')
            if not account_number:
                return create_response(400, {"detail": "account_number es requerido"})
    
            # De queryStringParameters
            params = event.get('queryStringParameters') or {}
            limit = int(params.get('limit', 10))
            cursor = params.get('cursor')
            from_date = params.get('from')
            to_date = params.get('to')
    
            # Validar límite
            limit = max(1, min(limit, 100))
    
            # --- Lógica de Consulta (idéntica a FastAPI) ---
            
            query_params = {
                'Limit': limit,
                'ScanIndexForward': False # Más reciente primero
            }
    
            key_condition = Key('account_number').eq(account_number)
    
            if from_date and to_date:
                key_condition = key_condition & Key('timestamp').between(from_date, to_date)
            elif from_date:
                key_condition = key_condition & Key('timestamp').gte(from_date)
            elif to_date:
                key_condition = key_condition & Key('timestamp').lte(to_date)
    
            query_params['KeyConditionExpression'] = key_condition
    
            # --- Lógica de Paginación ---
            
            if cursor:
                try:
                    decoded_key = base64.urlsafe_b64decode(cursor.encode('utf-8'))
                    query_params['ExclusiveStartKey'] = json.loads(decoded_key.decode('utf-8'))
                except Exception as e:
                    print(f"Cursor inválido: {e}")
                    return create_response(400, {"detail": "Cursor de paginación inválido"})
    
            # --- Ejecutar Consulta ---
            
            response = table.query(**query_params)
            items = response.get('Items', [])
    
            # --- Preparar Siguiente Cursor ---
            
            next_cursor = None
            if 'LastEvaluatedKey' in response:
                next_cursor = base64.urlsafe_b64encode(
                    json.dumps(response['LastEvaluatedKey']).encode('utf-8')
                ).decode('utf-8')
    
            # --- Construir Respuesta Final ---
            
            api_response = {
                "account_number": account_number,
                "items": items,
                "next_cursor": next_cursor
            }
            
            return create_response(200, api_response)
    
        except Exception as e:
            print(f"Error inesperado: {e}")
            return create_response(500, {"detail": "Error interno del servidor"})