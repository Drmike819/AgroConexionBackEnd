# parse_qs: convierte un query string ('a=1&b=2') en un dict {'a': ['1'], 'b': ['2']}
from urllib.parse import parse_qs
# decorator para ejecutar funciones síncronas de BD desde código async (usa un threadpool)
from channels.db import database_sync_to_async
# valida un JWT sin distinguir access/refresh (lanza si es inválido) 
from rest_framework_simplejwt.tokens import UntypedToken
# excepciones de SimpleJWT cuando el token no es válido
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
# representa a un usuario no autenticado
from django.contrib.auth.models import AnonymousUser 
# obtiene el modelo de usuario configurado (CustomUser si existe) 
from django.contrib.auth import get_user_model         

# alias al modelo de usuario usado en el proyecto
CustomUser = get_user_model()                         

# Función auxiliar para obtener usuario desde el token
@database_sync_to_async
def get_user_from_validated_token(validated_token):
    # extrae la claim 'user_id' del token validado
    user_id = validated_token.get('user_id') 
     
    # si no hay 'user_id' en el token, devuelve AnonymousUser         
    if not user_id:
        return AnonymousUser()                         
    try:
        # intenta buscar el usuario en la base de datos por id
        return CustomUser.objects.get(id=user_id)   
    # si no existe el usuario (fue eliminado), devuelve AnonymousUser   
    except CustomUser.DoesNotExist:
        return AnonymousUser()                         


# Middleware estilo "factory" (usado envolviendo el inner app)
class JWTAuthMiddleware:
    def __init__(self, inner):
        # 'inner' es la app ASGI siguiente (p. ej. URLRouter)
        self.inner = inner                              

    # firma ASGI: recibe scope, receive y send
    async def __call__(self, scope, receive, send):  
        # parsea query_string (viene en bytes), devuelve dict   
        query_string = parse_qs(scope.get("query_string", b"").decode())
        # toma el primer valor de ?token=... o None si no existe
        token = query_string.get("token", [None])[0]    

        # si no vino token por query string, buscar en headers
        if not token:                                   
            # scope['headers'] es una lista de tuplas (b'header-name', b'value'), por eso decodificamos
            headers = dict((k.decode(), v.decode()) for k, v in scope.get("headers", []))
            # intenta obtener el header 'authorization'
            auth_header = headers.get("authorization", "")  
             # si tiene esquema Bearer, extraer el token
            if auth_header.startswith("Bearer "):         
                token = auth_header.split("Bearer ")[1]

        # si ya tenemos un token (query o header)
        if token:                                       
            try:
                # valida firma/expiración; lanza InvalidToken/TokenError si falla
                validated_token = UntypedToken(token)   
                # busca usuario en BD y lo asigna al scope
                scope['user'] = await get_user_from_validated_token(validated_token)  
                # print de debugging (puedes quitarlo en producción)
                print("✅ Token válido, usuario:", scope['user'])  
            except (InvalidToken, TokenError):
                # token inválido -> marcar como anónimo
                scope['user'] = AnonymousUser()        
        else:
            # no vino token -> usuario anónimo
            scope['user'] = AnonymousUser()            
        # seguir la cadena ASGI con el scope modificado
        return await self.inner(scope, receive, send)  


# Variante "instance" (otro patrón de middleware)
class JWTAuthMiddlewareInstance:
    def __init__(self, scope, middleware):
        # guarda el scope (este patrón crea una instancia por scope)
        self.scope = scope        
        # guarda referencia al middleware padre                      
        self.middleware = middleware                    

     # firma ASGI; ojo: en este código se usa self.scope en lugar del parámetro scope
    async def __call__(self, scope, receive, send):   
        # Intentar leer token desde query string (usando self.scope)
        query_string = parse_qs(self.scope.get("query_string", b"").decode())
        # primer token de la query o None
        token = query_string.get("token", [None])[0]   

        # Si no viene en query string, buscar en headers
        if not token:
            headers = dict((k.decode(), v.decode()) for k, v in self.scope.get("headers", []))
            auth_header = headers.get("authorization", "")
            if auth_header.startswith("Bearer "):
                token = auth_header.split("Bearer ")[1]

        if token:
            try:
                # valida el token
                validated_token = UntypedToken(token)   
                # asigna usuario encontrado al scope
                self.scope['user'] = await get_user_from_validated_token(validated_token)  
                print("✅ Token válido, usuario:", self.scope['user'])
            except (InvalidToken, TokenError):
                # token inválido -> anónimo
                self.scope['user'] = AnonymousUser()    
        else:
            # sin token -> anónimo
            self.scope['user'] = AnonymousUser()        
        # obtiene la app interna pasando el scope (patrón Channels)
        inner = self.middleware.inner(self.scope)   
        # ejecuta la app interna con receive/send   
        return await inner(receive, send)               