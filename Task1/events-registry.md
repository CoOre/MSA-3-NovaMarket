# Реестр событий Saga-хореографии «Оформление заказа»

Сценарий оформления заказа реализован как **Saga-хореография**: сервисы не вызывают
друг друга напрямую, а реагируют на события в брокере (Kafka). Каждый сервис —
участник саги — публикует результат своего шага, а следующий участник подписан на это
событие.

Типы событий:
- **domain** — успешный результат бизнес-шага (двигает сагу вперёд);
- **failure** — ошибка на шаге (запускает откат);
- **compensation** — компенсирующее действие (откатывает уже выполненные шаги).

> **О классификации `OrderCancelled`.** Это событие одновременно фиксирует финальное
> доменное состояние заказа («Отменён»). Мы относим его к типу **compensation**,
> потому что в рамках саги оно играет роль компенсации исходного шага `OrderCreated`:
> завершает откат и переводит заказ в терминальное «отменён». Если рассматривать его
> как чисто доменное состояние — допустима трактовка `domain`; на логику саги это не
> влияет.

| Этап | Тип события | Название | Издатель | Подписчики |
| --- | --- | --- | --- | --- |
| Создание заказа | domain | `OrderCreated` | Order Service | Inventory Service |
| Резервирование товара — успех | domain | `InventoryReserved` | Inventory Service | Payment Service, Order Service |
| Резервирование товара — ошибка | failure | `InventoryReservationFailed` | Inventory Service | Order Service |
| Оплата — успех | domain | `PaymentSucceeded` | Payment Service | Delivery Service, Notification Service, Order Service |
| Оплата — ошибка | failure | `PaymentFailed` | Payment Service | Inventory Service, Order Service |
| Формирование доставки — успех | domain | `DeliveryRequestCreated` | Delivery Service | Notification Service, Order Service |
| Формирование доставки — ошибка | failure | `DeliveryRequestFailed` | Delivery Service | Payment Service, Inventory Service, Order Service |
| Завершение заказа | domain | `OrderConfirmed` | Order Service | Notification Service |
| Компенсация: освобождение резерва | compensation | `InventoryReleased` | Inventory Service | Order Service |
| Компенсация: возврат средств | compensation | `PaymentRefunded` | Payment Service | Order Service |
| Компенсация: отмена заказа | compensation | `OrderCancelled` | Order Service | Notification Service |

## Логика компенсаций

- **Ошибка резервирования** (`InventoryReservationFailed`) → откатывать нечего, заказ
  сразу отменяется (`OrderCancelled`).
- **Ошибка оплаты** (`PaymentFailed`) → нужно освободить резерв
  (`InventoryReleased`), затем `OrderCancelled`.
- **Ошибка доставки** (`DeliveryRequestFailed`) → вернуть деньги (`PaymentRefunded`)
  и освободить резерв (`InventoryReleased`), затем `OrderCancelled`.
