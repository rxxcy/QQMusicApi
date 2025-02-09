"""请求 Session 管理"""

import contextvars
from typing import TypedDict

import httpx
from aiocache import Cache
from aiocache.serializers import JsonSerializer

from .credential import Credential
from .qimei import get_qimei


class ApiConfig(TypedDict):
    """API 配置"""

    version: str
    version_code: int
    enable_sign: bool
    endpoint: str
    enc_endpoint: str


class Session(httpx.AsyncClient):
    """Session 类,用于管理 QQ 音乐的登录态和 API 请求

    Args:
        credential: 全局凭证,每个请求都将使用.
        enable_sign: 是否启用加密接口
        enable_cache: 是否启用请求缓存
        cache_ttl: 缓存过期时间
    """

    HOST = "y.qq.com"
    UA_DEFAULT = "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.54"

    def __init__(
        self,
        *,
        credential: Credential | None = None,
        enable_sign: bool = False,
        enable_cache: bool = True,
        cache_ttl: int = 120,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.credential = credential
        self.headers.update(
            {
                "User-Agent": self.UA_DEFAULT,
                "Referer": self.HOST,
            }
        )
        self.api_config = ApiConfig(
            version="13.2.5.8",
            version_code=13020508,
            enable_sign=enable_sign,
            endpoint="https://u.y.qq.com/cgi-bin/musicu.fcg",
            enc_endpoint="https://u.y.qq.com/cgi-bin/musics.fcg",
        )
        self.enable_cache = enable_cache
        self._cache = Cache(serializer=JsonSerializer(), ttl=cache_ttl)
        self.qimei = get_qimei(self.api_config["version"])["q36"]

    async def __aenter__(self) -> "Session":
        """进入 async with 上下文时调用"""
        self._previous_session = _session_context.set(self)
        return self

    async def __aexit__(self, *args, **kwargs) -> None:
        """退出 async with 上下文时调用"""
        _session_context.reset(self._previous_session)
        await self.aclose()


_session_context: contextvars.ContextVar[Session | None] = contextvars.ContextVar("_session_context", default=None)


def get_session() -> Session:
    """获取当前上下文的 Session"""
    session = _session_context.get()
    if session is None:
        session = Session()
        _session_context.set(session)
    return session


def set_session(session: Session) -> None:
    """设置当前上下文的 Session"""
    _session_context.set(session)


def clear_session() -> None:
    """清除当前上下文的 Session"""
    try:
        _session_context.set(None)
    except LookupError:
        pass
