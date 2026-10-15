# Big Night Out

A 2D point-and-click comedy adventure in Unity: painted backgrounds, cut-out characters, one campus, one very big night.
Working names (hero Dex Dooley, the show *Speed Daters Live*, and so on) are placeholders and can change.

Plan: https://claude.ai/code/artifact/310973cf-fb08-4b26-95a7-0b2d8a5cc66a

## What is here

| Folder | Contents |
| --- | --- |
| `Assets/_Project/Scripts/Core` | `GameState` (the only saved state), `GameManager`, the dialogue interface |
| `Assets/_Project/Scripts/Rooms` | Room definitions, entry points, the additive room loader |
| `Assets/_Project/Scripts/Interaction` | Walkable floor, player walking, hotspots, mouse controls |
| `Assets/_Project/Scripts/Inventory` | Items, the item database with combinations, the inventory bar |
| `Assets/_Project/Scripts/Save` | JSON save slots, autosave on every room change |
| `Assets/_Project/Scripts/Dialogue` | Yarn Spinner bridge: commands and functions for Yarn scripts |
| `Assets/_Project/Dialogue` | `BigNightOut.yarnproject` (picks up every `.yarn` file in this folder) and `DormHallway.yarn`, the vertical-slice puzzle |

Controls: left click walks or uses, right click looks, click an inventory item to hold it, then click a hotspot to use it there or another item to combine.

## One-time setup

1. Install Unity Hub and **Unity 6.3 LTS** (6000.3.x).
2. In Unity Hub, create a new project from the **Universal 2D** template, named `BigNightOut`. Close Unity.
3. Copy everything in this folder into the new project's root, merging `Assets/`. Keep `.gitignore` and `.gitattributes`.
4. Open the project. In **Window > Package Manager**, make sure these are installed: 2D Animation, 2D PSD Importer, 2D Sprite Shape, Input System, Cinemachine. Most come with the template.
5. Install Yarn Spinner for free: **Package Manager > + > Add package from git URL**, then paste
   `https://github.com/YarnSpinnerTool/YarnSpinner-Unity.git#current` (needs Git installed).
   Until Yarn is installed, the Yarn bridge folder is simply skipped and everything else compiles.
6. **Edit > Project Settings > Editor**: Version Control mode = Visible Meta Files, Asset Serialization = Force Text.
7. In a terminal at the project root: `git init`, `git lfs install`, then commit and push to the private GitHub repository.

## Building the first room

After setup (including installing Yarn Spinner), run **Big Night Out > Build Dorm Hallway Slice** from the menu bar. It:

- generates flat-colour placeholder sprites in `Art/Placeholder`,
- creates the six items, the item database (with `lemon` + `soda`) and the `dorm_hallway` room asset,
- builds `Scenes/Rooms/DormHallway.unity`: background, floor, entry point and four hotspots (Lacey Rae, Gil, the vending machine, the drinks table) wired to their Yarn nodes,
- builds `Scenes/Boot.unity`: camera, player, room loader, mouse controls, hover label, inventory bar, Yarn's Dialogue System with our bridge,
- puts Boot and DormHallway in the build list and opens Boot.

Press Play in Boot. The slice is solved when Dex has the cowboy hat: earplugs from the vending machine go to Gil for the album, the drinks table gives a lemon and a soda to combine, and both go to Lacey Rae.

Running the tool again overwrites the generated scenes and placeholders, so stop using it once real art goes into those scenes. The first time it adds TextMeshPro text, Unity may ask to import TMP Essentials; accept.

## What each hotspot runs

| Hotspot | Look | Use | Item responses |
| --- | --- | --- | --- |
| Lacey Rae | `Lacey_Look` | `Lacey_Talk` | `dance_album` > `Lacey_GiveAlbum`, `hallway_hooch` > `Lacey_GiveDrink` |
| Gil | `Gil_Look` | `Gil_Talk` | `earplugs` > `Gil_GiveEarplugs` |
| Vending machine | `Vending_Look` | `Vending_Use` | |
| Drinks table | `DrinksTable_Look` | `DrinksTable_Use` | |

## Yarn commands and functions

```
<<give item>>  <<take item>>  <<flag name>>  <<unflag name>>  <<add counter 1>>  <<act 2>>  <<go room_id entry>>
has("item")  flagged("name")  counter("name")  current_act()
```

## Not done yet

- Pathfinding: the player walks in a straight line, clamped to the floor.
- Save and load menu (the code exists; there is no UI for it yet).
- Localisation tables for names.
- The scripts were written without a Unity editor at hand, so expect a few compile fixes on first open.
- If Yarn is installed but `YarnCommands` does not compile in, check that the package name in `BigNightOut.Yarn.asmdef` (`versionDefines`) matches the name Package Manager shows for Yarn Spinner.
