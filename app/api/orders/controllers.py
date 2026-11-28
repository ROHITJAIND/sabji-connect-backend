"""Order controller — delegates to OrderService."""

from typing import Optional

from app.api.orders.schemas import CreateOrderRequest, OrderResponse
from app.api.orders.services import OrderService
from app.models.user import User


class OrderController:
    @staticmethod
    async def list_orders(user: User) -> list[OrderResponse]:
        return await OrderService.list_orders(user)

    @staticmethod
    async def create_order(user: User, body: Optional[CreateOrderRequest] = None) -> OrderResponse:
        return await OrderService.create_order(user, body)

    @staticmethod
    async def get_order(order_id: str) -> OrderResponse:
        return await OrderService.get_order(order_id)

    @staticmethod
    async def update_order(order_id: str, body: dict, user: User) -> OrderResponse:
        return await OrderService.update_order(order_id, body, user)

    @staticmethod
    async def delete_order(order_id: str, user: User) -> dict:
        return await OrderService.delete_order(order_id, user)
