class_name StoryEchoes
## The three Echoes: memories you play by laying a keepsake in the Little Hearth.
## I. Lark's Song (one age ago)  II. The Last Winter (the night of the flood)
## III. Vesper (the first wick, just before it). Flags inside an Echo start with
## its id ("lark:", "maud:", "vesper:") and are forgotten when it is replayed.

const LINES := {
	# --- keepsakes ---------------------------------------------------------------
	"keepsake_lantern": [
		{"who": "", "text": "An old lantern, the same shape as yours. Cold right through. It has been waiting here, where it went out."},
		{"who": "", "text": "(A keepsake. Lay it in the Little Hearth in Old Hollow, and the fire will show you what it remembers.)"},
	],
	"keepsake_bell": [
		{"who": "", "text": "A brass handbell, green from the water. When you lift it, it doesn't ring. It holds its breath."},
		{"who": "", "text": "(A keepsake. Lay it in the Little Hearth in Old Hollow, and the fire will show you what it remembers.)"},
	],
	"keepsake_page": [
		{"who": "", "text": "A small slate, worn nearly smooth. Somebody carved it by hand, a long time ago, and pressed very hard."},
		{"who": "", "text": "(A keepsake. Lay it in the Little Hearth in Old Hollow, and the fire will show you what it remembers.)"},
	],

	# --- I. Lark's Song ------------------------------------------------------------
	"echo_lark_start": [
		{"who": "", "text": "The lantern is warm in your hands. Full. It has never been so full."},
		{"who": "Lark", "text": "Right. Down, then. All the way down. How hard can it be?"},
		{"who": "", "text": "(This is a memory. Lark carries six embers. Share them, and the people you warm will light the way.)"},
	],
	"lark_gate_hint": [
		{"who": "", "text": "A Keeper eye-gate, shut. Its eye-stone is far up on the ledge behind you. It only opens while the stone sees a light."},
		{"who": "Lark", "text": "And I can't be up there and down here at once. Somebody would have to stay by it."},
	],
	"lark_burrow": [
		{"set": "lark:met_burrow"},
		{"who": "Burrow", "text": "Don't mind me. Just a pup. Just sitting. Just very, very cold."},
		{"who": "Burrow", "text": "Ma says stay by the eye-stone till she's back. It opens the gate for her, if somebody keeps it lit."},
		{"who": "Burrow", "text": "I can't keep anything lit. I'm a mole."},
		{"who": "Lark", "text": "Hold your paws out, then.", "choices": [
			{"text": "Give Burrow an ember", "give": "lark_burrow", "goto": "lark_burrow_given"},
			{"text": "Not yet", "goto": "lark_burrow_wait"},
		]},
	],
	"lark_burrow_given": [
		{"who": "Burrow", "text": "Oh! It's warm! It's warm right through my claws!"},
		{"who": "Burrow", "text": "And look, the eye's awake! It likes me! Nothing's ever liked me before. Except Ma."},
		{"who": "Lark", "text": "That's yours now. Keep it."},
		{"who": "Burrow", "text": "I'll keep it forever. I'll dig a hole and keep it in it. Thank you, lantern-person!"},
	],
	"lark_burrow_wait": [
		{"who": "Burrow", "text": "That's all right. I'm good at waiting. Moles are mostly waiting."},
	],
	"lark_burrow_after": [
		{"who": "Burrow", "text": "Still warm! I keep checking. Still warm."},
	],
	"lark_shades_hint": [
		{"who": "", "text": "The cold things are thick here, drifting over a frozen pool. They gather where the dark is deepest."},
		{"who": "Lark", "text": "A light that stayed put would keep them off. Mine won't stay. I've somewhere to be."},
	],
	"lark_gudgeon": [
		{"set": "lark:met_gudgeon"},
		{"who": "", "text": "A fish in a shallow pool, half frozen into it. Young, as fish go. Old, as anything else goes."},
		{"who": "Gudgeon", "text": "Mm. Lantern. Do not stop here. The cold things come to this pool to drink. They drink warmth."},
		{"who": "Gudgeon", "text": "I am too slow to leave. Fish have a long while. Not this long, maybe."},
		{"who": "Lark", "text": "Then I'll make it a warm pool.", "choices": [
			{"text": "Give Gudgeon an ember", "give": "lark_gudgeon", "goto": "lark_gudgeon_given"},
			{"text": "Not yet", "goto": "lark_gudgeon_wait"},
		]},
	],
	"lark_gudgeon_given": [
		{"who": "Gudgeon", "text": "Mm... the water is warm. The cold things will not come here now. They do not like to be seen."},
		{"who": "Gudgeon", "text": "I will remember you, lantern. Fish forget most things. Not this."},
	],
	"lark_gudgeon_wait": [
		{"who": "Gudgeon", "text": "Mm. Go carefully, then. They are hungry tonight."},
	],
	"lark_gudgeon_after": [
		{"who": "Gudgeon", "text": "Mm. Warm. Go on, lantern. The way is safe while I am here."},
	],
	"lark_glim": [
		{"set": "lark:met_glim"},
		{"who": "Glim", "text": "Hush, little one, hush. Oh! A lantern. Don't look at me, I'm a fright. I've gone all dim."},
		{"who": "Glim", "text": "I've an egg on the way, you see. Down the old seam it's warm, they say. I'll lay it there, where it won't freeze."},
		{"who": "Glim", "text": "If I can get there. I'm so tired. And it's so dark."},
		{"who": "Lark", "text": "...", "choices": [
			{"text": "Give Glim an ember", "give": "lark_glim", "goto": "lark_glim_given"},
			{"text": "Not yet", "goto": "lark_glim_wait"},
		]},
	],
	"lark_glim_given": [
		{"set": "lark:warmed_glim"},
		{"who": "Glim", "text": "Oh, look at me. Glowing like a girl again!"},
		{"who": "Glim", "text": "I'll go down the seam tonight. And when my little one hatches, I'll tell her about you. The lantern-person who glowed us both home."},
	],
	"lark_glim_wait": [
		{"who": "Glim", "text": "Go on, dear. Don't mind us. We'll manage. We always manage."},
	],
	"lark_glim_after": [
		{"who": "Glim", "text": "Down the old seam I go. Down where it's warm."},
	],
	"lark_dim_hint": [
		{"who": "", "text": "The lantern is lighter than it was. The dark presses a little closer with every step."},
		{"if": "given>=3", "who": "Lark", "text": "Less light. More friends. I've done the sums and I still can't decide which is better."},
		{"if": "!given>=3", "who": "Lark", "text": "Still plenty in here. Plenty to go round."},
	],
	"lark_egg": [
		{"who": "", "text": "At the very bottom of the cave, something small and round, glowing the faintest green. Then not glowing at all."},
		{"who": "Lark", "text": "Oh, little one. Somebody left you here. Somebody meant to come back."},
		{"if": "embers>=1", "who": "", "text": "There is one ember left in the lantern.", "choices": [
			{"text": "Give the last ember", "give": "lark_egg", "set": "lark:egg_warm", "goto": "lark_last"},
		]},
		{"set": "lark:egg_warm", "who": "", "text": "The lantern is nearly cold. There is nothing left in it to give. So Lark gives the egg the last of the lantern's own warmth, the way you'd give someone your coat."},
		{"goto": "lark_last"},
	],
	"lark_last": [
		{"event": "refresh"},
		{"who": "", "text": "The egg stirs. It glows a small, stubborn green. Somewhere inside it, something hiccups."},
		{"who": "Lark", "text": "There. That's better. That's much better."},
		{"event": "lantern_out", "who": "", "text": "Lark sits down beside it, the lantern in their lap, and watches the light inside it shrink to a coal. And then to nothing."},
		{"who": "Lark", "text": "That's all right. That's what it was for."},
		{"who": "Lark", "text": "I'll just rest a bit. Then I'll go on. In a bit."},
		{"wait": 1.5},
		{"card": "Lark's Song", "sub": "Lark never did go on. They called Lark 'Ash', after that.", "hold": 3.5},
		{"event": "echo_end"},
	],
	"after_echo_lark": [
		{"who": "", "text": "The fire gives the lantern back. It is still cold. But it is lighter, somehow, to hold."},
		{"if": "gave_ash", "who": "", "text": "Ash is beside you. You don't know how long they have been watching the flames."},
		{"if": "gave_ash", "who": "Ash", "text": "You saw it. Didn't you. Where it went out."},
		{"if": "!gave_ash", "who": "", "text": "Ash should have this back. They are still down in the Glimmerdeep, by the black water."},
		{"who": "", "text": "And Glim went down the old seam, under the Glimmerdeep, to lay her egg where it was warm. Wisp has been waiting for Mama ever since."},
	],

	# --- II. The Last Winter -------------------------------------------------------
	"echo_maud_start": [
		{"who": "", "text": "Supper is laid in the long hall. The bowls are still warm. Nobody has come up to eat."},
		{"who": "", "text": "Far, far below, something enormous goes quiet. Every lamp in the hall gutters at once."},
		{"who": "Maud", "text": "...That's the Hearth. That's the Hearth gone out."},
		{"who": "", "text": "Then the sound of water. A great deal of water, coming up the stairs."},
		{"who": "Maud", "text": "Right. Everyone home. EVERYONE HOME!"},
		{"who": "", "text": "(This is a memory. Maud has no lantern, only her handbell. Ring it with {key:flare}: the sound lights the halls for a moment, and wakes anyone asleep.)"},
		{"event": "rising_start"},
	],
	"maud_hollis_hint": [
		{"who": "Maud", "text": "Hollis! Asleep at the supper table, with his hat over his eyes. Of course he is."},
	],
	"maud_stair": [
		{"who": "Maud", "text": "The Long Stair. Five of them, up there, asleep at their benches. Hollis, Fitch, Tobin, Pim and Wren. I'm not leaving one."},
	],
	"maud_not_yet": [
		{"who": "Maud", "text": "That's {followers} of them. Not five. Not yet. I'm not leaving one in the water."},
	],
	"maud_door": [
		{"who": "Maud", "text": "Hollis. Fitch. Tobin. Pim. Wren. Everybody through the door! Go on, go on!"},
		{"who": "Fitch", "text": "Where are we going, Maud?"},
		{"who": "Maud", "text": "Up. Out. Right out of the mountain. Find a roof somewhere and build doors under it. Lots of doors."},
		{"who": "Maud", "text": "Right. That's everyone. That's..."},
		{"who": "", "text": "Maud counts again. And again."},
		{"who": "Maud", "text": "...Where's Bell?"},
		{"wait": 1.0},
		{"sfx": "bell_ring", "who": "", "text": "From far below, under the water, very faint: ding... ding... ding..."},
		{"who": "", "text": "Bell. Ringing for supper. Calling everyone home, the way Maud taught her."},
		{"who": "Maud", "text": "Oh, my girl. Oh, my brave girl. You're calling us home."},
		{"who": "Maud", "text": "Go on, all of you. Don't wait for me. I'm going to fetch my daughter."},
		{"who": "", "text": "Maud goes back down the Long Stair, into the black water, ringing her bell so Bell will know she is coming."},
		{"card": "The Last Winter", "sub": "Maud did not come back up. Neither did Bell. But everyone else did.", "hold": 3.5},
		{"event": "echo_end"},
	],
	"after_echo_maud": [
		{"who": "", "text": "The fire gives the handbell back. It is cold from the water, and then, slowly, it isn't."},
		{"who": "", "text": "Five Keepers climbed out of the mountain that night. They found a fallen tree with a hollow under its roots, and they built doors. Forty of them."},
		{"if": "!gave_bell", "who": "", "text": "Bell should have this. She is still down in the Drowned Halls, ringing for supper."},
	],

	# --- III. Vesper ---------------------------------------------------------------
	"echo_vesper_start": [
		{"who": "", "text": "Warm. The whole mountain is warm. Lamps hang along every root, and somewhere a hundred chisels are tapping."},
		{"who": "Edda", "text": "There you are, little wick! Up early. Or late. It's always the same o'clock down here."},
		{"who": "Edda", "text": "I'm to walk you as far as the last gate. The rest is yours. That's how it's done. Well. That's how we think it's done. You're the first."},
		{"who": "Vesper", "text": "...Is it far?"},
		{"who": "Edda", "text": "All the way down. Don't fret. Everybody's cheering for you. Listen!"},
		{"who": "", "text": "(This is a memory. The deeper Vesper goes, the more afraid. Company helps.)"},
	],
	"v_hollis": [
		{"who": "Hollis", "text": "The bees are buzzing for you, wick! Well. They're buzzing. I've decided it's for you."},
	],
	"v_hollis_after": [
		{"who": "Hollis", "text": "Wick? Wick, where's the warm gone? The bees have all gone quiet."},
	],
	"v_tobin": [
		{"who": "Tobin", "text": "I mended your lantern-ring myself. It won't squeak. Nothing I mend squeaks. Off you go."},
	],
	"v_tobin_after": [
		{"who": "Tobin", "text": "Everything's gone cold. I can't mend this. I don't know how to mend this."},
	],
	"v_wren": [
		{"who": "Wren", "text": "I made you a song! It goes: down, down, down, warm, warm, warm. It's not finished. You can finish it."},
	],
	"v_wren_after": [
		{"who": "Wren", "text": "...I can't remember how the song went."},
	],
	"v_pim": [
		{"who": "Pim", "text": "I swept the whole way down for you. Mind the bottom step. It's always dusty. Everything ends dusty."},
	],
	"v_pim_after": [
		{"who": "Pim", "text": "Why's the floor wet? Why is the floor WET?"},
	],
	"v_maud": [
		{"who": "Maud", "text": "Look at you. Have you eaten? You haven't eaten. Nobody walks down a mountain on an empty stomach."},
		{"who": "Maud", "text": "Bell's made you a supper for after. She's very proud of it. It's mostly bread."},
	],
	"v_maud_after": [
		{"who": "Maud", "text": "Run, little wick. Don't stop. I've got to find my Bell."},
	],
	"vesper_gate": [
		{"who": "Edda", "text": "Well. Here's the last gate. This is as far as I'm allowed, little wick."},
		{"who": "Vesper", "text": "...Can't you come a little further?"},
		{"who": "Edda", "text": "I'd go all the way if I could. But the Hearth only takes a wick. The rest of us would just... burn."},
		{"who": "Edda", "text": "I'll be right here. I'll wait. When it's lit, I'll feel it in the stone."},
		{"event": "stay:edda"},
	],
	"vesper_hearth": [
		{"who": "", "text": "The Hearth. It fills the whole cavern, white at its heart, roaring like a held breath let go."},
		{"who": "", "text": "Beside it, the Cradle, shaped exactly like a wick. Shaped exactly like Vesper."},
		{"who": "Vesper", "text": "It's so big."},
		{"who": "", "text": "Vesper takes one step. Another. And cannot take the third.", "choices": [
			{"text": "Step in", "locked": true},
			{"text": "Turn back", "goto": "vesper_turns"},
		]},
	],
	"vesper_turns": [
		{"set": "vesper:fear_off"},
		{"who": "Vesper", "text": "I can't. I can't. I'm sorry. I can't."},
		{"who": "", "text": "Vesper turns round. Behind them the Hearth sighs, very softly, like someone who has waited a long time and must now wait longer."},
		{"event": "hearth_gutter", "music": "echo_vesper_dark"},
		{"wait": 2.0},
		{"event": "darken", "who": "", "text": "Every lamp in the mountain goes out at once. And from below, where the Hearth was, the cold comes up."},
		{"event": "rising_start", "who": "", "text": "Run."},
	],
	"vesper_end": [
		{"who": "Edda", "text": "Vesper? Vesper! What happened? The stone's gone cold. The whole mountain's gone cold."},
		{"who": "Vesper", "text": "I was afraid."},
		{"who": "", "text": "The dark that followed Vesper up the stairs does not stop at the gate. It gathers round them, soft as a cloak. And it stays."},
		{"event": "become_hollow"},
		{"wait": 3.0},
		{"who": "The Hollow One", "text": "...I was afraid."},
		{"who": "Edda", "text": "Oh, little wick. It was too much. It was too much to ask of just one."},
		{"sfx": "carve", "who": "", "text": "That night, by the light of nothing at all, Edda carves a page for the Book of Wicks. The very first page."},
		{"card": "ONE FLAME ALONE BURNS OUT", "sub": "Many flames together burn on. No wick should walk down alone.", "hold": 4.0},
		{"card": "Vesper", "sub": "The first wick. The first cold. The first page.", "hold": 3.0},
		{"event": "echo_end"},
	],
	"after_echo_vesper": [
		{"who": "", "text": "The fire gives the page back. The carving is worn almost smooth, but you can still read it."},
		{"who": "", "text": "NO WICK SHOULD WALK DOWN ALONE."},
		{"if": "!ending_many", "who": "", "text": "Somewhere far below, at the bottom of the roots, the Hollow One is waiting. It has been waiting a very long time."},
		{"if": "ending_many,gave_hollow_one", "who": "", "text": "At the edge of the firelight, where it always sits, the Hollow One has turned its head. It is looking at the page."},
	],
	"hollow_one_vesper": [
		{"set": "hollow_heard_vesper"},
		{"who": "The Hollow One", "text": "...You have Edda's page. You have been to the fire. You saw."},
		{"who": "The Hollow One", "text": "Then you know there is nothing to forgive. I was afraid. That is all. That is all it ever is."},
		{"if": "!ending_many", "who": "The Hollow One", "text": "Keep the page, little wick. Read it at the bottom. I never did."},
		{"if": "ending_many", "who": "The Hollow One", "text": "Keep the page, little wick. I read it a very long time ago, and I did not listen. I am listening now."},
		{"if": "ending_many,echo_lark,echo_maud", "goto": "hollow_one_walk"},
	],
}
