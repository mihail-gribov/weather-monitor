# CLI команда plot - основная функциональность

- Номер: 005
- Depends on: [004]
- Спецификация: `.specification/01_cli_plotting_interface.md#команда-plot`, `.specification/04_technical_architecture.md#расширение-cli-команд`
- Тип: backend
- Приоритет: P1
- Статус: done

## Definition of Ready
- Все зависимости закрыты; ссылки на спецификацию валидны; Inputs/Outputs описаны; команды запуска/проверки даны.

## Контекст
Добавить новую CLI команду `plot` в существующий `weather_monitor.py` для быстрого создания графиков погодных данных через командную строку.

## Цель
Реализовать команду `python weather_monitor.py plot <metric> [options]` с поддержкой всех опций согласно спецификации.

## Inputs
- Переменные окружения: нет
- Входные артефакты: `weather_monitor.py` (существующий CLI), `plotting.py` (модуль графиков), `config.yaml`

## Outputs
- Обновленный `weather_monitor.py` с командой `plot`
- Парсинг аргументов и опций команды
- Интеграция с модулем `plotting.py`
- Валидация входных параметров

## Объем работ (Scope)
1) Добавление команды `plot` в CLI:
   - Аргумент `metric` (temperature, humidity, pressure, wind-speed, precipitation, all)
   - Опция `--regions/-r` (список регионов через запятую)
   - Опция `--hours/-h` (количество часов назад, по умолчанию 24)
   - Опция `--days/-d` (альтернатива hours)
   - Опция `--ascii` (показать ASCII график в терминале)
   - Опция `--save <filename>` (сохранить в файл)
   - Опция `--width <pixels>` (ширина графика, по умолчанию 800)
   - Опция `--height <pixels>` (высота графика, по умолчанию 600)
2) Валидация параметров:
   - Проверка существования указанных регионов
   - Валидация временных диапазонов
   - Проверка формата файла для сохранения
3) Интеграция с WeatherPlotter:
   - Вызов соответствующих методов для ASCII или файлового вывода
   - Передача параметров конфигурации
4) Обработка ошибок:
   - Информативные сообщения об ошибках
   - Graceful fallback при отсутствии данных
5) Справочная информация и примеры использования
- Out of scope: интерактивный выбор регионов, пресеты, команда dashboard

## Артефакты
- `weather_monitor.py` (обновлен)
- Документация команды в `--help`

## Acceptance criteria
- Команда: `python weather_monitor.py plot --help` → код 0, показывает справку по команде
- Команда: `python weather_monitor.py plot temperature --regions moscow --ascii` → код 0 или информативная ошибка
- Команда: `python weather_monitor.py plot humidity --regions moscow,spb --save test.png` → создается файл test.png
- Команда: `python weather_monitor.py plot invalid_metric --regions moscow` → код ≠ 0, сообщение об ошибке
- Команда: `python weather_monitor.py plot temperature --regions invalid_region` → код ≠ 0, сообщение об ошибке
- Валидация: опции `--hours` и `--days` взаимоисключающие
- Существующие команды CLI продолжают работать без изменений

## Тесты
- Unit: тестирование парсинга аргументов команды plot
- Unit: тестирование валидации параметров
- Integration: тестирование интеграции с WeatherPlotter
- E2E: полный цикл выполнения команды с реальными данными
- E2E: тестирование обработки ошибок

## Команды для проверки
```bash
# проверка справки
python weather_monitor.py plot --help
# проверка существующих команд
python weather_monitor.py --help
python weather_monitor.py latest
# тестирование новой команды (если есть данные)
python weather_monitor.py plot temperature --regions moscow --ascii || echo "Expected: no data or region error"
# тестирование валидации
python weather_monitor.py plot invalid_metric --regions moscow 2>&1 | grep -i "error\|invalid" && echo "Validation works"
# тестирование сохранения в файл
python weather_monitor.py plot temperature --regions moscow --save test_plot.png || echo "Expected: no data error"
ls -la test_plot.png 2>/dev/null && echo "File created" || echo "File not created (expected if no data)"
rm -f test_plot.png
```

## Definition of Done
- Lint/type-check/tests/build OK
- Команда `plot` добавлена в CLI с всеми опциями согласно спецификации
- Валидация входных параметров работает корректно
- Интеграция с WeatherPlotter функционирует
- Обработка ошибок реализована с информативными сообщениями
- Справочная информация доступна через `--help`
- Существующая функциональность CLI не нарушена
- Статус задачи обновлён на `done`

## Риски и допущения
- Риск: конфликт с существующими командами CLI
- Риск: отсутствие данных в БД для тестирования функциональности
- Допущение: библиотека Click используется для CLI (или совместимый подход)
- Допущение: модуль plotting.py корректно реализован

## Ссылка на следующую задачу
- 006

## Отчет о выполнении

**Дата выполнения:** 2025-01-27 16:30

### Выполненные работы:
1. ✅ Добавление команды `plot` в CLI:
   - Аргумент `metric` с валидацией (temperature, humidity, pressure, wind-speed, precipitation, all)
   - Опция `--regions/-r` (список регионов через запятую, обязательная)
   - Опция `--hours/-h` (количество часов назад)
   - Опция `--days/-d` (альтернатива hours)
   - Опция `--ascii` (показать ASCII график в терминале)
   - Опция `--save <filename>` (сохранить в файл)
   - Опция `--width <pixels>` (ширина графика, по умолчанию 800)
   - Опция `--height <pixels>` (высота графика, по умолчанию 600)
2. ✅ Валидация параметров:
   - Проверка существования указанных регионов
   - Валидация временных диапазонов
   - Взаимоисключающие опции --hours и --days
   - Обязательность --ascii или --save
3. ✅ Интеграция с WeatherPlotter:
   - Вызов соответствующих методов для ASCII или файлового вывода
   - Передача параметров конфигурации
   - Обработка ошибок ImportError для отсутствующих библиотек
4. ✅ Обработка ошибок:
   - Информативные сообщения об ошибках
   - Graceful fallback при отсутствии данных
   - Показ доступных регионов при ошибке валидации
5. ✅ Справочная информация и примеры использования

### Особенности реализации:
- **Валидация метрик:** Использование click.Choice для ограничения доступных метрик
- **Взаимоисключающие опции:** Проверка конфликта между --hours и --days
- **Обязательные флаги:** Требование указания --ascii или --save
- **Конвертация размеров:** Автоматическое преобразование пикселей в дюймы для matplotlib
- **Расширенная валидация регионов:** Показ списка доступных регионов при ошибке

### Технические детали:
- **Интеграция с Click:** Использование существующей структуры CLI
- **Обработка ошибок:** Информативные сообщения с кодами выхода
- **Конфигурация:** Загрузка настроек из config.yaml
- **Размеры графиков:** Настраиваемые размеры с конвертацией единиц измерения

### Проверки:
- ✅ Команда `plot --help` показывает справку
- ✅ Валидация метрик работает (invalid_metric → ошибка)
- ✅ Валидация регионов работает (invalid_region → список доступных)
- ✅ Взаимоисключающие опции работают (--hours + --days → ошибка)
- ✅ Создание файловых графиков работает (PNG)
- ✅ Существующие команды CLI продолжают работать

### Обновленные файлы:
- `weather_monitor.py` - добавлена команда plot
- `plotting.py` - добавлен метод get_available_regions()

### Примеры использования:
```bash
# Создание ASCII графика
python weather_monitor.py plot temperature --regions moscow --ascii

# Сохранение в файл
python weather_monitor.py plot humidity --regions moscow,spb --save humidity.png

# Настройка размеров
python weather_monitor.py plot pressure --regions moscow --save pressure.png --width 1200 --height 800

# Использование дней вместо часов
python weather_monitor.py plot temperature --regions moscow --days 7 --save weekly_temp.png
```
