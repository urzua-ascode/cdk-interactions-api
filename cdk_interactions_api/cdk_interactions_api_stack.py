from aws_cdk import (
    Stack,
    RemovalPolicy,
    CfnOutput,
    Duration,
    aws_dynamodb as dynamodb,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
)
from constructs import Construct

class CdkInteractionsApiStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # --- 1. Definir la Base de Datos DynamoDB ---
        # Cumple con el modelo de datos (PK: account_number, SK: timestamp)
        
        interactions_table = dynamodb.Table(
            self, "InteractionsTable",
            table_name="Interactions", # Nombre fijo de la tabla
            partition_key=dynamodb.Attribute(
                name="account_number",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="timestamp",
                type=dynamodb.AttributeType.STRING
            ),
            # Usar PAY_PER_REQUEST (Serverless) como se recomienda
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            
            # Política de destrucción: Eliminar la tabla al destruir el stack
            # (NO USAR EN PRODUCCIÓN)
            removal_policy=RemovalPolicy.DESTROY
        )

        # --- 2. Definir la Función Lambda ---
        
        api_lambda = _lambda.Function(
            self, "ApiLambdaHandler",
            runtime=_lambda.Runtime.PYTHON_3_11,
            # Directorio que contiene el código
            code=_lambda.Code.from_asset("lambda"),
            # Archivo y función a ejecutar
            handler="app.handler",
            timeout=Duration.seconds(10),
            memory_size=256,
            environment={
                # Pasar el nombre de la tabla a la Lambda
                "INTERACTIONS_TABLE_NAME": interactions_table.table_name
            }
        )

        # --- 3. Conceder Permisos ---
        
        # Dar permisos a la Lambda para LEER (Query) de la tabla
        interactions_table.grant_read_data(api_lambda)

        # --- 4. Definir el API Gateway ---
        
        api = apigw.LambdaRestApi(
            self, "InteractionsApiEndpoint",
            handler=api_lambda,
            # Usar un proxy simple. 
            # Las rutas se manejan en el código de Lambda (o FastAPI)
            # Pero para este caso, definimos la ruta explícitamente.
            proxy=False,
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=apigw.Cors.ALL_ORIGINS,
                allow_methods=apigw.Cors.ALL_METHODS
            )
        )
        
        # Definir el recurso: /interactions
        interactions_resource = api.root.add_resource("interactions")
        
        # Definir el recurso: /interactions/{account_number}
        account_resource = interactions_resource.add_resource("{account_number}")
        
        # Añadir el método GET a /interactions/{account_number}
        account_resource.add_method("GET") # Se integra con 'api_lambda'

        # --- 5. Salida (Output) ---
        
        # Imprimir la URL de la API en la consola al finalizar el deploy
        CfnOutput(
            self, "ApiUrlOutput",
            value=api.url,
            description="La URL base de la API de Interacciones"
        )