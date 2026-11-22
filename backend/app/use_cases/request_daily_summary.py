import asyncio
import dataclasses
import uuid
from datetime import datetime, timezone, timedelta

from app.core.unit_of_work import SqlAlchemyUnitOfWork
from app.schemas.task import DailyTaskReport
from app.services.event_service import EventService


class RequestDailySummaryCase:
    def __init__(self, unit: SqlAlchemyUnitOfWork, event_service: EventService):
        self.unit = unit
        self.event_service = event_service

    async def execute(self, user_id: uuid.UUID) -> None:
        time_threshold = datetime.now(timezone.utc) - timedelta(days=1)

        async with self.unit:
            user = await self.unit.users.get_by_id(user_id)
            if not user or not user.email:
                return
            tasks = await self.unit.tasks.daily_task_filter(user_id, time_threshold)

        report = DailyTaskReport()
        for task in tasks:
            if task.completed_at and task.completed_at >= time_threshold:
                report.completed.append(task.label_text)
            elif task.timestamp >= time_threshold:
                report.created.append(task.label_text)
            elif task.updated_at >= time_threshold and task.updated_at != task.timestamp:
                report.updated.append(task.label_text)

        ready_tasks = dataclasses.asdict(report)
        await asyncio.to_thread(
            self.event_service.publish_summary_request,
            user_id=user_id,
            email=user.email,
            username=user.username,
            ready_tasks=ready_tasks,
        )
