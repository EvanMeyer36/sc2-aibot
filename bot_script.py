import os
import random
import logging
from typing import List, Dict, Set

# Set the StarCraft II game path
os.environ["SC2PATH"] = "W:/StarCraft II"

# Import necessary modules from the sc2 library
from sc2.bot_ai import BotAI
from sc2.data import Difficulty, Race
from sc2.main import run_game
from sc2.player import Bot, Computer
from sc2 import maps
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.ids.upgrade_id import UpgradeId
from sc2.position import Point2

# Set up logging to write bot output to a file
logging.basicConfig(filename='bot_output.txt', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s', filemode='w')
logger = logging.getLogger()

class ImprovedTerranBot(BotAI):
    def __init__(self):
        super().__init__()
        self.attack_groups: Dict[UnitTypeId, Set[int]] = {}
        self.expand_interval: int = 300
        self.last_expand_time: int = 0
        self.combatUnits = {UnitTypeId.MARINE, UnitTypeId.MARAUDER, UnitTypeId.SIEGETANK, UnitTypeId.MEDIVAC}
        self.scout_sent = False
        self.enemy_air_units_detected = False

    async def on_step(self, iteration: int):
        try:
            # Log detailed information every 100 iterations
            if iteration % 100 == 0:
                logger.info(f"Iteration: {iteration}, Minerals: {self.minerals}, Vespene: {self.vespene}, "
                            f"Supply: {self.supply_used}/{self.supply_cap}, Workers: {self.workers.amount}, "
                            f"Army Supply: {self.supply_army}")

            # Prioritize army building and production
            await self.distribute_workers()
            await self.produce_workers()  # New method to continuously produce workers
            await self.build_supply()
            await self.build_refinery()
            await self.expand()
            await self.build_army_buildings()
            await self.build_army()
            await self.manage_army()
            await self.attack()
            
            # Lower priority tasks
            await self.scout()
            await self.manage_idle_workers() 
            await self.resource_management()
            await self.research_upgrades()
            await self.medivac_harass()
        except Exception as e:
            logger.error(f"Error in on_step: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())




    async def scout(self):
        if not self.scout_sent and self.workers:
            scout = self.workers.random
            await self.do(scout.move(self.enemy_start_locations[0]))
            self.scout_sent = True
            logger.info(f"Scout sent to {self.enemy_start_locations[0]}")

    async def build_workers(self):
        for cc in self.townhalls.ready.idle:
            if self.can_afford(UnitTypeId.SCV) and self.workers.amount < min(self.townhalls.amount * 22, 70):
                await self.do(cc.train(UnitTypeId.SCV))
                logger.debug(f"Training SCV at {cc.position}")

    async def build_supply(self):
        if (
            self.supply_left < 6
            and not self.already_pending(UnitTypeId.SUPPLYDEPOT)
            and self.can_afford(UnitTypeId.SUPPLYDEPOT)
        ):
            workers = self.workers.gathering
            if workers:
                worker = workers.furthest_to(self.start_location)
                location = await self.find_placement(UnitTypeId.SUPPLYDEPOT, near=worker.position, placement_step=3)
                if location:
                    await self.build(UnitTypeId.SUPPLYDEPOT, location)
                    logger.info(f"Building supply depot at {location}")

    async def build_refinery(self):
        for th in self.townhalls.ready:
            vespenes = self.state.vespene_geyser.closer_than(15, th)
            for vespene in vespenes:
                if not self.units(UnitTypeId.REFINERY).closer_than(1, vespene):
                    if self.can_afford(UnitTypeId.REFINERY) and not self.already_pending(UnitTypeId.REFINERY):
                        worker = self.select_build_worker(vespene.position)
                        if worker:
                            await self.do(worker.build(UnitTypeId.REFINERY, vespene))
                            logger.info(f"Building refinery at {vespene.position}")
                            return  # Build one refinery at a time



    async def produce_workers(self):
        for cc in self.townhalls.ready:
            if (self.can_afford(UnitTypeId.SCV) and 
                self.workers.amount < min(self.townhalls.amount * 22, 70) and
                cc.is_idle):  # Check if the command center is idle
                await self.do(cc.train(UnitTypeId.SCV))
                logger.info(f"Training SCV at {cc.position}")

    async def expand(self):
        if (
            self.can_afford(UnitTypeId.COMMANDCENTER)
            and not self.already_pending(UnitTypeId.COMMANDCENTER)
            and self.townhalls.amount < 3
        ):
            await self.expand_now()
            logger.info("Expanding to a new location")

    async def build_army_buildings(self):
        ccs = self.units(UnitTypeId.COMMANDCENTER).ready
        if ccs:
            # Build Barracks
            if self.units(UnitTypeId.BARRACKS).amount < 3 and self.can_afford(UnitTypeId.BARRACKS):
                await self.build(UnitTypeId.BARRACKS, near=ccs.first.position.towards(self.game_info.map_center, 8))
                logger.info("Building Barracks")

            # Build Factory
            if self.units(UnitTypeId.FACTORY).amount < 2 and self.can_afford(UnitTypeId.FACTORY):
                if self.units(UnitTypeId.BARRACKS).ready:
                    await self.build(UnitTypeId.FACTORY, near=self.units(UnitTypeId.BARRACKS).first)
                    logger.info("Building Factory")

            # Build Starport
            if self.units(UnitTypeId.STARPORT).amount < 1 and self.can_afford(UnitTypeId.STARPORT):
                if self.units(UnitTypeId.FACTORY).ready:
                    await self.build(UnitTypeId.STARPORT, near=self.units(UnitTypeId.FACTORY).first)
                    logger.info("Building Starport")

        # Add Tech Labs
        for barracks in self.units(UnitTypeId.BARRACKS).ready:
            if not barracks.has_add_on and self.can_afford(UnitTypeId.BARRACKSTECHLAB):
                await self.do(barracks.build(UnitTypeId.BARRACKSTECHLAB))
                logger.info(f"Adding Tech Lab to Barracks at {barracks.position}")

        # Ensure Factory has a Tech Lab before training Siege Tanks
        for factory in self.units(UnitTypeId.FACTORY).ready:
            if not factory.has_add_on and self.can_afford(UnitTypeId.FACTORYTECHLAB):
                await self.do(factory.build(UnitTypeId.FACTORYTECHLAB))
                logger.info(f"Adding Tech Lab to Factory at {factory.position}")

    async def build_army(self):
        # Train Marines and Marauders from Barracks
        for rax in self.units(UnitTypeId.BARRACKS).ready.idle:
            if rax.has_add_on and self.can_afford(UnitTypeId.MARAUDER):
                await self.do(rax.train(UnitTypeId.MARAUDER))
                logger.info(f"Training Marauder at {rax.position}")
            elif not rax.has_add_on and self.can_afford(UnitTypeId.MARINE):
                await self.do(rax.train(UnitTypeId.MARINE))
                logger.info(f"Training Marine at {rax.position}")

        # Train Siege Tanks from Factories
        for factory in self.units(UnitTypeId.FACTORY).ready.idle:
            if factory.has_add_on and self.can_afford(UnitTypeId.SIEGETANK):
                await self.do(factory.train(UnitTypeId.SIEGETANK))
                logger.info(f"Training Siege Tank at {factory.position}")

        # Train Medivacs from Starports
        for starport in self.units(UnitTypeId.STARPORT).ready.idle:
            if self.can_afford(UnitTypeId.MEDIVAC):
                await self.do(starport.train(UnitTypeId.MEDIVAC))
                logger.info(f"Training Medivac at {starport.position}")


    async def attack(self):
        """ Sends units to attack only if a critical mass is reached """
        if self.supply_army > 60:  # Attack with larger forces
            logger.info(f"Initiating attack with {self.supply_army} supply of army")
            for unit in self.units.of_type(self.combatUnits).idle:
                await self.do(unit.attack(self.enemy_start_locations[0]))
                logger.debug(f"{unit.type_id} attacking enemy base")
        else:
            logger.info(f"Waiting for larger army. Current army supply: {self.supply_army}")

    async def manage_army(self):
        """ Handles army movement, attack, and retreat """
        for unit_type in self.combatUnits:
            for unit in self.units(unit_type):
                if self.known_enemy_units:
                    closest_enemy = self.known_enemy_units.closest_to(unit)

                    # Retreat logic: If army size is too small, retreat
                    if self.supply_army < 30:
                        await self.do(unit.move(self.start_location))
                        logger.debug(f"Retreating {unit.type_id} to start location")
                    else:
                        if unit.weapon_cooldown == 0:
                            await self.do(unit.attack(closest_enemy))
                            logger.debug(f"{unit_type} attacking enemy at {closest_enemy.position}")
                        elif unit.weapon_cooldown > 0:
                            await self.do(unit.move(unit.position.towards(closest_enemy, -5)))
                            logger.debug(f"{unit_type} retreating from enemy at {closest_enemy.position}")
                else:
                    await self.do(unit.attack(self.enemy_start_locations[0]))
                    logger.debug(f"{unit_type} moving to enemy start location")

        # Handle Siege Tanks
        for tank in self.units(UnitTypeId.SIEGETANK):
            if self.known_enemy_units.closer_than(13, tank):
                await self.do(tank(AbilityId.SIEGEMODE_SIEGEMODE))
                logger.debug(f"Siege Tank entering siege mode at {tank.position}")
            else:
                await self.do(tank(AbilityId.UNSIEGE_UNSIEGE))
                logger.debug(f"Siege Tank un-sieging at {tank.position}")
    
    async def medivac_support(self):
        """ Use Medivacs to heal and transport troops """
        for medivac in self.units(UnitTypeId.MEDIVAC).idle:
            injured_units = self.units.filter(lambda u: u.health_percentage < 1 and u.is_biological)
            if injured_units:
                closest_injured = injured_units.closest_to(medivac)
                await self.do(medivac(AbilityId.HEAL_HEAL, closest_injured))
                logger.debug(f"Medivac healing {closest_injured.type_id}")
            else:
                # If no injured units, use Medivacs for troop transportation
                marines = self.units(UnitTypeId.MARINE).idle
                if marines.amount >= 8:
                    pickup_point = medivac.position.towards(self.start_location, 3)
                    for marine in marines.take(8):
                        await self.do(marine.move(pickup_point))
                    for marine in marines.take(8):
                        await self.do(medivac(AbilityId.LOAD_MEDIVAC, marine))
                    await self.do(medivac.move(self.enemy_start_locations[0]))
                    logger.info(f"Launching Medivac support with Marines")

    async def manage_idle_workers(self):
        if self.townhalls.exists:
            for worker in self.workers.idle:
                th = self.townhalls.closest_to(worker)
                mfs = self.mineral_fields.closer_than(10, th)  # Use mineral_fields here
                if mfs:
                    mf = mfs.closest_to(worker)
                    await self.do(worker.gather(mf))
                    logger.debug(f"Assigning idle worker to gather minerals at {mf.position}")
        else:
            for worker in self.workers.idle:
                await self.do(worker.move(self.start_location))
                logger.debug(f"Moving idle worker to start location")



    async def resource_management(self):
        if self.minerals > 500:
            await self.build_additional_barracks()
            await self.expand()

    async def build_additional_barracks(self):
        if self.can_afford(UnitTypeId.BARRACKS) and self.units(UnitTypeId.BARRACKS).amount < 8:
            await self.build(UnitTypeId.BARRACKS, near=self.townhalls.first.position.towards(self.game_info.map_center, 8))
            logger.info("Building additional Barracks due to excess minerals")

    async def medivac_harass(self):
        idle_medivacs = self.units(UnitTypeId.MEDIVAC).idle  
        if idle_medivacs and self.units(UnitTypeId.MARINE).idle.amount > 8:
            medivac = idle_medivacs.random
            marines = self.units(UnitTypeId.MARINE).idle.take(8)
            pickup_point = medivac.position.towards(self.start_location, 3)
            for marine in marines:
                await self.do(marine.move(pickup_point))
            for marine in marines:
                await self.do(medivac(AbilityId.LOAD_MEDIVAC, marine))
            await self.do(medivac.move(self.enemy_start_locations[0]))
            logger.info(f"Launching Medivac harass with {len(marines)} Marines")

    async def research_upgrades(self):
        if self.units(UnitTypeId.ENGINEERINGBAY).ready:
            eb = self.units(UnitTypeId.ENGINEERINGBAY).first  
            if self.can_afford(UpgradeId.TERRANINFANTRYWEAPONSLEVEL1) and not self.already_pending_upgrade(UpgradeId.TERRANINFANTRYWEAPONSLEVEL1):
                await self.do(eb.research(UpgradeId.TERRANINFANTRYWEAPONSLEVEL1))
                logger.info("Researching Infantry Weapons Level 1")
            elif self.can_afford(UpgradeId.TERRANINFANTRYARMORSLEVEL1) and not self.already_pending_upgrade(UpgradeId.TERRANINFANTRYARMORSLEVEL1):
                await self.do(eb.research(UpgradeId.TERRANINFANTRYARMORSLEVEL1))
                logger.info("Researching Infantry Armor Level 1")
        else:
            if self.can_afford(UnitTypeId.ENGINEERINGBAY):
                await self.build(UnitTypeId.ENGINEERINGBAY, near=self.townhalls.first.position.towards(self.game_info.map_center, 5))
                logger.info("Building Engineering Bay")

# Run the game
def main():
    run_game(
        maps.get("(4) Twilight Fortress"),
        [
            Bot(Race.Terran, ImprovedTerranBot()),
            Computer(Race.Zerg, Difficulty.Hard)
        ],
        realtime=False,
        save_replay_as="my_bot_game.SC2Replay"       
    )

if __name__ == "__main__":
    main()