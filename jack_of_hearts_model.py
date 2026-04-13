import random
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional


# ──────────────────────────────────────────────
# Enums & Types
# ──────────────────────────────────────────────

class Suit(Enum):
    HEARTS   = "❤️ Cuori"
    DIAMONDS = "♦️ Quadri"
    CLUBS    = "♣️ Fiori"
    SPADES   = "♠️ Picche"


class GuessResult(Enum):
    CORRECT   = "salvato"
    WRONG     = "eliminato"
    PENDING   = "in attesa"


class RoundStatus(Enum):
    IN_PROGRESS = "in corso"
    COMPLETED   = "completato"


class GameOutcome(Enum):
    PLAYERS_WIN   = "I giocatori vincono"
    JACK_WINS     = "Il Jack di Cuori vince"
    IN_PROGRESS   = "in corso"


# ──────────────────────────────────────────────
# Player
# ──────────────────────────────────────────────

@dataclass
class Player:
    """
    Rappresenta un giocatore nella partita.

    Responsabilità:
    - Conosce il proprio seme segreto (ma non lo "vede")
    - Può vedere i semi degli altri giocatori
    - Sottomette un guess per ogni round
    - Tiene traccia della propria storia di round
    """
    name: str
    is_jack: bool = False

    # Stato interno (non visibile al giocatore stesso)
    _suit: Optional[Suit] = field(default=None, repr=False)

    # Stato corrente nel round
    _current_guess: Optional[Suit] = field(default=None, repr=False)
    _guess_result: GuessResult = field(default=GuessResult.PENDING, repr=False)

    # Storico (lista di bool: True = sopravvissuto quel round)
    round_history: list[bool] = field(default_factory=list, repr=False)

    @property
    def suit(self) -> Suit:
        """Il seme reale del giocatore (accessibile solo dal Game/Tournament)."""
        return self._suit

    def assign_suit(self, suit: Suit) -> None:
        """Chiamato dal Game per assegnare il seme segreto."""
        self._suit = suit
        self._current_guess = None
        self._guess_result = GuessResult.PENDING

    def submit_guess(self, guess: Suit) -> None:
        """Il giocatore dichiara il proprio seme per questo round."""
        if self._current_guess is not None:
            raise ValueError(f"{self.name} ha già sottomesso un guess questo round.")
        self._current_guess = guess

    def get_visible_suits(self, all_players: list["Player"]) -> dict[str, Suit]:
        """
        Restituisce i semi di tutti gli altri giocatori (visibili a questo giocatore).
        Il proprio seme NON è incluso.
        """
        return {
            p.name: p.suit
            for p in all_players
            if p.name != self.name
        }

    def reveal_guess_result(self, result: GuessResult) -> None:
        """Chiamato dal Game dopo la valutazione del round."""
        self._guess_result = result
        self.round_history.append(result == GuessResult.CORRECT)

    def reset_for_new_round(self) -> None:
        """Resetta lo stato per il round successivo (il seme verrà riassegnato)."""
        self._current_guess = None
        self._guess_result = GuessResult.PENDING

    @property
    def current_guess(self) -> Optional[Suit]:
        return self._current_guess

    @property
    def guess_result(self) -> GuessResult:
        return self._guess_result

    @property
    def is_alive(self) -> bool:
        """True se il giocatore non è stato eliminato nell'ultimo round giocato."""
        if not self.round_history:
            return True
        return self.round_history[-1]

    def __repr__(self):
        jack_str = " [JACK]" if self.is_jack else ""
        return f"Player('{self.name}'{jack_str})"


# ──────────────────────────────────────────────
# Game — gestisce UN singolo round
# ──────────────────────────────────────────────

@dataclass
class Game:
    """
    Gestisce la logica di un singolo round:
    - Distribuisce i semi ai giocatori
    - Raccoglie i guess
    - Valuta i risultati

    NON conosce le regole di eliminazione del Jack o la
    progressione tra round: quello è compito del Tournament.
    """
    round_number: int
    players: list[Player]
    status: RoundStatus = RoundStatus.IN_PROGRESS

    def __post_init__(self):
        self._distribute_suits()

    def _distribute_suits(self) -> None:
        """Assegna un seme casuale a ogni giocatore."""
        suits = list(Suit)
        for player in self.players:
            assigned = random.choice(suits)
            player.assign_suit(assigned)

    def submit_guess(self, player_name: str, guess: Suit) -> None:
        """Registra il guess di un giocatore."""
        player = self._find_player(player_name)
        player.submit_guess(guess)

    def all_guesses_submitted(self) -> bool:
        """True quando tutti i giocatori hanno sottomesso un guess."""
        return all(p.current_guess is not None for p in self.players)

    def evaluate_round(self) -> dict[str, GuessResult]:
        """
        Valuta i guess di tutti i giocatori e restituisce i risultati.
        Può essere chiamato solo quando tutti hanno sottomesso un guess.
        """
        if not self.all_guesses_submitted():
            raise RuntimeError("Non tutti i giocatori hanno sottomesso un guess.")
        if self.status == RoundStatus.COMPLETED:
            raise RuntimeError("Questo round è già stato valutato.")

        results: dict[str, GuessResult] = {}
        for player in self.players:
            if player.current_guess == player.suit:
                result = GuessResult.CORRECT
            else:
                result = GuessResult.WRONG
            player.reveal_guess_result(result)
            results[player.name] = result

        self.status = RoundStatus.COMPLETED
        return results

    def get_visible_suits_for(self, player_name: str) -> dict[str, Suit]:
        """Restituisce i semi visibili per un dato giocatore."""
        player = self._find_player(player_name)
        return player.get_visible_suits(self.players)

    def get_results(self) -> dict[str, GuessResult]:
        """Restituisce i risultati correnti (anche prima della valutazione finale)."""
        return {p.name: p.guess_result for p in self.players}

    def _find_player(self, name: str) -> Player:
        for p in self.players:
            if p.name == name:
                return p
        raise ValueError(f"Giocatore '{name}' non trovato in questo round.")


# ──────────────────────────────────────────────
# Tournament — gestisce le regole e i round multipli
# ──────────────────────────────────────────────

@dataclass
class Tournament:
    """
    Gestisce la logica ad alto livello della partita:
    - Crea e avanza i round
    - Applica le regole di eliminazione
    - Gestisce la logica speciale del Jack di Cuori
    - Determina il vincitore

    Il Tournament crea un nuovo Game per ogni round con i
    soli giocatori sopravvissuti.
    """
    all_players: list[Player]
    max_rounds: int = 5

    current_round: int = field(default=0, repr=False)
    current_game: Optional[Game] = field(default=None, repr=False)
    game_history: list[Game] = field(default_factory=list, repr=False)
    eliminated: list[Player] = field(default_factory=list, repr=False)
    outcome: GameOutcome = GameOutcome.IN_PROGRESS

    def __post_init__(self):
        self._assign_jack()

    def _assign_jack(self) -> None:
        """Sceglie casualmente un giocatore come Jack di Cuori."""
        jack = random.choice(self.all_players)
        jack.is_jack = True

    @property
    def survivors(self) -> list[Player]:
        """Giocatori ancora in gioco."""
        return [p for p in self.all_players if p not in self.eliminated]

    @property
    def jack(self) -> Optional[Player]:
        """Il Jack di Cuori (se ancora vivo)."""
        for p in self.survivors:
            if p.is_jack:
                return p
        return None  # Il Jack è stato eliminato

    def start_next_round(self) -> Game:
        """
        Avanza al round successivo e crea un nuovo Game
        con i giocatori sopravvissuti.
        """
        if self.outcome != GameOutcome.IN_PROGRESS:
            raise RuntimeError("La partita è già terminata.")
        if self.current_round >= self.max_rounds:
            raise RuntimeError("Numero massimo di round raggiunto.")

        self.current_round += 1
        for p in self.survivors:
            p.reset_for_new_round()

        self.current_game = Game(
            round_number=self.current_round,
            players=list(self.survivors),
        )
        self.game_history.append(self.current_game)
        return self.current_game

    def apply_elimination_rules(self) -> list[Player]:
        """
        Dopo che il Game ha valutato il round, applica le regole di eliminazione:

        Regole standard:
        - Chi ha indovinato è salvo.
        - Chi ha sbagliato è eliminato.

        Regola Jack di Cuori:
        - Il Jack conosce il proprio seme: indovina SEMPRE (a meno che i giocatori
          non lo abbiano già identificato e votato per eliminarlo).
        - Se TUTTI i non-Jack sbagliano in un round, il Jack ottiene un bonus
          (può eliminare un giocatore extra a scelta).

        Ritorna la lista dei giocatori eliminati questo round.
        """
        if self.current_game is None:
            raise RuntimeError("Nessun game in corso.")
        if self.current_game.status != RoundStatus.COMPLETED:
            raise RuntimeError("Il round non è ancora stato valutato.")

        newly_eliminated: list[Player] = []
        results = self.current_game.get_results()

        for player in list(self.survivors):
            if results.get(player.name) == GuessResult.WRONG:
                self.eliminated.append(player)
                newly_eliminated.append(player)

        self._check_game_outcome()
        return newly_eliminated

    def vote_to_eliminate_jack_suspect(self, suspect_name: str) -> Optional[Player]:
        """
        I giocatori possono votare per eliminare chi credono sia il Jack.
        Se il sospettato è davvero il Jack, viene eliminato.
        Se sbaglia, il votante viene penalizzato (eliminato).

        Restituisce il giocatore eliminato, oppure None.
        """
        suspect = next((p for p in self.survivors if p.name == suspect_name), None)
        if suspect is None:
            raise ValueError(f"'{suspect_name}' non è tra i sopravvissuti.")

        if suspect.is_jack:
            self.eliminated.append(suspect)
            self._check_game_outcome()
            return suspect
        else:
            # Accusare l'innocente ha conseguenze (regola opzionale)
            return None

    def _check_game_outcome(self) -> None:
        """Aggiorna l'outcome della partita dopo ogni eliminazione."""
        if self.jack is None:
            # Il Jack è stato eliminato → i giocatori vincono
            self.outcome = GameOutcome.PLAYERS_WIN
            return

        non_jack_survivors = [p for p in self.survivors if not p.is_jack]
        if len(non_jack_survivors) == 0:
            # Solo il Jack è rimasto → il Jack vince
            self.outcome = GameOutcome.JACK_WINS
            return

        if self.current_round >= self.max_rounds:
            # Round finiti: se il Jack è ancora vivo, vince lui
            self.outcome = GameOutcome.JACK_WINS

    def get_status(self) -> dict:
        """Snapshot dello stato corrente della partita."""
        return {
            "round": self.current_round,
            "max_rounds": self.max_rounds,
            "survivors": [p.name for p in self.survivors],
            "eliminated": [p.name for p in self.eliminated],
            "jack_alive": self.jack is not None,
            "jack_name": self.jack.name if self.jack else "eliminato",
            "outcome": self.outcome.value,
        }


# ──────────────────────────────────────────────
# Demo / smoke test
# ──────────────────────────────────────────────

if __name__ == "__main__":
    players = [
        Player("Alice"),
        Player("Bruno"),
        Player("Carlo"),
        Player("Diana"),
    ]

    tournament = Tournament(players, max_rounds=3)
    print(f"\n=== INIZIO TORNEO ===")
    print(f"Jack di Cuori: {tournament.jack.name}")

    for _ in range(tournament.max_rounds):
        if tournament.outcome != GameOutcome.IN_PROGRESS:
            break

        game = tournament.start_next_round()
        print(f"\n--- Round {game.round_number} ---")

        # Ogni giocatore fa un guess casuale (logica di esempio)
        for player in game.players:
            visible = game.get_visible_suits_for(player.name)
            #print(f"  {player.name} vede: {', '.join(f'{n}: {s.value}' for n, s in visible.items())}")
            guess = random.choice(list(Suit))
            # Il Jack conosce il suo seme
            if player.is_jack:
                guess = player.suit
            game.submit_guess(player.name, guess)
            print(f"  {player.name} guessa: {guess.value}  (reale: {player.suit.value})")

        results = game.evaluate_round()
        newly_elim = tournament.apply_elimination_rules()

        for name, res in results.items():
            print(f"  → {name}: {res.value}")
        if newly_elim:
            print(f"  Eliminati: {[p.name for p in newly_elim]}")

    print(f"\n=== FINE ===")
    status = tournament.get_status()
    print(f"Risultato: {status['outcome']}")
    print(f"Sopravvissuti: {status['survivors']}")
    print(f"Eliminati:    {status['eliminated']}")
