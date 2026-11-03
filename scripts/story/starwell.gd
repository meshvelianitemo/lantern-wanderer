class_name StoryStarwell
## Under the Lake: the Starwell. A sunken Keeper observatory, Orrin the
## star-counter, shadow-play, and the Great Orrery.

const LINES := {
	"starwell_arrive": [
		{"who": "", "text": "Old Gudgeon carries you down through black water, deeper than any light has been in a hundred winters."},
		{"who": "", "text": "Then glass. A great dome on the floor of the lake, full of air, like a breath someone took and never let go."},
	],
	"tablet_starwell_1": [
		{"who": "", "text": "THE STARWELL. ONE STRAIGHT HOLE FROM THE TOP OF THE MOUNTAIN TO THE BOTTOM OF THE LAKE."},
		{"who": "", "text": "SO THAT THE STARS COULD SEE US, DOWN HERE IN THE DARK. AND SO THAT WE COULD SEE THEM."},
	],
	"tablet_starwell_2": [
		{"who": "", "text": "SHADOW-PLAY, FOR CHILDREN. HOLD THE TIN BEFORE THE LAMP. THE SHAPE ON THE GLASS IS A STAR'S NAME."},
		{"who": "", "text": "A HELD FLAME TREMBLES. A TREMBLING SHADOW HOLDS NOTHING. HANG YOUR LIGHT STILL, AND STAND ON THE DARK IT MAKES."},
	],
	"tablet_starwell_3": [
		{"who": "", "text": "EVERY KEEPER HAS A STAR. WE CARVE THE NAME ON A STONE AND DROP IT DOWN THE WELL, TO SIT BENEATH IT."},
		{"who": "", "text": "THE HEARTH IS A STAR THAT FELL. WE BUILT THE WELL SO THAT IT COULD SEE ITS SISTERS. - O."},
	],

	# --- Old Gudgeon, waiting in the lock ---------------------------------------
	"gudgeon_starwell": [
		{"who": "Old Gudgeon", "text": "Mm. Back up to the halls, little light? The water is cold, but I am warm enough for two.",
			"choices": [
				{"text": "Take me back up.", "goto": "gudgeon_surface"},
				{"text": "Not yet.", "goto": "gudgeon_starwell_wait"},
			]},
	],
	"gudgeon_surface": [
		{"who": "Old Gudgeon", "text": "Mm. Hold your flame close."},
		{"event": "go:drowned:4"},
	],
	"gudgeon_starwell_wait": [
		{"who": "Old Gudgeon", "text": "Mm. I will be here. Fish have a long while."},
	],

	# --- Orrin ------------------------------------------------------------------
	"orrin_wake": [
		{"who": "", "text": "Someone small is asleep in a chair by the telescope, with frost in their beard and a brass key across their knees."},
		{"who": "???", "text": "Hm? Hmm. Is it morning? ...No. It's dark. Good. I haven't missed the stars."},
		{"who": "Orrin", "text": "Orrin. Star-counter to the Keepers. I must have nodded off. The water was rising, and I thought, I'll just rest my eyes..."},
		{"who": "Orrin", "text": "You're a wick! A little lantern-walker. Bless you. Whose turn is it now? Fenn's? No, Fenn was ages ago."},
		{"set": "met_orrin"},
		{"who": "Orrin", "text": "How long was I asleep, do you suppose?",
			"choices": [
				{"text": "A very long time.", "goto": "orrin_long"},
				{"text": "The halls are drowned.", "goto": "orrin_drowned"},
				{"text": "...", "goto": "orrin_quiet"},
			]},
	],
	"orrin_long": [
		{"who": "Orrin", "text": "Hm. Yes. I rather thought so. My beard has been busy without me."},
		{"goto": "orrin_task"},
	],
	"orrin_drowned": [
		{"who": "Orrin", "text": "...All of them? The stairs, the kitchens, the little ones' beds?"},
		{"who": "Orrin", "text": "Hm. Well. The water was always going to win in the end. Water is patient. So are Keepers, mostly."},
		{"goto": "orrin_task"},
	],
	"orrin_quiet": [
		{"who": "Orrin", "text": "Too long to say out loud. I see. Then we won't say it."},
		{"goto": "orrin_task"},
	],
	"orrin_task": [
		{"who": "Orrin", "text": "Do me a kindness, little wick. At the very top of the well is the Great Orrery. It has gone cold. I can feel it."},
		{"who": "Orrin", "text": "Light it for me, and I'll show you the sky. The real one. Well. The next best thing."},
		{"who": "Orrin", "text": "The way up is shadow-play. Hold a tin plate before a still light, and the glass catches its shadow. Firm as a step."},
		{"who": "Orrin", "text": "Start with that lamp. Any flame will light it. A Keeper lamp isn't fussy."},
	],
	"orrin_repeat": [
		{"who": "Orrin", "text": "A still light, little wick. Your lantern shakes with every step you take, and shadows don't like to be shaken."},
		{"if": "gift_hook", "who": "Orrin", "text": "Hang your flame on a hook and walk on in the dark. The dark is only the shadow of something, after all."},
		{"who": "Orrin", "text": "The Great Orrery is at the top. Mind the gaps. I'll be here. Counting."},
	],
	"orrery_lit": [
		{"who": "", "text": "The rings begin to turn. Light runs out through a thousand pinholes in the brass, and up, and across the glass."},
		{"who": "", "text": "The whole dome fills with stars. The Keepers' sky, the way it looked before the water came."},
		{"if": "pell_follows", "who": "Pell", "text": "Oh. Oh, there's so many of them. Which one is the moon? I need to know which one is the moon."},
	],
	"orrin_stars": [
		{"who": "", "text": "Orrin is standing, for the first time in an age, with his face tipped up to the well. Stars shine in his spectacles."},
		{"who": "Orrin", "text": "Oh. Oh, there they are. There's the Boat. And the Fish. And the Moth, look, with her wings out."},
		{"who": "Orrin", "text": "I counted them every night in the dark, from memory. I was afraid I had them wrong. I didn't. I didn't have them wrong."},
		{"if": "names>=1", "who": "Orrin", "text": "And gold ones! Those are Keepers' stars. You found their name-stones, and the sky remembers them."},
		{"if": "name:orrin", "who": "Orrin", "text": "...Is that one mine? It is. I'd wondered where I'd put myself."},
		{"if": "names>=1", "event": "stars_named"},
		{"set": "orrin_saw_stars"},
		{"goto": "orrin_ask"},
	],
	"orrin_ask": [
		{"who": "Orrin", "text": "Do you know what stars are, little wick? Lanterns, very far away, that nobody has to carry."},
		{"who": "Orrin", "text": "They burn, and they share it, and never once ask who's looking. I always thought that was the bravest thing."},
		{"if": "embers>=1", "who": "Orrin", "text": "I'd like to see the real ones, once more. But the well is a long cold climb, and my lamp went out ages ago.",
			"choices": [
				{"text": "Give Orrin an ember.", "give": "orrin", "goto": "orrin_given"},
				{"text": "I need it.", "goto": "orrin_refuse"},
				{"text": "...", "goto": "orrin_refuse"},
			]},
		{"if": "!embers>=1", "who": "Orrin", "text": "Never mind me. I've a whole sky now. I'll sit here and count it properly. It may take a while."},
	],
	"orrin_ask_again": [
		{"who": "Orrin", "text": "...You still smell of embers. I'm not asking. I'm only an old Keeper who'd like to see one real star.",
			"choices": [
				{"text": "Give Orrin an ember.", "give": "orrin", "goto": "orrin_given"},
				{"text": "Not yet.", "goto": "orrin_refuse"},
			]},
	],
	"orrin_given": [
		{"who": "", "text": "You tip one ember into the little lantern hanging from his key. It catches at once, and his spectacles glow."},
		{"who": "Orrin", "text": "Warm! Warm right down to the toes. I'd forgotten I had toes. Keepers do, you know. Small ones."},
		{"who": "Orrin", "text": "A hollow up top, with a hearth? Then I'll set my telescope on its roof and look at the real thing."},
		{"who": "Orrin", "text": "Gudgeon knows the springs. We'll manage. Thank you, little wick. You're brighter than half of these."},
	],
	"orrin_refuse": [
		{"who": "Orrin", "text": "Quite right. Quite right. You've further to go than me. Keep it close."},
		{"who": "Orrin", "text": "I'll stay with the orrery. Someone should wind it. Someone always should."},
	],
	"orrin_after": [
		{"who": "Orrin", "text": "Two hundred and twelve, two hundred and thirteen... Hm? Oh, it's you. I'm counting again. Properly this time."},
		{"if": "embers>=1", "goto": "orrin_ask_again"},
	],
	"orrin_names": [
		{"who": "Orrin", "text": "Is that {new_names}? Oh, I remember. I remember every one of them."},
		{"if": "in:starwell,orrery_lit", "who": "Orrin", "text": "Look up. There. Their stars are lit again. Thank you for bringing them home."},
		{"if": "!in:starwell", "who": "Orrin", "text": "Down in the Starwell their stars will be shining again. I can feel it from here. Thank you for bringing them home."},
		{"event": "stars_named"},
	],
	"orrin_hollow": [
		{"who": "Orrin", "text": "Look at it! The whole sky, with nothing in the way. I keep losing count. I don't mind a bit."},
		{"if": "!ending_many", "who": "Orrin", "text": "When you get to the bottom, little wick, look up now and then. Even from down there. They're watching."},
	],
	"orrin_epilogue": [
		{"who": "Orrin", "text": "There's a new one tonight. Small and orange, right over the Hollow. I've named it. You can guess what I named it."},
	],
}
