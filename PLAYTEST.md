# Playtesting & release checklist

Three parts: how to run a playtest with someone else, a full checklist for your own
end-to-end run, and what's left before a release (itch.io or Steam).

Build first: double-click `export.bat`, then give testers `export/LanternWanderer.exe`.
A new PC starts with no save, which is what you want.

---

## 1. Running a playtest

**Before:** tell the tester only this:

> It's a short adventure game about carrying a lantern. Play however you like.
> Please think out loud: say what you're trying to do and what you expect.
> I won't help, because I need to see where the game fails to explain itself.

**During:** sit behind them, stay quiet, and write down:

| Note | Why |
|---|---|
| The clock time each new area starts | How long each part really is (the title card shows the name) |
| Every time they're stuck for over a minute | The game didn't explain something |
| Every fall into a pit, death to a shade, or retry of a jump | Difficulty spikes, especially the Starwell shadow hops |
| Lines they skip without reading, or read twice | Dialogue that's too long, or unclear |
| Anything they say out loud ("oh, cute", "huh?", "ugh") | How the game actually feels to them |
| Anything broken | Bugs (use the template in part 3) |

Help only if they've been stuck for about 5 minutes, and mark it as **"needed help"**.
That's the most important thing you'll learn.

**After:** ask, and write the answers down word for word:

1. What was the game about?
2. What was your favourite moment? The worst?
3. Where were you confused?
4. Who did you give embers to, and why? (Shows whether the sharing choice landed.)
5. Was it too easy, too hard, or right? Where?
6. Would you pay for this? How much?

One tester tells you a little. Three to five tell you what's real: if two people get stuck in
the same place, it's the game's fault.

---

## 2. Your own end-to-end run

Tick these off across one or more full playthroughs. `play.bat` hides error messages; to see them,
run `C:\Users\Administrator\Godot\Godot_v4.7.2-stable_win64_console.exe --path .` from this folder
and watch the console window for red lines.

### The journey
- [ ] Mossgrave Woods: from the start to Old Hollow and the cave.
- [ ] Old Hollow: Nan Tallow, Pell, the Little Hearth, all three Wickways.
- [ ] The Glimmerdeep: crystals, shades, Burrow, Wisp, Ash, Old Gudgeon.
- [ ] The Drowned Halls: Bell, the Archivist, the **Hook** gift, eye-gates.
- [ ] The Starwell: give Old Gudgeon an ember in the Drowned Halls, then talk to him again.
      Lesson step, hook bridge (and the way back), orrery bridge, both lifts, the Great Orrery, Orrin.
- [ ] The Rootdark: Sprig, the Root-Mother, the **Flare** gift, thorn-roots, the Hollow One.
- [ ] The Hearth: all three endings (keep a save from just before it):
  - [ ] **The Long Dark**: turn back.
  - [ ] **The Last Wick**: step in having shared fewer than 4 embers.
  - [ ] **Many Hands**: step in having shared 4 or more. Everyone you warmed arrives.
  - [ ] **The First Page**: Many Hands with all three Echoes seen and the Hollow One warmed.
- [ ] After each ending the credits roll, then the title screen comes back.

### The Echoes and the Hollow
- [ ] Find Lark's lantern (violet glimmer above Ash's chamber, needs 3 embers), lay it in the
      Little Hearth, play **Lark's Song**. Does warming people feel like it *opens* the way?
      Is it clear the gate needs Burrow? Does Lark's scarf burn shorter with each gift?
- [ ] Find Maud's handbell (Drowned Halls: hang your flame on the hook by the far eye-stone,
      drop down the crack in the library floor). Play **The Last Winter**: is the flood fair,
      too slow, too fast? Can you see enough with only the bell?
- [ ] Get the first page from the Root-Mother (she gives it right after the Flare; on an older
      save, talk to her again). Play **Vesper**: does the fear feel like fear? Does the
      greyed-out "Step in" land?
- [ ] After an ending (keep that save): find a keepsake you missed, lay it in the Little Hearth,
      play its Echo. With all three seen, talk to the Hollow One in the Hollow: "Walk down
      together" should lead to **The First Page**, and you wake with the scarf burnt halfway.
- [ ] Speech bubbles: people with something new to say show a small bubble. Does anyone keep
      one forever after you've talked to them?
- [ ] Quit to title in the middle of an Echo, then Continue: you're back at the Little Hearth.
- [ ] Replay an Echo from the Little Hearth ("Remember again"): it starts fresh.
- [ ] After Lark's Song, find Glim at the bottom of the old seam (the crack between the
      Glimmerdeep's second shrine and Ash's chamber) and bring her home to Wisp.
- [ ] Suppers: rest at the Little Hearth with 3+ people living there. Do they talk like a family?
- [ ] Orrin's telescope (Journal > Names), Gudgeon's ferry from the well, the Journal's Echoes page.

### Things to collect
- [ ] Every ember asker: Tallow, Wisp, Ash, Bell, Gudgeon, Orrin, Sprig, the Hollow One.
      Each one you warm moves to Old Hollow.
- [ ] All 10 Keeper name-stones (Journal > Names counts them). Show them to Orrin.
- [ ] Every tablet (Journal > Tablets).
- [ ] The Journal reads correctly on all four pages.

### Saving
- [ ] Quit to title in the middle of an area, then Continue: you're back where you last saved.
- [ ] Close the game completely and reopen it: Continue still works.
- [ ] New Journey asks first, and "Keep my journey" really keeps it.

### Options
- [ ] Fullscreen on and off (from Options and with F11). Each window size.
- [ ] Music and sound volume, including all the way to zero. They're remembered after a restart.
- [ ] Each text speed, including Instant.
- [ ] Rebind a few keys and play a while with them. Prompts and tutorial cards show the new key.
- [ ] Reset to defaults.
- [ ] Play a whole chapter on a gamepad. Prompts switch to pad buttons, and back when you type.

### Sound (nobody has listened yet)
- [ ] Every area's music, the title music, the Starwell before and after the Orrery, the ending.
- [ ] Every character's voice. Do any grate after a few minutes?
- [ ] Nothing is much louder than the rest.

### Other machines
- [ ] The exported `.exe` on a second PC, ideally an old laptop with a small screen.
- [ ] Alt-tab, unplug the gamepad mid-game, minimise and restore.

---

## 3. Bug report template

```
What happened:
What I expected:
Where (area, roughly where in it):
Can I make it happen again? How:
Keyboard or gamepad:
Screenshot: (Win+Shift+S)
```

---

## 4. Before a release

### Either store
- [x] Your name in `MADE_BY` at the top of `scripts/credits.gd` (Temo Meshveliani).
- [ ] Add playtesters and thanks to the lists below it.
- [ ] Fix what the playtests found, then rebuild with `export.bat`.
- [ ] Final check of the `.exe` on another PC.
- [ ] Decide what to say about AI. The story, art, music and voices were made with Claude.
      Steam requires disclosing that on the store page; itch.io asks too.
      You might also credit it in the game.
- [ ] Screenshots (in-game, at a big window size) and a short trailer (60-90 s).

### itch.io (the easy first step)
- [ ] Upload `LanternWanderer.exe` as a Windows download. Free or pay-what-you-want.
- [ ] Share the page with friends and small communities, and collect feedback.

### Steam
- [ ] Steamworks account: identity, tax and bank details, the $100 app fee.
- [ ] Store page: capsule images in Valve's sizes (the main one is worth paying an artist for),
      5+ screenshots, the trailer, a description, tags, price.
- [ ] Publish the page as "Coming Soon" early, so it collects wishlists. Valve requires it to be
      public for a while before launch, and new developers have a waiting period. Check the
      current rules in the Steamworks docs.
- [ ] Upload the build with SteamPipe (the contents of `export/`).
- [ ] Optional: **Steam Cloud** with Auto-Cloud, pointing it at
      `%APPDATA%/Godot/app_userdata/Lantern Wanderer/` (`save.json`, `settings.cfg`). No code needed.
- [ ] Optional: achievements (needs the GodotSteam plugin), a Steam Deck check, a demo for Next Fest.
