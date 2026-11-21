# Log

Append-only. One line per operation: `## [YYYY-MM-DD] op | title` where op is one of add, update, supersede, verify, verify-failed, prune, handoff, index. Newest at the bottom. Never edited, only appended; this is the history the entries themselves do not carry.

## [2026-10-27] init | scaffolded
## [2026-10-27] update | AGENTS.md pointer added
## [2026-10-27] add | solution: Skill undertriggers on small repos and direct edit requests
## [2026-10-27] add | decision: Publish game-juice as a public repository
## [2026-10-27] update | Published as a public repository; HANDOFF rewritten

## [2026-11-12] docs | GitHub wiki (9 pages, 1.3.5), social preview, Works-with sections on sfxwright/ludowright/grindwright/madnesswright wikis

## [2026-11-18] update | 1.3.9: damage through controls, shield ripples, bullet holes, audio param dedupe (technique-harvest batch G; GPU-Bandits and voidstruck ideas only)

## [2026-11-19] update | 1.3.10: hit-stop notes gain shake through the freeze and snap into contact (technique-harvest PA20 P5, patch-gg/pixelfx MIT)

## [2026-11-19] update | 1.3.11: P-29 frozen feel table and launch timer resets; juice_scan 1.2.0 findings scattered_feel_constants and launch_without_timer_reset; fixture web-platformer

## [2026-11-20] update | 1.3.12: juice_scan 1.3.0 findings hit_stop_ignores_hit_rate (freeze vs gap between hits) and anim_speed_not_tied_to_move_speed (foot sliding); fixtures godot-wave-hero (trips both) and unity-wave-hero (tuned, trips neither) (technique-harvest #33, post 1xajfgh)

## [2026-11-20] update | 1.4.0: juice_scan 1.4.0 reads inline <script> of .html/.htm; findings streak_without_pitch_ladder, no_near_miss, no_graze_margin, reduce_motion_not_applied; --audio pass (audio_no_falloff, audio_loop_restart, audio_no_headroom); coyote/buffer only when jump is bound to an input; 13 fixtures; 23 principles rows (technique-harvest web-game round, written fresh)
## [2026-11-20] update | 1.4.1: book round (Campos, Godot 4 patterns, 4.3): P-05 buffers attack and dash with per-press expiry and a held-or-tap decision; godot.md traps for freed parents, shared ShaderMaterial flash (reader extension, check on 4.3+) and autoload music with cross-fade. Noted only: a juice-scan check for AnimationTree transitions that wait for clip end (no rules list to fit, no project to test).
## [2026-11-21] update | 1.5.0: juice_scan finding batch_resolve_without_stagger (2 fixtures) and three parameter rows (staggered resolution, reward reveal, turn-based kill) measured from a turn-based dice game's store clips, tier A only, nothing copied
