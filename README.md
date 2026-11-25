# Мышонок Тим — корпус и новые сказки

Репозиторий для исследования детских книг о мышонке Тиме и создания новых неофициальных иллюстрированных сказок на основе выявленных литературных принципов.

[![Build changed stories](https://github.com/Hozren/mouse-tim-fairy-tales/actions/workflows/build-stories.yml/badge.svg)](https://github.com/Hozren/mouse-tim-fairy-tales/actions/workflows/build-stories.yml)

## Что находится в проекте

- `origin/` — 24 распакованные книги (оригинальные EPUB удалены как дубли): 23 книги Анны Казалис и отдельная сказка Дианы Булушевой «Запасливый мышонок Тим»;
- `generated/` — новые неофициальные сказки, каждая в собственной директории;
- `docs/` — литературный анализ, описание сборочного pipeline и реестр производных артефактов;
- `.skills/tim-story-production/` — воспроизводимый процесс подготовки сказки, раскадровки, иллюстраций, EPUB и PDF;
- `.github/workflows/build-stories.yml` — выборочная сборка изменённых сказок в GitHub Actions.

В `generated/` находятся сказки:

- «Мышонок Тим. Лили надевает всё сразу!» — завершённая иллюстрированная книга, 17 сцен.
- «Мышонок Тим. Лили и зимнее солнышко» — новая история об одежде не по погоде, 16 сцен, обложка, готовые EPUB3 и PDF.

- «Мышонок Тим опять уронил прод» — взрослая айтишная пародия, 17 сцен, обложка, проверенные EPUB3 и PDF на 18 страниц.

## Сборка EPUB и PDF

Для сборки нужны Python 3.12 и зависимости из `.github/requirements-build.txt`.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r .github/requirements-build.txt

python .skills/tim-story-production/scripts/build_epub.py \
  generated/mishonok-tim-lili-nadevaet-vse-srazu

python .skills/tim-story-production/scripts/build_pdf.py \
  generated/mishonok-tim-lili-nadevaet-vse-srazu
```

По умолчанию сборки сохраняются в игнорируемый `_dist/<story-slug>/`, а не рядом с исходниками. Готовые книги: [GitHub Releases](https://github.com/Hozren/mouse-tim-fairy-tales/releases).

Оба сборщика используют `generated/<story-slug>/book.json` как единый источник данных. Полноразмерные PNG остаются мастер-исходниками, а в публикационные файлы попадают оптимизированные JPEG-производные.

## Автоматическая сборка

GitHub Actions анализирует Git diff и формирует отдельный matrix job только для изменённых директорий `generated/<story-slug>/`. Для каждой выбранной сказки публикуется отдельный artifact с EPUB и PDF. Изменения остальных сказок не вызывают их пересборку.

Ручной запуск `workflow_dispatch` пересобирает все сказки. Подробности: [docs/build-pipeline.md](docs/build-pipeline.md).

## Как добавить новую сказку

1. Прочитать [AGENTS.md](AGENTS.md), [литературный анализ](docs/literary-analysis.md) и локальный skill [.skills/tim-story-production/](.skills/tim-story-production/SKILL.md).
2. Создать отдельную директорию `generated/<story-slug>/`.
3. Подготовить текст, раскадровку, визуальный якорь персонажей и иллюстрации.
4. Добавить финальный `book.json` и собрать обе публикационные версии.
5. Проверить EPUB, PDF, соответствие сцен иллюстрациям и обновить [реестр артефактов](docs/artifact-registry.md).

## Документация

- [Литературный анализ корпуса](docs/literary-analysis.md)
- [Сборка сказок в GitHub Actions](docs/build-pipeline.md)
- [Реестр аналитики и артефактов ИИ](docs/artifact-registry.md)
- [Правила работы агентов](AGENTS.md)

## Статус и права

Проект исследовательский и неофициальный. Он не является официальным продолжением серии и не заявляет авторство оригинальных произведений. Права на исходные книги, персонажей и иллюстрации принадлежат их правообладателям.
