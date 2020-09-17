from typing import List
import minerl.herobraine
import minerl.herobraine.hero.handlers as handlers
from minerl.herobraine.env_specs.simple_env_spec import SimpleEnvSpec


class ChestClock(SimpleEnvSpec):

    def determine_success_from_rewards(self, rewards: list) -> bool:
        return 10 in rewards

    def __init__(self, version: int, stop_early=False, noisy=True):

        name = 'ChestClock{}{}{}-v0'.format('EarlyStop'if stop_early else '',
                                            'Noisy' if noisy else '',
                                            version)

        self.stop_early = stop_early
        self.noisy = noisy
        xml = 'chest_clock_{}.xml'.format(version)
        super().__init__(name, xml)

    def is_from_folder(self, folder: str) -> bool:
        return False

    def create_mission_handlers(self) -> List[minerl.herobraine.hero.AgentHandler]:
        mission_handlers = [
            handlers.EpisodeLength(1000),
        ]
        return mission_handlers

    def create_observables(self) -> List[minerl.herobraine.hero.AgentHandler]:
        return [
            handlers.POVObservation(self.resolution),
            handlers.FlatInventoryObservation(['diamond_pickaxe', 'clock', 'redstone', 'gold_block', 'gold_ingot'])
        ]

    def create_actionables(self) -> List[minerl.herobraine.hero.AgentHandler]:
        return super().create_actionables() + [handlers.PlaceBlock(['none', 'dirt'])]

    def get_docstring(self):
        return """        
        In this task, the agent must collect materials in order to craft a clock, and then open the chest while holding
        the clock to complete the mission. 
        """
