# Core principles of juice (medium-independent)

Back to [SKILL.md](../SKILL.md). Lenses that apply these: [lenses.md](lenses.md). Sources and dates: [RESEARCH.md](../RESEARCH.md); book key: [sources.md](sources.md).

Each principle has an ID (`P-xx`) so reports can cite it in a few characters. They are written so they hold for a game, a video edit, a web UI, or a slide deck; the game reading follows each one. Citations: Swink = *Game Feel* (2009, printed pages); Schell = *The Art of Game Design* 2e (2015, printed pages); Hodent = *The Gamer's Brain* (2017, chapter and section); Rogers 2e = *Level Up!* 2nd ed. (2014, PDF pages), Rogers 3e = 3rd ed. (chapter and section).

## A. Timing: the event and its envelope

**P-01 Response fuses with cause under ~100 ms.** When the result of an action arrives within roughly one perceptual cycle (about 100 ms), people perceive it as caused by them and instant. Later than that and it feels like lag, whatever the frame rate. In games: measure from the input frame to the first visible or audible response, not to the end of the animation. *Swink ch. 2 p. 35, ch. 4 p. 70.*

**P-02 Protect the correction loop (~240 ms).** Real-time control is a cycle of perceive, decide, act, perceive again, about 240 ms for most people (roughly 100 perception + 70 cognition + 70 motor, with wide ranges). Effects and lockouts that stop the user from correcting inside that cycle reduce control. In games: flag long uncancellable animations, input locks during effects, and hit-stop that also eats input. *Swink ch. 2 pp. 35-38.*

**P-03 Anticipation, impact, follow-through (the envelope).** Every action has an attack, a peak, and a release (Swink calls it attack, decay, sustain, release). A short wind-up makes the action legible, the peak lands the moment, and the follow-through (settle, overshoot, recoil, dust) tells you the weight. In games: tween curves (ease-out-back, elastic), squash on land, recoil after a shot, a small settle after UI slides in. *Swink ch. 7 pp. 140-154; ch. 9 pp. 155-157.*

**P-04 Stop time to mark impact (hit-stop).** Freezing or slowing the moment of contact for a few frames gives the brain time to register it and sells force. Scale the pause with the strength of the hit, and keep input buffered through it. In games: 2-6 frames (about 30-100 ms) for normal hits, longer for finishers; never on every bullet of a fast weapon. *Rogers 2e ch. 14 p. 364; Nijman 2013 and Sakurai, see RESEARCH.md.*

**P-05 Forgive intent at the edges.** Keep player intent alive briefly when the rules would otherwise discard it: accept a jump a few frames after leaving a ledge (coyote time) or a few frames before landing (input buffer). This removes friction that has nothing to do with the intended challenge. Buffer every core action, not only jump: attack and dash presses wait the same way. Give each stored press its own expiry (one timer for the whole queue lets later presses outlive the window), ignore key-repeat echoes, and consume the press that fired. Decide whether a buffered jump still needs the button held at landing: requiring it suits variable-height jumps but drops quick early taps, which most buffers exist to catch. In games: coyote 80-150 ms, jump buffer 100-150 ms. *Swink ch. 6 pp. 121-137, ch. 13; Hodent ch. 11 "Minimum Workload"; Thorson 2018; Campos, Game Development Patterns with Godot 4, ch. 13 (action buffer).*

## B. Layering: one event, many channels

**P-06 Layer channels for one event.** People perceive animation, particles, sound, camera, and haptics that arrive together as a single event. Two or three agreeing channels beat one strong one, and they make the event survive when one channel is unavailable (muted audio, colour blindness, no rumble). *Swink ch. 9 pp. 151-152, 167-169; Schell Lens #66 pp. 271-272; Hodent ch. 11 "Flexibility and Accessibility".*

**P-07 Effects must agree on what happened.** The channels have to say the same thing about mass, material, and force. A deep boom on a weightless sprite reads as wrong, so audit the combined impression rather than each effect alone. *Swink ch. 9 pp. 152, 167-169; Schell Lens #71 pp. 289-290.*

**P-08 Second-order motion makes small input feel rich.** Motion that follows from the user's action without being directly controlled (a cape swinging, a counter that overshoots and settles, a button that squishes) makes a small action feel big. *Schell Lens #64 "Juiciness" pp. 265-266.*

**P-09 Sound maps to touch, so vary it.** Sound is the cheapest way to make an interface feel tactile. The ear notices a repeated identical sample, so vary pitch (±5-10%) and volume slightly, and keep a few variants per sound. *Schell ch. 15 "Sound Maps to Touch" p. 275; Rogers 2e ch. 14 pp. 364-370.*

**P-10 Feedback is information first.** Feedback should tell the user what happened, whether it worked, how much, which way, and what they can do now. Decoration that answers none of those is noise. Distinguish hit, miss, block, and critical. *Schell Lens #63 pp. 260-263; Hodent ch. 11 "Signs and Feedback"; Rogers 2e ch. 5 pp. 127-130.*

## C. Contrast and proportion

**P-11 Scale feedback with importance.** A small hit, a critical, and a boss kill should not look and sound the same. Keep tiers (small, medium, signature) and save the biggest response for the rarest moment, so the big one still has room to land. *Rogers 2e ch. 14-15; Hodent ch. 5 "Attention".*

**P-12 Contrast needs a baseline.** An effect reads against the stillness around it. A screen that is always shaking makes a real explosion invisible, so quiet stretches are part of the design. *Hodent ch. 11 "Clarity" (signal detection); Schell interest curves, ch. 16.*

**P-13 Form follows function.** An effect's look should match its meaning. Something that looks dangerous should be dangerous, and the same feedback code should mean the same thing everywhere (damage colour, heal sound, "not ready" buzz). *Hodent ch. 11 "Form Follows Function", "Consistency".*

**P-14 Perceived properties beat simulated ones.** People judge weight, speed, and size from motion, sound, and animation, not from physics values. Non-linear tweaks (extra gravity on the way down, faster stops than starts) often feel more "physical" than accurate physics. *Swink ch. 8 pp. 152-154, ch. 12 pp. 187-190.*

## D. Restraint: when juice becomes noise

**P-15 Attention is a budget.** Attention is limited and selective, and people miss changes when their attention is elsewhere (inattentional and change blindness). Every effect spends some of that budget, so stacked effects compete with the threat or information the user actually needs. *Hodent ch. 4-5.*

**P-16 Polish cannot fix broken control.** Fix latency, lockouts, and unclear rules before adding effects. Polish can hide a bad mechanic for a while, and it makes later tuning harder. *Swink ch. 9; ch. 5 pp. 81-84.*

**P-17 Do not hide what the user needs.** Flashes, blur, particles, and shake must not hide the avatar, the threat, the cursor, or the text. Give every heavy effect a time limit and a way to reduce it. *Rogers 2e ch. 6 pp. 152-158; Schell Lens #62 pp. 259-260.*

**P-18 Comfort and access are part of feel.** Motion, flashing, and camera movement can cause sickness or seizures. Keep flashes to 3 per second or fewer and avoid saturated red flashes. Offer reduce-motion and shake-intensity settings, and never put information only in shake, colour, or sound. Low-health effects (blood, blur, vignette) must not hide the threat from a player who is already losing, and a camera takeover is signalled before it starts; in VR never take the camera at all. *Hodent ch. 3, ch. 11, 2e (2026) ch. 18; Rogers 3e ch. 4 "Platform, Technology and Scope", ch. 6; WCAG 2.3.1 and 2.3.3, Game Accessibility Guidelines, see RESEARCH.md.*

**P-19 Reward meaning, not every action.** Celebrating everything wears the celebration out. Big rewards should tie to real progress and mastery; rewards that pressure the player or play out as a cascade on every action undermine intrinsic motivation. A loss beat can show what went well (best combo, distance reached) so the player reappraises the run instead of quitting. *Hodent ch. 6 "Motivation", ch. 12 "Engageability".*

**P-20 Test with people, measure with tools.** The author's sense of feel is unreliable. Instrument latency and frame timing, then watch someone else play. *Swink ch. 5 pp. 81-84; Rogers 2e ch. 7; Hodent ch. 3.*

## E. The toy test

**P-21 It should be fun to poke with no goal.** Moving, jumping, or clicking should be pleasant in an empty room with no objective. If it isn't, work on the toy first. *Schell Lens #17 "Toy" p. 107; Swink ch. 1 pp. 4-5 (simulated space gives motion meaning).*

**P-22 Space gives motion meaning.** Speed and weight only read against references: ground texture, parallax, nearby objects, collisions. In games: dust on the ground, speed lines, objects that react when the player brushes past. *Swink ch. 1 pp. 4-5.*

**P-23 Classify the feel before tuning it.** Feel in the full sense needs three parts: real-time control, a simulated space, and polish. Something with only polish (a menu, a turn-based board, a slide deck) gets presentation goals, not control goals: promise "satisfying", never "tight". In games: say which parts a game has before scanning; a card game's feel moments are its UI and reveal moments. *Swink ch. 1.*

**P-24 Space and motion are tuned as a pair.** Obstacle size, gap width and pickup spacing only feel right against the avatar's speed, jump height and turning radius, and a challenge that leans on the weakest part of the control (precise landings in 3D, say) stays unpleasant whatever the polish. In games: write down the movement metrics, build spaces from them, and keep targets several avatar widths wide where the control is loose. *Swink ch. 5; ch. 15 pp. 248-249.*

**P-25 Rules are part of the feel.** Lives, hit points, rewards and caps change how control feels: one-hit death makes the avatar feel fragile, a high-value risky target pulls the player into close, skilled moves, a cap on shots alive turns range into fire rate. In games: when motion feels wrong, check the reward and damage rules before the tween curves. *Swink ch. 11; ch. 12 p. 198; ch. 14 p. 245; ch. 16 p. 295.*

**P-26 Choose direct or simulated per axis.** Each input can set a value directly (position, facing) or add force to a simulation (velocity, acceleration). Mixing them, one axis crisp and one with inertia, is often where a distinctive feel comes from; perception-driven hacks (setting velocity mid-jump, extra rules on top of physics) are fine when they read better. In games: list each input with what it modulates and whether it is direct or simulated. *Swink ch. 7; ch. 12 pp. 188, 199; ch. 13 p. 228; ch. 15 p. 248.*

**P-27 Build feel bottom-up.** Tune the core simulation in an empty space first, then build the world around its metrics, then reward the interactions players already enjoy, then link those rewards. Polish and scoring layered on an untuned core hide the problem (P-16). *Swink ch. 16 pp. 295-296; P-21.*

**P-28 Spoken lines are a system, not a sound.** Barks and voice lines come from a pool per situation and skip any line heard recently, so an often-hit moment never repeats word for word. Each line carries a priority: an important one cuts off a minor one already playing, a minor one waits or is dropped and never cuts off the important one. In games: give each bark trigger several lines, a no-repeat memory and a priority, and let at most one voice talk per speaker. *Gregory, Game Engine Architecture 2e (2014), sec. 13.6.2; P-09.*

**P-29 Tune feel from one frozen table; launches reset forgiveness together.** Feel numbers scattered through the code drift apart and nobody can tune them, so keep them in one named, read-only table (coyote, buffer, held-jump lift, launch squash, step heights) that a designer can read in one screen. Forgiveness windows are state, and state leaks: every event that throws the player upward (jump, spring, bounce, stomp, launch pad) clears the coyote timer, the jump buffer and any stomp flag in the same call, so a buffered press cannot fire a second jump on top of a spring. In games: a frozen constants object or resource, and one `launch(v)` helper that every upward path calls. *Thorson 2018 (forgiveness); P-05, P-27; pattern seen in a commercial web platformer, idea only.*

## Parameter starting points (tune by eye, then by playtest)

These are starting values that published talks and the books converge on, not rules. They are dated in RESEARCH.md.

| Technique | Start | Notes |
|---|---|---|
| Hit-stop | 2-6 frames (33-100 ms) light; 8-15 frames heavy | buffer input during it; scale with damage (P-04); shorten or skip on fast repeated hits (light weapons, high fire rate), since stacked freezes read as stutter; keep screen shake running through the freeze (2-4 px) so it reads as impact, not a dropped frame; snap to the contact pose with no easing, keyed about 0.02 s before the hit (R-20261119-1) |
| Screen shake (trauma model) | trauma += 0.2-0.5 per hit, decays 1.0-1.5 per s; offset = max × trauma² × noise | max offset 4-12 px (2D) or 0.1-0.3 units; rotation ≤ 3°; Perlin noise beats white noise (Eiserloh 2016) |
| Smooth follow (camera, UI, value) | each frame move a fraction f = 1 - exp(-rate × dt) toward the target; rate 8-15 per s | a fixed fraction per frame (x += (target - x) × 0.1) only holds at one frame rate: after 0.5 s it reaches 79% at 30 fps and 100% at 144 fps against 96% at 60. Use the exp form or run it in the fixed update (fixed-loop engines in Sung and others, Build Your Own 2D Game Engine, 2nd ed., ch. 3 and 7) |
| Camera kick | 2-6 px away from shot direction, recover over 80-150 ms | directional, unlike shake |
| Squash/stretch | 1.2-1.4 × along motion, inverse on the other axis, 80-150 ms back | preserve volume |
| UI press | scale 0.9-0.95 down 50 ms, back with ease-out-back 120-200 ms | plus a click sound |
| Pickup | pop scale 1.3 then 0, 150-250 ms; pitch climbs on a streak | P-09, P-11 |
| Damage flash | white or tint for 1-3 frames (≤ 100 ms) | never full screen faster than 3 Hz (P-18); Godot: `modulate` above 1 is the cheap flash, but it multiplies colour so dark pixels stay dark; a flash shader gives true white |
| Pitch variation | ±5-10% random per play | P-09 |
| Coyote time / jump buffer | 80-150 ms / 100-150 ms | P-05; attack and dash use the same buffer, expiry per press, echoes ignored; a held jump adds lift while the button stays down; every launch clears both timers (P-29) |
| Launch squash | scale 1 ± 0.3-0.35 on the launch frame, back in 80-150 ms | the same value for jump, spring and bounce keeps them reading as one family (P-29) |
| Step up / step down | step up about 0.6 units, snap down about 0.5, probed in 0.04-unit increments | small lips stop catching the feet; probe from high to low and keep the first clear height (P-05, P-29) |
| Particles on impact | 6-20 particles, 0.2-0.5 s life, pooled | P-15: fewer, bigger, shorter |
| Locomotion sync | animation rate = ground speed / clip stride speed; blend walk and run by speed | root motion or foot IK keeps feet planted; sliding feet read as weightless (P-07, P-14) |
| Knockback | reaction clip with 1-3 back steps whose travel matches the push | never slide an idle pose across the floor (P-03, P-07) |
| Attack wind-up / swing | wind-up at 0.6-0.8x clip speed, swing at 1.2-1.5x | no source gives numbers; a community start value (Reddit r/gamedev thread 1xajfgh, 2026), tune by eye (P-03) |
| Damage felt through controls | below about 35% armour or health: turn rate × 0.6-0.8 and aim offset = amp × sin(t × 2-4 Hz), amp growing as health falls | an alternative to camera shake: the hurt shows in handling, not in the view. Fades back as health returns; give it its own accessibility toggle (idea from GPU-Bandits, sloppysteaks69, no licence: idea only) (P-04, P-18) |
| Shield hits | up to 4 ripple rings at once, each from its own hit point, radius growing over 0.3-0.6 s while fading; holes and a warmer tint as strength drops | rings that replace each other read as one hit; keep a small ring buffer. Shader recipe: threewright-shaders (idea from GPU-Bandits) (P-06, P-07) |
| Bullet holes | persistent marks capped at 16-32, oldest recycled; glowing rim that cools over 1-2 s | lasting damage proves the hit landed. Shader recipe: threewright (idea from GPU-Bandits) (P-07) |
| Audio tied to motion | each frame, ramp a param (pitch, gain, filter) only when the new target differs from the last one sent by more than 1% | caching the last target keeps per-frame calls from stacking scheduled ramps (Web Audio `setTargetAtTime`); idea from voidstruck (P-09) |
| Scene transition | 250-500 ms ease-in-out fade or wipe; audio fade with it | P-03 |
| Flash-cut transition | 1 frame to near white, hold 0.1-0.25 s, then a linear fade over 0.4-0.65 s | masks a scene or renderer swap, or releases a charge; one flash per event, behind the flash toggle (P-18) |
| Streak pitch ladder | from the 3rd success in a row, +1 semitone a step (factor 2^(n/12)), capped at +4; both notes of a two-note cue move together; reset with the streak | `juice_scan.py` flags a counter whose cue never climbs (`streak_without_pitch_ladder`) (P-09, P-11) |
| Haptics per outcome | normal success a 12 ms tap, best result a 15-30-15 ms double pulse, failure one 25 ms buzz | distinct patterns let the hand read the result; behind the haptics toggle; the web vibrate call is missing on some mobile browsers, so never carry meaning by touch alone (P-18) |
| Timing bands | grade by absolute error at about 75 / 160 / 300 ms (best / good / ok, miss beyond); show the signed error as EARLY or LATE | the sign tells the player which way to correct; a best window of ±24-36 ms is tight and suits experts only (P-05, P-13) |
| Pattern shuffle | draw the next pattern at random but never repeat the last one (draw again on a match) | a plain random draw repeats often enough to read as a bug (P-09) |
| Crash hit-stop | heavy crash: freeze 130-150 ms (tiers 60 / 90 / 140 ms) with particles still moving at about 15% speed; flash at about 0.55 opacity fading over about 320 ms; shake halving every about 140 ms | slowed particles keep the freeze from reading as a dropped frame (P-04, P-07) |
| Near miss and graze | reward passes closer than about a quarter of a lane (sound, short FOV kick of 6-16 degrees decaying as exp(-4t)); hurt box about 0.08 m inside the art | track the smallest clearance per obstacle while it passes; `juice_scan.py` flags `no_near_miss` and `no_graze_margin` (P-05, P-11) |
| Stumble before death | the first glancing hit costs speed and plays a stumble; a second hit inside about 5.5 s ends the run | a tier between "fine" and "dead" turns one mistake into tension instead of a restart (P-05, P-25) |
| Charged action | a progress ring on the actor, tint and brightness built with an ease-in, charge length scaled to cost (about 2 s cheap, about 5 s irreversible) | the effect lasts exactly as long as the hold and clears within 1-3 frames of release or cancel (P-03, P-13) |
| Engine plume or thrust glow | first-order ease toward the target, time constant 110-130 ms each way; boost scales the same effect 2.5-3x | scaling one effect reads as more of the same thrust; a new effect reads as a different event (P-03, P-06) |
| HUD numbers that change continuously | update text at about 10 Hz in rounded steps while visuals run every frame; typewriter text about 30 characters a second on the same tick | per-frame digits flicker and cannot be read (P-13) |
| Refused action | answer every refused input with its reason in a fixed caption slot ("not enough energy") and a short error cue | silence reads as a dropped input (P-01, P-13) |
| Muzzle flash at rapid fire | flash life a little longer than the fire interval (for example 0.13 s against 0.09 s) so it reads as a steady glow | above about 3 shots a second a per-shot flash strobes; a large flashing area counts against the 3 Hz limit, a small muzzle area much less (P-15, P-18) |
| Invisible aim assist | forgive with a larger hit sphere on targets, never by bending visible bullets; tune the pad with a bot, since hit rate can jump sharply near a threshold (a few units of pad doubled it in one measured case) | bent bullets were noticed from a chase camera; a generous pad was not (P-05) |
| Chase camera comfort | camera up vector follows about 35% of the vehicle's roll; FOV widens up to +14 degrees with speed, eased at about 4 per s; follow rate 6-7 per s in the exp form | full roll follow causes motion sickness (P-18) |
| Side-view vehicle camera | look ahead 0.4 x speed, clamped to -17% / +22% of view width; zoom out up to 10% with speed; follow 4.4 per s, zoom at about half that | landing shake by airtime tier in the ratio 1 : 2 : 3.5 : 5 (P-07, P-22) |
| Shake as one additive value | add per event, cap the sum (about 2.6 x the base amplitude), decay exponentially (about 6.5 per s, half-life about 0.1 s) | a variant of the trauma model above; the cap stops stacked events from throwing the view (P-15) |
| Distance falloff for sound | gain = base x max(0, 1 - d / r), r = half the larger screen side; base levels 0.18 (frequent, remote) to 0.38 (rare, big); a low-resource alarm every 1.2 s below 25% | start a looped sound once (ignition, then sustain) instead of on every frame; `juice_scan.py --audio` checks all three (P-09) |
| Killing blow keeps its feedback | hold the win screen until the last hit's feedback has finished (about 0.9 s) | in one measured turn-based game 17% of damage numbers never showed: every one was the killing blow, cut by the result screen (P-04, P-11) |
| Feedback that survives re-render | start hit flashes on elements the next render keeps (or re-apply after render), never on nodes about to be replaced | a flash class on a node that a full re-render swaps out never plays; it looks fine in review and only shows when measured (threewright `tw feel`) (P-01) |
| Feedback keyed to damage applied | size numbers, shake and impact sound by the damage after block and armour, not the incoming amount | a fully blocked hit that still shakes and shows a number lies to the player (P-04, P-25) |
| Turn-based hit timing | release to impact number about 220 ms; shake only when the player is hurt, about 320 ms; damage number about 0.9 s with a 70 px rise | turn-based games have time for longer feedback, but keep input open during it (P-03, P-23) |
| Staggered resolution | resolve a batch (dice, cards, loot) one item at a time about 100 ms apart, each landing with a small settle; the running total pops (a brief scale-up, then back) on every change | `juice_scan.py` flags a loop that fires feedback for every item in one frame (`batch_resolve_without_stagger`); cap a long run near 600 ms by stepping faster, and give the last item the biggest response (P-03, P-11) |
| Reward reveal | anticipation glow that grows for about 150 ms, then a flat silhouette in the rarity's tint for about 100 ms, a 100 ms cross-fade to the item, about 350 ms in all; several rewards reveal together | the tint tells the rarity before the item is readable, so the player feels the tier first (P-03, P-11, P-13) |
| Turn-based kill | the defeated sprite turns into a flat white silhouette for about 150-170 ms, then breaks into puffs or dissolves over about 2 frames; no camera shake | a kill without shake keeps shake meaning "you are hurt"; the silhouette is longer than a damage flash because it marks an ending, not a hit (P-11, P-12) |

## Adding a principle

Give it the next free `P-` id, write it so it holds outside games, cite a source with a page or section, and log the change in [CHANGELOG.md](../CHANGELOG.md). Never renumber existing IDs; reports in the wild cite them.
