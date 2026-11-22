
from app.core.unit_of_work import SqlAlchemyUnitOfWork
from app.tasks.email import process_user_daily_summary


class DispatchDailySummariesCase:
    def __init__(self, unit: SqlAlchemyUnitOfWork):
        self.unit = unit

    async def execute(self) -> None:
        async with self.unit:
            user_ids = await self.unit.users.get_all()
            if not user_ids:
                return
        for user_id in user_ids:
            process_user_daily_summary.delay(str(user_id))