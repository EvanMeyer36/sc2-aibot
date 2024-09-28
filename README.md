# ImprovedTerranBot
![Alt text](https://i.ibb.co/4tkNJLj/2f08e8d2-76f9-448f-9445-cb7fd483b657.webp)

This repository contains the code for **ImprovedTerranBot**, a custom bot for StarCraft II using the [python-sc2](https://github.com/BurnySc2/python-sc2) library. The bot is designed to manage the Terran faction, build structures, expand, and control an army to defeat a computer opponent.

## Features

- **Basic Economy Management**: The bot builds workers, refineries, and supply depots to maintain the economy.
- **Building Construction**: The bot constructs Barracks, Factories, and Starports to produce military units.
- **Army Production**: The bot trains Marines, Marauders, Siege Tanks, and Medivacs.
- **Army Micro**: Units are managed with attack and retreat logic, including special handling of Siege Tanks and Medivacs.
- **Resource Management**: The bot manages idle workers and expands to new bases when required.
- **Upgrade Management**: The bot researches infantry upgrades to improve the effectiveness of its army.

## Prerequisites

To run the bot, you will need the following:

1. **StarCraft II** installed on your system.
2. **python-sc2** library installed in your Python environment:
   `pip install sc2` 

3.  Ensure the `SC2PATH` environment variable is set correctly to your StarCraft II installation directory in the code:
    `os.environ["SC2PATH"] = "W:/StarCraft II"` 
    

## Running the Bot

To run the bot, you can execute the `main` function in the script:

`python bot_script.py` 

This will start a game between **ImprovedTerranBot** (Terran) and a Zerg computer opponent at Hard difficulty on the **AcropolisLE** map.
### Changing map and difficulty
If you would like to change the map you can do so in the main method of the bot, just simply switch the name out for one you have saved. 
Make sure you have a Maps folder in your `/Starcraft2/` installation (this might need to be made a loaded manually. 
Additionally you can add and change the difficulty and opponents in the run method as well.
```
def main():
    run_game(
        maps.get("AcropolisLE"),
        [
            Bot(Race.Terran, ImprovedTerranBot()),
            Computer(Race.Zerg, Difficulty.Hard)
        ],
        realtime=False,
        save_replay_as="my_bot_game.SC2Replay"       
    )

if __name__ == "__main__":
    main()
```

### Steps to Run

1.  Clone this repository.
2.  Ensure the `SC2PATH` environment variable is set correctly in the script.
3.  Run the script using Python 3.

## Bot Overview

### Army Composition

-   **Marines**
-   **Marauders**
-   **Siege Tanks**
-   **Medivacs**

### Building Logic

-   Builds Barracks (for infantry), Factories (for tanks), and Starports (for Medivacs).
-   Adds Tech Labs to Barracks and Factories to unlock advanced units like Marauders and Siege Tanks.
-   Expands to new Command Centers when the mineral fields are near depletion.

### Army Control

-   The bot waits for a critical mass of units (60 supply) before attacking.
-   Retreats if outnumbered or overwhelmed.
-   Uses Medivacs for healing and transporting troops into battle.
-   Siege Tanks are set to Siege Mode automatically when close to enemies.

### Upgrade Management

-   Researches infantry upgrades at the Engineering Bay to increase the army's effectiveness.
-   Adds additional Engineering Bays for simultaneous research of armor and weapons upgrades.

## Known Issues

-   **Tech Lab Construction**: Occasionally, the bot may attempt to add a Tech Lab to a Barracks or Factory when the building isn't ready.
-   **Army Micro**: The army currently tends to rush in without sufficient micro, which can lead to unnecessary losses if the enemy is stronger.
-   **Factory Production**: Sometimes the bot fails to properly train Siege Tanks due to missing prerequisites like Tech Labs.

## Future Improvements

-   **Better Army Micro**: Implement improved logic for unit positioning, kiting, and grouping to prevent units from getting wiped out too easily.
-   **Smarter Expansion Timing**: Improve the decision-making for expansions to maintain a stronger economy.
-   **Combat Grouping**: Group combat units into multiple squads for more tactical attacks and defense.

## Contributions

Contributions are welcome! If you'd like to contribute, feel free to submit a pull request or report issues.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
