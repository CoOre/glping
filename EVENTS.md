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
| **Pipeline** | skipped | ✅ | ✅ |
| **Job** | running | ✅ | ✅ |
| **Job** | success | ✅ | ✅ |
| **Job** | failed | ✅ | ✅ |
| **Job** | pending | ✅ | ✅ |
| **Job** | canceled | ✅ | ✅ |
| **Job** | skipped | ✅ | ✅ |
| **Job** | manual | ✅ | ✅ |
| **Deployment** | created | ✅ | ✅ |
| **Deployment** | running | ✅ | ✅ |
| **Deployment** | success | ✅ | ✅ |
| **Deployment** | failed | ✅ | ✅ |
| **Deployment** | canceled | ✅ | ✅ |
| **Deployment** | skipped | ✅ | ✅ |
| **Release** | created | ✅ | ✅ |
| **Release** | updated | ✅ | ✅ |
| **Release** | deleted | ✅ | ✅ |
| **WikiPage** | created | ✅ | ✅ |
| **WikiPage** | updated | ✅ | ✅ |
| **WikiPage** | deleted | ✅ | ✅ |
| **TagPush** | created | ✅ | ✅ |
| **TagPush** | deleted | ✅ | ✅ |
| **Member** | added | ✅ | ✅ |
| **Member** | removed | ✅ | ✅ |
| **Member** | updated | ✅ | ✅ |

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
9. **Release события** - события управления релизами, включают создание, обновление и удаление релизов
10. **WikiPage события** - события управления wiki страницами, включают создание, обновление и удаление
11. **TagPush события** - события управления тегами, включают создание и удаление тегов
12. **Member события** - события управления участниками проекта, включают добавление, удаление и обновление прав доступа

## Статистика реализации

- **Реализовано событий**: 50 из 50 (100%)
- **Покрыто тестами**: 50 из 50 реализованных (100%)
- **Не реализовано**: 0 из 50 (0%)
- **Полностью покрытые типы**: MergeRequest, Issue, Note, Pipeline, Push, Job, Deployment, Release, WikiPage, TagPush, Member
- **Осталось реализовать**: Нет

## Новые события в Приоритете 2

### Pipeline (добавлено 1 действие):
- `skipped` - Pipeline пропущен

### Job (добавлено 7 новых действий):
- `running` - Job выполняется
- `success` - Job успешно выполнен
- `failed` - Job выполнен с ошибкой
- `pending` - Job ожидает
- `canceled` - Job отменен
- `skipped` - Job пропущен
- `manual` - Job запущен вручную

### Deployment (добавлено 6 новых действий):
- `created` - Развертывание создано
- `running` - Развертывание выполняется
- `success` - Развертывание успешно
- `failed` - Развертывание с ошибкой
- `canceled` - Развертывание отменено
- `skipped` - Развертывание пропущено

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

## Новые события в Приоритете 3

### Release (добавлено 3 новых действия):
- `created` - Релиз создан
- `updated` - Релиз обновлен
- `deleted` - Релиз удален

### WikiPage (добавлено 3 новых действия):
- `created` - Wiki страница создана
- `updated` - Wiki страница обновлена
- `deleted` - Wiki страница удалена

### TagPush (добавлено 2 новых действия):
- `created` - Тег создан
- `deleted` - Тег удален

### Member (добавлено 3 новых действия):
- `added` - Участник добавлен
- `removed` - Участник удален
- `updated` - Участник обновлен

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
- `test_ci_cd_events.py` - специализированные тесты для CI/CD событий
- `test_gitlab_events.py` - симуляция всех типов событий
- `test_all_notifications.py` - тестирование уведомлений для всех типов
- `test_new_events.py` - специализированные тесты для новых событий Приоритета 1
- `test_project_management_events.py` - специализированные тесты для событий управления проектом (Release, WikiPage, TagPush, Member)
- `test_url_comparison.py` - тестирование URL генерации для разных типов событий