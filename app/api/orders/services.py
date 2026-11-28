"""Order service — business logic, DB queries, and WS broadcast."""

from datetime import datetime, timezone
from typing import Optional

from beanie import PydanticObjectId

from app.api.orders.schemas import (
    CreateOrderRequest,
    OrderResponse,
)
from app.api.websocket.services import ws_manager
from app.core.exceptions import BadRequestError, NotAuthorizedError, NotFoundError
from app.models.enums import OrderStatus, UserRole
from app.models.order import Order, OrderItem
from app.models.user import User


class OrderService:
    @staticmethod
    def serialize_order(order: Order) -> OrderResponse:
        items = []
        for item in order.items:
            cid = str(item.catalog_item_id) if item.catalog_item_id else ""
            items.append({
                "catalog_item_id": cid,
                "catalogId": cid,
                "name": item.name,
                "qty": item.qty,
                "unit": item.unit or "pieces",
                "status": item.status or "pending",
            })
        return OrderResponse(
            id=str(order.id),
            status=order.status,
            items=items,
            createdBy=str(order.created_by) if order.created_by else "",
            createdByName=order.created_by_name or "",
            familyId=str(order.family_id) if order.family_id else None,
            orderDate=order.order_date or "",
            fulfilledBy=str(order.fulfilled_by) if order.fulfilled_by else None,
            publishTrigger=order.publish_trigger,
            totalExpense=order.total_expense or 0.0,
            batchId=order.batch_id,
            createdAt=order.created_at.isoformat() if order.created_at else None,
            updatedAt=order.updated_at.isoformat() if order.updated_at else None,
        )

    @staticmethod
    async def list_orders(user: User) -> list[OrderResponse]:
        if user.role == UserRole.ADMIN:
            orders = await Order.find_all().to_list()
        elif user.role == UserRole.SETHJI:
            filters = {"status": {"$in": [OrderStatus.PUBLISHED, OrderStatus.FULFILLING, OrderStatus.ARCHIVED]}}
            if user.family_ids:
                f_ids = []
                for fid in user.family_ids:
                    f_ids.append(str(fid))
                    try:
                        f_ids.append(PydanticObjectId(str(fid)))
                    except Exception:
                        pass
                filters["family_id"] = {"$in": f_ids}
            orders = await Order.find(filters).to_list()
        else:
            # Hukum role:
            # Can see own orders (including Drafts)
            # AND any family orders that are Published, Fulfilling, or Archived
            u_ids = [user.id, str(user.id)]
            try:
                u_ids.append(PydanticObjectId(str(user.id)))
            except Exception:
                pass

            or_conditions = [{"created_by": {"$in": u_ids}}]
            if user.family_ids:
                f_ids = []
                for fid in user.family_ids:
                    f_ids.append(str(fid))
                    try:
                        f_ids.append(PydanticObjectId(str(fid)))
                    except Exception:
                        pass
                or_conditions.append({
                    "family_id": {"$in": f_ids},
                    "status": {"$in": [OrderStatus.PUBLISHED, OrderStatus.FULFILLING, OrderStatus.ARCHIVED]},
                })
            orders = await Order.find({"$or": or_conditions}).to_list()

        return [OrderService.serialize_order(o) for o in orders]

    @staticmethod
    async def create_order(user: User, body: Optional[CreateOrderRequest] = None) -> OrderResponse:
        order_date = (
            body.order_date
            if body and body.order_date
            else datetime.now(timezone.utc).strftime("%Y-%m-%d")
        )
        order_family_id = (
            body.family_id
            if body and body.family_id
            else (user.family_ids[0] if user.family_ids else None)
        )
        order_status = (
            body.status
            if body and body.status
            else OrderStatus.PUBLISHED
        )
        order_items = []
        if body and body.items:
            order_items = [
                OrderItem(**item) if isinstance(item, dict) else item
                for item in body.items
            ]
        publish_trigger = body.publish_trigger if body else None

        created_by_name = user.display_name or getattr(user, "username", "") or (user.email.split("@")[0] if user.email else "Family Member")
        order = Order(
            status=order_status,
            items=order_items,
            created_by=user.id,
            created_by_name=created_by_name,
            family_id=order_family_id,
            order_date=order_date,
            publish_trigger=publish_trigger,
        )
        await order.insert()

        if order.family_id:
            await ws_manager.broadcast_to_family(
                order.family_id,
                "order_created",
                {
                    "orderId": str(order.id),
                    "status": order.status,
                },
            )

        return OrderService.serialize_order(order)

    @staticmethod
    async def get_order(order_id: str) -> OrderResponse:
        order = await Order.get(PydanticObjectId(order_id))
        if not order:
            raise NotFoundError("Order not found")
        return OrderService.serialize_order(order)

    @staticmethod
    async def update_order(order_id: str, body: dict, user: User) -> OrderResponse:
        order = await Order.get(PydanticObjectId(order_id))
        if not order:
            raise NotFoundError("Order not found")

        # Restrict Hukum from editing another Hukum's order
        if user.role == UserRole.HUKUM and str(order.created_by) != str(user.id):
            raise NotAuthorizedError("You can only edit your own orders")

        update_data: dict = {"updated_at": datetime.now(timezone.utc)}

        key_map = {
            "status": "status",
            "items": "items",
            "fulfilledBy": "fulfilled_by",
            "publishTrigger": "publish_trigger",
            "orderDate": "order_date",
            "totalExpense": "total_expense",
            "batchId": "batch_id",
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

        if user.role != UserRole.ADMIN and str(order.created_by) != str(user.id):
            raise NotAuthorizedError("You can only delete your own orders")

        await order.delete()

        if order.family_id:
            await ws_manager.broadcast_to_family(
                order.family_id,
                "order_deleted",
                {"orderId": order_id},
            )

        return {"id": order_id, "message": "Deleted"}
