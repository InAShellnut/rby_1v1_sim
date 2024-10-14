from battle_engine.pkmn_battle import *

# TODO: CHANGE THIS TO NOT RELY ON STRINGS!!


class Move:
    # some sensible defaults
    BASE_POWER = 0
    ALWAYS_EFFECT = False
    EFFECT_CHANCE = 0
    ACCURACY = 255
    TYPE = "Normal"
    HIGH_CH = False
    NAME = "Move"
    MAX_PP = 8
    SPECIAL = False
    EXPLOSION = False
    RECOIL = False
    RECOIL2 = False
    IS_CONFUSION_HIT = False

    def __init__(self):
        self.pp = self.MAX_PP

    def use(self, user, opponent):
        if self.pp <= 0:
            raise PPError()
        self.pp -= 1
        if not self.IS_CONFUSION_HIT:
            logging.debug("{} used {}".format(user.nickname, self.NAME))
            self.main_effect(user, opponent)
            if rng(self.ACCURACY):
                if self.BASE_POWER:
                    self.do_damage(user, opponent)
                if self.ALWAYS_EFFECT or rng(self.EFFECT_CHANCE):
                    self.side_effect(user, opponent)
            else:
                logging.debug("But it missed!")
        else:
            logging.debug("{} hit itself in it's confusion.".format(user.nickname))
            self.do_damage(user, opponent)

    def calc_damage(self, user, opponent, crit=False, rand_val=None):
        basepower = self.BASE_POWER
        if self.SPECIAL:
            attack_stat = "special"
            defence_stat = "special"
        else:
            attack_stat = "attack"
            defence_stat = "defence"
        if crit:
            attack = user.stats[attack_stat]
            defence = opponent.stats[defence_stat]
        else:
            attack = user.get_stat(attack_stat)
            defence = opponent.get_stat(defence_stat)
        if self.SPECIAL:
            if opponent.light_screen:
                defence = (defence * 2) % 1024
        elif opponent.reflect:
            defence = (defence * 2) % 1024
        if self.EXPLOSION:
            attack = attack // 2
            defence = defence // 4
        if crit:
            level = user.level * 2
        else:
            level = user.level
        if self.TYPE in user.TYPES:
            stab = 3
        else:
            stab = 2
        if rand_val is None:
            rand_val = random.randint(217, 255)
        damage = ((level * 2) // 5) + 2
        damage = (damage * attack * basepower) // defence
        damage = (damage // 50) + 2
        damage = (damage * stab) // 2
        damage = (damage * effectiveness(self, opponent)) // 4
        damage = (damage * rand_val) // 255
        return max(damage, 1)

    def do_damage(self, user, opponent):
        if self.BASE_POWER == 0:
            return
        crit = user.critical_hit(self.HIGH_CH)
        if crit:
            logging.debug("It's a critical hit!")
        damage = self.calc_damage(user, opponent, crit)
        opponent.hp -= damage
        if self.RECOIL:
            user.hp -= damage // 4
        if self.RECOIL2:
            user.hp -= damage // 3
        logging.debug("{} damage".format(damage))

    def side_effect(self, user, opponent):
        """Effects that may occur after a successful accuracy check"""
        raise NotImplementedError

    def main_effect(self, user, opponent):
        """Effects that always occur without requiring an accuracy check"""
        return ""


class ParalysingMove(Move):
    def side_effect(self, user, opponent):
        if self.TYPE not in opponent.TYPES and opponent.status is None:
            opponent.status = "PAR"
            opponent.status_mod = {"speed": 4}
            logging.debug("{} is paralysed! It may be unable to move!".format(opponent.nickname))


class FreezingMove(Move):
    def side_effect(self, user, opponent):
        if self.TYPE not in opponent.TYPES and opponent.status is None:
            opponent.status = "FRZ"
            logging.debug("{} is Frozen Solid!".format(opponent.nickname))


class BurnMove(Move):
    def side_effect(self, user, opponent):
        if self.TYPE not in opponent.TYPES and opponent.status is None:
            opponent.status = "BRN"
            opponent.status_mod = {"attack": 2}
            logging.debug("{} is Burnt!".format(opponent.nickname))


class SelfDestruct(Move):
    BASE_POWER = 130
    TYPE = "Normal"
    EXPLOSION = "True"
    NAME = "Self-Destruct"

    def main_effect(self, user, opponent):
        user.hp = 0


class BodySlam(ParalysingMove):
    BASE_POWER = 85
    TYPE = "Normal"
    NAME = "Body Slam"
    EFFECT_CHANCE = 76
    MAX_PP = 24


class ConfusionDamage(Move):
    BASE_POWER = 40
    TYPE = "Typeless"
    NAME = "Confusion Damage"
    MAX_PP = 1024
    ACCURACY = 1024
    IS_CONFUSION_HIT = True

    def do_damage(self, user, opponent):
        basepower = self.BASE_POWER
        attack_stat = "attack"
        defence_stat = "defence"
        attack = user.get_stat(attack_stat)
        defence = user.get_stat(defence_stat)
        damage = ((user.level * 2) // 5) + 2
        damage = (damage * attack * basepower) // defence
        damage = damage // 50 + 2
        user.hp -= damage
        logging.debug("{} damage!".format(damage))


class BodySlamTwo(Move):
    BASE_POWER = 85
    TYPE = "Normal"
    NAME = "Body Slam Two"
    MAX_PP = 24


class MegaKick(ParalysingMove):
    BASE_POWER = 120
    TYPE = "Normal"
    NAME = "Mega Kick"
    MAX_PP = 8
    ACCURACY = 179


class DrillPeck(Move):
    BASE_POWER = 80
    TYPE = "Flying"
    NAME = "Drill Peck"
    MAX_PP = 32


class Blizzard(FreezingMove):
    BASE_POWER = 120
    TYPE = "Ice"
    NAME = "Blizzard"
    EFFECT_CHANCE = 25
    ACCURACY = 231
    MAX_PP = 8
    SPECIAL = True


class IceBeam(FreezingMove):
    BASE_POWER = 95
    TYPE = "Ice"
    NAME = "Blizzard"
    EFFECT_CHANCE = 25
    ACCURACY = 255
    MAX_PP = 16
    SPECIAL = True


class FireBlast(BurnMove):
    BASE_POWER = 120
    TYPE = "Fire"
    NAME = "Fire Blast"
    EFFECT_CHANCE = 76
    ACCURACY = 218
    MAX_PP = 8
    SPECIAL = True


class Psychic(Move):
    BASE_POWER = 90
    TYPE = "Psychic"
    NAME = "Psychic"
    EFFECT_CHANCE = 76
    ACCURACY = 255
    MAX_PP = 16
    SPECIAL = True

    def side_effect(self, user, opponent):
        logging.debug("{}'s special fell!".format(opponent.nickname))
        opponent.lower_stat("special", 1)
        if opponent.status == "PAR":
            opponent.status_mod["speed"] *= 4
        elif opponent.status == "BRN":
            opponent.status_mod["attack"] *= 2


class HyperBeam(Move):
    BASE_POWER = 150
    TYPE = "Normal"
    NAME = "Hyper Beam"
    ALWAYS_EFFECT = True
    MAX_PP = 8
    ACCURACY = 231

    def side_effect(self, user, opponent):
        user.recharge = True


class Earthquake(Move):
    BASE_POWER = 100
    TYPE = "Ground"
    NAME = "Earthquake"
    SPECIAL = False
    MAX_PP = 16


class Surf(Move):
    BASE_POWER = 95
    TYPE = "Water"
    NAME = "Surf"
    SPECIAL = True
    MAX_PP = 24


class HydroPump(Move):
    BASE_POWER = 120
    TYPE = "Water"
    NAME = "Surf"
    SPECIAL = True
    MAX_PP = 24
    ACCURACY = 218


class ThunderWave(Move):
    ALWAYS_EFFECT = True
    TYPE = "Electric"
    NAME = "Thunder Wave"
    MAX_PP = 32

    def side_effect(self, user, opponent):
        if opponent.status is None:
            opponent.status = "PAR"
            opponent.status_mod = {"speed": 4}
            logging.debug("{} is paralysed! It may be unable to move!".format(opponent.nickname))
        else:
            logging.debug("But it Failed!")


class Thunderbolt(ParalysingMove):
    BASE_POWER = 95
    TYPE = "Electric"
    NAME = "Thunderbolt"
    EFFECT_CHANCE = 26  # not sure if effect chances should be out of 255 or not? If so 25 or 26??
    SPECIAL = True
    MAX_PP = 24


class Thunder(ParalysingMove):
    BASE_POWER = 120
    TYPE = "Electric"
    NAME = "Thunder"
    EFFECT_CHANCE = 26  # not sure if effect chances should be out of 255 or not? If so 25 or 26??
    SPECIAL = True
    MAX_PP = 24
    ACCURACY = 179


class SeismicToss(Move):
    TYPE = "Fighting"
    NAME = "Seismic Toss"
    BASE_POWER = 1
    MAX_PP = 32

    def do_damage(self, user, opponent):
        opponent.hp -= user.level
        logging.debug("{} damage!".format(user.level))


class Amnesia(Move):
    NAME = "Amnesia"
    MAX_PP = 32

    def main_effect(self, user, opponent):
        logging.debug("{}'s special greatly rose!".format(user.nickname))
        user.raise_stat("special", 2)
        if opponent.status == "PAR":
            opponent.status_mod["speed"] *= 4
        elif opponent.status == "BRN":
            opponent.status_mod["attack"] *= 2


class Agility(Move):
    NAME = "Agility"
    MAX_PP = 48

    def main_effect(self, user, opponent):
        logging.debug("{}'s speed greatly rose!".format(user.nickname))
        user.raise_stat("speed", 2)
        if opponent.status == "PAR":
            opponent.status_mod["speed"] *= 4
        elif opponent.status == "BRN":
            opponent.status_mod["attack"] *= 2


class SwordsDance(Move):
    NAME = "SwordsDance"
    MAX_PP = 48

    def main_effect(self, user, opponent):
        logging.debug("{}'s attacl greatly rose!".format(user.nickname))
        user.raise_stat("attack", 2)
        if opponent.status == "PAR":
            opponent.status_mod["speed"] *= 4
        elif opponent.status == "BRN":
            opponent.status_mod["attack"] *= 2


class Recover(Move):
    NAME = "Recover"
    MAX_PP = 32

    def main_effect(self, user, opponent):
        if user.max_hp - user.hp % 256 != 0:
            user.hp = min(user.max_hp, user.hp + user.max_hp // 2)
        else:
            logging.debug("But it Failed!")


class Rest(Move):
    NAME = "Rest"
    MAX_PP = 16

    def main_effect(self, user, opponent):
        if user.max_hp - user.hp % 256 != 0:
            user.hp = user.max_hp
            user.status = "SLP"
            user.sleep_count = 1
        else:
            logging.debug("But it Failed!")


class SoftBoiled(Recover):
    NAME = "Soft-Boiled"
    MAX_PP = 16


class Reflect(Move):
    NAME = "Reflect"
    MAX_PP = 32

    def main_effect(self, user, opponent):
        if user.reflect:
            logging.debug("But it Failed!")
        else:
            user.reflect = True
            logging.debug("{} gained armour!".format(user.nickname))


class Struggle(Move):
    NAME = "Struggle"
    BASE_POWER = 40
    RECOIL = True
    TYPE = "Normal"


class Skip(Move):
    NAME = "Skip"
    ALWAYS_EFFECT = True

    def side_effect(self, user, opponent):
        user.recharge = True


class DoubleEdge(Move):
    NAME = "DoubleEdge"
    BASE_POWER = 100
    RECOIL2 = True
    TYPE = "Normal"


class Submission(Move):
    NAME = "Submission"
    BASE_POWER = 80
    RECOIL = True
    TYPE = "Fighting"


class ConfuseRay(Move):
    ALWAYS_EFFECT = True
    TYPE = "Ghost"
    NAME = "Confuse Ray"
    MAX_PP = 16

    def side_effect(self, user, opponent):
        if opponent.confused is False:
            opponent.confused = True
            opponent.confused_count = 2 + (random.randint(0, 255) & 3)
            logging.debug("Enemy {} became confused!".format(opponent.nickname))
        else:
            logging.debug("But it Failed!")


class Sing(Move):
    ALWAYS_EFFECT = True
    TYPE = "Normal"
    NAME = "Sing"
    MAX_PP = 24
    ACCURACY = 140

    def side_effect(self, user, opponent):
        if opponent.status is None:
            opponent.status = "SLP"
            while opponent.sleep_count == 0:
                rand_num = random.randint(0, 255) & 7
                logging.debug(f"{rand_num}")
                opponent.sleep_count = rand_num
            logging.debug(f"{opponent.sleep_count}")
            logging.debug("Enemy {} fell asleep!".format(opponent.nickname))
        else:
            logging.debug("But it Failed!")


# This move does nothing it's used to do stuff like handle switching onto the field or something
class SkipTurn(Move):
    NAME = "SkipTurn"
    MAX_PP = 256

    def main_effect(self, user, opponent):
        pass
