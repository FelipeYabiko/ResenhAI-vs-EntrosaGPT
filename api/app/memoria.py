"""In-memory storage for queries, proposals and events.

Temporary: everything is lost when the API restarts. Postgres replaces this
(docs/ARQUITETURA.md, "Modelo de dados"). Good enough for one API process
in the demo; several processes would not share proposals or events.
"""

import asyncio
from collections import deque
from collections.abc import AsyncIterator

from app.schemas import ConsultaResultado, Evento, Proposta

LIMITE_HISTORICO = 1000


class CentralDeEventos:
    """Keeps recent events and delivers new ones to every open listener."""

    def __init__(self) -> None:
        self._historico: deque[Evento] = deque(maxlen=LIMITE_HISTORICO)
        self._ouvintes: set[asyncio.Queue[Evento]] = set()

    def historico(self) -> list[Evento]:
        return list(self._historico)

    def publicar(self, evento: Evento) -> None:
        self._historico.append(evento)
        for fila in self._ouvintes:
            fila.put_nowait(evento)

    async def assinar(self, depois_de: str | None) -> AsyncIterator[Evento]:
        """Yield missed events (after the id the browser sent back), then new ones as they happen.

        An unknown id (for example, after an API restart) replays the whole history.
        """
        fila: asyncio.Queue[Evento] = asyncio.Queue()
        self._ouvintes.add(fila)  # register before reading history, so nothing slips between the two
        try:
            perdidos = self.historico()
            ids = [e.id for e in perdidos]
            if depois_de in ids:
                perdidos = perdidos[ids.index(depois_de) + 1 :]
            elif depois_de is None:
                perdidos = []
            for evento in perdidos:
                yield evento
            while True:
                yield await fila.get()
        finally:
            self._ouvintes.discard(fila)


class Memoria:
    def __init__(self) -> None:
        self.limpar()

    def limpar(self) -> None:
        self.consultas: dict[str, ConsultaResultado] = {}
        self.propostas: dict[str, Proposta] = {}
        self.eventos = CentralDeEventos()


memoria = Memoria()
