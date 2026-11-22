import httpx

from config import settings
from prompts import SYSTEM_PROMPT
from schemas import DailyTaskReport


def _format_tasks_for_prompt(username: str, tasks: DailyTaskReport) -> str:
    sections = [f"Имя пользователя: {username}"]

    if tasks.completed:
        completed_list = "\n".join(f"- {item}" for item in tasks.completed)
        sections.append(f"Выполненные задачи:\n{completed_list}")

    if tasks.created:
        created_list = "\n".join(f"- {item}" for item in tasks.created)
        sections.append(f"Новые созданные задачи:\n{created_list}")

    if tasks.updated:
        updated_list = "\n".join(f"- {item}" for item in tasks.updated)
        sections.append(f"Обновлённые задачи:\n{updated_list}")

    return "\n\n".join(sections)


async def generate_summary(
    client: httpx.AsyncClient,
    username: str,
    tasks: DailyTaskReport,
) -> str:
    if not tasks.completed and not tasks.created and not tasks.updated:
        return (
            f"Привет, {username}!\n\n"
            "За последние 24 часа изменений по вашим задачам не было. "
            "Отличный повод запланировать пару шагов на завтра!"
        )

    user_content = _format_tasks_for_prompt(username, tasks)

    headers = {
        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": settings.GROQ_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        "temperature": 0.6,
    }

    response = await client.post(
        settings.GROQ_API_URL,
        headers=headers,
        json=payload,
        timeout=20.0,
    )
    response.raise_for_status()
    data = response.json()

    return data["choices"][0]["message"]["content"].strip()