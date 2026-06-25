import os
import time
from dataclasses import dataclass

import requests
from requests import exceptions as request_exceptions


@dataclass(frozen=True)
class WebResult:
    title: str
    url: str
    content: str
    position: int


class WebSearchError(RuntimeError):
    user_message = '联网搜索暂时不可用，已基于本地资料回答。'


class WebSearchConfigError(WebSearchError):
    user_message = '联网搜索未配置，请检查 Tavily API Key。'


class WebSearchAuthError(WebSearchError):
    user_message = '联网搜索认证失败，请检查 Tavily API Key。'


def search_web(query: str, max_results: int | None = None) -> list[WebResult]:
    api_key = os.getenv('TAVILY_API_KEY', '').strip()
    if not api_key:
        raise WebSearchConfigError('TAVILY_API_KEY 未配置')

    limit = max_results or int(os.getenv('TAVILY_MAX_RESULTS', '5'))
    search_depth = os.getenv('TAVILY_SEARCH_DEPTH', 'basic')
    retries = int(os.getenv('TAVILY_MAX_RETRIES', '1'))
    backoff = float(os.getenv('TAVILY_RETRY_BACKOFF_SECONDS', '0.2'))
    timeout = float(os.getenv('TAVILY_TIMEOUT_SECONDS', '20'))

    response = _post_with_retries(
        'https://api.tavily.com/search',
        headers={
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
        },
        json={
            'query': query,
            'search_depth': search_depth,
            'max_results': limit,
            'include_answer': False,
            'include_raw_content': False,
        },
        timeout=timeout,
        retries=retries,
        backoff=backoff,
    )
    data = response.json()

    results: list[WebResult] = []
    for index, item in enumerate(data.get('results', []), start=1):
        title = (item.get('title') or '').strip()
        url = (item.get('url') or '').strip()
        content = (item.get('content') or '').strip()
        if not url or not content:
            continue
        results.append(
            WebResult(
                title=title or url,
                url=url,
                content=content[:800],
                position=index,
            )
        )
    return results


def _post_with_retries(
    url: str,
    headers: dict[str, str],
    json: dict,
    timeout: float,
    retries: int,
    backoff: float,
) -> requests.Response:
    last_error: Exception | None = None
    attempts = max(1, retries + 1)

    for attempt in range(attempts):
        try:
            response = requests.post(
                url,
                headers=headers,
                json=json,
                timeout=timeout,
            )
            _raise_for_tavily_status(response)
            return response
        except (WebSearchAuthError, WebSearchConfigError):
            raise
        except (
            request_exceptions.Timeout,
            request_exceptions.ConnectionError,
            request_exceptions.ChunkedEncodingError,
            WebSearchError,
        ) as exc:
            last_error = exc
            if attempt >= attempts - 1:
                break
            if backoff > 0:
                time.sleep(backoff * (attempt + 1))

    raise WebSearchError(str(last_error or 'Tavily request failed'))


def _raise_for_tavily_status(response: requests.Response) -> None:
    status_code = response.status_code
    if status_code < 400:
        return
    if status_code in (401, 403):
        raise WebSearchAuthError(_safe_error_text(response))
    if status_code == 400:
        raise WebSearchConfigError(_safe_error_text(response))
    if status_code == 429 or status_code >= 500:
        raise WebSearchError(_safe_error_text(response))
    raise WebSearchError(_safe_error_text(response))


def _safe_error_text(response: requests.Response) -> str:
    return response.text[:500] if response.text else f'HTTP {response.status_code}'
