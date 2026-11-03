# Lantern Wanderer: development notes

How to run, test, extend and build the game. For what the game is, see the
[README](README.md); the design bible (story, lore, cast, systems, endings) is
[DESIGN.md](DESIGN.md).

## Play

- Double-click `play.bat` to play, or `edit.bat` to open the project in the Godot editor.
- Godot 4.7.2 (portable) lives in `C:\Users\Administrator\Godot\`.
- The game saves by itself (shrines, the Little Hearth, every area you enter).
  "Continue" on the title screen picks up from there.

## Playing on another PC

`play.bat` needs Godot at the path above, so copying this folder alone isn't enough.
Instead, double-click `export.bat`. It builds `export/LanternWanderer.exe`, a single file
with the whole game inside. Copy that one file to any 64-bit Windows PC and run it;
nothing needs installing. Any graphics card with OpenGL 3.3 runs it.

Saves live in `%APPDATA%\Godot\app_userdata\Lantern Wanderer\save.json`, outside this folder
(options and key bindings sit next to it in `settings.cfg`).
Copy that file to the same place on the other PC to keep your progress.
The `.exe` and `play.bat` share the same save.

The credits name is `MADE_BY` at the top of `scripts/credits.gd`; add playtesters and thanks
in the lists below it. [PLAYTEST.md](PLAYTEST.md) has the playtest plan and the release checklist.

Rebuild the `.exe` after changing anything. New files that aren't Godot resources
(like the `levels/*.txt` maps) must be listed in `include_filter` in `export_presets.cfg`,
or the export leaves them out.

| Action | Keyboard | Gamepad |
|---|---|---|
| Move | A / D or arrow keys | Left stick / D-pad |
| Jump | Space, W, Up, Z | A |
| Drop through a platform | Down + Jump | Down + A |
| Talk / interact / advance text | E, X, Enter | X / B |
| Choose a dialogue option | Up / Down | D-pad |
| Flare (once you have it) | F, C, L, Shift | Y / RB |
| Journal (places, people, tablets, names) | Tab | Select |
| Pause: journal, options, quit to title | Esc, P | Start |
| Fullscreen | F11 | |

Every key above can be changed in **Options > Controls** (from the title screen or the pause menu),
up to four keys per action. Gamepad buttons are fixed. Options also has fullscreen, window size,
music and sound volume, and text speed. Button prompts show whatever key is bound, or the
gamepad button once you touch a pad.

## The journey

| Area | File | What's there |
|---|---|---|
| Mossgrave Woods (Ch I) | `levels/mossgrave.txt` | Mossback the totem; west to Old Hollow, east to the cave |
| Old Hollow (hub) | `levels/old_hollow.txt` | Nan Tallow, Pell, the Little Hearth, three Wickways; everyone you help moves in |
| The Glimmerdeep (Ch II) | `levels/glimmerdeep.txt` | Glimmer crystal, shades, Burrow, Wisp, Ash, Old Gudgeon |
| The Drowned Halls (Ch III) | `levels/drowned.txt` | Bell, the Archivist and the Book of Wicks, the **Hook** gift, eye-gates |
| The Starwell (side chapter, *Under the Lake*) | `levels/starwell.txt` | Warm Old Gudgeon and he dives you down to it. Orrin, shadow-play, orrery lifts, the Great Orrery |
| The Rootdark (Ch IV) | `levels/rootdark.txt` | Sprig, the Root-Mother, the **Flare** gift, thorn-roots, the Hollow One |
| The Hearth (Ch V) | `levels/hearth.txt` | The end of the road, and four endings |
| Echo I: Lark's Song | `levels/echo_lark.txt` | Lay Lark's lantern (Glimmerdeep, above Ash) in the Little Hearth. Play as Lark: warm people and they light the way |
| Echo II: The Last Winter | `levels/echo_maud.txt` | Maud's handbell (Drowned Halls, the sunk supper hall). Play as Maud: ring the bell, wake five Keepers, outrun the flood |
| Echo III: Vesper | `levels/echo_vesper.txt` | The first page (the Root-Mother keeps it). Play as Vesper, the first wick: fear, the Hearth, the run back up |

Old Hollow fills up as people move in: suppers at the Little Hearth once three people live
there, new lines for everyone as the story moves, Glim (Wisp's mama, found in the old seam
after Lark's Song), Orrin's telescope hints, and Gudgeon's ferry from the well. See DESIGN.md
section 7 for the whole expansion, including the fourth ending, *The First Page*.

The Echoes stay open after an ending: find a keepsake late and the Little Hearth still takes
it. With all three seen, the Hollow One asks to walk down with you, and The First Page plays.
A small speech bubble over someone means they have something new to tell you.

## Project layout

| Path | What it is |
|---|---|
| `scenes/main.tscn` | Main scene: level, camera, HUD, title screen |
| `scripts/level.gd` | Builds a level from an ASCII map; **legend and header format at the top** |
| `levels/*.txt` | The maps. Edit them directly (or `art_src/make_maps.py`, then regenerate one) |
| `scripts/story.gd` | The cast (`Story.NPCS`), Pell's remarks, helpers |
| `scripts/story/*.gd` | All dialogue, one file per chapter |
| `scripts/dialogue.gd` | Dialogue box + entry format (conditions, giving embers, events, cards) |
| `scripts/game.gd` | Global state, flags, conditions, travel, saving, fades, default keys (autoload `Game`) |
| `scripts/sound.gd` | Music, ambience, effects and character voices (autoload `Sound`) |
| `scripts/settings.gd` | Volumes, window, text speed, key bindings, keyboard-or-pad (autoload `Settings`) |
| `scripts/options.gd`, `credits.gd`, `key_prompt.gd` | Options & Controls screens, credits and licenses, button prompts |
| `scripts/npc.gd`, `pell.gd`, `totem.gd` | Characters |
| `scripts/shade.gd`, `glimmer.gd`, `hook.gd`, `gate.gd`, `eye.gd`, `thorn.gd`, `water.gd` | Light mechanics |
| `scripts/caster.gd`, `starlamp.gd`, `orrery.gd`, `great_orrery.gd` | The Starwell: shadow-play plates, star-lamps, orrery suns, the sky |
| `scripts/journal.gd`, `journal_data.gd`, `name_stone.gd` | The Journal and its content, Keeper name-stones |
| `scripts/keepsake.gd`, `follower.gd`, `rising.gd`, `landing.gd`, `old_hearth.gd` | Echoes: keepsakes, Keepers/Edda walking behind you, the rising flood/dark, checkpoints, the old Hearth |
| `scripts/story/echoes.gd`, `story/home.gd` | Echo dialogue; suppers, resident threads, the First Page ending |
| `shaders/memory.gdshader` | The memory filter over Echoes (and Vesper's fear) |
| `scripts/wickway.gd`, `hearth.gd`, `great_hearth.gd`, `door.gd` | Lifts, hearths, endings, doors & triggers |
| `scenes/backdrops/*.tscn` | Parallax backdrop for each theme |
| `art_src/` | Python scripts that generate every image **and sound** in `assets/` |

## Adding content

- **Area:** a new `levels/<id>.txt`, with `@name`, `@theme`, `@light`, `@music` and
  `@char` lines on top. Link areas with `@char <c> door <id> <level> <door>` on both sides.
- **Character:** an entry in `Story.NPCS` (sprite, animations, light, `talks`, `where`)
  plus dialogue in `scripts/story/`. Place it with `@char <c> npc <id>`.
- **Conditions** anywhere: `flag`, `!flag`, `embers>=N`, `given>=N`, `names>=N`, `new_names`, `in:<level>`, comma-separated (all must hold); `a|b` means either.
- **Sharing an ember:** a dialogue choice with `"give": "<npc>"`.
- **Naming a key in text:** write `{key:flare}` (any action) in dialogue or a title card. It shows
  as `[F]`, or whatever the player bound, or `[Y]` on a gamepad. Never write a key name directly.
- **Journal entries:** add to `scripts/journal_data.gd` (places, people, tablets, Keeper names).
  Signs mark themselves read; a new Keeper name needs an entry in `NAMES` and a `@char <c> name <id>` in a map.
- **Echoes:** a map with `@echo <id>` and `@hero <skin>` (sprites `hero_<anim>_<skin>.png`) is a
  playable memory; `Game.start_echo(id)` / `end_echo()` keep the real journey safe meanwhile.
  Flags inside one start with `<id>:` and are forgotten on replay. Map kinds for them: `keepsake`,
  `landing`, `sleeper`, `follower`, `rising`, `headcount`, `old_hearth` (legend in `scripts/level.gd`).
- **Suppers:** add `[id, condition]` to `StoryHome.SUPPERS` and a `supper_<id>` dialogue; give
  each resident's line an `"if": "gave_<them>"` so it only plays when they live there.
- **Shadow puzzles:** a still light at L throws a plate's shadow to `2C - L`, twice the plate's size.
  Work the numbers out in `art_src/make_maps.py` (see `starwell()`), which prints where every shadow lands.

## Art & audio pipeline

Everything is drawn and synthesized by code in a shared palette (`art_src/pix.py`):

```
cd art_src
python tiles.py      # forest ground + wall tilesets
python cave.py       # Glimmerdeep tiles, backdrop, crystals, glimmer, Wickway
python drowned.py    # Drowned Halls: masonry, water, hooks, eye-gates
python rootdark.py   # Rootdark: roots, fungus, thorn-roots
python hearth_env.py # The Hearth chamber and the great Hearth
python starwell.py   # the Starwell: tiles, backdrop, props, plates, lamps, orreries
python npcs3.py      # Orrin, name-stones, stars, journal icon
python hero.py       # the wanderer (npcs2.py makes the burnt-scarf stages)
python npcs.py       # Tallow, Pell, Burrow, Wisp, Ash, shades, the Little Hearth
python npcs2.py      # Archivist, Bell, Gudgeon, Root-Mother, Sprig, Hollow One
python bg.py         # forest parallax
python deco.py       # forest props, Mossback, shrine, embers, lights
python keeper.py     # Keeper lore tablet
python ui.py         # pixel font, UI frames, keycap and gamepad-button prompts
python icon.py       # the game icon (icon.png, icon.ico in the project root)
python audio.py      # music, ambience, sfx, voices (needs numpy + soundfile; ~3 min)
python audio_starwell.py   # the Starwell's music, sfx and Orrin's voice (~1 min)
python echoes.py     # Echoes & Home art: Lark/Maud/Vesper, Keepers, Glim, Edda, keepsakes, props
python audio_echoes.py     # Echoes & Home music, ambience, sfx and voices
python make_maps.py hearth   # regenerate one map (overwrites levels/hearth.txt!)
python gifs.py FRAMES OUT.gif  # recorded frames -> a crisp GIF (see "GIFs" below)
python scarf_gif.py ../media/gifs/00_the_scarf.gif   # the scarf burning shorter, from the hero sheets
```

Previews go to `art_src/_preview/`. After regenerating, run Godot once with
`--import` (or open the editor) so new files are imported.

## Debug flags

Pass these after `--` to jump around and take automated screenshots
(debug runs use a separate save file, so they never touch your real save):

```
Godot.exe --path . -- --skip-intro --level=glimmerdeep --door=1 --embers=3 --frames=60 --shot=C:/tmp/shot.png
```

`--level=ID`, `--door=ID`, `--warp=X,Y` (tile coordinates), `--embers=N`, `--given=N`,
`--flags=a,b,c`, `--hold=move_right[@frame]`, `--press=interact@40,flare@90`,
`--dialogue=ID`, `--shot=PATH` with `--frames=N`, `--skip-intro`, `--trace=N` (print the player's
position every N frames), `--key=Q@50` (press a real key, for testing rebinding), `--pad` (show
gamepad prompts), `--window` (apply the window settings, which debug runs otherwise skip),
`--sfxlog` (print every sound effect, marking the ones played during dialogue).
Debug runs also keep their own `debug_settings.cfg`. Frames are rendered frames, which can run
slower than the 60 Hz physics, so use `--trace` to time presses instead of guessing.

## GIFs

`media/gifs/` holds GIFs of the game's best moments, for store pages and posts (960x540;
`media/gifs/small/` has 480x270 copies for sites with upload limits). To film a new one, record
frames with a fixed frame rate (then frame numbers are exact game time: 60 per second), and turn
them into a GIF:

```
Godot.exe --path . --fixed-fps 60 --resolution 480x270 -- --skip-intro --level=starwell
    --warp=58,18 --flags=orrery_lit --hold=move_left@40 --record=C:/tmp/sw --from=20 --every=3 --frames=260
cd art_src
python gifs.py C:/tmp/sw ../media/gifs/starwell.gif --fps 20 --scale 2
```

`--record=DIR` saves every `--every`-th frame from `--from` up to `--frames`, then quits.
`gifs.py` takes `--skip`/`--take` to trim, `--hold` to linger on the last frame, and `--check`
to verify the result. It shares one palette across frames and stores unchanged pixels as
transparent, so still shots stay small. Clips with a moving camera or the Echoes' film grain
run larger (up to about 10 MB).
