import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def generate_nginx_config():
    # Загружаем .env из корня проекта
    project_root = Path(__file__).parent.parent
    env_path = project_root / ".env"

    if env_path.exists():
        load_dotenv(env_path)
    else:
        print(f"⚠️  .env не найден: {env_path}")
        print("Будут использованы значения по умолчанию.\n")

    # Загружаем переменные
    domain = os.getenv("DOMAIN", "ingria-farm.com")
    webapp_root = os.getenv("WEBAPP_ROOT", "C:/Users/Administrator/Desktop/fb-shop/webapp")
    ssl_cert = os.getenv("SSL_CERT_PATH", "C:/nginx/ssl/ingria-farm.crt")
    ssl_key = os.getenv("SSL_KEY_PATH", "C:/nginx/ssl/ingria-farm.key")

    # Пути к файлам
    template_path = project_root / "nginx" / "conf" / "nginx.conf.example"
    output_path = project_root / "nginx" / "conf" / "nginx.conf"

    if not template_path.exists():
        print(f"❌ Шаблон не найден: {template_path}")
        print("Убедитесь, что файл nginx.conf.example существует.")
        sys.exit(1)

    # Читаем шаблон
    template = template_path.read_text(encoding="utf-8")

    # Подставляем значения
    config = template.replace("{{DOMAIN}}", domain)\
                   .replace("{{WEBAPP_ROOT}}", webapp_root.replace("\\", "/"))\
                   .replace("{{SSL_CERT_PATH}}", ssl_cert.replace("\\", "/"))\
                   .replace("{{SSL_KEY_PATH}}", ssl_key.replace("\\", "/"))

    # Сохраняем
    output_path.write_text(config, encoding="utf-8")
    print(f"✅ nginx.conf создан: {output_path}")
    print(f"   Домен: {domain}")
    print(f"   WebApp: {webapp_root}")
    print(f"   SSL cert: {ssl_cert}")

    # Проверка конфига (если nginx в PATH)
    nginx_test = os.system("nginx -t")
    if nginx_test == 0:
        print("\n✅ Конфигурация nginx валидна")

        # Предлагаем перезагрузить
        reload = input("\nПерезагрузить nginx? (y/n): ").strip().lower()
        if reload == "y":
            os.system("nginx -s reload")
            print("✅ nginx перезагружен")
    else:
        print("\n⚠️  Не удалось проверить конфигурацию (nginx не в PATH или ошибка)")
        print("   Проверьте вручную: nginx -t")

if __name__ == "__main__":
    generate_nginx_config()
