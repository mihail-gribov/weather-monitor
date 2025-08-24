# Расширение конфигурации - добавление секций plotting и web_server

- Номер: 003
- Depends on: [002]
- Спецификация: `.specification/01_cli_plotting_interface.md#конфигурация`, `.specification/02_web_dashboard_interface.md#конфигурация`, `.specification/04_technical_architecture.md#расширение-конфигурации`
- Тип: backend
- Приоритет: P1
- Статус: done

## Definition of Ready
- Все зависимости закрыты; ссылки на спецификацию валидны; Inputs/Outputs описаны; команды запуска/проверки даны.

## Контекст
Необходимо расширить существующий `config.yaml` новыми секциями для поддержки функциональности графиков и веб-сервера, а также добавить пресеты регионов.

## Цель
Добавить в конфигурацию секции `plotting`, `web_server`, `region_presets` и `web_interface` с параметрами по умолчанию согласно спецификации.

## Inputs
- Переменные окружения: нет
- Входные артефакты: существующий `config.yaml`

## Outputs
- Обновленный `config.yaml` с новыми секциями
- Сохранение существующих настроек регионов и базы данных
- Валидная YAML структура

## Объем работ (Scope)
1) Анализ существующего `config.yaml`
2) Добавление секции `plotting`:
   - default_colors (список цветов для графиков)
   - ascii_symbols (символы для ASCII графиков)
   - figure_size (размер графиков по умолчанию)
   - dpi (разрешение графиков)
3) Добавление секции `web_server`:
   - default_port (8080)
   - default_host ("localhost")
   - auto_refresh_interval (300 секунд)
   - max_data_points (1000)
   - enable_cors (true)
4) Добавление секции `region_presets`:
   - major-cities (moscow, spb, belgrade, minsk)
   - moscow-region (moskva_station, ostafyevo, domodedovo)
   - international (belgrade, minsk, prague)
5) Добавление секции `web_interface`:
   - theme ("light")
   - default_chart_type ("line")
   - show_grid (true)
   - animation_duration (500)
6) Валидация YAML синтаксиса
- Out of scope: изменение существующих секций, миграция старых настроек

## Артефакты
- `config.yaml` (обновлен)
- Резервная копия `config.yaml.backup` (создана)

## Acceptance criteria
- Команда: `python -c "import yaml; yaml.safe_load(open('config.yaml'))"` → код 0, валидный YAML
- Команда: `python -c "import yaml; c=yaml.safe_load(open('config.yaml')); print(c['plotting']['default_colors'])"` → вывод содержит список цветов
- Команда: `python -c "import yaml; c=yaml.safe_load(open('config.yaml')); print(c['web_server']['default_port'])"` → вывод содержит `8080`
- Команда: `python -c "import yaml; c=yaml.safe_load(open('config.yaml')); print(len(c['region_presets']['major-cities']))"` → вывод содержит `4`
- Существующие секции `regions` и `database` остались без изменений

## Тесты
- Unit: валидация YAML структуры и типов данных
- Integration: загрузка конфигурации в существующем коде
- E2E: проверка что существующие команды CLI работают с новой конфигурацией

## Команды для проверки
```bash
# создание резервной копии
cp config.yaml config.yaml.backup
# валидация YAML
python -c "import yaml; yaml.safe_load(open('config.yaml')); print('YAML valid')"
# проверка новых секций
python -c "
import yaml
config = yaml.safe_load(open('config.yaml'))
assert 'plotting' in config
assert 'web_server' in config  
assert 'region_presets' in config
assert 'web_interface' in config
print('All sections present')
"
# проверка существующей функциональности
python weather_monitor.py --help
# восстановление из резервной копии при необходимости
# cp config.yaml.backup config.yaml
```

## Definition of Done
- Lint/type-check/tests/build OK
- config.yaml содержит все новые секции согласно спецификации
- YAML синтаксис валиден
- Существующие секции не изменены
- Резервная копия создана
- Существующая функциональность CLI работает
- Статус задачи обновлён на `done`

## Риски и допущения
- Риск: нарушение существующего YAML синтаксиса
- Риск: конфликт с существующими ключами конфигурации
- Допущение: библиотека PyYAML доступна для валидации
- Допущение: существующий config.yaml имеет валидный синтаксис

## Ссылка на следующую задачу
- 004

## Отчет о выполнении

**Дата выполнения:** 2025-01-27 16:00

### Выполненные работы:
1. ✅ Анализ существующего `config.yaml`
2. ✅ Создание резервной копии `config.yaml.backup`
3. ✅ Добавление секции `plotting`:
   - default_colors: ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
   - ascii_symbols: ['─', '┄', '┅', '┈', '┉']
   - figure_size: [10, 6]
   - dpi: 100
4. ✅ Добавление секции `web_server`:
   - default_port: 8080
   - default_host: "localhost"
   - auto_refresh_interval: 300
   - max_data_points: 1000
   - enable_cors: true
5. ✅ Добавление секции `region_presets`:
   - major-cities: [moscow, spb, belgrade, minsk]
   - moscow-region: [moskva_station, ostafyevo, domodedovo]
   - international: [belgrade, minsk, prague]
6. ✅ Добавление секции `web_interface`:
   - theme: "light"
   - default_chart_type: "line"
   - show_grid: true
   - animation_duration: 500
7. ✅ Валидация YAML синтаксиса

### Особенности реализации:
- **Совместимость:** Все существующие секции (`regions`, `database`) остались без изменений
- **Резервное копирование:** Создана резервная копия перед внесением изменений
- **Валидация:** YAML синтаксис проверен и корректен
- **Пресеты регионов:** Добавлены готовые наборы регионов для быстрого выбора

### Технические детали:
- **Цветовая схема:** Использованы стандартные цвета matplotlib для графиков
- **ASCII символы:** Подобраны Unicode символы для ASCII графиков
- **Веб-сервер:** Настроен на порт 8080 с поддержкой CORS
- **Пресеты:** Включены основные города и регионы для удобства использования

### Проверки:
- ✅ YAML синтаксис валиден
- ✅ Все новые секции присутствуют
- ✅ Существующая функциональность CLI работает
- ✅ Количество регионов не изменилось (19)
- ✅ Путь к базе данных остался прежним

### Обновленные файлы:
- `config.yaml` - добавлены новые секции
- `config.yaml.backup` - резервная копия создана
