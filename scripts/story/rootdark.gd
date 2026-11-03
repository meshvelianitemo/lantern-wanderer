class_name StoryRootdark
## Chapter IV: The Rootdark. Sprig, the Root-Mother, the Flare, and the
## Hollow One - the first wick, who turned back.

const LINES := {
	"tablet_root_1": [
		{"who": "", "text": "THE FOREST DRINKS FROM THE HEARTH THROUGH THESE ROOTS. WE DO NOT CUT THEM. WE DO NOT ASK THEM TO STOP."},
	],
	"tablet_root_2": [
		{"who": "", "text": "Behind the burnt thorns, an old tablet, carved deeper than the others, as if someone wanted it never to wear away:"},
		{"who": "", "text": "FIRE ONLY CATCHES FROM FIRE. ONE FLAME ALONE BURNS OUT. MANY FLAMES TOGETHER BURN ON."},
		{"set": "read_first_page"},
	],
	"chase_start": [
		{"who": "", "text": "Behind you, the dark thickens. Two pale eyes open, high up. Much too high up."},
		{"who": "", "text": "The shades are stirring. All of them, all at once, as if something has called them."},
	],
	"hearth_enter": [
		{"who": "", "text": "The roots thin, and end. Below them a stair goes down, warm underfoot, the colour of old embers."},
	],

	# --- Sprig ----------------------------------------------------------------
	"sprig_intro": [
		{"who": "???", "text": "Hello? Are you the sun? I've been waiting such a long time for the sun."},
		{"who": "Sprig", "text": "I'm Sprig. A seed fell down a crack a long, long time ago, and that was me. I've been growing towards the sun ever since."},
		{"who": "Sprig", "text": "Only it's quite far. And I'm quite cold. And I've only grown this much."},
		{"set": "met_sprig"},
		{"goto": "sprig_ask"},
	],
	"sprig_repeat": [
		{"who": "Sprig", "text": "Still here. Still small. Still growing, though! Slowly."},
		{"goto": "sprig_ask"},
	],
	"sprig_ask": [
		{"if": "embers>=1", "who": "Sprig", "text": "You're not the sun. But you're a bit like the sun. A small one. Could you spare a bit of small sun?",
			"choices": [
				{"text": "Give Sprig an ember.", "give": "sprig", "goto": "sprig_given"},
				{"text": "I need my light.", "goto": "sprig_refuse"},
				{"text": "...", "goto": "sprig_refuse"},
			]},
		{"if": "!embers>=1", "who": "Sprig", "text": "Your light's ever so small. Like me! We can be small together. Small is still something."},
	],
	"sprig_given": [
		{"who": "", "text": "You set an ember in the soil beside Sprig. The leaves lift, slowly, the way a sleeper stretches."},
		{"who": "Sprig", "text": "Oh! Oh, I'm green! Am I green? I FEEL green!"},
		{"who": "Sprig", "text": "There's a hollow up top with a hearth? And a hole in the roof where the light comes in? I'll grow there! The roots know the way!"},
	],
	"sprig_refuse": [
		{"who": "Sprig", "text": "That's alright. I'll keep growing. Slowly. Slowly is still growing."},
	],
	"sprig_thanks": [
		{"who": "Sprig", "text": "Bye! Bye! I'm going up through the roots! It tickles!"},
	],

	# --- The Root-Mother ---------------------------------------------------------
	"rootmother_intro": [
		{"who": "", "text": "The wall of roots shifts. Two eyes open in it, slow as seasons, glowing the violet of deep fungus."},
		{"who": "???", "text": "...Little spark. You came home."},
		{"who": "The Root-Mother", "text": "I am the Root-Mother. I drink the Hearth's warmth and carry it up, through stone and dark, to the forest. Every breath it breathes, I gave it."},
		{"who": "The Root-Mother", "text": "And when the Hearth flickers and a spark leaps loose, I carry that up too. Gently. All the way to the moss, where the old totem waits."},
		{"who": "The Root-Mother", "text": "I carried you, little wick. You were the last spark the Hearth had. I held you in my roots nine nights so you would not go out.",
			"choices": [
				{"text": "So I came from the Hearth.", "goto": "rootmother_from"},
				{"text": "Why me?", "goto": "rootmother_why"},
				{"text": "...", "goto": "rootmother_quiet"},
			]},
	],
	"rootmother_from": [
		{"who": "The Root-Mother", "text": "Everything warm came from the Hearth. You are only going home. ...I know home is not always a gentle word."},
		{"goto": "rootmother_page"},
	],
	"rootmother_why": [
		{"who": "The Root-Mother", "text": "Not 'you'. Never 'you'. Just: a spark, when one was needed. You made yourself into you along the way. That part was all yours."},
		{"goto": "rootmother_page"},
	],
	"rootmother_quiet": [
		{"who": "The Root-Mother", "text": "Yes. Hold it quietly. It is a great deal to hold."},
		{"goto": "rootmother_page"},
	],
	"rootmother_page": [
		{"who": "The Root-Mother", "text": "Listen. The Keepers wrote a first page in their book, long ago. The water took it. But I remember, because it is written in me too."},
		{"who": "The Root-Mother", "text": "Fire only catches from fire. One flame alone burns out. Many flames together... burn on."},
		{"if": "given>=3", "who": "The Root-Mother", "text": "I can feel the hearths you lit on your way down. They are warm against my roots, all the way up. Remember that, at the bottom."},
		{"if": "!given>=3", "who": "The Root-Mother", "text": "You have kept your flame close. That is not wrong. But at the bottom, remember: no wick was ever meant to burn alone."},
		{"set": "read_first_page"},
		{"goto": "rootmother_gift"},
	],
	"rootmother_gift": [
		{"who": "The Root-Mother", "text": "The dark is thick down here, and full of thorns. Let me teach you how to breathe."},
		{"who": "", "text": "The roots breathe in. You feel it too: your lantern drawing in, and in, and then pushing out in one warm rush."},
		{"set": "gift_flare", "sfx": "flare"},
		{"card": "Lantern Gift: Flare", "sub": "Press {key:flare} to push your light out in a burst", "hold": 3.0},
		{"who": "The Root-Mother", "text": "Push your light out all at once: thorn-roots burn, and shades scatter. It costs you nothing, but you must breathe in again before the next."},
		{"who": "The Root-Mother", "text": "Something waits further down. The oldest shade. It was a wick once, like you. Be kind to it, if you can. Be brave, if you can't."},
		{"if": "!keepsake:page", "goto": "rootmother_keepsake"},
	],
	# the first page itself: a keepsake (its Echo is Vesper's)
	"rootmother_keepsake": [
		{"who": "The Root-Mother", "text": "And one more thing, little spark. The water took the first page, I said. It did not take all of it."},
		{"who": "The Root-Mother", "text": "When the flood came down, a small slate fell through my roots, and I caught it. I have held it ever since. It was never mine to read."},
		{"set": "keepsake:page", "sfx": "keepsake", "card": "The First Page", "sub": "Carved by Edda, after the first cold.", "hold": 2.2},
		{"goto": "keepsake_page"},
	],
	"rootmother_repeat": [
		{"who": "The Root-Mother", "text": "Breathe in. Push out. You have it."},
		{"who": "The Root-Mother", "text": "Further down, little spark. Something old is waiting for you. And then... home."},
	],

	# --- The Hollow One ----------------------------------------------------------
	"hollow_one_meet": [
		{"who": "", "text": "At the bottom of the roots, where the dark is deepest, it waits. A shape like yours: hood, and scarf, and two pale eyes. But made of night, and very tall."},
		{"who": "???", "text": "...Turn back, little wick."},
		{"who": "The Hollow One", "text": "I know where you are going. I went there first. The very first. Before the Keepers had a book to write it in."},
		{"who": "The Hollow One", "text": "My name was Vesper. I walked all the way down to the Hearth, and I looked at it, and it looked at me... and I was afraid."},
		{"who": "The Hollow One", "text": "So I turned back. And the Hearth went cold. And the water rose. And the dark that was left over gathered around me. Became me."},
		{"who": "The Hollow One", "text": "Every shade you have met is a little piece of a fire that went out. I am the first of them. I am what you get, for turning back."},
		{"set": "hollow_one_spoke"},
		{"who": "The Hollow One", "text": "And still. Still. I would rather be this than ash. Wouldn't you?",
			"choices": [
				{"text": "I'm not afraid.", "goto": "hollow_one_brave"},
				{"if": "given>=3", "text": "I'm not going alone.", "goto": "hollow_one_together"},
				{"text": "Why do you want me to turn back?", "goto": "hollow_one_why"},
				{"text": "...", "goto": "hollow_one_quiet"},
			]},
	],
	"hollow_one_brave": [
		{"who": "The Hollow One", "text": "Neither was I. Until I was. ...Go on, then. Find out."},
		{"goto": "hollow_one_offer"},
	],
	"hollow_one_together": [
		{"who": "The Hollow One", "text": "...Not alone?"},
		{"who": "The Hollow One", "text": "I can feel them. Up above. Little hearths, all the way up the mountain. You lit them."},
		{"who": "The Hollow One", "text": "I never lit anything. I only carried mine down, alone, and held it so tightly."},
		{"goto": "hollow_one_offer"},
	],
	"hollow_one_why": [
		{"who": "The Hollow One", "text": "Because I am tired of being the only one who did. ...No. That is not true."},
		{"who": "The Hollow One", "text": "Because I do not want you to burn. Is that so strange, from the dark?"},
		{"goto": "hollow_one_offer"},
	],
	"hollow_one_quiet": [
		{"who": "The Hollow One", "text": "Silence. I remember silence. I was quiet too, at the Hearth's edge. For a very long time."},
		{"goto": "hollow_one_offer"},
	],
	"hollow_one_offer": [
		{"if": "embers>=1", "who": "The Hollow One", "text": "You are looking at your lantern. ...You wouldn't. Not to me.",
			"choices": [
				{"text": "Offer the Hollow One an ember.", "give": "hollow_one", "goto": "hollow_one_given"},
				{"text": "Let me pass.", "goto": "hollow_one_pass"},
			]},
		{"goto": "hollow_one_pass"},
	],
	"hollow_one_given": [
		{"who": "", "text": "You hold out an ember. The Hollow One looks at it for a long, long time. Then a hand of night closes around it, very gently."},
		{"who": "The Hollow One", "text": "...Warm. It is warm. Nobody has ever given the dark anything warm."},
		{"who": "The Hollow One", "text": "I will not stop you. I will follow, a long way behind. I would like to see it lit. Just once."},
		{"set": "hollow_one_gone"},
	],
	"hollow_one_pass": [
		{"who": "The Hollow One", "text": "Then go. The way down is behind me. I will not stop you. I have never been able to stop anyone. That was never what the dark was for."},
		{"who": "The Hollow One", "text": "Go and burn, little wick."},
		{"set": "hollow_one_gone"},
	],
	"hollow_one_repeat": [
		{"who": "The Hollow One", "text": "...Go on. I am only the dark. I will be here."},
	],
}
