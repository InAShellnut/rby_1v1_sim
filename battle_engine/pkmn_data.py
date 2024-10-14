from battle_engine.pkmn_battle import *
from battle_engine.pkmn_moves import *


class Pokemon:
    def __init__(self, level, moves, nickname=None, starting_dmg=0):
        self.level = level
        if nickname:
            self.nickname = nickname
        else:
            self.nickname = self.NAME
        self.max_hp = 10 + level + (((self.BASE_HP + 15) * 2 + 63) * level) // 100
        self.hp = self.max_hp - starting_dmg
        self.moves = {move.NAME: move() for move in moves}
        self.stats = {
            "attack": self._calc_stat(level, self.BASE_ATTACK),
            "defence": self._calc_stat(level, self.BASE_DEFENCE),
            "speed": self._calc_stat(level, self.BASE_SPEED),
            "special": self._calc_stat(level, self.BASE_SPECIAL),
        }
        # tuple of numerator and denominator
        self.stat_mods = {
            "attack": (2, 2),
            "defence": (2, 2),
            "speed": (2, 2),
            "special": (2, 2),
        }
        self.status = None
        self.status_mod = {}
        self.reflect = False
        self.light_screen = False
        self.ch_attempts = 0
        self.ches = 0
        self.fp_turns = 0
        self.fps = 0
        self.sleep_count = 0
        self.recharge = False
        self.confused = False
        self.confused_count = 0

    def get_move(self, move_name):
        move = self.moves[move_name]
        if move.pp > 0:
            return move
        else:
            return None

    def get_stat(self, stat):
        if stat not in self.stats:
            raise ValueError("bad stat name")
        value = self.stats[stat]
        value = value // self.status_mod.get(stat, 1)
        mod_numerator, mod_denominator = self.stat_mods[stat]
        value = (value * mod_numerator) // mod_denominator
        return value

    def raise_stat(self, stat, levels):
        numerator, denominator = self.stat_mods[stat]
        for _ in range(levels):
            if denominator == 2:
                numerator = min(8, numerator + 1)
            else:
                denominator = denominator - 1
        self.stat_mods[stat] = (numerator, denominator)

    def lower_stat(self, stat, levels):
        numerator, denominator = self.stat_mods[stat]
        for _ in range(levels):
            if numerator == 2:
                denominator = min(8, denominator + 1)
            else:
                numerator = numerator - 1
        self.stat_mods[stat] = (numerator, denominator)

    def critical_hit(self, high_ch=False):
        self.ch_attempts += 1
        target = self.BASE_SPEED // 2
        if high_ch:
            target = target * 8
        target = min(target, 255)
        if rng(target):
            self.ches += 1
            return True
        else:
            return False

    def attack(self, move, opponent):
        # TODO: This system of requesting a move from a pokemon then passing it
        # back to the pokemon is a little weird. try and think of another way
        # to do this
        if self.recharge:
            self.recharge = False
            logging.debug("{} must recharge".format(self.nickname))
            return
        if self.status == "FRZ":
            logging.debug("{} is frozen solid!".format(self.nickname))
            return
        if self.status == "SLP":
            if self.sleep_count == 0:
                self.status = None
                logging.debug("{} woke up!".format(self.nickname))
                return
            else:
                self.sleep_count -= 1
                logging.debug("{} is fast asleep!".format(self.nickname))
                return
        if self.status == "PAR":
            self.fp_turns += 1
            if rng(64):
                self.fps += 1
                logging.debug("{} is fully paralysed!".format(self.nickname))
                return
        if self.confused:
            logging.debug("{} is confused!".format(self.nickname))
            # todo: account for weird interactions with substitute and recharge and stuff
            self.confused_count -= 1
            # logging.debug(f"{self.confused_count}")
            if self.confused_count <= 0:
                logging.debug("{} snapped out of its confusion!".format(self.nickname))
                self.confused = False
                self.confused_count = 0
            else:
                if rng(129):
                    confusion_dmg = ConfusionDamage()
                    confusion_dmg.use(self, opponent)
                    del confusion_dmg
                    return

        move.use(self, opponent)
        if self.status == "BRN" or self.status == "PSN":
            self.hp -= self.max_hp // 16

    def _calc_stat(self, level, base_stat):
        return 5 + (((base_stat + 15) * 2 + 63) * level) // 100


class Hitmonchan(Pokemon):
    BASE_HP = 50
    BASE_ATTACK = 105
    BASE_DEFENCE = 79
    BASE_SPECIAL = 35
    BASE_SPEED = 76
    TYPES = ("Fighting",)
    NAME = "Hitmonchan"


class NidoranF(Pokemon):
    BASE_HP = 55
    BASE_ATTACK = 47
    BASE_DEFENCE = 52
    BASE_SPECIAL = 40
    BASE_SPEED = 41
    TYPES = ("Poison",)
    NAME = "NidoranF"


class Lapras(Pokemon):
    BASE_HP = 130
    BASE_ATTACK = 85
    BASE_DEFENCE = 80
    BASE_SPECIAL = 95
    BASE_SPEED = 60
    TYPES = ("Water", "Ice")
    NAME = "Lapras"


class Jynx(Pokemon):
    BASE_HP = 65
    BASE_ATTACK = 50
    BASE_DEFENCE = 35
    BASE_SPECIAL = 95
    BASE_SPEED = 95
    TYPES = ("Ice", "Psychic")
    NAME = "Jynx"


class Articuno(Pokemon):
    BASE_HP = 90
    BASE_ATTACK = 85
    BASE_DEFENCE = 100
    BASE_SPECIAL = 125
    BASE_SPEED = 85
    TYPES = ("Ice", "Flying")
    NAME = "Articuno"


class Tentacruel(Pokemon):
    BASE_HP = 80
    BASE_ATTACK = 70
    BASE_DEFENCE = 65
    BASE_SPECIAL = 120
    BASE_SPEED = 100
    TYPES = ("Water", "Poison")
    NAME = "Tentacruel"


class Gyarados(Pokemon):
    BASE_HP = 95
    BASE_ATTACK = 125
    BASE_DEFENCE = 79
    BASE_SPECIAL = 100
    BASE_SPEED = 81
    TYPES = ("Water", "Flying")
    NAME = "Gyarados"


class Vaporeon(Pokemon):
    BASE_HP = 130
    BASE_ATTACK = 65
    BASE_DEFENCE = 60
    BASE_SPECIAL = 110
    BASE_SPEED = 65
    TYPES = ("Water",)
    NAME = "Vaporeon"


class Dewgong(Pokemon):
    BASE_HP = 90
    BASE_ATTACK = 70
    BASE_DEFENCE = 80
    BASE_SPECIAL = 95
    BASE_SPEED = 70
    TYPES = ("Water", "Ice")
    NAME = "Dewgong"


class Moltres(Pokemon):
    BASE_HP = 90
    BASE_ATTACK = 100
    BASE_DEFENCE = 90
    BASE_SPECIAL = 125
    BASE_SPEED = 90
    TYPES = ("Fire", "Flying")
    NAME = "Moltres"


class Ninetales(Pokemon):
    BASE_HP = 73
    BASE_ATTACK = 76
    BASE_DEFENCE = 75
    BASE_SPECIAL = 100
    BASE_SPEED = 100
    TYPES = ("Fire",)
    NAME = "Ninetales"


class Starmie(Pokemon):
    BASE_HP = 60
    BASE_ATTACK = 75
    BASE_DEFENCE = 85
    BASE_SPECIAL = 100
    BASE_SPEED = 115
    TYPES = ("Water", "Psychic")
    NAME = "Starmie"


class Alakazam(Pokemon):
    BASE_HP = 55
    BASE_ATTACK = 50
    BASE_DEFENCE = 45
    BASE_SPECIAL = 135
    BASE_SPEED = 120
    TYPES = ("Psychic",)
    NAME = "Alakazam"


class Electabuzz(Pokemon):
    BASE_HP = 65
    BASE_ATTACK = 83
    BASE_DEFENCE = 57
    BASE_SPECIAL = 85
    BASE_SPEED = 105
    TYPES = ("Electric",)
    NAME = "Electabuzz"


class Tauros(Pokemon):
    BASE_HP = 75
    BASE_ATTACK = 100
    BASE_DEFENCE = 95
    BASE_SPECIAL = 70
    BASE_SPEED = 110
    TYPES = ("Normal",)
    NAME = "Tauros"


class Kangaskhan(Pokemon):
    BASE_HP = 105
    BASE_ATTACK = 95
    BASE_DEFENCE = 80
    BASE_SPECIAL = 40
    BASE_SPEED = 90
    TYPES = ("Normal",)
    NAME = "Kangaskhan"


class Dodrio(Pokemon):
    BASE_HP = 60
    BASE_ATTACK = 110
    BASE_DEFENCE = 70
    BASE_SPECIAL = 60
    BASE_SPEED = 100
    TYPES = ("Normal", "Flying")
    NAME = "Dodrio"


class Zapdos(Pokemon):
    BASE_HP = 90
    BASE_ATTACK = 90
    BASE_DEFENCE = 85
    BASE_SPECIAL = 125
    BASE_SPEED = 100
    TYPES = ("Electric", "Flying")
    NAME = "Zapdos"


class Clefable(Pokemon):
    BASE_HP = 95
    BASE_ATTACK = 70
    BASE_DEFENCE = 73
    BASE_SPECIAL = 85
    BASE_SPEED = 60
    TYPES = ("Normal",)
    NAME = "Clefable"


class Snorlax(Pokemon):
    BASE_HP = 160
    BASE_ATTACK = 110
    BASE_DEFENCE = 65
    BASE_SPECIAL = 65
    BASE_SPEED = 35
    TYPES = ("Normal",)
    NAME = "Snorlax"


class Chansey(Pokemon):
    BASE_HP = 250
    BASE_ATTACK = 5
    BASE_DEFENCE = 5
    BASE_SPECIAL = 105
    BASE_SPEED = 50
    TYPES = ("Normal",)
    NAME = "Chansey"


class Machamp(Pokemon):
    BASE_HP = 90
    BASE_ATTACK = 130
    BASE_DEFENCE = 80
    BASE_SPECIAL = 65
    BASE_SPEED = 55
    TYPES = ("Fighting",)
    NAME = "Machamp"


class Jolteon(Pokemon):
    BASE_HP = 65
    BASE_ATTACK = 65
    BASE_DEFENCE = 60
    BASE_SPECIAL = 110
    BASE_SPEED = 130
    TYPES = ("Electric",)
    NAME = "Jolteon"
