# Функциональность экспорта данных и графиков

- Номер: 013
- Depends on: [012]
- Спецификация: `.specification/02_web_dashboard_interface.md#экспорт-и-сохранение`, `.specification/01_cli_plotting_interface.md#примеры-использования`
- Тип: backend
- Приоритет: P2
- Статус: done
- Время начала: 2025-01-24 11:35:00

## Definition of Ready
- Все зависимости закрыты; ссылки на спецификацию валидны; Inputs/Outputs описаны; команды запуска/проверки даны.

## Контекст
Реализовать функциональность экспорта графиков в различные форматы и экспорта данных в CSV/JSON для CLI и веб-интерфейса.

## Цель
Добавить возможности экспорта графиков в PNG/SVG/PDF и экспорта данных в CSV/JSON/Excel форматы как через CLI, так и через веб-интерфейс.

## Inputs
- Переменные окружения: нет
- Входные артефакты: `plotting.py` (графики), веб-интерфейс (Plotly.js графики), API данные

## Outputs
- Расширенная функциональность экспорта в `plotting.py`
- API эндпоинты для экспорта данных
- JavaScript функции для экспорта из веб-интерфейса
- Поддержка множественных форматов файлов

## Объем работ (Scope)
1) Расширение модуля `plotting.py`:
   - Метод `export_chart_data()` для экспорта данных в CSV/JSON
   - Улучшение `plot_metric_file()` для поддержки SVG и PDF
   - Метод `generate_report()` для создания PDF отчетов
2) Новые API эндпоинты в `web_server.py`:
   - `GET /api/export/data` - экспорт данных в CSV/JSON
   - `GET /api/export/chart` - экспорт графика в PNG/SVG
   - `POST /api/export/report` - генерация PDF отчета
3) JavaScript функциональность экспорта:
   - Использование встроенных возможностей Plotly.js для экспорта графиков
   - Функции для скачивания данных в различных форматах
   - UI кнопки для экспорта в веб-интерфейсе
4) CLI расширения:
   - Опция `--export-data <format>` для команды plot
   - Поддержка форматов: csv, json, excel
   - Автоматическое именование файлов экспорта
5) Форматы экспорта:
   - Графики: PNG, SVG, PDF
   - Данные: CSV, JSON, Excel (xlsx)
   - Отчеты: PDF с графиками и статистикой
6) Обработка ошибок и валидация:
   - Проверка доступности форматов экспорта
   - Обработка ошибок записи файлов
   - Валидация размеров и параметров экспорта
- Out of scope: экспорт в базы данных, облачные сервисы, email отправка

## Артефакты
- `plotting.py` (обновлен с методами экспорта)
- `web_server.py` (обновлен с API эндпоинтами экспорта)
- `web/static/js/export.js` (создан)
- `web/templates/components/export_panel.html` (создан)
- `requirements.txt` (обновлен с openpyxl для Excel)

## Acceptance criteria
- CLI: `python weather_monitor.py plot temperature --regions moscow --save chart.png` → создает PNG файл
- CLI: `python weather_monitor.py plot temperature --regions moscow --export-data csv` → создает CSV файл
- API: `GET /api/export/data?regions=moscow&metric=temperature&format=json` → возвращает JSON данные
- Web: кнопка экспорта графика в веб-интерфейсе сохраняет PNG файл
- Web: кнопка экспорта данных скачивает CSV файл
- Форматы: поддержка PNG, SVG, PDF для графиков
- Форматы: поддержка CSV, JSON, Excel для данных
- Валидация: корректная обработка недоступных форматов

## Тесты
- Unit: тестирование методов экспорта с различными форматами
- Unit: тестирование API эндпоинтов экспорта
- Integration: тестирование создания файлов экспорта
- Integration: тестирование веб-интерфейса экспорта
- E2E: полный цикл экспорта через CLI и веб

## Команды для проверки
```bash
# проверка зависимостей для экспорта
python -c "import openpyxl; print('Excel export available')" || echo "Install openpyxl for Excel support"
# тестирование CLI экспорта (если есть данные)
python weather_monitor.py plot temperature --regions moscow --save test_export.png || echo "Expected: no data error"
ls -la test_export.png 2>/dev/null && echo "PNG export works" || echo "PNG not created (expected if no data)"
# тестирование экспорта данных
python -c "
from plotting import WeatherPlotter
import os
if os.path.exists('weather_data.db'):
    plotter = WeatherPlotter('weather_data.db', {})
    try:
        plotter.export_chart_data('temperature', ['moscow'], 24, 'test_export.csv')
        print('CSV export method exists')
    except Exception as e:
        print('Expected error:', str(e))
"
# очистка тестовых файлов
rm -f test_export.png test_export.csv
# проверка API эндпоинтов (требует запущенного сервера)
# curl -s "http://localhost:8080/api/export/data?regions=moscow&metric=temperature&format=json" | jq . && echo "Export API works"
```

## Definition of Done
- Lint/type-check/tests/build OK
- Методы экспорта реализованы в plotting.py
- API эндпоинты для экспорта функционируют
- CLI поддерживает экспорт графиков и данных
- Веб-интерфейс имеет кнопки экспорта
- Поддержка всех указанных форматов файлов
- Обработка ошибок экспорта реализована
- Валидация параметров экспорта работает
- Автоматическое именование файлов функционирует
- Статус задачи обновлён на `done`

## Риски и допущения
- Риск: проблемы с правами записи файлов в различных ОС
- Риск: большие размеры файлов при экспорте больших наборов данных
- Допущение: библиотеки для экспорта (openpyxl, matplotlib) установлены
- Допущение: браузеры поддерживают скачивание файлов через JavaScript

## Ссылка на следующую задачу
- 014

## Отчёт о выполнении

**Дата завершения:** 2025-08-24 11:23:00

### Реализованная функциональность:

#### 1. Расширение модуля `plotting.py`:
- ✅ Добавлен метод `export_chart_data()` для экспорта данных в CSV, JSON, Excel
- ✅ Добавлен метод `generate_report()` для создания PDF отчетов с графиками и статистикой
- ✅ Добавлен метод `get_supported_formats()` для получения списка поддерживаемых форматов
- ✅ Реализованы приватные методы `_export_to_csv()`, `_export_to_json()`, `_export_to_excel()`

#### 2. Новые API эндпоинты в `web_server.py`:
- ✅ `GET /api/export/data` - экспорт данных в CSV/JSON/Excel
- ✅ `GET /api/export/chart` - экспорт графика в PNG/SVG
- ✅ `POST /api/export/report` - генерация PDF отчета
- ✅ Добавлен метод `_get_content_type()` для определения MIME-типов файлов

#### 3. JavaScript функциональность экспорта:
- ✅ Создан `web/static/js/export.js` с классами `ExportManager` и `ExportUtils`
- ✅ Реализованы методы `exportData()`, `exportChart()`, `generateReport()`
- ✅ Добавлена поддержка клиентского экспорта через Plotly.js
- ✅ Реализованы уведомления о прогрессе и ошибках

#### 4. CLI расширения:
- ✅ Добавлена опция `--export-data <format>` для команды plot
- ✅ Поддержка форматов: csv, json, excel
- ✅ Автоматическое именование файлов с временными метками

#### 5. CSS стили и UI компоненты:
- ✅ Добавлены стили для экспорта в `web/static/css/components.css`
- ✅ Стили для прогресс-баров, уведомлений, выпадающих меню

#### 6. Тестирование:
- ✅ Создан `tests/test_export.py` с 12 тестами
- ✅ Покрытие: CSV, JSON, Excel экспорт, PDF отчеты, обработка ошибок
- ✅ Все 84 теста проекта проходят успешно

### Технические особенности реализации:

#### Зависимости:
- **openpyxl>=3.0.0** - для экспорта в Excel формат
- **reportlab>=4.0.0** - для генерации PDF отчетов
- **plotext** - для ASCII графиков (установлен дополнительно)

#### Архитектурные решения:
- **Модульная структура**: каждый формат экспорта в отдельном методе
- **Graceful degradation**: корректная обработка отсутствующих библиотек
- **Валидация**: проверка форматов, метрик, регионов перед экспортом
- **Обработка ошибок**: логирование ошибок и возврат False при неудаче

#### Форматы файлов:
- **CSV**: стандартный формат с заголовками Region, Timestamp, Metric
- **JSON**: структурированные данные с метаданными
- **Excel**: xlsx формат с листами для каждого региона
- **PDF**: отчеты с графиками, таблицами и статистикой

#### Производительность:
- **Оптимизация**: использование pandas для больших наборов данных
- **Память**: потоковая обработка для больших файлов
- **Кэширование**: переиспользование данных между операциями

### Результаты тестирования:

#### CLI тестирование:
```bash
# Успешный экспорт CSV
python weather_monitor.py plot temperature --regions moscow --hours 168 --save test.png --export-data csv
# Результат: weather_data_temperature_moscow_20250824_112252.csv создан
```

#### API тестирование:
```bash
# Экспорт через API
curl -s "http://localhost:8001/api/export/data?regions=moscow&metric=temperature&hours=24&format=csv"
```

#### Unit тестирование:
- ✅ 12 тестов в `tests/test_export.py` - все проходят
- ✅ Покрытие всех форматов экспорта
- ✅ Тестирование обработки ошибок
- ✅ Тестирование больших наборов данных

### Совместимость и версии:
- **Python**: 3.7+ (тестировано на 3.13.0)
- **openpyxl**: 3.1.5
- **reportlab**: 4.4.3
- **matplotlib**: для графиков PNG/SVG
- **pandas**: для обработки данных

### Полезные инсайты для других задач:
1. **Установка зависимостей**: openpyxl и reportlab требуют отдельной установки
2. **Права доступа**: экспорт файлов требует прав записи в директорию
3. **Размеры файлов**: большие наборы данных могут создавать файлы размером в МБ
4. **MIME-типы**: важно правильно устанавливать Content-Type для скачивания файлов
5. **Временные метки**: автоматическое именование файлов предотвращает конфликты
6. **Обработка ошибок**: graceful degradation критически важно для пользовательского опыта
