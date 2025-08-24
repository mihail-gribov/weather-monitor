# CLI команда serve - запуск веб-сервера

- Номер: 009
- Depends on: [008]
- Спецификация: `.specification/02_web_dashboard_interface.md#новая-команда-для-запуска-сервера`
- Тип: backend
- Приоритет: P1
- Статус: done

## Definition of Ready
- Все зависимости закрыты; ссылки на спецификацию валидны; Inputs/Outputs описаны; команды запуска/проверки даны.

## Контекст
Добавить CLI команду `serve` для запуска веб-сервера дашборда с различными опциями конфигурации.

## Цель
Реализовать команду `python weather_monitor.py serve [options]` для запуска локального веб-сервера с поддержкой всех опций согласно спецификации.

## Inputs
- Переменные окружения: `PORT` (int, default: 8080), `HOST` (string, default: "localhost")
- Входные артефакты: `web_server.py` (класс WeatherWebServer), `config.yaml` (секция web_server)

## Outputs
- Команда `serve` в CLI
- Интеграция с WeatherWebServer
- Поддержка всех опций запуска сервера
- Автооткрытие браузера и daemon режим

## Объем работ (Scope)
1) Добавление команды `serve` в weather_monitor.py:
   - Опция `--port <number>` (порт сервера, по умолчанию 8080)
   - Опция `--host <address>` (адрес привязки, по умолчанию localhost)
   - Опция `--open-browser/-o` (автоматически открыть браузер)
   - Опция `--daemon/-d` (запустить в фоновом режиме)
   - Опция `--debug` (режим отладки с автоперезагрузкой)
2) Интеграция с WeatherWebServer:
   - Создание экземпляра сервера с конфигурацией
   - Передача параметров запуска
   - Обработка сигналов для корректной остановки
3) Функциональность автооткрытия браузера:
   - Использование модуля webbrowser
   - Задержка для запуска сервера перед открытием
   - Обработка ошибок при недоступности браузера
4) Daemon режим:
   - Запуск сервера в фоновом потоке
   - Сохранение PID для возможности остановки
   - Логирование в файл вместо stdout
5) Debug режим:
   - Включение Flask debug режима
   - Автоперезагрузка при изменении файлов
   - Детальные сообщения об ошибках
6) Обработка ошибок и graceful shutdown
- Out of scope: SSL/HTTPS поддержка, конфигурация через файлы, мониторинг

## Артефакты
- `weather_monitor.py` (обновлен с командой serve)
- Логи сервера (при daemon режиме)

## Acceptance criteria
- Команда: `python weather_monitor.py serve --help` → код 0, показывает справку
- Команда: `python weather_monitor.py serve` → запускает сервер на localhost:8080
- Команда: `python weather_monitor.py serve --port 3000 --host 0.0.0.0` → сервер доступен на всех интерфейсах порт 3000
- Опция: `--open-browser` автоматически открывает браузер с адресом сервера
- Опция: `--daemon` запускает сервер в фоне и возвращает управление
- Опция: `--debug` включает режим отладки Flask
- Graceful shutdown: Ctrl+C корректно останавливает сервер

## Тесты
- Unit: тестирование парсинга опций команды serve
- Integration: тестирование запуска сервера с различными параметрами
- Integration: тестирование автооткрытия браузера (mock)
- Integration: тестирование daemon режима
- E2E: полный цикл запуска и остановки сервера

## Команды для проверки
```bash
# проверка справки
python weather_monitor.py serve --help
# тестирование базового запуска (короткий тест)
timeout 3s python weather_monitor.py serve --port 8082 || echo "Expected timeout"
# проверка что команда добавлена в общую справку
python weather_monitor.py --help | grep serve && echo "Serve command listed"
# тестирование с кастомными параметрами
timeout 3s python weather_monitor.py serve --port 8083 --host 127.0.0.1 --debug || echo "Expected timeout"
# проверка daemon режима (если реализован)
# python weather_monitor.py serve --daemon --port 8084 &
# sleep 2
# curl -s http://localhost:8084/api/health && echo "Daemon server running"
# pkill -f "weather_monitor.py serve"
```

## Definition of Done
- Lint/type-check/tests/build OK
- Команда `serve` добавлена в CLI с всеми опциями согласно спецификации
- Интеграция с WeatherWebServer функционирует корректно
- Автооткрытие браузера работает при указании опции
- Daemon режим запускает сервер в фоне
- Debug режим включает отладочные возможности Flask
- Graceful shutdown по Ctrl+C реализован
- Обработка ошибок (занятый порт, недоступный хост) работает
- Статус задачи обновлён на `done`

## Риски и допущения
- Риск: конфликты портов с другими приложениями
- Риск: проблемы с правами доступа при привязке к портам <1024
- Допущение: модуль webbrowser доступен для автооткрытия браузера
- Допущение: WeatherWebServer корректно реализован и тестирован

## Ссылка на следующую задачу
- 010

## Отчет о выполнении

**Дата выполнения:** 2025-01-27 17:30

### Выполненные работы:
1. ✅ Добавление команды `serve` в weather_monitor.py:
   - Опция `--port/-p <number>` (порт сервера, по умолчанию 8080)
   - Опция `--host/-h <address>` (адрес привязки, по умолчанию localhost)
   - Опция `--open-browser/-o` (автоматически открыть браузер)
   - Опция `--daemon/-d` (запустить в фоновом режиме)
   - Опция `--debug` (режим отладки с автоперезагрузкой)
2. ✅ Интеграция с WeatherWebServer:
   - Создание экземпляра сервера с конфигурацией
   - Передача параметров запуска
   - Обработка сигналов для корректной остановки
3. ✅ Функциональность автооткрытия браузера:
   - Использование модуля webbrowser
   - Задержка для запуска сервера перед открытием
   - Обработка ошибок при недоступности браузера
4. ✅ Daemon режим:
   - Запуск сервера в фоновом потоке
   - Сохранение PID для возможности остановки
   - Логирование в файл вместо stdout
5. ✅ Debug режим:
   - Включение Flask debug режима
   - Автоперезагрузка при изменении файлов
   - Детальные сообщения об ошибках
6. ✅ Обработка ошибок и graceful shutdown

### Особенности реализации:
- **Graceful degradation:** Команда корректно обрабатывает отсутствие Flask
- **Автооткрытие браузера:** Асинхронное открытие браузера с задержкой
- **Daemon режим:** Фоновый запуск с возможностью остановки
- **Debug режим:** Полная поддержка Flask debug возможностей
- **Валидация:** Проверка существования базы данных перед запуском

### Технические детали:
- **Threading:** Использование threading для автооткрытия браузера
- **Webbrowser модуль:** Стандартный Python модуль для открытия браузера
- **Graceful shutdown:** Обработка KeyboardInterrupt для корректной остановки
- **Конфигурация:** Переопределение параметров сервера из командной строки
- **Обработка ошибок:** Детальные сообщения об ошибках с инструкциями

### Проверки:
- ✅ Команда `serve --help` показывает справку
- ✅ Команда добавлена в общий список команд CLI
- ✅ Обработка отсутствия Flask с полезными сообщениями
- ✅ Поддержка всех опций командной строки
- ✅ Корректная обработка таймаутов
- ✅ Graceful shutdown по Ctrl+C

### Обновленные файлы:
- `weather_monitor.py` - добавлена команда serve с полной функциональностью

### Примеры использования:
```bash
# Базовый запуск
python weather_monitor.py serve

# Кастомный порт и хост
python weather_monitor.py serve --port 3000 --host 0.0.0.0

# С автооткрытием браузера
python weather_monitor.py serve --open-browser

# Daemon режим
python weather_monitor.py serve --daemon --port 8081

# Debug режим
python weather_monitor.py serve --debug --port 8082
```

### Вывод команды:
```
Usage: weather_monitor.py serve [OPTIONS]

  Start web server for weather dashboard.

Options:
  -p, --port INTEGER  Port to run server on (default: 8080)
  -h, --host TEXT     Host to bind server to (default: localhost)
  -o, --open-browser  Automatically open browser
  -d, --daemon        Run server in background
  --debug             Enable debug mode
  -c, --config TEXT   Path to configuration file (default: config.yaml)
```
