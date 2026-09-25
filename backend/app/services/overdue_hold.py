"""逾期扫描时的占位去留。"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.models import RailPlacement, WorkOrder


def release_hung_overdue(db: Session, order: WorkOrder, now: datetime) -> None:
    """已 hung 且到期：标 overdue，同时释放其 active 占位，腾出杆位。"""
    order.status = "overdue"
    rows = db.scalars(
        select(RailPlacement).where(RailPlacement.order_id == order.id, RailPlacement.active == 1)
    ).all()
    for row in rows:
        row.active = 0


def mark_ready_overdue(db: Session, order: WorkOrder, now: datetime) -> None:
    """ready 到期：只改状态为 overdue，不产生任何占位。"""
    order.status = "overdue"
