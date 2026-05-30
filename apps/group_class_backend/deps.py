from __future__ import annotations

from dataclasses import dataclass, field

from fastapi import Header


@dataclass(frozen=True)
class ActorContext:
    """请求发起人身份上下文，由 FastAPI Depends 注入路由函数。"""

    actor_id: str
    actor_roles: list[str] = field(default_factory=list)


def get_actor(
    x_actor_id: str = Header(default="u_anonymous"),
    x_actor_roles: str = Header(default=""),
) -> ActorContext:
    """从 HTTP Header 解析 actor 信息。后期替换为 JWT 只改此函数。"""

    roles = [role.strip() for role in x_actor_roles.split(",") if role.strip()]
    return ActorContext(actor_id=x_actor_id, actor_roles=roles)
