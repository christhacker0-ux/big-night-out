# Art style 2: how the rooms and characters are painted

Act 1 is painted in "style 2" by `tools/art/act1_style2.py`, which uses the kit in `tools/art/style2.py`.
Use the same kit for later acts. Every room, character, sign and prop must be our own design.
Learn technique and palette from reference art, but never copy its characters, logos, sign text, props
or layouts.

## The look
- **Rooms are 3/4-perspective boxes.** Each has a back wall, two angled side walls, a ceiling (with beams,
  pipes, cables or rafters) and a deep floor that runs to a vanishing point. Outdoor scenes use the same
  camera, with no side walls and the sky in place of a ceiling.
- **Lived-in grunge.**
  - Walls: chipped plaster showing brick, stains with drips, cracks, scuffs along the skirting.
  - Decorations: peeling, taped-up posters; cobwebs in the corners; hanging cables.
  - Clutter: on shelves and on the floor at the back of the room.
- **Palette.**
  - Walls are magenta, pink or purple.
  - Accents are teal: dados, doors, furniture.
  - Light is warm yellow, from lamps with soft cones and pools.
  - Shadows and the vignette are cool violet.
  - Each room has one or two coloured light sources, such as a TV, a lava lamp or moonlight.
- **Line and paint.**
  - Outlines are dark violet (`INK`), hand-wobbled, and vary in width (thicker on the shadow side).
  - Shading is soft cel shading, with a lit edge and a rim highlight.
  - A light paper/brush texture goes over everything (`painterly`).
- **Foreground framing.** Dark, slightly blurred silhouettes (plants, bottles, chair backs, cables, a
  lampshade) sit at the bottom and in the corners of the frame. They are painted into the background, so
  keep them **below y ≈ 985 px** or outside the walkable x range. Never put them over a hotspot.

## Using style2.py
```python
from style2 import *          # also brings in paint.py's helpers (Sh, ell, rect, rrect, blob, mix, ...)

c = Canvas2(W_BG, H_BG, bg=(20, 10, 30, 255), light=(-0.3, -0.95), lw=3.4, seed=1)
R = Room(c, vp=(960, vp_for_walk(762, 975)), back=(330, 250, 1590, 690))   # back wall rect in px
R.shell(left_fn=..., right_fn=..., floor_fn=..., ceil_fn=...)   # flat painters, warped into perspective
R.paint_plane("back", 0, R.Wb, 0, R.Hb, back_fn)
R.ao(0.5); R.edges()                                             # corner shading + corner lines
R.ink_box(X0, X1, Y0, Y1, Z0, Z1, colour)                        # furniture: 3-D boxes in room space
x, y = R.pt(X, Y, Z)                                             # room space -> screen px
room_grade(c, lights=[(x, y, radius, strength, colour?)], ...)   # light pools + violet vignette
c.painterly(0.05)
fg_paint(c, lambda sub: (fg_plant(sub, 80, 1100, 300), ...))     # out-of-focus foreground
c.save_png("bg_room.png")
```
- `c.ink(shape, fill, ...)` is the core brush. It draws the fill, the cel shadow, the highlight, the rim
  light, the variable outline and the texture. Pass `line_only`, `clip` or `atop` for special cases.
  `c.stroke(points, w, colour)` draws tapered lines; `glow2` and `light_cone` add light.
- **Room space.** X runs across the back wall (0 to `Wb`), Y up from the floor, and Z toward the camera.
  On the back wall (Z = 0), 1 unit is 1 px. Flat painters get a sub-canvas with `sub.ax(a)` / `sub.by(b)`
  to convert plane coordinates.
- **Surfaces.** `grunge_wall` and `two_tone_wall` (in act1_style2.py), `plaster_wall`, `chip`, `stain`,
  `crack`, `scuffs`, `planks`, `tiles`, `carpet`, `wainscot`, `poster`, `night_sky`, `flat_door`.
- **Props.** `cable`, `hanging_cable`, `pipe`, `pendant_lamp`, `bulb`, `string_lights2`, `book_row`, `shelf`,
  `cobweb`. Room props also live in act1_style2.py: `panel_light`, `vending_machine`, `couch`, `crt_tv`,
  `bookcase`, `banker_lamp`, `beanbag`, `lamppost`, `facade_windows`, `window_flat`, `doorway_flat`. Move
  them into style2.py if a later act needs them.
- **Characters.** Build each one from `Body(c, fx, fy, height, build, pose, skin)`, which provides
  `torso_pts`, `sleeve`, `leg_shape`, `head_pts`, `eyes`, `brows`, `nose`, `mouth`, `hand`, `shoe` and more.
  Finish with `finish_sprite(c, name, flip)`.
  - Draw every character facing **right**. Pass `flip=True` for characters who face left.
  - Text on a flipped sprite uses `c.label(..., mirror=True)` so it reads correctly after the flip.

## Character sizes
- Proportions: about 6.5 heads tall, slim, with big eyes. Feet sit at the bottom centre of the sprite.
  The sprite is cropped to its content.
- **Dex** (`player_dex.png`) has a 440 px crown height (469 px with hair), about 43% of the screen. The game
  scales him from 1.0 at the bottom of the walkable area to 0.6 at its top.
- **NPC and prop sprites are not scaled by the game.** Paint each NPC at the size it has where it stands:
  `height = 440 × depth_scale(feet_y) × rel`, where `rel` is how tall they are next to Dex (`NPC_REL`).
  `npc_height()` does this from the room layout. Stand NPCs near the front (feet y ≈ 945 px) so they come
  out 370–490 px tall.
  - If an NPC appears in several rooms, use the same feet y in each.
  - NPC hotspot boxes are 1.9 units wide × the sprite height.
- Current sprites (px):

  | Sprite | Size | Sprite | Size |
  |---|---|---|---|
  | Dex | 174×469 | Lacey | 146×428 |
  | Gil | 198×403 | Ivy | 139×373 |
  | Ms. Hush | 217×376 | Roxy | 133×407 |
  | Boomer | 373×493 | Doreen | 327×417 |
  | Kyle | 290×407 | Percival | 191×436 |

## Perspective and walkable areas
- **The vanishing point must agree with the game's linear depth scale.** Make the walkable area span
  y_top … y_bot in px (Act 1 uses 762 … 975) and put the eye line at
  `vp_y = y_top − 1.5 × (y_bot − y_top)`; `vp_for_walk()` computes this (442.5 for Act 1). Then something
  painted on the floor shrinks at exactly the rate the game shrinks Dex.
- The back wall meets the floor at about y = 680–700 px. Keep furniture behind y_top, or cut it out of the
  walkable polygon (the bunk bed in Gil's room and the floor hatch in the stacks do this).
- Each room's layout is a `LAYOUT[...]` entry in act1_style2.py, written in screen px:
  - `walk_px`: the polygon.
  - `hotspots`: for each `(name, n)`, either a `box` or the `npc`/`sprite` with its `feet`, plus a `stand`
    point.
  - `entries`.

  `--layout` converts these to world units and writes them into `act1.json`. It touches only `walkable`,
  `feet`, `size`, `standAt` and entry `pos`. Afterwards run `python3 tools/check_world.py`.
- Check every room with `--composite`. It draws the room with its sprites at their feet, Dex scaled by
  depth at the front stand points and at the back of the walkable area, the hotspot boxes, the stand points
  and the entries.

## Regenerating
`paint.py` and `act1_more.py` still paint the Act 1 item icons. A plain run of either skips the files listed
in its `SUPERSEDED_BY_STYLE2`, so it can't overwrite the new art; name a file explicitly to bring back the
old version. Run `act1_style2.py` for everything else in Act 1.
