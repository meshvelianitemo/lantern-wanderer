class_name StoryGlimmer
## Chapter II: The Glimmerdeep. Burrow, Wisp, Ash, and the black water.

const LINES := {
	"tablet_glimmer_1": [
		{"who": "", "text": "Old letters, carved small and careful by the Keepers:"},
		{"who": "", "text": "WE TEND THE FLAME. THE FLAME TENDS THE MOUNTAIN. EACH AGE, A WICK."},
		{"who": "", "text": "The rest is worn away by water."},
	],
	"tablet_glimmer_2": [
		{"who": "", "text": "THE WICKWAY. FOR THOSE WHO GO DOWN, AND THOSE WHO COME BACK."},
		{"who": "", "text": "Below it, scratched much more recently, in a shaky hand: 'not everyone comes back. - L.'"},
	],
	"tablet_glimmer_3": [
		{"who": "", "text": "GLIMMER REMEMBERS WHAT IS GIVEN TO IT. SO DOES EVERYTHING."},
	],
	"glimmer_violet_hint": [
		{"who": "", "text": "Violet glimmer, dark and deep. It stirs at your flame, but doesn't wake."},
		{"who": "", "text": "It wants a bigger light than you are carrying."},
	],

	# --- Burrow ---------------------------------------------------------------
	"burrow_intro": [
		{"who": "???", "text": "Oi. Who's that clomping about? You've got a hum to you. A warm hum."},
		{"who": "Burrow", "text": "Burrow's the name. Been digging glimmer down here since before your lot started carrying lights about."},
		{"who": "Burrow", "text": "No, I can't see your lantern. Never seen a thing in my life. Don't need to. I can hear the glimmer singing."},
		{"who": "Burrow", "text": "See, glimmer drinks light. Hold your flame near it and it goes solid as bedrock. Take the flame away, it's mist again."},
		{"who": "Burrow", "text": "Bigger the flame, further it reaches. So mind how much of it you give away, eh?",
			"choices": [
				{"text": "What's further down?", "goto": "burrow_below"},
				{"text": "Do you need anything?", "goto": "burrow_need"},
				{"text": "...", "goto": "burrow_quiet"},
			]},
	],
	"burrow_below": [
		{"who": "Burrow", "text": "Further down's the Wickway. Old Keeper lift. Runs all the way up to the Hollow, if anybody bothers lighting it."},
		{"who": "Burrow", "text": "Below that... water. Black water. Something big lives in it. Mostly harmless. Mostly."},
		{"goto": "burrow_end"},
	],
	"burrow_need": [
		{"who": "Burrow", "text": "Need? Ha! Moles don't need. Moles dig."},
		{"who": "Burrow", "text": "...There's a little glow-grub lost down the east tunnel. Keeps crying. I'd fetch her, but she's scared of my claws. Fair enough."},
		{"set": "heard_wisp"},
		{"goto": "burrow_end"},
	],
	"burrow_quiet": [
		{"who": "Burrow", "text": "Quiet type. Good. Glimmer doesn't like chatter."},
		{"goto": "burrow_end"},
	],
	"burrow_end": [
		{"who": "Burrow", "text": "And watch for shades. Cold, creeping things. They hate a big flame. They love a small one."},
		{"set": "met_burrow"},
	],
	"burrow_repeat": [
		{"if": "!embers>=3", "who": "Burrow", "text": "Still humming, are you? Quieter than before. Keep your flame big near the shades."},
		{"if": "embers>=3", "who": "Burrow", "text": "Now THAT'S a hum. The violet glimmer will hear you singing like that. Deep stuff. Picky stuff."},
		{"who": "Burrow", "text": "Off you go. Mind the drop. I've fallen down it twice. Didn't see it coming. Ha."},
	],
	"burrow_wisp_thanks": [
		{"who": "Burrow", "text": "Heard the grub stopped crying. Heard it was you did that."},
		{"who": "Burrow", "text": "...Hmph. Good. Tunnels are too quiet now, mind. I'll get used to it."},
		{"set": "burrow_heard_wisp"},
	],

	# --- Wisp -----------------------------------------------------------------
	"wisp_intro": [
		{"who": "???", "text": "...is somebody there? Please don't be a shade. Please be a nice somebody."},
		{"who": "Wisp", "text": "I'm Wisp. I'm a glowworm. Only I'm not glowing. It went out when the shades came, and now I can't find the way home."},
		{"who": "Wisp", "text": "Mama said if your glow goes out, you just need a little bit of somebody else's. But nobody's down here. Only you."},
		{"set": "met_wisp"},
		{"goto": "wisp_ask"},
	],
	"wisp_repeat": [
		{"who": "Wisp", "text": "Are you still here, nice somebody? ...I'm still not glowing."},
		{"goto": "wisp_ask"},
	],
	"wisp_ask": [
		{"if": "embers>=1", "who": "Wisp", "text": "Is that glow in your lantern? It's so pretty. Could you... spare a tiny bit?",
			"choices": [
				{"text": "Share an ember with her.", "give": "wisp", "goto": "wisp_given"},
				{"text": "I can't spare one.", "goto": "wisp_refuse"},
				{"text": "...", "goto": "wisp_refuse"},
			]},
		{"if": "!embers>=1", "who": "Wisp", "text": "Your light's so little too. That's okay. We can both be little."},
	],
	"wisp_given": [
		{"who": "", "text": "You lower your lantern. An ember drifts down, and Wisp swallows it with a hiccup."},
		{"who": "Wisp", "text": "Oh! Oh, I'm glowing! Look! I'm a light! I'm a LIGHT!"},
		{"who": "Wisp", "text": "I'll go up to the Hollow. Nan Tallow will know where Mama is. Nan knows everything."},
		{"who": "Wisp", "text": "Thank you, nice somebody. I'll glow at you every single day."},
	],
	"wisp_refuse": [
		{"who": "Wisp", "text": "Oh. That's okay. You need it for the big dark. I'll just... wait here. I'm good at waiting."},
	],
	"wisp_thanks": [
		{"who": "Wisp", "text": "I'm going! I'm going! I'm just practising glowing first. Look. Glow. Glow."},
	],

	# --- Ash ------------------------------------------------------------------
	"ash_intro": [
		{"who": "???", "text": "...Another light. I thought I'd dreamed you."},
		{"who": "???", "text": "Don't look so surprised. You didn't think you were the first, did you?"},
		{"who": "Ash", "text": "They call me Ash now. Well. That's what I am. I had a brighter name, before."},
		{"who": "Ash", "text": "I carried an ember down here once. Gave a bit to this one, a bit to that one... and one night I looked down and my lantern was cold."},
		{"who": "Ash", "text": "Let me guess. The old totem called you 'little wick.'",
			"choices": [
				{"text": "He did.", "goto": "ash_wick"},
				{"text": "What does it mean?", "goto": "ash_wick_mean"},
				{"text": "...", "goto": "ash_wick"},
			]},
	],
	"ash_wick": [
		{"who": "Ash", "text": "He called me that too. Kind of him. Kinder than the truth."},
		{"goto": "ash_ask"},
	],
	"ash_wick_mean": [
		{"who": "Ash", "text": "A wick is the part of the candle that burns, little one. Ask Nan Tallow. Ask the Hearth, when you get there."},
		{"goto": "ash_ask"},
	],
	"ash_ask": [
		{"set": "met_ash"},
		{"if": "embers>=1", "who": "Ash", "text": "I won't ask you for anything. I gave mine away, and it wasn't enough."},
		{"if": "embers>=1", "who": "Ash", "text": "...But if you had one to spare, I think I could walk home.",
			"choices": [
				{"text": "Give Ash an ember.", "give": "ash", "goto": "ash_given"},
				{"text": "Keep it.", "goto": "ash_refuse"},
				{"text": "...", "goto": "ash_refuse"},
			]},
		{"if": "!embers>=1", "who": "Ash", "text": "No embers either? Ha. A matched pair, us. Go on down. Maybe you'll be luckier."},
	],
	"ash_given": [
		{"who": "", "text": "The ember settles into Ash's cold lantern. For a long moment, nothing. Then - a flicker."},
		{"who": "Ash", "text": "...Oh. I'd forgotten it felt like this."},
		{"who": "Ash", "text": "I'll go up to the Hollow and sit with Tallow. Someone should be waiting for you when you come back."},
		{"who": "Ash", "text": "If you come back. ...No. When."},
	],
	"ash_refuse": [
		{"who": "Ash", "text": "Good. You're learning faster than I did."},
		{"who": "Ash", "text": "Don't give it all away, little wick. And don't keep it all, either. Neither one works. Believe me."},
	],
	"ash_repeat": [
		{"who": "Ash", "text": "Still here. Still grey. The Wickway's just past me, if you want to go home for a while."},
		{"goto": "ash_ask_again"},
	],
	"ash_ask_again": [
		{"if": "embers>=1", "who": "Ash", "text": "...",
			"choices": [
				{"text": "Give Ash an ember.", "give": "ash", "goto": "ash_given"},
				{"text": "Rest well, Ash."},
			]},
	],
	"ash_thanks": [
		{"who": "Ash", "text": "I'm going. Just... let me sit with it a minute. It's been so long since my hands were warm."},
	],

	# --- Old Gudgeon at the black water ---------------------------------------
	"gudgeon_intro": [
		{"who": "", "text": "The tunnel ends in still, black water. Far below the surface, pale lights drift, like windows in a sunken house."},
		{"who": "", "text": "Something huge rises. Two milky eyes. Whiskers like old rope."},
		{"who": "Old Gudgeon", "text": "Mmmm. A little light, at the edge of my water. It has been a long time since one of you came."},
		{"who": "Old Gudgeon", "text": "Old Gudgeon, they called me. I ferried the Keepers, once. Down to their halls, and back. Mostly down, at the end."},
		{"who": "Old Gudgeon", "text": "You will want to go down too. They all do. Climb on, if you like. Mind the whiskers.",
			"choices": [
				{"text": "Ride down to the Drowned Halls.", "goto": "gudgeon_ride"},
				{"text": "Not yet.", "goto": "gudgeon_wait"},
			]},
		{"set": "met_gudgeon"},
	],
	"gudgeon_ferry_repeat": [
		{"who": "Old Gudgeon", "text": "Mm. Still here, little light. The halls are still drowned. Shall we?",
			"choices": [
				{"text": "Ride down to the Drowned Halls.", "goto": "gudgeon_ride"},
				{"text": "Not yet.", "goto": "gudgeon_wait"},
			]},
	],
	"gudgeon_ride": [
		{"set": "met_gudgeon"},
		{"who": "", "text": "You climb onto Old Gudgeon's broad, cold back. The black water closes around your lantern like a held breath."},
		{"event": "go:drowned:1"},
	],
	"gudgeon_wait": [
		{"set": "met_gudgeon"},
		{"who": "Old Gudgeon", "text": "Mm. I will wait. I am very good at waiting. It is most of what a fish is."},
	],
}
