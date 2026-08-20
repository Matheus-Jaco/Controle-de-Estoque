import sys
import os

# Adiciona o diretório da aplicação ao path do sistema
sys.path.insert(0, r'c:\Users\jacom\OneDrive\Desktop\Projetos\Peças_Barel')

try:
    from app import app
    print("Sucesso ao importar o app Flask!")
except Exception as e:
    print(f"Erro ao importar o app: {e}")
    sys.exit(1)

def test_security_routes():
    print("\n--- INICIANDO TESTE DE SEGURANÇA DAS ROTAS ---")
    client = app.test_client()
    
    # Mapeamento de rotas e métodos a testar sem login
    # Colocamos rotas dinâmicas com IDs fictícios para garantir o teste completo
    routes_to_test = [
        ('/', 'GET'),
        ('/dashboard', 'GET'),
        ('/inicial', 'GET'),
        ('/inicio', 'GET'),
        ('/products', 'GET'),
        ('/products/add', 'GET'),
        ('/products/add', 'POST'),
        ('/products/edit/1', 'GET'),
        ('/products/edit/1', 'POST'),
        ('/products/delete/1', 'POST'),
        ('/products/move/1', 'POST'),
        ('/notes', 'GET'),
        ('/notes/add', 'GET'),
        ('/notes/add', 'POST'),
        ('/notes/edit/1', 'GET'),
        ('/notes/edit/1', 'POST'),
        ('/notes/toggle/1', 'POST'),
        ('/notes/delete/1', 'POST'),
        ('/reports', 'GET'),
        ('/logout', 'GET'),
        ('/login', 'GET'),    # Pública - deve retornar 200
        ('/login', 'POST'),   # Pública - processa login
        ('/static/css/style.css', 'GET')  # Pública - estático
    ]
    
    failures = 0
    successes = 0
    
    for route, method in routes_to_test:
        # Fazer requisição sem session de usuário logado
        if method == 'GET':
            response = client.get(route)
        elif method == 'POST':
            response = client.post(route)
            
        status_code = response.status_code
        location = response.headers.get('Location', '')
        
        # Classificar se é rota pública legítima
        is_public = route in ['/login'] or route.startswith('/static')
        
        if is_public:
            # Rotas públicas devem retornar status 200 (ou redirect 302 se for o POST de login sem dados válidos)
            if status_code in [200, 302]:
                print(f"[OK] ROTA PÚBLICA: {method} {route} -> Status: {status_code} (Acesso Permitido)")
                successes += 1
            else:
                print(f"[AVISO] ROTA PÚBLICA: {method} {route} -> Retornou status inesperado: {status_code}")
        else:
            # Rotas protegidas DEVEM redirecionar (302) para a tela de login (/login ou http://localhost/login)
            if status_code == 302 and ('/login' in location or location.endswith('/login')):
                print(f"[OK] ROTA PROTEGIDA: {method} {route} -> Redirecionado com sucesso para {location} (Status: {status_code})")
                successes += 1
            else:
                print(f"[FALHA] ROTA VULNERÁVEL: {method} {route} -> Retornou {status_code} (Deveria redirecionar para /login!)")
                failures += 1
                
    print("\n--- RESULTADO FINAL ---")
    print(f"Total de testes bem-sucedidos (Rotas protegidas/públicas corretas): {successes}")
    print(f"Falhas de segurança encontradas (Acesso indevido sem login): {failures}")
    
    if failures > 0:
        print("\nATENÇÃO: Existem falhas de controle de acesso na aplicação!")
        sys.exit(1)
    else:
        print("\nParabéns! Todas as rotas estão devidamente protegidas pelo middleware de autenticação.")
        sys.exit(0)

if __name__ == '__main__':
    test_security_routes()
