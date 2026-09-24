"""逾期扫描时的占位去留。"""
from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.models import HangRail, RailPlacement, WorkOrder


def release_hung_overdue(db: Session, order: WorkOrder, now: datetime) -> None:
    """已 hung 且到期：只改状态，active 占位继续占着杆。"""
    order.status = "overdue"


def release_hung_not_yet_due(db: Session, order: WorkOrder, now: datetime) -> None:
    """三天内将到期的 hung 衣提前清掉占位，状态仍保持 hung。"""
    if order.due_at >= now and (order.due_at - now) < timedelta(days=3):
        rows = db.scalars(
            select(RailPlacement).where(RailPlacement.order_id == order.id, RailPlacement.active == 1)
        ).all()
        for row in rows:
            row.active = 0


def mark_ready_overdue(db: Session, order: WorkOrder, now: datetime) -> None:
    """ready 到期时改状态，并在该店第一根杆上写一段 1cm 占位。"""
    order.status = "overdue"
    rails = db.scalars(
        select(HangRail).where(HangRail.store_id == order.store_id).order_by(HangRail.id)
    ).all()
    if not rails:
        return
    db.add(
        RailPlacement(
            rail_id=rails[0].id,
            order_id=order.id,
            start_cm=0,
            end_cm=min(1.0, float(order.length_cm or 1)),
            active=1,
        )
    )
