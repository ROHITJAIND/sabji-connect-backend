"""Order service — business logic, DB queries, and WS broadcast."""

from datetime import datetime, timezone
from typing import Optional

from beanie import PydanticObjectId

from app.api.orders.schemas import (
    CreateOrderRequest,
    OrderResponse,
)
from app.api.websocket.services import ws_manager
from app.core.exceptions import BadRequestError, NotFoundError
from app.models.order import Order, OrderItem
from app.models.user import User


class OrderService:
    @staticmethod
    def serialize_order(order: Order) -> OrderResponse:
        return OrderResponse(
            id=str(order.id),
            status=order.status,
            items=[item.model_dump() for item in order.items],
            createdBy=order.created_by,
            createdByName=order.created_by_name,
            familyId=order.family_id,
            orderDate=order.order_date,
            fulfilledBy=order.fulfilled_by,
            publishTrigger=order.publish_trigger,
            createdAt=order.created_at.isoformat() if order.created_at else None,
            updatedAt=order.updated_at.isoformat() if order.updated_at else None,
        )

    @staticmethod
    async def list_orders(user: User) -> list[OrderResponse]:
        if user.role == "Admin":
            orders = await Order.find_all().to_list()
        elif user.role == "Sethji":
            filters = {"status": {"$in": ["Published", "Fulfilling", "Archived"]}}
            if user.family_id:
                filters["family_id"] = user.family_id
            orders = await Order.find(filters).to_list()
        else:
            orders = await Order.find(Order.created_by == str(user.id)).to_list()

        return [OrderService.serialize_order(o) for o in orders]

    @staticmethod
    async def create_order(user: User, body: Optional[CreateOrderRequest] = None) -> OrderResponse:
        order_date = (
            body.order_date
            if body and body.order_date
            else datetime.now(timezone.utc).strftime("%Y-%m-%d")
        )
        order = Order(
            status="Draft",
            items=[],
            created_by=str(user.id),
            created_by_name=user.display_name or user.email.split("@")[0],
            family_id=user.family_id,
            order_date=order_date,
        )
        await order.insert()
        return OrderService.serialize_order(order)

    @staticmethod
    async def get_order(order_id: str) -> OrderResponse:
        order = await Order.get(PydanticObjectId(order_id))
        if not order:
            raise NotFoundError("Order not found")
        return OrderService.serialize_order(order)

    @staticmethod
    async def update_order(order_id: str, body: dict) -> OrderResponse:
        order = await Order.get(PydanticObjectId(order_id))
        if not order:
            raise NotFoundError("Order not found")

        update_data: dict = {"updated_at": datetime.now(timezone.utc)}

        key_map = {
            "status": "status",
            "items": "items",
            "fulfilledBy": "fulfilled_by",
            "publishTrigger": "publish_trigger",
            "orderDate": "order_date",
        }

        for frontend_key, model_key in key_map.items():
            if frontend_key in body:
                value = body[frontend_key]
                if model_key == "items" and isinstance(value, list):
                    value = [
                        OrderItem(**item) if isinstance(item, dict) else item
                        for item in value
                    ]
                update_data[model_key] = value

        await order.set(update_data)

        if order.family_id:
            await ws_manager.broadcast_to_family(
                order.family_id,
                "order_updated",
                {
                    "orderId": order_id,
                    "status": update_data.get("status", order.status),
                },
            )

        return OrderService.serialize_order(order)

    @staticmethod
    async def delete_order(order_id: str, user: User) -> dict:
        order = await Order.get(PydanticObjectId(order_id))
        if not order:
            raise NotFoundError("Order not found")

        if user.role != "Admin" and order.created_by != str(user.id):
            raise BadRequestError("You can only delete your own orders")

        await order.delete()

        if order.family_id:
            await ws_manager.broadcast_to_family(
                order.family_id,
                "order_deleted",
                {"orderId": order_id},
            )

        return {"id": order_id, "message": "Deleted"}
