import re          # модуль поиска текста по шаблону (регулярные выражения)
import subprocess  # модуль запуска команд терминала из Python

# Белый список: IP, которые НЕЛЬЗЯ банить никогда
WHITELIST = ["127.0.0.1", "192.168.1.50"]


def read_auth_log():
    log_file = 'test_auth.log'   # для боевого режима: '/var/log/auth.log'

    try:
        with open(log_file, 'r') as f:
            lines = f.readlines()
        return lines
    except PermissionError:
        # Сработает, если нет прав на чтение файла
        print("Ошибка: нужен root доступ. Запусти через sudo!")
        return []
    except FileNotFoundError:
        # Сработает, если файла не существует
        print(f"Ошибка: файл {log_file} не найден!")
        return []


def find_failed_logins(lines):
    failed_lines = []
    for line in lines:
        if 'Failed password' in line:
            failed_lines.append(line)
    return failed_lines


def count_ips(failed_lines):
    ip_count = {}

    for line in failed_lines:
        # Ищем в строке слово "from", пробелы, и 4 группы цифр через точку.
        # Скобки ( ) = группа №1, её заберём через match.group(1)
        match = re.search(r'from\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', line)

        if match:                      # если шаблон найден (match не пустой)
            ip = match.group(1)        # достаём группу №1 — сам IP-адрес

            if ip in ip_count:         # IP уже встречался?
                ip_count[ip] += 1      # да: прибавляем зарубку
            else:
                ip_count[ip] = 1       # нет: создаём запись с единицей

    return ip_count


def ban_ip(ip):
    # Запускаем команду терминала: sudo ufw deny from <ip>
    # capture_output=True: вывод не на экран, а в переменную result
    # text=True: вывод как текст, а не байты
    result = subprocess.run(
        ['sudo', 'ufw', 'deny', 'from', ip],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:         # код выхода 0 = команда удалась
        print(f" IP {ip} ЗАБЛОКИРОВАН через UFW")
    else:
        # stderr = "труба ошибок" команды; там лежит причина провала
        print(f" Ошибка блокировки {ip}: {result.stderr}")


def main():
    print("Читаем логи...")
    lines = read_auth_log()

    if not lines:
        return

    failed = find_failed_logins(lines)
    print(f"Найдено неудачных попыток входа: {len(failed)}")

    ip_stats = count_ips(failed)

    print("\n--- СТАТИСТИКА АТАК ---")
    for ip, count in ip_stats.items():
        if count > 5:
            print(f"🚨 ВНИМАНИЕ! Подозрительный IP: {ip} (Попыток: {count})")
            if ip in WHITELIST:
                print(f" IP {ip} в белом списке — НЕ баню")
            else:
                ban_ip(ip)
        else:
            print(f"IP: {ip} | Попыток: {count}")
    print("-----------------------")


if __name__ == "__main__":
    main()   # кнопка "ПУСК"