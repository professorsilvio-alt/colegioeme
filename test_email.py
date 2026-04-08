#!/usr/bin/env python
"""
Script de teste de envio de email via SMTP GoDaddy.
Execute com: python test_email.py
Preencha a senha no arquivo .env antes de rodar.
"""
import os
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / '.env')

EMAIL_HOST     = os.environ.get('EMAIL_HOST', 'smtpout.secureserver.net')
EMAIL_PORT     = int(os.environ.get('EMAIL_PORT', 465))
EMAIL_USE_SSL  = os.environ.get('EMAIL_USE_SSL', 'True') == 'True'
EMAIL_USE_TLS  = os.environ.get('EMAIL_USE_TLS', 'False') == 'True'
EMAIL_USER     = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_PASS     = os.environ.get('EMAIL_HOST_PASSWORD', '')
FROM_EMAIL     = os.environ.get('DEFAULT_FROM_EMAIL', EMAIL_USER)

# ─── Destinatário de teste ───────────────────────
PARA = input("Digite o email de destino para o teste: ").strip()
if not PARA:
    print("❌ Email de destino não informado. Encerrando.")
    sys.exit(1)

if not EMAIL_PASS or EMAIL_PASS == 'COLOQUE_AQUI_A_SENHA_DO_EMAIL':
    print("❌ Senha de email não configurada no arquivo .env!")
    print("   Edite o .env e preencha EMAIL_HOST_PASSWORD com a senha do suporte@capelum.com")
    sys.exit(1)

# ─── Montar mensagem ─────────────────────────────
msg = MIMEMultipart('alternative')
msg['Subject'] = 'Capelum — Teste de Email SMTP ✅'
msg['From']    = FROM_EMAIL
msg['To']      = PARA

html = """\
<html>
<body style="font-family:Arial,sans-serif;background:#0f0f1a;padding:40px;color:#e2e8f0;">
  <div style="max-width:500px;margin:0 auto;background:#1a1a2e;border-radius:12px;padding:32px;">
    <h2 style="color:#3b82f6;">✅ Teste de Email — Capelum</h2>
    <p>Parabéns! O servidor SMTP GoDaddy está configurado corretamente.</p>
    <p style="color:#94a3b8;font-size:13px;">Este é um email de teste enviado de <strong>suporte@capelum.com</strong>.</p>
  </div>
</body>
</html>
"""
msg.attach(MIMEText(html, 'html'))

# ─── Enviar ──────────────────────────────────────
print(f"\n⚙️  Conectando ao servidor SMTP...")
print(f"   Host : {EMAIL_HOST}:{EMAIL_PORT}")
print(f"   User : {EMAIL_USER}")
print(f"   SSL  : {EMAIL_USE_SSL} | TLS: {EMAIL_USE_TLS}")
print(f"   Para : {PARA}\n")

try:
    if EMAIL_USE_SSL:
        server = smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT, timeout=10)
    else:
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT, timeout=10)
        if EMAIL_USE_TLS:
            server.starttls()

    server.login(EMAIL_USER, EMAIL_PASS)
    server.sendmail(EMAIL_USER, [PARA], msg.as_string())
    server.quit()
    print(f"✅ Email enviado com sucesso para {PARA}!")
    print("   Verifique sua caixa de entrada (ou spam).")

except smtplib.SMTPAuthenticationError:
    print("❌ Erro de autenticação! Verifique o usuário e senha no .env")
except smtplib.SMTPConnectError as e:
    print(f"❌ Não foi possível conectar ao servidor SMTP: {e}")
except Exception as e:
    print(f"❌ Erro inesperado: {type(e).__name__}: {e}")
