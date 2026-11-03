class_name StoryHearth
## Chapter V: The Hearth, and the three endings.
##   The Long Dark   - you turn back
##   The Last Wick   - you burn alone (shared with fewer than 4)
##   Many Hands      - those you warmed come and give it back (shared with 4+)

const LINES := {
	"hearth_arrive": [
		{"who": "", "text": "The stair ends. Everything ends here, at the bottom of the mountain."},
		{"who": "", "text": "Ahead, between great stone Keepers with their hands raised, something vast and dark sits in the rock. It is very nearly cold."},
	],
	"tablet_hearth_1": [
		{"who": "", "text": "HERE THE KEEPERS SANG THE WICKS HOME."},
	],
	"tablet_hearth_2": [
		{"who": "", "text": "EACH AGE, A WICK. EACH WICK, AN AGE."},
		{"who": "", "text": "Underneath, smaller, newer: 'Fire only catches from fire. Don't forget the first page.'"},
	],

	"hearth_final": [
		{"music": "hearth", "who": "", "text": "The Hearth. Up close it is enormous: a heart of stone and old cinders, and in its centre, a small hollow."},
		{"who": "", "text": "The hollow is shaped like someone very small, in a hood. It is exactly your size."},
		{"if": "pell_follows,!ending_many", "who": "Pell", "text": "Oh. Oh, no. I see what this is. ...I really wish I didn't see what this is."},
		{"if": "vesper_walk,!ending_first_page", "who": "", "text": "Behind you, at the very edge of the light, the Hollow One has stopped on the bridge. It is waiting to see what you do."},
		{"who": "", "text": "Your scarf stirs, though there is no wind. The very end of it is glowing."},
		{"goto": "hearth_choice"},
	],
	"hearth_choice": [
		{"who": "", "text": "The Cradle waits.",
			"choices": [
				{"text": "Step into the Cradle.", "goto": "hearth_step"},
				{"text": "Turn back.", "goto": "hearth_turn"},
				{"text": "...", "goto": "hearth_wait"},
			]},
	],
	"hearth_wait": [
		{"who": "", "text": "You stand at the edge for a long time. The Hearth waits too. It has always been good at waiting."},
		{"if": "given>=4", "who": "", "text": "Far above, through the stone, you can almost feel them: little fires, all the way up the mountain. Yours."},
		{"if": "!given>=4", "who": "", "text": "It is very quiet down here. Just you, and your small light, and the dark."},
		{"goto": "hearth_choice"},
	],
	"hearth_turn": [
		{"who": "", "text": "You turn around. You walk back along the bridge, past the stone Keepers, and you do not look back."},
		{"event": "ending_dark"},
	],
	"hearth_step": [
		{"if": "pell_follows", "who": "Pell", "text": "I'll stay right here. At the edge. I'm not following you in. ...I'm following the light. I'll wait for it to come back out."},
		{"who": "", "text": "You climb into the Cradle. It is warm, a little. Like a hand that has been holding something for a long time."},
		{"who": "", "text": "You open your lantern, and let what is left of your flame go into the Hearth."},
		{"who": "", "text": "Then the end of your scarf catches."},
		{"event": "ending_burn"},
	],

	# --- Many Hands: everyone you warmed comes down ----------------------------
	"many_begin": [
		{"who": "", "text": "It is not enough. You feel it at once: one small wick, and a whole cold mountain."},
		{"who": "", "text": "And then, behind you, footsteps on the bridge."},
	],
	"arrive_ash": [
		{"who": "Ash", "text": "I said I'd be waiting when you came back. Turns out I'm bad at waiting. Here. This is yours. It grew."},
	],
	"arrive_tallow": [
		{"if": "gave_ash", "who": "Nan Tallow", "text": "Candles aren't much for walking, dear, so Ash carried me. Don't laugh. Here's your ember. It's twice the size. That's interest."},
		{"if": "!gave_ash", "who": "Nan Tallow", "text": "Candles aren't much for walking, but the Wickways are very good for sitting. Here, dear. Your ember. That's interest on it."},
	],
	"arrive_wisp": [
		{"who": "Wisp", "text": "I followed the glow! My glow! It came down all the stairs ahead of me! Here, have it back! It's BIGGER now!"},
	],
	"arrive_glim": [
		{"who": "Glim", "text": "Right behind my little one, as promised. Mamas always come back. Here, love. Warmer than you gave it."},
	],
	"arrive_bell": [
		{"who": "Bell", "text": "Ding! Ding! Everybody to the Hearth! That's what I rang! And everybody CAME!"},
	],
	"arrive_gudgeon": [
		{"who": "", "text": "In the black pool beneath the bridge, something enormous surfaces."},
		{"who": "Old Gudgeon", "text": "Mm. I swam the springs all the way down. Fish have a long while. Here, little light. Warmer than you gave it."},
	],
	"arrive_orrin": [
		{"who": "Orrin", "text": "Down all those stairs, with these knees! I counted every step, little wick. Here. Your star. It has grown."},
	],
	"arrive_sprig": [
		{"who": "", "text": "Roots push up through the cinders, and from them a single green leaf uncurls."},
		{"who": "Sprig", "text": "The roots knew the way! I came down the roots! Here's your small sun back. I kept it warm!"},
	],
	"arrive_hollow_one": [
		{"who": "", "text": "At the very edge of the light, the dark gathers itself into a tall, hooded shape."},
		{"who": "The Hollow One", "text": "I said I would follow a long way behind. This is as close as I have ever come. Take it. It is warmer than when I held it."},
	],
	"many_end": [
		{"music": "ending", "who": "", "text": "The embers you gave away come home, one by one, and every one of them is bigger than when it left."},
		{"who": "", "text": "The Hearth catches. Not from one small wick, but from many hands."},
		{"who": "", "text": "It roars up, gold and red and white, and the whole mountain breathes in."},
		{"who": "", "text": "And you... you burn low. Very low. But you do not burn out."},
		{"card": "Many Hands", "sub": "", "hold": 2.6},
		{"set": "ending_many"},
		{"event": "go:old_hollow:epilogue"},
	],
	"epilogue_wake": [
		{"if": "!ending_first_page", "who": "", "text": "You wake by the Little Hearth, wrapped in someone's shawl. Your scarf is burnt down almost to the knot."},
		{"if": "ending_first_page", "who": "", "text": "You wake by the Little Hearth, wrapped in someone's shawl. Your scarf is burnt down to halfway. Only halfway."},
		{"if": "ending_first_page", "who": "", "text": "Beside you, asleep against the woodpile, Vesper. Their gold scarf is burnt to halfway too. Half each."},
		{"who": "", "text": "Through the roof-roots, for the first time in a hundred winters, there is morning."},
		{"if": "pell_follows", "who": "Pell", "text": "It came back out. The light. I told you I'd wait. I'm extremely good at waiting near lights."},
	],

	# --- The Last Wick: you burn alone ------------------------------------------
	"alone_end": [
		{"music": "ending", "who": "", "text": "The Hearth catches. It roars up, gold and red and white, and the whole mountain breathes in."},
		{"who": "", "text": "Far above, in Mossgrave, the snow begins to melt. In Old Hollow, doors open one by one to the warm air."},
		{"if": "gave_tallow", "who": "", "text": "Nan Tallow's hearth burns all that spring, and the next, and the next."},
		{"if": "pell_follows", "who": "", "text": "A small moth waits at the edge of the Hearth for a long time. Then it flies up, toward the morning."},
		{"who": "", "text": "In spring they hang your lantern on Mossback's branch. It is empty. For a while."},
		{"who": "", "text": "Then one night the old totem opens his eyes, and sees a small light glowing inside it."},
		{"who": "Mossback", "text": "...Hm? A light. After so many dark nights... a light."},
		{"card": "The Last Wick", "sub": "The End", "hold": 3.5},
		{"event": "the_end"},
	],

	# --- The Long Dark: you turn back --------------------------------------------
	"dark_end": [
		{"music": "", "who": "", "text": "You climb, and climb. Behind you the Hearth gutters, and goes out, and the cold comes up the stairs after you."},
		{"who": "", "text": "The glimmer stops singing. The water rises. In Mossgrave, the snow does not melt that spring."},
		{"who": "", "text": "Somewhere deep in the dark, a new shade drifts, small and cold, with a ragged scarf."},
		{"who": "", "text": "It remembers being warm. It is drawn to every light it sees."},
		{"card": "The Long Dark", "sub": "The End", "hold": 3.5},
		{"event": "the_end"},
	],
	"the_end_card": [
		{"music": "ending", "card": "Lantern Wanderer", "sub": "Thank you for carrying the light.", "hold": 4.0},
		{"event": "the_end"},
	],
}
