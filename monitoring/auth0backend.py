import requests
from social_core.backends.oauth import BaseOAuth2


class Auth0(BaseOAuth2):
    """Auth0 OAuth authentication backend"""
    name = 'auth0'
    SCOPE_SEPARATOR = ' '
    ACCESS_TOKEN_METHOD = 'POST'
    EXTRA_DATA = [
        ('picture', 'picture')
    ]

    def authorization_url(self):
        """Return the authorization endpoint."""
        return "https://" + self.setting('DOMAIN') + "/authorize"

    def access_token_url(self):
        """Return the token endpoint."""
        return "https://" + self.setting('DOMAIN') + "/oauth/token"

    def get_user_id(self, details, response):
        """Return current user id."""
        return details['user_id']

    def get_user_details(self, response):
        url = 'https://' + self.setting('DOMAIN') + '/userinfo'
        headers = {'authorization': 'Bearer ' + response['access_token']}
        resp = requests.get(url, headers=headers)
        userinfo = resp.json()
        
        return {
            'username': userinfo['nickname'],
            'first_name': userinfo['name'],
            'picture': userinfo['picture'],
            'user_id': userinfo['sub']
        }


# Función independiente fuera de la clase Auth0
def getRole(request):
    user = request.user
    
    # 1. Manejar superusuarios
    if user.is_superuser:
        return "Medico"  # O el rol que desees asignar a los superusuarios
    
    # 2. Usuarios normales (Auth0)
    try:
        # Evitar IndexError usando .get() en lugar de [0]
        auth0user = user.social_auth.get(provider="auth0")
    except user.social_auth.model.DoesNotExist:
        return None  # Si no existe registro de Auth0
    
    try:
        # 3. Obtener información del usuario desde Auth0
        accessToken = auth0user.extra_data['access_token']
        url = "https://dev-0160hm2d1l27zgy4.us.auth0.com/userinfo"
        headers = {'authorization': 'Bearer ' + accessToken}
        
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()  # Lanza error si la respuesta no es 200
        userinfo = resp.json()
        
        # 4. Obtener rol con manejo seguro de KeyError
        role = userinfo.get('dev-0160hm2d1l27zgy4.us.auth0.com/role', 'default_role')
        return role
    
    except requests.exceptions.RequestException as e:
        # Manejar errores de conexión con Auth0
        print(f"Error conectando a Auth0: {e}")
        return None