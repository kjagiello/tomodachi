import asyncio
import aiohttp
from typing import Any
from run_test_service_helper import start_service


def test_start_process_schedule(monkeypatch: Any, capsys: Any, loop: Any) -> None:
    services, future = start_service('tests/services/start_process_service_schedule.py', monkeypatch)

    assert services is not None
    assert len(services) == 1
    instance = services.get('test_schedule')
    assert instance is not None

    assert instance.uuid is not None

    async def _async(loop: Any) -> None:
        await asyncio.sleep(8)

    loop.run_until_complete(_async(loop))
    instance.stop_service()
    loop.run_until_complete(future)

    assert instance.function_order == [
        '_start_service',
        '_started_service',
        'every_fifth_second',
        'every_fifth_second',
        'stop_service',
        '_stop_service'
    ]


def test_start_process_http_early_request(monkeypatch: Any, capsys: Any, loop: Any) -> None:
    func, future = start_service('tests/services/start_process_service_http.py', monkeypatch, wait=False)
    port = 53251

    async def _async(loop: Any) -> None:
        await asyncio.sleep(2)
        async with aiohttp.ClientSession(loop=loop) as client:
            try:
                response = await client.get('http://127.0.0.1:{}/'.format(port))
            except Exception:
                response = False

            assert response is False

    loop.run_until_complete(_async(loop))
    loop.run_until_complete(future)

    services = func()
    assert services is not None
    assert len(services) == 1
    instance = services.get('test_http')
    assert instance is not None

    assert instance.uuid is not None

    assert instance.function_order == [
        '_start_service',
        '_started_service',
        '_stop_service'
    ]


def test_start_process_http_later_request(monkeypatch: Any, capsys: Any, loop: Any) -> None:
    func, future = start_service('tests/services/start_process_service_http.py', monkeypatch, wait=False)
    port = 53251

    async def _async(loop: Any) -> None:
        await asyncio.sleep(5)
        async with aiohttp.ClientSession(loop=loop) as client:
            try:
                response = await client.get('http://127.0.0.1:{}/'.format(port))
            except Exception:
                response = False

            assert response is not False

    loop.run_until_complete(_async(loop))
    loop.run_until_complete(future)

    services = func()
    assert services is not None
    assert len(services) == 1
    instance = services.get('test_http')
    assert instance is not None

    assert instance.uuid is not None

    assert instance.function_order == [
        '_start_service',
        '_started_service',
        'index',
        '_stop_service'
    ]
