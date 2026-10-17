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

Controls: left click walks or uses, right click looks, click an inventory item to hold it, then click a hotspot to use it there or another item to combine. You can also drag an item from the bar straight onto a person, an object or another item.

## Quick start (no Unity experience needed)

1. Install **Git** from https://git-scm.com/downloads (Unity needs it to download Yarn Spinner). Default options are fine.
2. Install **Unity Hub** from https://unity.com/download and sign in with a free Unity account.
3. In Unity Hub, open **Installs > Install Editor** and install the latest **Unity 6.3 LTS**.
4. Get the project: on the GitHub page, click the green **Code** button, then **Download ZIP**, and unzip it somewhere easy, like your Documents folder.
5. In Unity Hub, click **Add > Add project from disk** and pick the unzipped folder (it is called `big-night-out-main`). If Hub asks which editor version to use, pick the 6.3 version you installed.
6. Open the project. The first open takes a few minutes. The project then installs its own packages (Input System, Yarn Spinner) and builds the first room by itself. If Unity asks to restart to enable the new Input System, click **Yes**.
7. When the **Boot** scene opens, press the **Play** button at the top of the window.

Left click to walk and use things, right click to look. Click an item in the bar at the top to hold it, then click a person or another item to use it, or just drag the item onto them.

If anything shows red errors in the **Console** window, copy them and send them to Claude. To run the automatic setup again, use **Big Night Out > Run First-Time Setup Again** in the menu bar.

## Manual setup (for developers)

The auto-setup lives in `Assets/_Project/Editor/Setup/AutoSetup.cs`. Doing it by hand instead:

1. Open the project in Unity 6.3 LTS.
2. Install Input System from the Package Manager, and Yarn Spinner from git URL `https://github.com/YarnSpinnerTool/YarnSpinner-Unity.git#current`. Until both are installed, the game assemblies are skipped instead of failing to compile.
3. **Edit > Project Settings > Editor**: Version Control mode = Visible Meta Files, Asset Serialization = Force Text.

## Building the game

The auto-setup runs **Big Night Out > Build Game** for you the first time (the old name, Build Dorm Hallway Slice, still works). Run it again after any change. It reads `World/*.json` and:

- creates every item, the item database with its combinations, and one room asset per room,
- builds one scene per room in `Scenes/Rooms` from the room's painted background (`Art/Painted`) and its hotspots, falling back to flat-colour placeholders where art is missing,
- builds `Scenes/Boot.unity`: camera, player, room loader, mouse controls, hover label, inventory bar, pause menu, Yarn's Dialogue System with our bridge,
- puts Boot and every room in the build list and opens Boot.

Press Play in Boot. The whole story runs from Dex's dorm room to the live Speed Daters Live finale: five acts and a finale, 18 rooms. [Docs/WALKTHROUGH.md](Docs/WALKTHROUGH.md) has the full solution, [Docs/STORY.md](Docs/STORY.md) the story bible, and [Docs/WORLD_FORMAT.md](Docs/WORLD_FORMAT.md) how to add rooms and puzzles. `python3 tools/check_world.py` checks the JSON and Yarn files without Unity, and `python3 tools/art/paint.py` (plus `act2.py` to `finale.py`) regenerates the art.

Press **Esc** for the pause menu: Resume, Save, Load and Quit. Save and Load use one manual slot; the game also autosaves to its own slot on every room change.

Running the tool again overwrites the generated scenes, so make changes in the JSON, Yarn and art files rather than in the scenes. The first time it adds TextMeshPro text, Unity may ask to import TMP Essentials; accept.

## What each hotspot runs

| Hotspot | Look | Use | Item responses |
| --- | --- | --- | --- |
| Bed (Dex's room) | `Bed_Look` | `Bed_Use` | |
| Mirror (Dex's room) | `Mirror_Look` | `Mirror_Use` | |
| Desk (Dex's room) | `Desk_Look` | `Desk_Use` | |
| Door to hallway (Dex's room) | `DexDoor_Look` | `DexDoor_Use` | |
| Your door (hallway) | `HallDoor_Look` | `HallDoor_Use` | |
| Lounge (hallway) | `LoungeDoor_Look` | `LoungeDoor_Use` | |
| Hallway (lounge) | `LoungeExit_Look` | `LoungeExit_Use` | |
| Couch (lounge) | `Couch_Look` | `Couch_Use` | |
| TV (lounge) | `TV_Look` | `TV_Use` | |
| Sign-up sheet (lounge) | `SignUp_Look` | `SignUp_Use` | `cowboy_hat` > `SignUp_GiveHat` |
| Lacey Rae | `Lacey_Look` | `Lacey_Talk` | `dance_album` > `Lacey_GiveAlbum`, `hallway_hooch` > `Lacey_GiveDrink` |
| Gil | `Gil_Look` | `Gil_Talk` | `earplugs` > `Gil_GiveEarplugs` |
| Vending machine | `Vending_Look` | `Vending_Use` | `dollar` > `Vending_Use` |
| Drinks table | `DrinksTable_Look` | `DrinksTable_Use` | |

## Yarn commands and functions

```
<<give item>>  <<take item>>  <<flag name>>  <<unflag name>>  <<add counter 1>>  <<act 2>>  <<go room_id entry>>
has("item")  flagged("name")  counter("name")  current_act()
```

## Not done yet

- Pathfinding: the player walks in a straight line, clamped to the floor.
- More than one manual save slot.
- Localisation tables for names.
- The scripts were written without a Unity editor at hand, so expect a few compile fixes on first open.
- If Yarn is installed but `YarnCommands` does not compile in, check that the package name in `BigNightOut.Yarn.asmdef` (`versionDefines`) matches the name Package Manager shows for Yarn Spinner.
