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
| `Assets/_Project/Dialogue` | `DormHallway.yarn`, the vertical-slice puzzle |

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

## Building the slice scene by scene

**Data** (right click in `Assets/_Project/Data` > Create > Big Night Out):

- Room `dorm_hallway`, scene `DormHallway`.
- Items: `earplugs`, `dance_album`, `lemon`, `soda`, `hallway_hooch`, `cowboy_hat` (coloured squares are fine as icons for now).
- One Item Database with all six items and the combination `lemon` + `soda` > `Combine_Lemon_Soda`.

**Boot scene** (`Scenes/Boot.unity`, first in Build Profiles):

- `Game` object: `GameManager` and `RoomLoader` (list the room, first room `dorm_hallway`, entry `start`).
- `Player`: sprite, `PlayerMover`, a child `Visual` for flipping.
- `Input`: `PointerController` with the main camera, the player and the hover label.
- Canvas with `HoverLabel` (TextMeshPro text) and `InventoryBar` (a horizontal layout plus a slot prefab using `InventorySlot`). EventSystem with the Input System UI module.
- Yarn's Dialogue System prefab, plus `YarnDialogueStarter` on the same object. Create a Yarn Project that includes `DormHallway.yarn` and assign it.

**Room scene** (`Scenes/Rooms/DormHallway.unity`):

- Root object with `Room` (definition `dorm_hallway`, on-enter node `DormHallway_Enter`).
- Background layers as sprites, floor as a `PolygonCollider2D` (Is Trigger) with `WalkableArea`, one `EntryPoint` named `start`.
- Hotspots, each with a trigger collider and a walk-to point:

| Hotspot | Look | Use | Item responses |
| --- | --- | --- | --- |
| Lacey Rae | `Lacey_Look` | `Lacey_Talk` | `dance_album` > `Lacey_GiveAlbum`, `hallway_hooch` > `Lacey_GiveDrink` |
| Gil | | `Gil_Talk` | `earplugs` > `Gil_GiveEarplugs` |
| Vending machine | | `Vending_Use` | |
| Drinks table | `DrinksTable_Look` | `DrinksTable_Use` | |

The slice is solved when the player has the `cowboy_hat`.

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
