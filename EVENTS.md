# Поддерживаемые события GitLab

В этом документе перечислены все события GitLab, которые поддерживаются приложением glping.

## Таблица событий

| Тип события | Действие | Реализовано | Покрыто тестами |
|-------------|----------|-------------|-----------------|
| **MergeRequest** | opened | ✅ | ✅ |
| **MergeRequest** | updated | ✅ | ✅ |
| **MergeRequest** | closed | ✅ | ✅ |
| **MergeRequest** | merged | ✅ | ✅ |
| **MergeRequest** | reopened | ✅ | ✅ |
| **MergeRequest** | approved | ✅ | ✅ |
| **MergeRequest** | unapproved | ✅ | ✅ |
| **MergeRequest** | review_requested | ✅ | ✅ |
| **MergeRequest** | ready | ✅ | ✅ |
| **MergeRequest** | draft | ✅ | ✅ |
| **Issue** | opened | ✅ | ✅ |
| **Issue** | updated | ✅ | ✅ |
| **Issue** | closed | ✅ | ✅ |
| **Issue** | reopened | ✅ | ✅ |
| **Issue** | moved | ✅ | ✅ |
| **Note** | комментарий к MR | ✅ | ✅ |
| **Note** | комментарий к Issue | ✅ | ✅ |
| **Note** | комментарий к коммиту | ✅ | ✅ |
| **DiffNote** | комментарий к коду в MR | ✅ | ✅ |
| **Commit** | новый коммит | ✅ | ✅ |
| **Push** | pushed | ✅ | ✅ |
| **Push** | pushed new | ✅ | ✅ |
| **Push** | pushed to | ✅ | ✅ |
| **Push** | new branch | ✅ | ✅ |
| **Push** | delete branch | ✅ | ✅ |
| **Push** | tag push | ✅ | ✅ |
| **Pipeline** | pending | ✅ | ✅ |
| **Pipeline** | running | ✅ | ✅ |
| **Pipeline** | success | ✅ | ✅ |
| **Pipeline** | failed | ✅ | ✅ |
| **Pipeline** | canceled | ✅ | ✅ |
| **Pipeline** | skipped | ❌ | ❌ |
| **Job** | running | ❌ | ❌ |
| **Job** | success | ❌ | ❌ |
| **Job** | failed | ❌ | ❌ |
| **Deployment** | started | ❌ | ❌ |
| **Deployment** | finished | ❌ | ❌ |
| **Release** | created | ❌ | ❌ |
| **Release** | updated | ❌ | ❌ |
| **Release** | deleted | ❌ | ❌ |
| **WikiPage** | created | ❌ | ❌ |
| **WikiPage** | updated | ❌ | ❌ |
| **WikiPage** | deleted | ❌ | ❌ |
| **TagPush** | created | ❌ | ❌ |
| **TagPush** | deleted | ❌ | ❌ |
| **Member** | added | ❌ | ❌ |
| **Member** | removed | ❌ | ❌ |
| **Member** | updated | ❌ | ❌ |

## Легенда

- ✅ - Реализовано
- ❌ - Не реализовано  
- ❓ - Требуется проверка тестового покрытия

## Примечания

1. **Pipeline события** конвертируются в унифицированный формат через функцию `pipeline_to_event()`
2. **Push события** обрабатываются через `push_data` с информацией о ветках и коммитах
3. **Комментарии** поддерживаются для всех типов сущностей (MR, Issues, Commits)
4. **DiffNote** - это специальный тип комментария к коду в Merge Request
5. **Commit события** в GitLab API приходят через Push события, но в glping обрабатываются как отдельный тип
6. **TagPush** - отдельный тип события для операций с тегами, отличается от обычных Push событий
7. **Job события** - отдельные задачи внутри Pipeline, могут быть полезны для детального мониторинга CI/CD
8. **Deployment события** - события развёртывания, важны для мониторинга релизного процесса

## Статистика реализации

- **Реализовано событий**: 23 из 38 (60.5%)
- **Покрыто тестами**: 23 из 23 реализованных (100%)
- **Не реализовано**: 15 из 38 (39.5%)
- **Наиболее покрытые типы**: MergeRequest, Issue, Note, Pipeline, Push
- **Отсутствующие типы**: Job, Deployment, Release, WikiPage, TagPush, Member

## Новые события в Приоритете 1

### MergeRequest (добавлено 5 новых действий):
- `reopened` - Merge Request переоткрыт
- `unapproved` - Одобрение Merge Request отозвано
- `review_requested` - Запрошено ревью Merge Request
- `ready` - Merge Request переведен в статус Ready
- `draft` - Merge Request переведен в статус Draft

### Issue (добавлено 2 новых действия):
- `updated` - Задача обновлена
- `moved` - Задача перемещена

### Push (добавлено 3 новых действия):
- `new branch` - Создана новая ветка
- `delete branch` - Удалена ветка
- `tag push` - Создан/удален тег

## Детали тестового покрытия

### Полностью покрытые тестами события:
- **Pipeline**: все 5 статусов (success, failed, running, pending, canceled) имеют комплексные тесты в `test_pipeline_events.py` и `test_ci_integration_simple.py`
- **MergeRequest**: основные действия (opened, updated, closed, merged, approved) тестируются в `test_gitlab_events.py` и `test_all_notifications.py`
- **Issue**: основные действия (opened, closed, reopened) покрываются в симуляционных тестах
- **Note/DiffNote**: комментарии ко всем типам сущностей тестируются
- **Commit**: новые коммиты покрываются в тестах уведомлений
- **Push**: все варианты push событий тестируются

### Файлы тестов:
- `test_pipeline_events.py` - исчерпывающие тесты для pipeline событий
- `test_ci_integration_simple.py` - базовые CI тесты
- `test_gitlab_events.py` - симуляция всех типов событий
- `test_all_notifications.py` - тестирование уведомлений для всех типов
- `test_new_events.py` - специализированные тесты для новых событий Приоритета 1
- `test_url_comparison.py` - тестирование URL генерации для разных типов событий