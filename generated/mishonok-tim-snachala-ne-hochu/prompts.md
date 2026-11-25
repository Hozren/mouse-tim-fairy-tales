# Промпты иллюстраций

Дата: 2026-11-25. Автор: Аркан / ИИ. Инструмент: встроенный image_gen, без CLI/API fallback.

Общий визуальный контракт:

Use case: illustration-story. Original children’s picture book illustration, lively fine ink outlines, warm watercolor and gouache washes, visible cream paper texture, expressive kind faces, cozy home. Horizontal landscape 3:2. Use reference anchor for consistent identities and proportions: Tim small golden-orange mouse, big round pink ears, white muzzle, pink nose and tail, head tuft; father taller warm brown mouse with round glasses and teal cardigan over cream shirt, brown trousers; mother sandy beige mouse with cream blouse and green skirt, no glasses; Teddy small inanimate brown plush bear with red bow. Clothes as specified per scene override reference. No text, letters, numbers, labels, logos, signature or watermark. No photorealism, 3D, panels, inset scenes or invented people. One coherent illustration.

Якорь: предыдущий проектный якорь используется только для внешности Тима и Тедди; новый якорь включает маму и папу. Затем images/character-anchor.png — обязательный reference для каждой иллюстрации и обложки. Полные отдельные промпты сцен сохранены в prompts.json.

Обложка: вертикальная композиция 2:3, Тим в голубой пижаме у коробки-корабля, Тедди внутри, папа рядом; три карточки с пиктограммами капли, щётки и пижамы, без печатного заголовка.

## Уточнения после визуальной проверки

Сцены 02, 03, 06, 09, 10: локальное редактирование окна — тёмное вечернее небо вместо дневной листвы, сохранены композиция и действия. В 03, 09, 10 удалён лишний Тедди из ванной.
Сцена 13: Тедди носом в мягком низком домашнем тапке, не в уличном ботинке; вечерний свет. Корабль уточнён как простая открытая прямоугольная коробка, один наклеенный синий круг и две трубы. Эта исправленная сцена — дополнительный предметный reference для 12, 17 и обложки вместе с обязательным character-anchor.png.
Сцена 15: дверь ведёт в спальню, а не в сад; парусник заменён той же простой коробкой с синим кругом и двумя трубами; лишний Тедди со скамьи удалён.
Сцены 12, 17 и обложка: убраны конус, крылья, звёзды и лишняя отделка корабля, сохранены персонажи и действия; единый корабль как в сцене 13. Обложка — вертикальная, семейная сцена занимает нижние три четверти, без печатного текста.
Все правки выполнены встроенным image_gen; оригинальные результаты остались в его каталоге, в images/ сохранены только выбранные мастер-изображения.
