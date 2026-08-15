# Теоритическое введение, необходимое для понимания работы фреймворка (любого)

## 1. Coroutine VS Task
**Coroutine** - это функция, объект, который может быть приостановлен и возобновлен в любой момент. Она позволяет выполнять асинхронные операции без блокировки основного потока выполнения.

**Task** - это обертка надо корутиной, которую asyncio передает event loop для ПЛАНИРУЕМОГО выполнения.

*СУТЬ: Корутина - это функция, которая может быть приостановлена и возобновлена, а Task - это объект, который управляет выполнением корутины в рамках event loop.*

**Главное преимущество Task - запустить несколько coroutine конкурентно.**

    Coroutine - это awaitable объект, представляющий приостановляемое выполнение асинхронной функции. Task - это объект asyncio, который оборачивает coroutine и планирует её выполнение в event loop.

## 2. Отмена задач и CancelledError
### Что такое отмена Task?
В asyncio Task можно отменить, вызвав метод `cancel()`. Когда Task отменяется, она поднимает исключение `CancelledError`. Он запрашивает отмену. При следующей возможности внутри coroutine возникает `asyncio.CancelledError`

Например:
```python
import asyncio

async def worker():
    try:
        await asyncio.sleep(10)
        print("закончил работу")
    except asyncio.CancelledError:
        print("отмена задачи")
        raise

async def main():
    task = asyncio.create_task(worker())

    await asyncio.sleep(1)

    task.cancel()

    try:
        await task
    except asyncio.CancelledError:
        print("задача была отменена")

asyncio.run(main())
```

```
create_task()
     ↓
worker запущен
     ↓
await sleep(10)
     ↓
task.cancel()
     ↓
CancelledError
     ↓
worker получает исключение
     ↓
finally / cleanup
     ↓
Task становится cancelled
```
### Что такое CancelledError?
`asyncio.CancelledError` - это специальное исключение, которое используется для сигнализации отмены задачи.

```python
try:
    await something()
except asyncio.CancelledError:
    # cleanup
    raise
```

### Как проверить, отменена ли Task?
Есть такая штука как `task.cancelled()`, которая возвращает True, если Task была отменена.

```python
task = asyncio.create_task(worker())
await asyncio.sleep(1)
task.cancel()
if task.cancelled():
    print("Task была отменена")
```

### Очень важная разница: cancel() vs CancelledError
На собеседовании могут спросить:
`Что делает task.cancel()?`
Здесь важно правильно ответить, что `task.cancel()` не отменяет задачу мгновенно. Она просто ставит флаг отмены и при следующей возможности внутри coroutine будет поднято исключение `CancelledError`. Т. е. `task.cancel()` запрашивает отмену Task. При обработке этого запроса в выполняемой coroutine возникает CancelledError, обычно в точке приостановки await.

### Как отвечать на собеседовании?
В asyncio Task можно отменить с помощью `task.cancel()`. Это не мгновенное убийство Task, а запрос на отмену. Когда coroutine получает возможность обработать отмену, в ней возникает `asyncio.CancelledError`. Обычно это исключение нужно не поглощать, а после необходимого cleanup пробросить через `raise`, чтобы состояние отмены сохранилось. Для освобождения ресурсов используют `finally`. При `await` отменённой Task вызывающему коду также передаётся `asyncio.CancelledError`.

# Coming Soon
- asyncio.gather/wait,
- contextvars (понадобится для request-scope DI),
- почему блокирующий вызов в корутине убивает весь сервер.