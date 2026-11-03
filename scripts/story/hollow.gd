class_name StoryHollow
## Old Hollow, the hub: Nan Tallow, Pell, and everyone who moves in.

const LINES := {
	"sign_hollow": [
		{"who": "", "text": "OLD HOLLOW\nKeep your door shut and your hearth lit."},
		{"who": "", "text": "Below, in smaller letters: 'Forty doors. Forty fires. Come in out of the cold.'"},
	],
	"tablet_hollow_secret": [
		{"who": "", "text": "Behind the burnt thorns, a Keeper tablet, half swallowed by roots:"},
		{"who": "", "text": "WHEN THE WICK GOES DOWN, LEAVE THE DOORS UNLOCKED. SOMETIMES SOMEONE COMES BACK UP."},
	],
	"sign_wickway_hollow": [
		{"who": "", "text": "WICKWAYS - FOR THOSE WHO GO DOWN, AND THOSE WHO COME BACK."},
	],

	# --- Nan Tallow ---------------------------------------------------------
	"tallow_intro": [
		{"who": "???", "text": "Mind the step, dear. And mind your flame. The draught in here would snuff a sunrise."},
		{"who": "Nan Tallow", "text": "Nan Tallow. I keep the hearth in Old Hollow. Kept. Keep. ...It's been a long winter for verbs."},
		{"who": "Nan Tallow", "text": "There were forty doors lit in this hollow once. Now there's me, the moth, and a hearth gone grey."},
		{"who": "Nan Tallow", "text": "My wick's too short to light it anymore. Burned most of myself keeping it going, I'm afraid."},
		{"set": "met_tallow"},
		{"goto": "tallow_ask"},
	],
	"tallow_ask": [
		{"if": "embers>=1", "who": "Nan Tallow", "text": "But you're carrying embers, aren't you? Could you spare one for an old woman's hearth?",
			"choices": [
				{"text": "Give her an ember.", "give": "tallow", "goto": "tallow_given"},
				{"text": "I need it for the Deep.", "goto": "tallow_refuse"},
				{"text": "...", "goto": "tallow_refuse_quiet"},
			]},
		{"if": "!embers>=1", "who": "Nan Tallow", "text": "If you find an ember to spare on your travels, bring it by. No hurry. I've waited this long."},
	],
	"tallow_given": [
		{"who": "", "text": "You tip your lantern. One ember drifts out, and settles into the cold hearth."},
		{"who": "Nan Tallow", "text": "Oh... oh, look at that. Look at it, dear."},
		{"who": "Nan Tallow", "text": "Your light's a little smaller now. Mine's a little bigger. Warmth never really leaves, you know. It just moves house."},
		{"who": "Nan Tallow", "text": "You're a wick too, aren't you? I can always tell. We burn the same way, dear. From the top down."},
		{"who": "Nan Tallow", "text": "Anyone you find down there who's gone cold... send them up to me. The hearth will keep them."},
		{"who": "Nan Tallow", "text": "Go on. And come home sometimes. A hearth needs faces around it."},
	],
	"tallow_refuse": [
		{"who": "Nan Tallow", "text": "Of course. Of course you do. The Deep needs it more than an old candle."},
		{"who": "Nan Tallow", "text": "If you change your mind, I'll be here. Candles aren't much for walking."},
	],
	"tallow_refuse_quiet": [
		{"who": "Nan Tallow", "text": "Ha. A quiet one. That's alright. Silence keeps warm better than most talk."},
		{"who": "Nan Tallow", "text": "If you change your mind, I'll be here. Candles aren't much for walking."},
	],
	"tallow_after": [
		{"if": "!given>=2", "who": "Nan Tallow", "text": "There you are. Sit a minute. The hearth likes to see you."},
		{"if": "given>=2,!given>=4", "who": "Nan Tallow", "text": "The Hollow's filling up again. I'd almost forgotten what it sounds like."},
		{"if": "given>=4", "who": "Nan Tallow", "text": "Listen to them all. Forty doors, I said. We'll get there yet."},
		{"if": "gave_wisp", "who": "Nan Tallow", "text": "That little glow-grub hasn't stopped talking since she arrived. I love her dearly. I'd love her more at half volume."},
		{"if": "gave_ash", "who": "Nan Tallow", "text": "Ash sits by the fire most nights. Watches the flames like they're an old friend who might leave."},
		{"if": "gave_bell", "who": "Nan Tallow", "text": "A ghost! In my Hollow! She rings that bell at supper. Nobody's late anymore."},
		{"if": "gave_gudgeon", "who": "Nan Tallow", "text": "And there is a FISH in my well, dear. A very polite one. I've stopped asking."},
		{"if": "gave_sprig", "who": "Nan Tallow", "text": "That sapling you sent up is growing like it's late for something. Roots in the floor already."},
		{"if": "gave_orrin", "who": "Nan Tallow", "text": "There's an old Keeper on top of the barrow with a telescope, dear. He waves at the sky. I've started waving back."},
		{"if": "visited_rootdark", "who": "Nan Tallow", "text": "You've gone very deep, haven't you. I can see it on you. Your scarf's gone short."},
		{"if": "visited_rootdark", "who": "Nan Tallow", "text": "...Whatever's waiting at the bottom, dear. You don't have to carry all of it alone. Remember that."},
		{"if": "!visited_rootdark", "who": "Nan Tallow", "text": "Mind your flame down there. Come home when you're cold."},
	],
	"tallow_epilogue": [
		{"who": "Nan Tallow", "text": "Look at you. Burnt right down to the knot, and still here."},
		{"who": "Nan Tallow", "text": "Sit by the fire, dear. That's all anyone wants of you now. Just sit, and be warm."},
	],

	# --- Pell ---------------------------------------------------------------
	"pell_intro": [
		{"who": "???", "text": "Oh! Oh oh oh. A light. A real one. Hello, light."},
		{"who": "Pell", "text": "Not you. The light. Hello to you too, I suppose. I'm Pell."},
		{"who": "Pell", "text": "I was circling the hearth, but the hearth stopped. So now I circle where the hearth used to be. It's less satisfying."},
		{"who": "Pell", "text": "You're going down into the dark? With that? Can I come? I won't be any help. I'll just be near the light. That's my whole thing.",
			"choices": [
				{"text": "Come along.", "goto": "pell_join"},
				{"text": "It'll be dangerous.", "goto": "pell_danger"},
				{"text": "...", "goto": "pell_quiet"},
			]},
	],
	"pell_join": [
		{"who": "Pell", "text": "Wonderful! I'm not following you, you understand. I'm following the light. Completely different."},
		{"set": "pell_follows"},
	],
	"pell_danger": [
		{"who": "Pell", "text": "Dangerous? I'm a moth. My entire life plan is flying into fire. I'll be fine."},
		{"set": "pell_follows"},
	],
	"pell_quiet": [
		{"who": "Pell", "text": "I'll take that as a yes. I take most things as a yes. It has served me very poorly."},
		{"set": "pell_follows"},
	],

	# --- residents ------------------------------------------------------------
	"wisp_hollow": [
		{"who": "Wisp", "text": "Nice somebody! Look, I'm still glowing! Nan says I glow LOUD."},
		{"if": "!given>=3", "who": "Wisp", "text": "Nan's looking after me till Mama comes back. Mama always comes back. Eventually."},
		{"if": "given>=3", "who": "Wisp", "text": "The Hollow's getting so bright. When Mama comes back she'll see it from all the way away."},
	],
	"ash_hollow": [
		{"who": "Ash", "text": "Tallow lets me tend the hearth. I'm not good at it yet. I keep feeding it too much."},
		{"if": "!visited_rootdark", "who": "Ash", "text": "When you get to the bottom, little wick... you'll know what to do. I didn't. I hope you do."},
		{"if": "visited_rootdark", "who": "Ash", "text": "You're close now. I can tell. I stopped about where you're standing, once. In my head, I mean."},
	],
	"ash_lark": [
		{"who": "Ash", "text": "You've got a look about you. Like you're holding something."},
		{"who": "Ash", "text": "...Go on, then.",
			"choices": [
				{"text": "Your name was Lark.", "goto": "ash_lark_told"},
				{"text": "It's nothing.", "goto": "ash_lark_not"},
			]},
	],
	"ash_lark_told": [
		{"who": "Ash", "text": "..."},
		{"who": "Ash", "text": "Lark. Yes. That was it. I used to sing, going down the stairs. That's why they called me that."},
		{"who": "Ash", "text": "I'd forgotten I was ever loud. Thank you, little wick. I think I'll keep both names."},
		{"set": "told_lark"},
		{"if": "!ash_told_lantern,!keepsake:lantern,!echo_lark", "goto": "ash_lantern"},
	],
	"ash_lark_not": [
		{"who": "Ash", "text": "Alright. Keep it, then. Things kept close stay warm."},
	],
	"ash_epilogue": [
		{"who": "Ash", "text": "You did it. And you're still here. I didn't know that was allowed."},
		{"if": "told_lark", "who": "Ash", "text": "Lark and Ash and you. Two burnt wicks and a moth. Some company you keep."},
	],
	"bell_hollow": [
		{"who": "Bell", "text": "I ring for supper now! Ding! Everyone comes! Even the fish tries."},
		{"who": "Bell", "text": "Ghosts don't get hungry. But I like to watch them eat. It's warm, watching."},
	],
	"gudgeon_hollow": [
		{"who": "Old Gudgeon", "text": "Mm. A well. Small, but the water's sweet, and the old woman sings to it at night."},
		{"who": "Old Gudgeon", "text": "I swam up through the springs. Took a long while. Fish have a long while. Fish have nothing else."},
	],
	"sprig_hollow": [
		{"who": "Sprig", "text": "Look how tall! Look! I can almost see the sky through the roof-roots!"},
		{"who": "Sprig", "text": "When I'm big I'll hold the roof up for everyone. That's what trees are for. Nan said."},
	],
	"wisp_epilogue": [
		{"who": "Wisp", "text": "You came back! You came back, you came back! I glowed at you the WHOLE time."},
	],
	"bell_epilogue": [
		{"who": "Bell", "text": "Ding! Ding! That's the welcome-home bell. I made it up just now."},
	],
	"gudgeon_epilogue": [
		{"who": "Old Gudgeon", "text": "Mm. The water's warm again. All the way down. I could feel it turn. Thank you, small one."},
	],
	"sprig_epilogue": [
		{"who": "Sprig", "text": "There's sun coming through the roof-roots! Real sun! I've never had real sun!"},
	],
	"hollow_epilogue": [
		{"who": "The Hollow One", "text": "...I am only sitting at the edge. Where the light thins out. It is enough, for now."},
		{"who": "The Hollow One", "text": "Tallow says there will be a door for me, when I am ready. Forty-one doors."},
	],
}
