SEARCH_MODE_LOCAL = 'local'
SEARCH_MODE_WEB = 'web'
SEARCH_MODE_HYBRID = 'hybrid'

SEARCH_MODE_CHOICES = (
    (SEARCH_MODE_LOCAL, '本地资料'),
    (SEARCH_MODE_WEB, '联网搜索'),
    (SEARCH_MODE_HYBRID, '混合搜索'),
)


def normalize_search_mode(search_mode: str | None, web_search: bool = False) -> str:
    mode = search_mode or SEARCH_MODE_LOCAL
    if web_search and mode == SEARCH_MODE_LOCAL:
        return SEARCH_MODE_HYBRID
    return mode


def uses_local_retrieval(search_mode: str) -> bool:
    return search_mode in (SEARCH_MODE_LOCAL, SEARCH_MODE_HYBRID)


def uses_web_search(search_mode: str) -> bool:
    return search_mode in (SEARCH_MODE_WEB, SEARCH_MODE_HYBRID)
