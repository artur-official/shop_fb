import os
import sys
import shutil
from pathlib import Path
from dotenv import load_dotenv

def generate_nginx_config():
    """
    Генерирует nginx.conf из шаблона и копирует в папку Nginx.

    Что делает:
    1. Читает переменные из .env (DOMAIN, пути к SSL, путь к webapp)
    2. Подставляет их в шаблон nginx.conf.example
    3. Сохраняет сгенерированный nginx.conf в папке проекта
    4. Копирует его в C:/nginx/conf/ (туда, где Nginx читает конфиг)
    5. Проверяет валидность конфига командой nginx -t
    6. Предлагает перезагрузить Nginx
    """

    # === 1. Загружаем .env из корня проекта ===
    project_root = Path(__file__).parent.parent
    env_path = project_root / ".env"

    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ .env загружен: {env_path}")
    else:
        print(f"⚠️  .env не найден: {env_path}")
        print("   Будут использованы значения по умолчанию.\n")

    # === 2. Загружаем переменные ===
    domain = os.getenv("DOMAIN", "ingria-farm.com")
    webapp_root = os.getenv("WEBAPP_ROOT", "C:/Users/Administrator/Desktop/fb-shop/webapp")
    ssl_cert = os.getenv("SSL_CERT_PATH", "C:/nginx/ssl/ingria-farm.crt")
    ssl_key = os.getenv("SSL_KEY_PATH", "C:/nginx/ssl/ingria-farm.key")

    # === 3. Пути к файлам ===
    template_path = project_root / "nginx" / "conf" / "nginx.conf.example"
    output_path = project_root / "nginx" / "conf" / "nginx.conf"
    nginx_dest = Path("C:/nginx/conf/nginx.conf")

    # Проверяем, есть ли шаблон
    if not template_path.exists():
        print(f"❌ Шаблон не найден: {template_path}")
        print("   Убедитесь, что файл nginx.conf.example существует.")
        sys.exit(1)

    # === 4. Читаем шаблон и подставляем значения ===
    template = template_path.read_text(encoding="utf-8")

    config = template.replace("{{DOMAIN}}", domain)\
                   .replace("{{WEBAPP_ROOT}}", webapp_root.replace("\\", "/"))\
                   .replace("{{SSL_CERT_PATH}}", ssl_cert.replace("\\", "/"))\
                   .replace("{{SSL_KEY_PATH}}", ssl_key.replace("\\", "/"))

    # === 5. Сохраняем в папку проекта ===
    output_path.write_text(config, encoding="utf-8")
    print(f"\n✅ nginx.conf создан в проекте: {output_path}")
    print(f"   Домен: {domain}")
    print(f"   WebApp: {webapp_root}")
    print(f"   SSL cert: {ssl_cert}")

    # === 6. Копируем в папку Nginx ===
    try:
        # Создаём backup старого конфига
        if nginx_dest.exists():
            backup_path = nginx_dest.with_suffix(".conf.backup")
            shutil.copy(nginx_dest, backup_path)
            print(f"\n📦 Backup создан: {backup_path}")

        shutil.copy(output_path, nginx_dest)
        print(f"✅ Скопировано в Nginx: {nginx_dest}")
    except Exception as e:
        print(f"\n❌ Не удалось скопировать в {nginx_dest}: {e}")
        print(f"   Скопируйте вручную:")
        print(f"   Copy-Item \"{output_path}\" \"{nginx_dest}\"")
        sys.exit(1)

    # === 7. Проверяем конфигурацию ===
    print("\n🔍 Проверка конфигурации...")
    nginx_test = os.system("nginx -t")

    if nginx_test == 0:
        print("\n✅ Конфигурация nginx валидна!")

        # === 8. Предлагаем перезагрузить ===
        reload = input("\n🔄 Перезагрузить nginx? (y/n): ").strip().lower()
        if reload == "y":
            os.system("nginx -s reload")
            print("✅ Nginx перезагружен!")
        else:
            print("⚠️  Nginx НЕ перезагружен. Сделайте вручную: nginx -s reload")
    else:
        print("\n❌ Ошибка в конфигурации!")
        print("   Восстановите из backup или проверьте шаблон.")
        sys.exit(1)

if __name__ == "__main__":
    generate_nginx_config()