"""In-memory storage for queries, proposals and events.

Temporary: everything is lost when the API restarts. Postgres replaces this
(docs/ARQUITETURA.md, "Modelo de dados"). Good enough for one API process
in the demo; several processes would not share proposals or events.
"""

import asyncio
from collections import deque
from collections.abc import AsyncIterator

from app.schemas import ConsultaResultado, Evento, Proposta

# Limits keep a public demo (no login) from filling the memory of the API.
LIMITE_HISTORICO = 1000  # events kept for reconnecting listeners
LIMITE_GUARDADOS = 1000  # queries and proposals; the oldest ones are dropped
LIMITE_OUVINTES = 50  # open /v1/eventos connections
LIMITE_FILA = 100  # undelivered events per listener; a slow listener loses the oldest ones


class CentralDeEventos:
    """Keeps recent events and delivers new ones to every open listener."""

    def __init__(self) -> None:
        self._historico: deque[Evento] = deque(maxlen=LIMITE_HISTORICO)
        self._ouvintes: set[asyncio.Queue[Evento]] = set()

    def lotado(self) -> bool:
        return len(self._ouvintes) >= LIMITE_OUVINTES

    def total_ouvintes(self) -> int:
        return len(self._ouvintes)

    def historico(self) -> list[Evento]:
        return list(self._historico)

    def publicar(self, evento: Evento) -> None:
        self._historico.append(evento)
        for fila in self._ouvintes:
            if fila.full():
                fila.get_nowait()
            fila.put_nowait(evento)

    async def assinar(self, depois_de: str | None) -> AsyncIterator[Evento]:
        """Yield missed events (after the id the browser sent back), then new ones as they happen.

        An unknown id (for example, after an API restart) replays the whole history.
        """
        fila: asyncio.Queue[Evento] = asyncio.Queue(maxsize=LIMITE_FILA)
        self._ouvintes.add(fila)  # keep these two steps with no await between them
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


class Guardados[T](dict[str, T]):
    """A dict that keeps at most LIMITE_GUARDADOS items, dropping the oldest."""

    def __setitem__(self, chave: str, valor: T) -> None:
        super().__setitem__(chave, valor)
        while len(self) > LIMITE_GUARDADOS:
            del self[next(iter(self))]


class Memoria:
    def __init__(self) -> None:
        self.limpar()

    def limpar(self) -> None:
        self.consultas: Guardados[ConsultaResultado] = Guardados()
        self.propostas: Guardados[Proposta] = Guardados()
        self.eventos = CentralDeEventos()


memoria = Memoria()
