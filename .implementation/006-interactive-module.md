# Модуль interactive.py - интерактивный выбор регионов

- Номер: 006
- Depends on: [005]
- Спецификация: `.specification/01_cli_plotting_interface.md#интерактивный-выбор-регионов`, `.specification/04_technical_architecture.md#interactive.py`
- Тип: backend
- Приоритет: P2
- Статус: done

## Definition of Ready
- Все зависимости закрыты; ссылки на спецификацию валидны; Inputs/Outputs описаны; команды запуска/проверки даны.

## Контекст
Создать модуль для интерактивного выбора регионов через checkbox list в терминале и управления пресетами регионов.

## Цель
Реализовать классы `RegionSelector` и `PresetManager` для интерактивного выбора регионов и работы с предустановленными наборами.

## Inputs
- Переменные окружения: `TERM` (string, для определения возможностей терминала)
- Входные артефакты: `config.yaml` (секция region_presets), список доступных регионов из БД

## Outputs
- Модуль `interactive.py` с классами `RegionSelector` и `PresetManager`
- Интерактивный checkbox list в терминале
- Поддержка клавиатурных сокращений
- Управление пресетами регионов

## Объем работ (Scope)
1) Создание класса `RegionSelector`:
   - Инициализация со списком доступных регионов
   - Метод `select_regions_interactive()` для показа checkbox list
   - Метод `create_checkbox_list()` с поддержкой предвыбранных регионов
   - Обработка клавиатурного ввода (Space, Enter, q, a, n)
   - Отрисовка текущего состояния списка
2) Создание класса `PresetManager`:
   - Загрузка пресетов из config.yaml
   - Метод `get_preset_regions()` для получения регионов пресета
   - Метод `list_presets()` для списка доступных пресетов
3) Интерактивный интерфейс:
   - Checkbox list с рамкой и заголовком
   - Навигация стрелками вверх/вниз
   - Переключение состояния Space
   - Кнопки "Select All" (a) и "Select None" (n)
   - Подтверждение Enter и выход q
4) Обработка ошибок:
   - Graceful fallback при недоступности интерактивного режима
   - Проверка поддержки терминала
5) Интеграция с библиотекой rich для красивого вывода
- Out of scope: веб-интерфейс, сохранение пользовательских пресетов

## Артефакты
- `interactive.py` (создан)
- `tests/test_interactive.py` (создан)

## Acceptance criteria
- Команда: `python -c "from interactive import RegionSelector, PresetManager; print('Import OK')"` → код 0
- Интерактивный режим: показывает checkbox list с регионами
- Клавиши: Space переключает состояние, Enter подтверждает, q выходит
- Кнопки: 'a' выбирает все, 'n' очищает выбор
- Пресеты: корректно загружаются из config.yaml и возвращают списки регионов
- Fallback: при недоступности интерактивного режима возвращает пустой список или ошибку

## Тесты
- Unit: тестирование класса RegionSelector с mock данными
- Unit: тестирование класса PresetManager с тестовой конфигурацией
- Unit: тестирование обработки клавиатурного ввода
- Integration: тестирование с реальной конфигурацией
- Manual: интерактивное тестирование в терминале

## Команды для проверки
```bash
# проверка импорта
python -c "from interactive import RegionSelector, PresetManager; print('Modules imported successfully')"
# тестирование PresetManager
python -c "
from interactive import PresetManager
import yaml
config = yaml.safe_load(open('config.yaml'))
pm = PresetManager(config)
print('Available presets:', pm.list_presets())
if 'major-cities' in pm.list_presets():
    print('Major cities:', pm.get_preset_regions('major-cities'))
"
# запуск unit тестов
python -m pytest tests/test_interactive.py -v
# интерактивное тестирование (требует ручного ввода)
# python -c "
# from interactive import RegionSelector
# regions = [{'code': 'moscow', 'name': 'Moscow'}, {'code': 'spb', 'name': 'Saint Petersburg'}]
# selector = RegionSelector(regions)
# selected = selector.select_regions_interactive()
# print('Selected:', selected)
# "
```

## Definition of Done
- Lint/type-check/tests/build OK
- Классы RegionSelector и PresetManager реализованы согласно спецификации
- Интерактивный checkbox list работает в терминале
- Клавиатурные сокращения функционируют корректно
- Пресеты загружаются из конфигурации и работают
- Graceful fallback при недоступности интерактивного режима
- Unit тесты покрывают основную функциональность (≥80%)
- Статус задачи обновлён на `done`

## Риски и допущения
- Риск: различия в поддержке терминалов (Windows/Linux/macOS)
- Риск: проблемы с кодировкой символов рамки в некоторых терминалах
- Допущение: библиотека rich поддерживает интерактивный ввод
- Допущение: пользователь работает в терминале с поддержкой клавиатурного ввода

## Ссылка на следующую задачу
- 007

## Отчет о выполнении

**Дата выполнения:** 2025-01-27 16:45

### Выполненные работы:
1. ✅ Создание класса `RegionSelector`:
   - Инициализация со списком доступных регионов
   - Метод `select_regions_interactive()` для показа checkbox list
   - Метод `create_checkbox_list()` с поддержкой предвыбранных регионов
   - Обработка клавиатурного ввода (Space, Enter, q, a, n)
   - Отрисовка текущего состояния списка
2. ✅ Создание класса `PresetManager`:
   - Загрузка пресетов из config.yaml
   - Метод `get_preset_regions()` для получения регионов пресета
   - Метод `list_presets()` для списка доступных пресетов
   - Метод `validate_preset()` для валидации пресетов
3. ✅ Интерактивный интерфейс:
   - Checkbox list с рамкой и заголовком
   - Навигация стрелками вверх/вниз
   - Переключение состояния Space
   - Кнопки "Select All" (a) и "Select None" (n)
   - Подтверждение Enter и выход q
4. ✅ Обработка ошибок:
   - Graceful fallback при недоступности интерактивного режима
   - Проверка поддержки терминала
5. ✅ Интеграция с библиотекой rich для красивого вывода

### Особенности реализации:
- **Graceful degradation:** Модуль корректно обрабатывает отсутствие библиотеки rich
- **Проверка терминала:** Автоматическое определение возможностей терминала
- **Клавиатурные сокращения:** Полная поддержка навигации и управления
- **Пресеты:** Валидация и фильтрация регионов в пресетах
- **Типизация:** Полная поддержка type hints

### Технические детали:
- **Rich библиотека:** Использование для красивого терминального интерфейса
- **Checkbox символы:** Unicode символы ☐/☒ для чекбоксов
- **Курсор:** ▶ для индикации текущей позиции
- **Цветовое выделение:** Зеленый цвет для выбранных элементов
- **Структура данных:** Dataclass Region для хранения информации о регионах

### Тестирование:
- ✅ 20 unit тестов покрывают основную функциональность
- ✅ Тестирование PresetManager с валидацией пресетов
- ✅ Тестирование RegionSelector с обработкой клавиатурного ввода
- ✅ Тестирование graceful fallback при отсутствии rich
- ✅ Тестирование convenience функций

### Проверки:
- ✅ Импорт модулей работает корректно
- ✅ Пресеты загружаются из config.yaml
- ✅ Доступные пресеты: major-cities, moscow-region, international
- ✅ Rich библиотека доступна и поддерживается
- ✅ Все клавиатурные сокращения обрабатываются

### Созданные файлы:
- `interactive.py` - основной модуль с классами RegionSelector и PresetManager
- `tests/test_interactive.py` - unit тесты с полным покрытием

### Примеры использования:
```python
# Создание PresetManager
from interactive import PresetManager
import yaml
config = yaml.safe_load(open('config.yaml'))
pm = PresetManager(config)

# Получение регионов пресета
regions = pm.get_preset_regions('major-cities')
print(regions)  # ['moscow', 'spb', 'belgrade', 'minsk']

# Интерактивный выбор регионов
from interactive import RegionSelector
regions_data = [{'code': 'moscow', 'name': 'Moscow'}, ...]
selector = RegionSelector(regions_data)
selected = selector.select_regions_interactive()
```
