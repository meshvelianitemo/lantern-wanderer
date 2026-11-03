# Lantern Wanderer: Design Bible

The decisions we made together, plus the plan for every campaign still to come.
If a new idea fits these pages, it belongs in the game. If it fights them, it doesn't.

---

## 1. The soul

> A small hooded wanderer carries the last ember down into the mountain to
> rekindle the dying Hearth, and slowly learns that the wick is them.

**Four pillars**

1. **Light is the only verb.** No combat, no weapons, no health bar. Everything you
   do is carrying, sharing or shining light. Danger comes from darkness and from falling.
2. **Warmth is shared, not spent.** Embers make your lantern bigger and safer. People
   you meet need them too. Giving makes your road darker and someone else's life warmer.
   The game never says which is right.
3. **Quiet, kind, a little sad.** Short lines, like fables. Silence (`...`) is always a
   valid answer. Nobody is evil, only cold.
4. **The wick burns.** Mossback calls you "little wick" from the very first scene. It is
   a pet name, and it is also the truth. Every chapter hints at it a little more.
   Nobody says it out loud until the very end.

**Writing rules**

- A line fits the dialogue box: about 110 characters at most.
- The hero never speaks, only chooses. Every big moment offers a `...` choice.
- Every important NPC has **one line about wicks or burning** that means more on a second playthrough.
- No modern slang, no jokes that break the world. Humour comes from character
  (Pell the moth, Burrow the mole), never from winking at the player.

**Visual motif:** the hero's **orange scarf is the wick**. In later chapters the
scarf gets a little shorter each time (planned: one hero sprite variant per chapter).

---

## 2. The shape of the world

All three structures combined:

```
                         OLD HOLLOW  (hub village)
                        /    |    \
           Mossgrave Woods   |     the Hollow fills with everyone you warmed
                  |          |
     ======== THE DESCENT (chapters, played in order) ==========
                  |          |
   Ch II   The Glimmerdeep --+  <- Wickway lift back up to the Hollow
                  |          |
   Ch III  The Drowned Halls-+  <- Wickway
                  |          |
   Ch IV   The Rootdark -----+  <- Wickway
                  |
   Ch V    THE HEARTH
```

- **Descent chapters:** the backbone of the game. Each chapter is a deeper region
  with its own mood, palette, mechanic and cast.
- **Hub:** **Old Hollow**, west of Mossgrave. NPCs you share an ember with move
  there. Its hanging lamps light up one by one and huts glow again. The hub is a
  visible record of your kindness.
- **Connected world:** each chapter ends at a **Wickway**, an old Keeper
  lantern-lift. Light it from below and it links that depth to the Hollow forever.
  Each chapter also brings a new **lantern gift** that opens sealed paths in
  earlier areas (optional NPCs, embers, lore).

---

## 3. Systems

| System | Rule |
|---|---|
| **Embers** | Collect to grow your light radius (+12% each, capped). Your total is in the top-left. |
| **Sharing** | NPCs in need can be offered an ember. It is gone from your lantern for good, and they are warmed (`gave_<npc>` flag, `Game.embers_given`). |
| **Shades** | Cold that remembers being warm. They drift toward you in the dark and dissolve while inside your light. A strong shade can reach you if your light is small. A touch knocks an ember loose (catch it before it fades). If you have no embers left, it sends you back to your shrine. |
| **Glimmer** | Crystal that drinks light. Solid only while your lantern touches it, and it remembers the light for a moment after. **Violet glimmer** only wakes for a strong flame (3+ embers). It always guards *optional* places, never the main path. |
| **Shrines** | Light once: checkpoint + save. |
| **Wickways** | Light from below, then ride between that depth and Old Hollow. |
| **Hook** *(gift, Ch III)* | Leave your flame burning on a Keeper hook. It lights everything around it as your lantern would, while you walk on in the dark with only a spark (and Pell, who stays with the light). Falling or getting caught brings it back to you. |
| **Eye-gates** | A carved eye on a stone door: hold light on it and it opens for good. Gates with separate **eye-stones** are open only *while* their stone is lit, so you need the Hook. Once you walk through, they remember. |
| **Flare** *(gift, Ch IV)* | Push your light out in one burst: burns thorn-roots, scatters shades. No cost, just a 3-second breath. Light is a push, never a weapon. |
| **Shadow-play** *(the Starwell)* | Tin plates the Keepers used to teach the constellations. A **still** light (a flame on a hook, a lit star-lamp, an orrery sun) throws a plate's shadow onto the dusk-glass, twice its size and mirrored away from the light (`S = 2C - L`), and the shadow is solid to stand on. Your carried lantern trembles, so it only throws a faint, shivering hint of where the shadow would fall. |
| **Star-lamps** | Light once with any flame (even the spark you keep while your flame hangs on a hook). They burn for good, so their shadows are permanent paths. |
| **Orrery suns** | Light one and it rides its brass rail back and forth forever. Its shadows sweep the other way: moving bridges and shadow lifts. |
| **Name-stones** | Every Keeper's name was carved on a stone and dropped down the Starwell. The flood scattered ten of them through the mountain. Each one you find goes in the Journal and becomes a gold star when the Great Orrery turns. Optional; Bell and Orrin notice. |
| **Journal** | Tab / Select, or from the pause menu: places (with Pell's opinion), people (and who you shared with), every tablet you've read, and the Keeper names. Unfound entries show as `???`. |
| **Cold water** | Black water sends you back to your last light. Shallow water (the Hollow's well) is just for wading. |
| **Saving** | Automatic: on lighting a shrine, resting at the Little Hearth, and every time you arrive in an area. |

**The core tension:** a big flame keeps shades away and wakes violet glimmer (secrets).
A small flame means you gave it to people who needed it. That choice matters at the end.

---

## 4. Chapters

Every chapter below is **built and playable**.

### Ch I: Mossgrave Woods
Dusk forest. The totem **Mossback**, first embers, first shrine, the broken bridge,
the cave mouth. West exit to Old Hollow. Mossback has new things to say each time you
come back from a deeper chapter.

### Hub: Old Hollow
A village sheltered under the roots of one enormous fallen tree. It had forty doors
once; now it is cold and nearly empty.
- **Nan Tallow** asks for your first ember to relight the **Little Hearth**
  (a checkpoint that burns brighter with every ember you ever share).
- **Pell** the moth joins you here and follows your light for the rest of the game.
- **Eight hanging lamps** light up, two for every ember you share. **Huts** glow once
  someone lives in them. The whole Hollow's light warms as it fills.
- **Three Wickways** on the west ledge, one for each depth.
- A **thorn-sealed barrow** outside (needs the Flare) hides a Keeper tablet and an ember.

### Ch II: The Glimmerdeep
Crystal caves. Blue-grey stone that gets darker the deeper you go.
- First **glimmer** bridge, the **Glimmer Gallery** chasm, an optional **violet** route
  to an ember cache, the first **shades**, a strong shade guarding a side tunnel.
- **Burrow** (the blind mole explains glimmer), **Wisp** (asks for an ember),
  **Ash** (asks, barely), **Old Gudgeon** (the ferry down to Chapter III).
- Keeper tablets: *"EACH AGE, A WICK"* and *"not everyone comes back. - L."*

### Ch III: The Drowned Halls
The flooded ruins of the Keepers. Masonry, black water, drowned lights.
- **Bell**, a ghost child ringing for supper (asks for an ember).
- **The Archivist** shows the **Book of Wicks** (and learns Lark is alive, if you met
  Ash), writes your line, and gives the **Hook**.
- The first **hook puzzle**: hang your flame by an eye-stone, cross a glimmer bridge
  it keeps lit, walk the dark to the gate.
- **The cistern**: platforms over black water. Old Gudgeon, cold now, asks for an ember.
- Wickway III, and the last eye-gate down to the roots.

### Side chapter: Under the Lake (The Starwell)
Optional, between III and IV, and a reward for kindness: only a **warmed** Old Gudgeon can
dive. He carries you to a Keeper observatory on the lake floor, sealed in a held breath of
air. Pale stone, brass, dark blue glass, lantern-fish outside the windows.
- **Orrin**, the Keepers' star-counter, asleep by his telescope since the winter the water
  rose. Your light wakes him. He teaches shadow-play and asks you to light the Great Orrery.
- The climb: a star-lamp step (the lesson), a hook bridge over black water with a star-lamp
  on the far side to come back by, the **Orrery Hall** (a sun on a rail sweeps a bridge of
  shadows across a pit; an ember hangs above it), and **the Well** (two upright orrery suns
  whose shadows are lifts).
- **The Great Orrery**: light it and the whole dome fills with stars, the darkness lifts, the
  music turns. Gold stars for every Keeper name you have found. Then down to Orrin, who sees
  the sky again and asks for an ember so he can see the real one. Warmed, he moves to Old
  Hollow and sits on the barrow with his telescope.
- Three name-stones here: Agathe, Corran, and Orrin's own.

### Ch IV: The Rootdark
The forest's roots, all the way down. Violet fungus on black. The darkest place.
- **Sprig**, a seedling under a crack where the sun once fell (asks for an ember).
- **The Root-Mother** reveals she carried you up as the Hearth's last spark, recites
  the Keepers' lost first page, and gives the **Flare**.
- Thorn passage, a hidden tablet (the first page, carved), then a long corridor
  where **every shade wakes at once** (the chase music plays).
- **The Hollow One** waits at the bottom. You can offer even it an ember.
- Wickway IV, and the stair to the Hearth.

### Ch V: The Hearth
A bronze bridge between giant stone Keepers, over nothing. The great Hearth, cold,
with the **Cradle** at its heart, shaped exactly like you.

---

## 5. Endings: "The wick burns"

At the Cradle you choose: **step in**, **turn back**, or **wait** (`...`).

| Ending | When | What happens |
|---|---|---|
| **The Long Dark** | You turn back | The Hearth goes out. The snow doesn't melt. Somewhere in the dark a new shade drifts, with a ragged scarf. |
| **The Last Wick** | You step in, having shared with **fewer than 4** | You burn alone. The forest breathes; in spring they hang your empty lantern on Mossback's branch, and one night a new light glows inside it: *"...Hm? A light."* |
| **Many Hands** | You step in, having shared with **4 or more** | Everyone you warmed walks down the bridge and gives your ember back, grown. The Hearth catches from many hands. You burn low, but not out, and wake in Old Hollow at morning with everyone there. Rest at the Little Hearth to end. |
| **The First Page** | Many Hands, plus all three Echoes seen and the Hollow One warmed | The Hollow One walks on into the Cradle beside you and becomes Vesper again. Two wicks: each scarf burns only halfway. Everyone wakes at supper, Vesper by the fire (see 7d). |

Eight characters can ask for an ember: **Tallow, Wisp, Ash, Bell, Gudgeon, Orrin (Starwell),
Sprig, the Hollow One**. There are 16+ embers in the world. You can't keep a big flame *and*
help everyone, and shades steal from small flames. That's the whole game.

Thesis line (Nan Tallow): *"Warmth never really leaves. It just moves house."*
The Keepers' first page: *"Fire only catches from fire. One flame alone burns out. Many flames together burn on."*

---

## 6. Cast

| Who | Where | Wants | Line that matters more the second time |
|---|---|---|---|
| **Mossback**, ancient totem | Mossgrave | To see the Hearth lit before he sleeps | *"I called that one 'little wick' too."* |
| **Nan Tallow**, old candle-woman | Old Hollow | Her Little Hearth lit again | *"We burn the same way, dear. From the top down."* |
| **Pell**, a moth | Hollow, then follows you | To be near the light | *"My entire life plan is flying into fire."* |
| **Burrow**, blind mole miner | Glimmerdeep | Nothing. Moles dig | *"Bigger the flame, further it reaches. So mind how much of it you give away."* |
| **Wisp**, lost glowworm | Glimmerdeep, then the Hollow | Her glow back, and her mama | *"If your glow goes out, you just need a little bit of somebody else's."* |
| **Ash** (once **Lark**), the Grey Wanderer | Glimmerdeep, then the Hollow | Nothing they'd ask for. The wick before you | *"Don't give it all away. And don't keep it all, either."* |
| **Old Gudgeon**, blind ferry-fish | Glimmerdeep and Drowned, then the Hollow's well | To be warm once more | *"Fish have a long while. Fish have nothing else."* |
| **Bell**, Keeper ghost child | Drowned, then the Hollow | Someone to come home for supper | *"Even ghosts get cold. Nobody tells you that."* |
| **The Archivist**, last Keeper ghost | Drowned | To remember every wick | *"Somebody has to remember who it ate."* |
| **Orrin**, Keeper star-counter | Starwell, then the Hollow's barrow | To see the sky once more | *"Lanterns, very far away, that nobody has to carry."* |
| **Sprig**, a seedling | Rootdark, then a tree in the Hollow | The sun | *"Slowly is still growing."* |
| **The Root-Mother**, the forest's root-heart | Rootdark | To carry warmth up, as always | *"I carried you, little wick."* |
| **The Hollow One** (once **Vesper**) | Rootdark | For you not to burn | *"I would rather be this than ash. Wouldn't you?"* |

---

## 6b. Lore codex

**The Hearth.** A fire at the root of the mountain. Its warmth rises through stone
and root; that is what "the forest breathing" means. Seasons turn because it burns.

**The Keepers.** A small, quiet, lantern-carrying people who lived inside the
mountain and tended the Hearth. They built the halls, the shrines (fire-bowls to carry
flame down safely), the Wickways, the hooks and the eye-gates, and they carved
everything they learned onto tablets. They discovered that the Hearth burns down
once an age and can only be rekindled by a **wick**: a living flame that gives
itself to it. *Fire only catches from fire.*

**Vesper, the first wick.** The first wick walked all the way down, looked at the
Hearth, was afraid, and turned back. That winter the Hearth went cold, the deep ice
melted, and the water rose and drowned the Keepers' halls. The cold that was left
gathered around Vesper and became **the Hollow One**.

**Shades.** Every flame that ever went out leaves a little cold behind that
remembers being warm. Those are shades. They creep toward light because they miss it.
Light thins them back into nothing. In Many Hands, the Hollow One brings its ember
back too: even the dark can carry warmth.

**The Book of Wicks.** After the flood, the Archivist stayed awake to remember every
wick by name: *Fenn, who sang. Ilse, who limped. Tamsin, who was afraid, and went
anyway. Oriel. Bram. Little Coll...* The book's **first page** (the warning that
no wick should burn alone) was lost to the water, and later wicks forgot it. The
Root-Mother still remembers it, and there is one carved copy in the Rootdark behind
the thorns.

**How a wick is born.** When the Hearth flickers, a spark leaps loose. The
Root-Mother carries it up through her roots (nine nights, for the last one) to the moss
of Mossgrave, where Mossback holds it until it wakes as a small hooded someone holding
a lantern. The Keepers carved Mossback to wait there and wake each wick.

**Lark, now Ash.** The wick before you. Lark gave embers to everyone they met, and
their lantern went out in the Glimmerdeep before they reached the Hearth. That is
why this age has run so long and so cold. The Archivist's book says Lark is gone;
if you met Ash, you can tell the Archivist otherwise, and later tell Ash their old name.

**The Starwell.** One straight shaft the Keepers bored from the top of the mountain to
the bottom of the lake, so that starlight could reach them in the dark. Their observatory
sat at the bottom, and survived the flood as a bubble of air under the water. They taught
their children the constellations with shadow-play (the Boat, the Fish, the Moth...) and
carved every Keeper's name on a stone dropped down the well to sit beneath their star.
Orrin's tablet holds his own theory: *the Hearth is a star that fell, and the well was built
so it could see its sisters.* Nobody has confirmed it. Nobody has disproved it either.

**The Keeper names.** Hollis, who kept the bees. Fitch, who was always late, and came
anyway. Tobin, who mended lanterns. Pim, who swept the Wickways. Maud, who called everyone
home for supper (Bell's mama). Wren, who sang on the stairs. Agathe, who taught the
shadow-plays. Corran, who fell asleep in every lesson. Orrin, who counted the stars. Edda,
who carved the first page.

**The scarf.** The hero's orange scarf is their wick. It is full in Chapters I–II,
singed shorter from the Drowned Halls on, and a glowing stub at the Hearth.
Every wick has one: Lark's is rose and burns shorter with each ember Lark gives away in
their Echo; Vesper's is long and gold. In The First Page two wicks share the Hearth, so
both scarves burn only halfway, and the hero wakes with the half-burnt scarf.

---

## 6c. Campaigns to make next

The main story is complete. Possible next campaigns, each about one chapter's worth of work:

1. **The Forty Doors** (post-game, hub): after Many Hands, the Hollow's empty doors
   open one by one. Bring back the forest folk who fled the cold, each a small
   Mossgrave errand. A "home" campaign with no shades at all.
2. **Lark's Song** (prequel): play as Lark, the wick before you, from waking to
   the Glimmerdeep. You already know how it ends; the game is about who they helped.
3. **The Keepers' Last Winter** (prequel, the Drowned Halls before the flood): play
   as Bell's mother, ringing everyone up the stairs as the water rises. A timed escape, no combat.
4. **Vesper** (the darkest one): the very first wick's walk down, and the moment they
   turned back. Short, sad, optional; unlocked by the Long Dark ending.
5. ~~**Under the Lake**~~: built, as the Starwell (see Chapters), with shadow-play instead
   of the swimming-light idea.
6. **Burrow's Deep Seam** (side chapter): Burrow's tunnels below the Glimmerdeep,
   where glimmer runs so deep it sings whole songs. Light-rhythm puzzles.
7. ~~**Lark's Song**, **The Keepers' Last Winter**, **Vesper**~~: built as the three Echoes, and
   ~~**The Forty Doors**~~ grew into "Old Hollow comes alive" (see section 7).

---

## 7. Echoes & Home (the expansion)

**Built and playable.** Two ideas, woven through the main journey, that make the game deeper
rather than longer.

**Echoes.** *Embers remember.* Some things the wicks and Keepers left behind still hold a
memory. Lay one of these **keepsakes** in the Little Hearth and the fire shows it to you, and
you play it: a short chapter in a familiar place at another time, as someone else, with one
rule that changes what light means. The three Echoes go **backwards in time**, each one
closer to why the Hearth is dying. Each is about 5 to 10 minutes long.

**Home.** Old Hollow stops being a waiting room. Everyone you warm gets a story that keeps
moving each time you come home. People eat supper together and talk to *each other*. They
help you in return, and the Hollow visibly fills up.

Each Echo is someone in the Hollow's story, so the two halves feed each other: residents send
you to find keepsakes, and Echoes change what residents say, and who comes home.

### 7a. Keepsakes and the Little Hearth

| Keepsake | Where | Who points you to it | Echo |
|---|---|---|---|
| **Lark's lantern** (cold) | Glimmerdeep: a violet-glimmer nook above Ash's chamber, where it went out | Ash (*"I left it where it went out. I couldn't carry it cold."*) | I. Lark's Song |
| **Maud's handbell** | Drowned Halls: the sunk supper hall, behind an eye-gate (needs the Hook) | Bell (*"Mama's handbell. She rang it so everyone came home."*) | II. The Last Winter |
| **The first page** | Rootdark: the Root-Mother kept it when it fell through her roots in the flood | The Root-Mother hands it over right after she teaches you the Flare | III. Vesper |

- At the lit Little Hearth, a keepsake you carry adds a choice: *Lay Lark's lantern in the fire.*
  The screen goes warm and grainy (the **memory filter**) and the Echo begins.
- In an Echo your own embers, gifts and Pell are left behind; the Echo has its own.
  Quitting mid-Echo puts you back at the Little Hearth. Finishing it brings you back there too,
  and the keepsake goes to its owner (lantern to Ash, bell to Bell, page to the Hollow One).
- Played Echoes can be replayed from the Little Hearth (*Remember again*).
- The Journal gets a fifth page, **Echoes**: keepsakes found, memories seen.

### 7b. The three Echoes

**I. Lark's Song** *(one age ago; the Glimmerdeep, younger and fuller of crystal)*
- **You are Lark**, the wick before you (later Ash), with a big lantern of 6 embers.
- **Rule: sharing lights the way.** Cold people sit along the path. Warm one and they become
  a light of their own, for good: their light holds eye-gates open, keeps shade nests safe
  and wakes glimmer near them. Every gift shrinks *your* light, so shades get bolder.
  You progress *because* you give, and get smaller doing it.
- **Who Lark warmed:** a young **Burrow** (who sits by an eye-stone), young **Old Gudgeon**
  in a cold pool (whose glow clears a shade nest), and **Glim**, a glow-grub with an egg
  (Wisp's mama). Glim is optional; warmed, she goes *down the old seam* to find warmth for her egg.
- **The end:** Lark's light is a stub. In the last dark cave Lark gives the last ember to a
  shivering egg-shaped glow, sits down, and the lantern goes cold. *"That's all right. That's
  what it was for."* (The egg was Wisp.)
- **After:** Ash gets the lantern back and tends the fire better (*"a little at a time"*).
  Burrow and Gudgeon remember the lantern-person. Wisp asks where Mama went, and the old
  seam opens in the Glimmerdeep: **find Glim**, still alive, cold, deep down. Warm her and she
  comes home to Wisp.

**II. The Last Winter** *(the night of the flood; the Drowned Halls, dry and lamp-lit)*
- **You are Maud**, Bell's mother, who called everyone home for supper. No lantern: the Hearth
  has just gone out, and the halls' lamps die one by one.
- **Rule: the bell.** Ring Maud's handbell (the Flare key) and a ring of sound goes out that
  lights the halls for a moment, and wakes anyone sleeping nearby.
- **The water rises** from the bottom, steadily. Landings are checkpoints. If it catches you,
  you go back to the last landing and the water drops back below it.
- **Call everyone home:** five Keepers are asleep in side rooms on the way up the Long Stair:
  Hollis, Fitch, Tobin, Pim and Wren (the name-stones you found). Ring near them and they wake
  and follow you in a line. Maud won't go through the top door without all of them.
- **The end:** at the top Maud counts heads. Everyone is there. Except Bell. From far below,
  faint: *ding... ding...* Bell is ringing for supper, calling everyone home, the way Maud
  taught her. *"Oh, my girl."* Maud goes back down into the water. The five Keepers who lived
  went up and out of the mountain and built a village under a fallen tree, with forty doors.
- **After:** give Bell the handbell. *"She came back for me. She did come."* Bell stops
  waiting; she rings Maud's bell for supper in the Hollow (a bell post appears). Tallow
  learns who built the Hollow, and why there are forty doors.

**III. Vesper** *(before the first cold; the Rootway, warm and busy with Keepers)*
- **You are Vesper**, the very first wick, walking down to the Hearth through a mountain that
  is warm and full of people cheering you on.
- **Rule: fear.** The deeper Vesper goes, the more afraid: the screen closes in at the edges,
  Vesper walks slower, and the dark starts whispering. Talking to Keepers on the way, and
  having **Edda** (the carver) walk beside you, holds the fear back. Edda has to stop at
  the last gate: *"This is as far as I'm allowed, little wick."*
- **The Hearth:** Vesper reaches it. The choice appears: *Step in* is there, but greyed out and
  can't be chosen. Only *Turn back* works. You feel why.
- **The cold:** the Hearth gutters. Darkness rises behind you, and you run back up through the
  Rootway as the lamps go out. If the dark catches you, you go back to the last landing.
- **The end:** Edda is waiting at the top. *"Vesper? What happened?"* The dark that followed
  Vesper up gathers around them, and the Hollow One stands where Vesper stood. Edda carves the
  first page: ONE FLAME ALONE BURNS OUT. MANY FLAMES TOGETHER BURN ON. NO WICK SHOULD WALK DOWN ALONE.
- **After:** the page goes to the Hollow One. It knows that you know.

### 7c. Old Hollow comes alive

- **Supper.** Once three or more people live in the Hollow, resting at the Little Hearth
  can start a supper (Bell rings for it once she lives there). Everyone gathers and talks to
  each other. Each supper scene plays once, in order of the story: after Chapter II, after
  Chapter III, after each Echo, when Glim comes home, before the Hearth.
- **Threads.** Every resident has new lines that move with the story and the Echoes (Ash and
  the lantern, Bell and her mama, Wisp waiting for Glim, Orrin and the sky, Gudgeon and the
  lantern-person he remembers, Tallow and the forty doors, Sprig growing).
- **Help in return.**
  - **Orrin's telescope:** he looks for name-stones for you; the Journal then says which area
    each missing one is in.
  - **Gudgeon's ferry:** from the Hollow's well he'll swim you to the Drowned Halls or the
    Starwell (once you've been).
  - **Bell's bell:** after Echo II, Maud's bell hangs on a post by the hearth, and Bell rings
    both bells to call every supper.
- **The Hollow fills up:** with 3+ residents a supper table appears, with 4+ bunting, with 6+
  the fuller Hollow music plays. Sprig grows taller each chapter. Glim's door glows once
  she's home.
- **Glim** is a new resident (Wisp's mama), found after Echo I.

### 7d. A new ending: The First Page

If you have seen **all three Echoes**, warmed **the Hollow One**, and shared enough for
**Many Hands**, the Hollow One comes to the Hearth last, as before. But this time it stops
beside you at the Cradle. *"I turned back once. Not twice."* The dark burns off it, and
**Vesper** steps into the fire with you. Two wicks: nobody burns alone, and nobody burns out.
The epilogue in the Hollow is the whole village at supper, with Vesper by the fire.

**After an ending.** Nothing is lost by finishing early. Keepsakes can still be found, and
laid in the Little Hearth, after Many Hands (or any ending). Once all three Echoes are seen,
the Hollow One (sitting at the edge of the Hollow's firelight) asks: *"I turned back once,
little wick. I would like not to, this time. Will you walk down with me?"* Saying yes takes
you straight to the Hearth; step into the Cradle again and The First Page plays.

### 7e. Not missing it (from the first playtest)

The first full playthrough found **none** of the keepsakes: each pointer was a second
conversation queued behind another (Ash told you about Lark, Bell read Maud's name-stone),
the Root-Mother never actually handed the page over, and the Little Hearth closed after the
ending. So:
- Pointers come in the conversation you can't miss: Ash mentions the lantern right after you
  tell them they were Lark; Bell asks about the handbell right after reading Maud's name;
  the Root-Mother gives the page as soon as she gives the Flare.
- **Speech bubbles**: a small bubble floats over anyone whose next conversation is new
  (it sets a flag you don't have yet: `Story.is_news`). It hides while the button prompt shows.
- The Journal's Echoes page shows where each keepsake is once you've met who knows.
- Everything above also works after an ending (see 7d).

### 7f. Systems (for building it)

- `@echo <id>` and `@hero <skin>` in a map header make it an Echo: hero sprites
  `hero_<anim>_<skin>.png`, the memory filter, no Pell, its own embers (`@embers N`).
  `Game.start_echo(id)` / `Game.end_echo()` keep the real game safe meanwhile.
- New map kinds: `keepsake <id>`, `landing` (an Echo checkpoint), `sleeper <keeper>` (wakes to
  the bell, then follows), `rising <water|dark> <speed>` (rises, sends you to the last landing),
  `follower <npc>` (walks behind you, like Edda), `headcount <n>` (Maud's door), `old_hearth`,
  `propif <cond> <prop>` (the Hollow filling up); header `@fear <from_row> <to_row>`.
- Every Echo restarts clean when replayed; quitting mid-Echo saves you back at the Little Hearth.
- Suppers play one per rest, in story order; Pell's remarks never interrupt a conversation.
- NPCs can have `"radius"`: once lit they count as a light (glimmer, eye-gates, shades).
- Dialogue choices can be `"locked": true`: shown greyed out, never chosen.
- Story text: `scripts/story/echoes.gd` (Echoes), `scripts/story/home.gd` (supper, threads).

### 7g. Assets

**Art** (`art_src/echoes.py`, palette from `pix.py`):

| File | Size | Frames |
|---|---|---|
| `sprites/hero_{idle,run,jump,fall,land}_lark.png` | 32x32 frames, same layout as `hero_*` | Lark: the wick, dusty slate-blue cloak, rose scarf (full length) |
| `sprites/hero_*_vesper.png` | same | Vesper: pale bone-white cloak, long gold scarf |
| `sprites/hero_*_maud.png` | same | Maud: a small Keeper woman, shawl and apron, a brass handbell held where the lantern would be (frame pixel ~25,26) |
| `sprites/glim.png` | 20x12 frames, 4 | glow-grub mother: 0-1 cold idle, 2-3 lit idle |
| `sprites/edda.png` | 20x28 frames, 8 | old Keeper carver with chisel: 0-1 idle, 2-3 talk, 4-7 walk |
| `sprites/keeper_{hollis,fitch,tobin,pim,wren}.png` | 16x20 frames, 8 | 0-1 asleep, 2-3 awake idle, 4-7 walk; each a different hat/colour (bee veil, late-scarf, mender's apron, broom, songbird) |
| `sprites/keepsake.png` | 16x16 frames, 3 | 0 Lark's cold lantern, 1 Maud's handbell, 2 the first page (slate) |
| `sprites/sapling_tree_2.png`, `sapling_tree_3.png` | 2 frames each, ~40x56 and ~56x76 | Sprig growing (same style as `sapling_tree.png`) |
| `fx/ring.png` | 96x96 | soft white ring for the bell pulse |
| `deco/supper_table.png`, `deco/bunting.png`, `deco/bell_post.png` | ~80x18, ~96x14 (hangs), ~12x34 | the Hollow filling up |
| `deco/keeper_lamp.png`, `deco/lamp_string.png`, `deco/banner.png` | small | the past: lit Keeper halls and the busy Rootway |

**Audio** (`art_src/audio_echoes.py`):

| File | What |
|---|---|
| `music/echo_lark.ogg` | gentle, music-box, an older lullaby version of the Glimmerdeep tune |
| `music/echo_maud.ogg` | urgent but tender, handbell motif, pulse of rising water |
| `music/echo_vesper.ogg` | warm, golden, busy (the mountain alive), then `echo_vesper_dark.ogg` for the chase |
| `music/hollow_full.ogg` | the Hollow theme with more voices (6+ residents) |
| `music/first_page.ogg` | the new ending (plays once) |
| `ambience/flood.ogg`, `ambience/rootway.ogg` | rushing water; warm hum with distant chisels |
| `sfx/bell_ring`, `keeper_wake`, `memory_in`, `memory_out`, `keepsake`, `fear_beat`, `dark_rise`, `carve`, `supper` | wav one-shots |
| `voice/{lark,maud,vesper,edda,keeper,glim}_0..7.wav` | voices in the existing style |

---

## 8. How to add content

- **A new area:** add `levels/<id>.txt` (header lines + ASCII map; legend at the top of
  `scripts/level.gd`). Link it with `@char <c> door <id> <level> <door>` on both sides.
- **A new NPC:** add an entry to `Story.NPCS` (sprite, animations, conditions) and
  their dialogue to `Story.DIALOGUES`, then place them with `@char <c> npc <id>`.
- **Conditions** (`if` on lines/choices, `talks` and `where` on NPCs): `flag`, `!flag`,
  `embers>=N`, `given>=N`, `in:<level>`, comma-separated = all must hold; `a|b` = either.
- **Sharing an ember:** a choice with `"give": "<npc>"` (disabled when you have none).
