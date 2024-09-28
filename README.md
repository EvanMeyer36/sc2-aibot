# ImprovedTerranBot

![ImprovedTerranBot Logo](https://i.ibb.co/4tkNJLj/2f08e8d2-76f9-448f-9445-cb7fd483b657.webp)

This repository contains the code for **ImprovedTerranBot**, a custom bot for StarCraft II using the [python-sc2](https://github.com/BurnySc2/python-sc2) library. The bot is designed to manage the Terran faction, build structures, expand, and control an army to defeat a computer opponent.

## Features

- **Basic Economy Management**: The bot builds workers, refineries, and supply depots to maintain the economy.
- **Building Construction**: The bot constructs Barracks, Factories, and Starports to produce military units.
- **Army Production**: The bot trains Marines, Marauders, Siege Tanks, and Medivacs.
- **Army Micro**: Units are managed with attack and retreat logic, including special handling of Siege Tanks and Medivacs.
- **Resource Management**: The bot manages idle workers and expands to new bases when required.
- **Upgrade Management**: The bot researches infantry upgrades to improve the effectiveness of its army.
- **Benchmark Mode**: Run multiple matches to benchmark the bot's performance.

## Prerequisites

To run the bot, you will need the following:

1. **StarCraft II** installed on your system.
2. **python-sc2** library installed in your Python environment:
   ```
   pip install sc2
   ```
3. Ensure the `SC2PATH` environment variable is set correctly to your StarCraft II installation directory in the code:
   ```python
   os.environ["SC2PATH"] = "W:/StarCraft II"
   ```

## Running the Bot

### Single Match

To run a single match with default settings:

```
python bot_script.py
```

### Benchmark Mode

To run multiple matches for benchmarking, use the following command-line arguments:

```
python bot_script.py --run-matches 20 --difficulty Hard --race Zerg --map AcropolisLE
```

#### Command-line Arguments

- `--run-matches`: Number of matches to run for benchmarking
- `--difficulty`: AI difficulty (Easy, Medium, Hard, VeryHard, CheatVision, CheatMoney, CheatInsane)
- `--race`: Opponent race (Terran, Zerg, Protoss, Random)
- `--map`: Map name (e.g., AcropolisLE)

## Bot Overview

### Army Composition

- Marines
- Marauders
- Siege Tanks
- Medivacs

### Building Logic

- Builds Barracks (for infantry), Factories (for tanks), and Starports (for Medivacs).
- Adds Tech Labs to Barracks and Factories to unlock advanced units like Marauders and Siege Tanks.
- Expands to new Command Centers when the mineral fields are near depletion.

### Army Control

- The bot waits for a critical mass of units (60 supply) before attacking.
- Retreats if outnumbered or overwhelmed.
- Uses Medivacs for healing and transporting troops into battle.
- Siege Tanks are set to Siege Mode automatically when close to enemies.

### Upgrade Management

- Researches infantry upgrades at the Engineering Bay to increase the army's effectiveness.
- Adds additional Engineering Bays for simultaneous research of armor and weapons upgrades.

## Benchmark

To run your own benchmarks:

1. Use the command-line interface as described above.
2. Results will be logged to `bot_output.log` and displayed in the console.
3. Analyze the results to gauge the bot's performance against different opponents and settings.

Example benchmark table:

| Opponent    | Difficulty | Map         | Win Rate | Average Game Length | Total Matches |
|-------------|------------|-------------|----------|---------------------|---------------|
| Zerg AI     | Hard       | AcropolisLE | 85%      | 22 minutes          | 20            |
| Protoss AI  | Hard       | ThunderbirdLE | 78%    | 25 minutes          | 15            |
| Zerg AI     | Very Hard  | Kairos Junction | 65%  | 27 minutes          | 10            |
| Terran AI   | Hard       | Ephemeron LE | 82%     | 24 minutes          | 18            |
| Random AI   | Elite      | Disco Bloodbath | 60%  | 30 minutes          | 5             |

## Known Issues

- **Tech Lab Construction**: Occasionally, the bot may attempt to add a Tech Lab to a Barracks or Factory when the building isn't ready.
- **Army Micro**: The army currently tends to rush in without sufficient micro, which can lead to unnecessary losses if the enemy is stronger.
- **Factory Production**: Sometimes the bot fails to properly train Siege Tanks due to missing prerequisites like Tech Labs.

## Future Improvements

- **Better Army Micro**: Implement improved logic for unit positioning, kiting, and grouping to prevent units from getting wiped out too easily.
- **Smarter Expansion Timing**: Improve the decision-making for expansions to maintain a stronger economy.
- **Combat Grouping**: Group combat units into multiple squads for more tactical attacks and defense.

## Contributions

Contributions are welcome! If you'd like to contribute, feel free to submit a pull request or report issues.

## License

This project is licensed under the MIT License - see the LICENSE file for details.