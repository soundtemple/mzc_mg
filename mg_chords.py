@OnLoad
	SetShortName {@/_@} 
	ResetNoteStates FALSE // #reset the locker with the value FALSE!
	mode = 0 //# See @HandleModeChange for modes
	songmode = 0 //# 0:Playsong 1:SceneLocked 2:ChordLocked
	SetMetroPPQN = 4
	ppqn = 4 
	scene_change_requested = -1 //# on pad down has next scene number
	chord_change_requested = -1 //# on pad down has next chord number
	scene_change_chord_reset = TRUE //# Goto chord 0 when user changes scene
	in_mode_select = FALSE //# Toggle for changing modes mode
	number_of_modes = 16 //# Change in operational mode 
	chords_out_octave = 3 //# base octave(3) for chords out (not harmony)
	allow_mode_chg_playbk = TRUE //# Mode change during playback
	return_to_song_mode_requested = FALSE //# used for switching on new bar 
	rec_chord_note_count = 0 //# recording notes in chord slot
	use_turn_around = TRUE //# last chord as turn around on last bar of scene
	//# used for LED feedback
	send_cc_back_to_knobs = FALSE 
	knob1_cc = 121 //# Used for sending midi feedback to LED knobs
	knob2_cc = 122
	knob3_cc = 123
	knob4_cc = 124
	ShowLayout 2
	LabelPads {MOZAIC KOMPOSER}
	Call @TransposeCalcArrays
	Call @InitKnobVariables //# All knob settings on start
	Call @SetupChordsScenes
	Call @SetupKnobset0
	Call @SetupLayout
	Call @ChangeScenePreset //# load preset 0 into scene 0
@End

@InitKnobVariables
	//# Any knobset knob should have a setting here
	scn_duration = 0 
	scn_txpose = 0 
	scn_preset = 1
	scn_mh1_mode = 0
	scn_mh2_mode = 0
	scn_mh3_mode = 0 
	scn_mh4_mode = 0
	scn_out1_on = 1 //# 0 for off default ON
	scn_out2_on = 1
	scn_out3_on = 1
	scn_out4_on = 1
	num_sc_presets = 11
	num_sc_mh_modes = 8 //# Harmonization rules for incoming midi
	//# modes: Off, ChordOnly, Round2Chord,  NonChord, Bass, Root, 3rd, 5th, Thru
	chrd_duration = 0
	chrd_inversion = 0
	chrd_bass = -1
	slct_chord_root = 0 //# Select chord mode only
	slct_chord_type = 0 //# Select chord mode only
	slct_chord_inversion = 0 //# Select chord mode only
	slct_chord_bass_note = -1 //# Select chord mode only
	
	//# Construct chords
	constructed_root = 0
	constructed_3rd = 2
	constructed_5th = 1
	constructed_7th = 3
	
	//# Midi channel options Mozaic uses 0-15 - we display 1-16
	//# Record Chords Ch [0]
	//# EXT MIDI IN CH's [1-4]
	//# INT MIDI IN CH's [5-8]
	//# Midi OUT CH's' [9-12] for outgoing chords. 
	//# ie Direct to arp or instrument
	
	midi_channels_used = [3,4,5,6,7,8,9,10,11,12,13,14,15]
	
	//# enable chords to be saved 
	FillArray sort_list, 0 //# empty array for sorting chord notes as arrive

	//# Selecting chords from types mode
	num_chord_types = 11 //# Chord types for select mode
	chord_types[0] = [4,7,-1] //# Major
	chord_types[5] = [3,7,-1] //# Minor
	chord_types[10] = [3,6,-1] //# Diminished
	chord_types[15] = [4,8,-1] //# Augmented
	chord_types[20] = [2,7,-1] //# Sus2
	chord_types[25] = [5,7,-1] //# Sus4
	chord_types[30] = [3,7,8] //# Minor 6th
	chord_types[35] = [4,7,9] //# Major 6th
	chord_types[40] = [3,7,10] //# Minor 7th
	chord_types[45] = [4,7,10] //# Dom 7th
	chord_types[50] = [4,7,11] //# Major 7th

	//# Intervals for constructing chords
	3rd_intervals = [2, 3, 4, 5] //# sus2, min, maj, sus4
	5th_intervals = [6, 7, 8] //# dim (b5), P5, aug (#5)
	7th_intervals = [-1, 8, 9, 10, 11] //# min6 (b6), maj6, min7 (b7), maj7	
	
	//# Color Scheme
	col_scene = 2
	col_sel_scene = 4
	col_chord = 2
	col_pattern = 2
	col_pattern_pending = 3
	col_sel_chord = 4
	col_rec_chord = 1 //# in record mode
	col_chord_waiting = 1 //# selected waiting for notes
	col_pending = 3
	loop_col = 6
	col_del_chord = 1
	col_mode_select = 6 //# Mode selection buttons
	col_unused = 0

@End

@SetupChordsScenes
	current_scene = 0 // #0-7 Pads 0-7
	current_chord = 0 // #0-7 Pads 8-15
	num_scale_types = 4
	
	//# scene config:
	//# [duration, txpose, preset, mg1-4_modes, out_ch1-4, pgmchg]
	//# MG Modes determine how harmonization occurs per scene
	sc_txp_slot = 1
	sc_preset_slot = 2
	sc_mh1_slot = 3 //# harmonization mode
	sc_mh2_slot = 4
	sc_mh3_slot = 5
	sc_mh4_slot = 6
	sc_och1_slot = 7 //# midi out ch per scene x4
	sc_och2_slot = 8
	sc_och3_slot = 9
	sc_och4_slot = 10
	sc_pgmchg_slot = 11
	sc_size = 15 //# ^ above slots + duration = 11 + 4 spare for even sizing 
	
	//# chord = [note1, note2, note3, note4, duration, inv, bass]
	dur_slot = 4 //# fixed location for duration
	inv_slot = 5
	bass_slot = 6
	patt_slot = 7
	
	//# TODO:- THIS MAYBE ADD TO ON UNASSIGNED......
	
	//# Create empty chord and scene arrays
	for s = 0 to 7 
		//# Create 8 scene arrays in scene_bank
		scene_bank[s*sc_size] = [0,6,1,0,0,0,0,0,0,0,0,-1]
		for c = 0 to 7
			//# Create 8 chord arrays for each scene
			chord_bank[(s*100) + (c*10)] = [-1, -1, -1, -1, 0, 0, -1,-1]
		endfor
	endfor
	
	//# indexing them by scene size (sc_size). Sample scenes
	scene_bank[0] = [4,6,1,0,0,0,0,0,0,0,0,-1] 
	//# eg scene2 ... scene_bank[sc_size * sc#(0-7)] = [2,6,0,0,0,0,0,1,1,1,1]
	
	//# Example chords: increment in 10's in each scene, new scenes on the 100
	//# chord_bank[0] = [60, 64, 67, 71, 4, 0, -1] //# Scene1 Chord 1
	//# chord_bank[10] = [67, 71, 74, 77, 8, 0, -1] //# Scene1 Chord 2
	//# chord_bank[100] = [65, 69, 72, 76, 8, 0, -1] //# Scene2 Chord 1
	//# chord_bank[110] = [69, 72, 76, 79, 4, 0, -1] //# Scene2 Chord 1
	
	//# Scale definitions for midi in key, scale handling
	//# Allowed scales for midi in
	allowed_scales = [1,2,3,4] 
	//# incoming midi key, scale. default C Major
	selected_midi_in_root = 0 // # root note -11 (C-B) Set in Knobset5
	selected_midi_in_scale = 0 // #see allowed_scales  
	midi_in_scales[10] = [0,2,4,5,7,9,11]  //# major
	midi_in_scales[20] = [0,2,3,5,7,8,10] // #minor_nat
	midi_in_scales[30] = [0,2,3,5,7,9,10]  // #minor_mel
	midi_in_scales[40] = [0,2,3,5,7,9,11]  // #minor_har
	Call @GetMidiInScale
	
	//# Setup Chord notes out - Options for how notes sent out
	cno_labels = [-1,0,1,3,5,7,15,135,1357,150,1350]
	cno_choices = 10 //# len(cno_labels) - 1
	cno_degrees[0] = [-1,-1,-1,-1]
	cno_degrees[4] = [0,-1,-1,-1]
	cno_degrees[8] = [1,-1,-1,-1]
	cno_degrees[12] = [3,-1,-1,-1]
	cno_degrees[16] = [5,-1,-1,-1]
	cno_degrees[20] = [7,-1,-1,-1]
	cno_degrees[24] = [1,5,-1,-1]
	cno_degrees[28] = [1,3,5,-1]
	cno_degrees[32] = [1,3,5,7]
	cno_degrees[36] = [0,1,5,-1]
	cno_degrees[40] = [0,1,3,5]
@End

@GetMidiInScale
	PresetScale allowed_scales[selected_midi_in_scale]
	SetRootNote selected_midi_in_root
	// #create an array with the notes of selected key scale
	scale_loc = allowed_scales[selected_midi_in_scale] * 10
	for scale_degree = 0 to 6
		// #ms is incoming_midi_scale
		midi_in_scale_notes[scale_degree] = (selected_midi_in_root + midi_in_scales[scale_loc + scale_degree]) % 12 
	endfor
	Log {Passing notes: }, (NoteName midi_in_scale_notes[1]), { }, (NoteName midi_in_scale_notes[3]), { }, (NoteName midi_in_scale_notes[5])
	Log {Play chord notes with: }, { }, (NoteName midi_in_scale_notes[0]), { }, (NoteName midi_in_scale_notes[2]), { }, (NoteName midi_in_scale_notes[4]), { }, (NoteName midi_in_scale_notes[6])
	Log {Incoming melody scale: }, RootNoteName, { }, ScaleName
@End

@OnHostStart
	//# Start beat count on same beat as host
	//# In AUM getting HostBeat to start on 0 seems flaky
	//# Fixed by BramBos in June2020
	Log HostBar, { : }, HostBeat, { = }, (HostBeatsPerMeasure * HostBar) + HostBeat
	if (HostBeat = 0) and (HostBar = 0)
		//# starting playback from beginning		
		chord_beat_count = -1
		scene_beat_count = -1
		scene_changed = FALSE
		if (songmode = 0)
			current_scene = 0
			current_chord = 0
		elseif (songmode = 1)
			current_chord = 0
		endif
		if mode > 2 
			//# No chord Rec, Select or Delete in playback
			mode = 0
		endif
	else
		//# continuing playback
		//# Could do nothing and allow continue with vars unchanged
		//# but in case use can jump timeline we are doing this to keep HostBeat aligned and chord/Scene at same relative positions.
		scene_completed_bars = scene_beat_count % HostBeatsPerMeasure
		chord_completed_bars = chord_beat_count % HostBeatsPerMeasure
		scene_beat_count = scene_completed_bars + HostBeat
		chord_beat_count = chord_completed_bars + HostBeat
	endif
	Log {---- Host Started ----}
	Call @SetupLayout
	Call @SendOutChordNotes //# Midi OUT channel processing for chords
@End

@OnHostStop
	Call @SetupLayout
	Call @ResetBeatCounts
	Call @TurnOffChordNotes
	Log {---- Host Stopped ---- }, scene_beat_count, { - }, chord_beat_count 
	Call @SetupLayout
@End 

@ResetBeatCounts
	//# Re-start when mode or scene changes
	scene_beat_count = 0
	chord_beat_count = 0
	//# Log {Beat counts reset}
@End

@OnMetroPulse
@End

@OnNewBar
	Log {--- new bar ---}
@End 

@OnNewBeat
	//# increment beat counts xonb
	scene_beat_count = scene_beat_count + 1
	chord_beat_count = chord_beat_count + 1
	
	//# Handle Scene and Chord changes
	current_scene_duration = scene_bank[current_scene * sc_size]  * HostBeatsPerMeasure //# IN BEATS!
	chord_slot = (current_scene * 100) + ((current_chord) * 10)
	current_chord_duration = chord_bank[chord_slot + dur_slot]
	
	current_host_beat = (HostBar * HostBeatsPerMeasure) + HostBeat
	
	//# Log {Scene beats left: }, current_scene_duration - scene_beat_count
	//# Log {Chord beats left: }, current_chord_duration - chord_beat_count
	time_for_turnaround = FALSE
	if use_turn_around
		Call @TimeForTurnaround
	endif
	
	//# Chord progressop -- Order of operations
	if (scene_change_requested > -1) and (HostBeat = 0)
		//# user requested scene change and its a new bar (& return to song)
		//# Log {Handling scene change request. It a new bar}
		Call @HandleSceneChange
	elseif (scene_beat_count >= current_scene_duration)
		//# its time to increment scene
		Call @HandleSceneChange
	elseif (chord_change_requested > -1)
		//# User requested chord change & its a new beat
		Call @HandleChordChange
	elseif time_for_turnaround
		Call @HandleChordChange
	elseif (chord_beat_count >= current_chord_duration)
		Call @HandleChordChange
	endif
	Call @LogCurrentInfo
@End

@TimeForTurnaround
	//# Under these conditions jump to last chord for 1 bar before scene change
	//# 2nd last chord in scene has no duration. Last chord has 4 beat duration
	//# Mode must be in song or scene lock
	//# must be 1 bar before scene ends
	//# Log {**** CHECKING TURN AROUND ****}
	chord6 = chord_bank[(current_scene * 100) + 60 + dur_slot]
	chord7 = chord_bank[(current_scene * 100) + 70 + dur_slot]
	//# Log {Chord6 dur: }, chord6, { Chord7 dur: }, chord7
	//# Log {SBC: }, scene_beat_count, { SC_DUR: }, current_scene_duration, { HBPM: }, HostBeatsPerMeasure
	//# Log scene_beat_count, { === }, (current_scene_duration - HostBeatsPerMeasure)
	if (songmode <= 1) and (chord6 = 0) and (chord7 = 4) and (current_chord <= 5) and (scene_beat_count = current_scene_duration - HostBeatsPerMeasure)
		time_for_turnaround = TRUE
		Log {Its TURN AROUND TIME!!}
	endif
@End

@HandleSceneChange
	//# Work out which scene is next xhsc
	scene_changed = TRUE
	if scene_change_requested > -1
		current_scene = scene_change_requested
		if return_to_song_mode_requested
			songmode = 0
		else
			songmode = 1 //# lock to scene if user requests
		endif
		return_to_song_mode_requested = FALSE
	elseif (songmode > 0)
		current_scene = current_scene
	elseif (current_scene = 7) //# End of song 
		current_scene = 0 //# TODO: Handle end of song
	elseif scene_bank[(current_scene * sc_size) + sc_size] <= 0
		//# also song end
		current_scene = 0 //# no duration in next scene return to beginning
	else
		current_scene = current_scene + 1 //# Going to next
	endif
	//# Send a program change message on new scene 
	pgm_chg_num = scene_bank[(current_scene * sc_size) + sc_pgmchg_slot]
	if pgm_chg_num >= 0
		chA = midi_channels_used[1]
		chB = midi_channels_used[2]
		chC = midi_channels_used[3]
		chD = midi_channels_used[4]
		Log {Sending Program change: }, pgm_chg_num 
		SendMIDIProgramChange chA, pgm_chg_num
		SendMIDIProgramChange chB, pgm_chg_num+10
		SendMIDIProgramChange chC, pgm_chg_num+20
		SendMIDIProgramChange chD, pgm_chg_num+30
	endif
	Call @ResetBeatCounts
	Log {----- SCENE CHANGE -----}, {S}, current_scene+1
	Call @HandleChordChange //# Scene change effect chord change
@End

@HandleChordChange
	//# Work out what the next chord is xhcc
	chord_slot = (current_scene * 100) + ((current_chord) * 10)
	if (chord_change_requested > -1)
		current_chord = chord_change_requested
		chord_change_requested = -1 //# reset request flag
		if songmode <= 2
			songmode = 2 //# Lock to chord if user requests chord change
		endif
	elseif (scene_change_requested > -1) //# also handle chord change
		//# Log {Scene change requested handling chord reset}
		current_chord = 0
		scene_change_requested = -1
		scene_changed = FALSE
	elseif scene_changed
		//# reset chord to 0 on scene change if songmode < 2
		if (songmode <= 1)
			Log {Scene changed reset chord to 0}
			current_chord = 0
		endif
		scene_changed = FALSE
	elseif (songmode = 2) //# Loop current chord & Scene
		current_chord = current_chord
	elseif (current_chord = 7) //# Wrap playback
		current_chord = 0
	elseif (time_for_turnaround)
		//# play last chord for one bar as a turn around before scene change
		current_chord = 7
	elseif (chord_bank[(chord_slot+10) + dur_slot] <= 0)
		current_chord = 0 //# no duration no next chord (chord_slot + 10)
	else
		current_chord = current_chord + 1
	endif
	chord_beat_count = 0 //# reset chord beat count on new chord
	
	//# send cc11 per chord message for pattern change in step poly arp
	chord_slot = (current_scene * 100) + ((current_chord) * 10)
	spa_pattern = chord_bank[chord_slot + patt_slot]
	if spa_pattern >= 0
		if spa_pattern = 16 //# select a random pattern
			spa_pattern = Random 0, 15
		endif
		Log {Changing SPA pattern }, spa_pattern
		SendMIDICC 0, 21, spa_pattern
	endif  
	if HostRunning
		Call @SendOutChordNotes
	endif
	//# Label pads
	LabelPads {Scene: }, current_scene+1, { Chord: }, current_chord+1
	Log {----- CHORD CHANGE -----}, {C}, current_chord+1
	Call @SetupLayout
@End

@LogCurrentInfo
	chord_slot = (current_scene * 100) + ((current_chord) * 10)
	current_chord_duration = chord_bank[chord_slot + dur_slot]
	current_scene_duration = scene_bank[current_scene * sc_size]
	Log {Playing: Scene: }, current_scene+1, { }, scene_beat_count+1, {/}, (current_scene_duration * HostBeatsPerMeasure), { beats}, { Chord:}, current_chord+1, { }, chord_beat_count+1, {/}, current_chord_duration, { beats}, { Mode: }, mode, { HostBeat: }, HostBeat+1
@End

@OnPadDown
	//# Splitting this event into separate handlers xopd
	if in_mode_select and (LastPad <= (number_of_modes - 1))
		if (HostRunning and (LastPad > 0) and NOT allow_mode_chg_playbk)
			Exit //# Only return to song allowed in playback
		elseif (LastPad=4 or LastPad=5 or LastPad=14)
			Exit //# Not in use
		elseif (HostRunning and (LastPad=8 or LastPad=9 or LastPad=11 or LastPad=12))
			Exit //# Not allowed in playback
		elseif (LastPad = 7)
			Call @LogCurrentSceneToPresetFormat
		elseif (LastPad>=8 and LastPad<=13)
			//# midi setup modes - dont exit in_select_mode
			for i = 0 to 15
				LatchPad i, NO
			endfor
			mode = LastPad
			LatchPad mode, YES
		elseif (HostRunning and LastPad=0)
			//# Return to song mode requested
			return_to_song_mode_requested = TRUE
			scene_change_requested = current_scene
			in_mode_select = FALSE
			songmode = 0
			mode = 0
			ColorPad 0, col_pending
			ColorPad 8, col_pending
		else
			mode = LastPad
			Log {MODE:}, mode
			in_mode_select = FALSE
		endif
		Call @HandleModeChange
		Call @SetupLayout
		if (LastPad = 7)
			LabelPads {Scene preset data printed. Check log!}
		endif
	//# NOT IN MODE SELECT......
	elseif NOT in_mode_select
		//# handle mode actions if record or reset else do knob scene change
		Call @OnPadDown_SceneChordChange
		Call @OnPadDown_KnobSetSelect
		if (mode = 3) and (LastPad > 7)
			Call @SetupLayout
			rec_chord_note_count = 0
			LabelPad current_chord+8, {...waiting}
			ColorPad current_chord+8, col_chord_waiting
		elseif (mode = 6) //# COPY/PASTE
			Call @CopyPaste
		elseif (mode = 15) and (LastPad <= 7) //# reset mode
			Log {Reset scene called}
			Call @ResetScene   
		elseif (mode = 15) and (LastPad >= 7)
			Log {Reset chord called}
			Call @ResetChord
		endif
		if NOT HostRunning and (LastPad >= 8)
			Call @SendOutChordNotes
		endif
	endif
@End

@OnPadUp
	if NOT HostRunning and (LastPad >= 8)
			Call @TurnOffChordNotes
	endif
@End

@HandleModeChange
	//# Handle Labels
	if mode = 0
		LabelPads {PLAYBACK: Loop whole song}
		songmode = 0
	elseif mode = 1
		LabelPads {+CHORDS SELECT: Select chord, THEN set root, type, bass note}
		songmode = 2 //# Lock to chord
		Call @SetupKnobset2
	elseif mode = 2
		LabelPads {+CHORDS CONSTRUCT: Use knobs to build chord}
		songmode = 2 //# Lock to chord
		Call @SetupKnobset6
	elseif mode = 3
		LabelPads {+CHORDS RECORD: Select record channel, chord pad, then play chord notes}
		songmode = 2 //# Lock to chord
		Call @SetupKnobset1
	elseif mode = 6
		//# Copy/Paste pad hit so 'copy' current scene and chord
		//# in_select_mode = FALSE its already been exited 
		songmode = 2 //# Lock to chord
		copied_scene = current_scene
		copied_chord = current_chord
		Log {Copied current s}, current_scene+1, { chord }, current_chord+1
		LabelPads {Current scene & chord copied. Select a scene or chord slot to paste to}
	elseif mode = 8
		if NOT HostRunning
			LabelPads {EXT MIDI Scale: Defines how EXT midi notes are transposed to chord notes}
			Call @SetupKnobset5
		endif
	elseif mode = 9
		if NOT HostRunning
			LabelPads {EXT MIDI IN/OUT CHANNELS: Midi harmonized to chord progresssion.}
			Call @SetupKnobset4
		endif
	elseif mode = 10
		LabelPads {EXT MIDI MODES:  0.OFF 1.Chord, 2.RoundToChord, 3.+NonChord, 4.Bass, 5.Root, 6.Third, 7.Fifth 8.THRU}
		//# Harmony modes: Off, ChordOnly, RoundToChord, +Passing, Bass, Root, 3rd, 5th, Thru
		songmode = 1 //# Lock to scene
		Call @SetupKnobset3
	elseif mode = 11
		if NOT HostRunning
			LabelPads {MG SEQUENCE: MG Sequences harmonized to chord progression.}
			Call @SetupKnobset8
		endif
	elseif mode = 12
		if NOT HostRunning
			LabelPads {CHORDS OUT: Midi channels}
			Call @SetupKnobset7
		endif
	elseif mode = 13
		if NOT HostRunning
			LabelPads {CHORDS OUT: Note type select}
			Call @SetupKnobset9
		endif
	elseif mode = 15
		LabelPads {DELETE: Select a scene or chord slot to reset}
	endif
	if send_cc_back_to_knobs
		Call @SendMidiCCBackToKnobs
	endif
@End

@OnPadDown_SceneChordChange
	//# handle scene/chord change xopds
	if (LastPad >= 0 and LastPad <= 7)
		//# Scene change
		Log { SCENE CHANGE REQUESTED }
		scene_change_requested = LastPad
		if NOT HostRunning //# immediate change else newbeat/bar handles
			Call @HandleSceneChange 
		endif
	elseif (LastPad >= 8 and LastPad <= 15) 	
		//# User Chord change 
		Log { CHORD CHANGE REQUESTED }
		chord_change_requested = LastPad - 8 //# chrd 0-7
		if NOT HostRunning //# immediate change else newbeat/bar handles
			Call @HandleChordChange 
		endif
	endif
	Call @SetupLayout	
@End

@OnPadDown_KnobSetSelect
	//# choose a knob set based on pad type
	if LastPad <= 7 and (NOT in_mode_select)
		if (mode = 1)	 //# Select quick chords 2 knobs
			Call @SetupKnobset2
		elseif (mode = 2) //# Construct chords 4 knobs
			Call @SetupKnobset6
		elseif (mode = 7)
			Call @SetupKnobset3 //# SCENE Midi IN Modes
		else
			Call @SetupKnobset0
		endif
	elseif LastPad >= 8 and NOT in_mode_select
		if (mode = 1)	
			Call @SetupKnobset2
		elseif (mode = 2) //# Construct chords 4 knobs
			Call @SetupKnobset6
		else
			Call @SetupKnobset1
		endif
	endif
	if send_cc_back_to_knobs
		Call @SendMidiCCBackToKnobs
	endif
@End

@SendMidiCCBackToKnobs
	//# Update controller knob vals with midi cc
	//# Log {Updating Twister... }, Round GetKnobValue 0
	SendMidiCC 0, knob1_cc, Round GetKnobValue 0
	SendMidiCC 0, knob2_cc, Round GetKnobValue 1
	SendMidiCC 0, knob3_cc, Round GetKnobValue 2
	SendMidiCC 0, knob4_cc, Round GetKnobValue 3
@End


@SaveSelectedChordPad
		//# save to pad in select mode once chord params chosen on knobs 
		
		//# chord to be updated
		chord_slot = (current_scene * 100) + ((current_chord) * 10)
		
		//# Set fields not updated here. Default if new else saved
		chrd_duration = 4 //# default value for new chord
		if chord_bank[chord_slot + dur_slot] > 0
			chrd_duration = chord_bank[chord_slot + dur_slot]
		endif
		chord_bank[chord_slot + dur_slot] = chrd_duration
		
		//# Only update changed fields
		if root_updated or type_updated
			//# Get chord_bank location and intervals for new chord
			chord_root = slct_chord_root
			chord_type_slot = slct_chord_type * 5 //# array saved in groups 5
			chord_3rd = (slct_chord_root + chord_types[chord_type_slot])
			chord_5th = (slct_chord_root + chord_types[chord_type_slot + 1])
			chord_7th = (slct_chord_root + chord_types[chord_type_slot + 2])
			//# A triad not a tetrad
			if chord_types[chord_type_slot + 2] = -1 
				chord_7th = -1
			endif
			//# update chord values in chord_bank
			chord_bank[chord_slot] = chord_root
			chord_bank[chord_slot + 1] = chord_3rd
			chord_bank[chord_slot + 2] = chord_5th
			chord_bank[chord_slot + 3] = chord_7th
			root_updated = FALSE
			type_updated = FALSE
		elseif inv_updated
			chrd_inversion = slct_chord_inversion	
			chord_bank[chord_slot + inv_slot] = chrd_inversion
			inv_updated = FALSE
		elseif bass_updated
			chrd_bass = slct_chord_bass_note
			chord_bank[chord_slot + bass_slot] =  chrd_bass
			bass_updated = FALSE
		endif	
		
		//# Update chord pads
		Log {Chord notes }, chord_root, { }, chord_3rd, { }, chord_5th, { }, chord_7th
		Log {7th VAL: }, chord_bank[chord_slot + 3], { BASS VAL: }, chord_bank[chord_slot + bass_slot]
		chrd_to_label = current_chord+8
		Call @LabelChordPad
@End

@SaveConstructedChordPad
	//# save to pad in construct mode  			
	//# chord to be updated
	chord_slot = (current_scene * 100) + ((current_chord) * 10)
	
	//# Set fields not updated here. Default if new else saved
	chrd_duration = 4 //# default value for new chord
	if chord_bank[chord_slot + dur_slot] > 0
		chrd_duration = chord_bank[chord_slot + dur_slot]
	endif
	chord_bank[chord_slot + dur_slot] = chrd_duration
	
	chord_3rd = constructed_root + 3rd_intervals[constructed_3rd]
	chord_5th = constructed_root + 5th_intervals[constructed_5th]
	if constructed_7th > 0
		chord_7th = constructed_root + 7th_intervals[constructed_7th]
	else
		chord_7th = -1
	endif
	//# Save notes to chord slot
	chord_bank[chord_slot] = constructed_root
	chord_bank[chord_slot + 1] = chord_3rd
	chord_bank[chord_slot + 2] = chord_5th
	chord_bank[chord_slot + 3] = chord_7th

	
	//# Update chord pads
	Log {Root: }, (NoteName, constructed_root)
	Log {3rd interval: }, 3rd_intervals[constructed_3rd]
	Log {5th interval: }, 5th_intervals[constructed_5th]
	Log {7th interval: }, 7th_intervals[constructed_7th]
	Log {Chord notes }, constructed_root, { }, chord_3rd, { }, chord_5th, { }, chord_7th
	Log {7th VAL: }, chord_bank[chord_slot + 3], { BASS VAL: }, chord_bank[chord_slot + bass_slot]
	chrd_to_label = current_chord+8
	Call @LabelChordPad
@End

@OnMidiNoteOn
	//# Process incoming midi to be re-harmonized (if not Rec Chords mode)
	//# Log {Midi received on CH: }, MIDIChannel, { note: }, MidiNote
	//# -1Off 0Chord 1Round 2+NonChord 3Bass 4Root 5Third 6Fifth 7thru
	for i = 1 to 8
		if MIDIChannel = midi_channels_used[i] and not (mode = 3)
			if i <= 4
				//# What is the scene harm. mode for this channel scene array slot 4-7
				sc_harm_mode = scene_bank[(current_scene * sc_size) + i + 2]
			else
				//# ch's 5-8 no mode select so default to 
				sc_harm_mode = 2 //# +NonChord = All Scale notes get harmonized
			endif
			//# Log {sc_harm_mode for harmony note is: }, sc_harm_mode, { Call CHN}
			//# Need to be able to call ConvertToHNotes to switch held notes 
			//# over chord change where there in no MidiNote
			midi_note = MidiNote
			midi_channel = MIDIChannel
			Call @ConvertToHarmonyNotes
		endif
	endfor
	
	//# Record chords from the channel set 
	if (MIDIChannel = midi_channels_used[0]) and (mode = 3)
		Call @HandleRecordNotes
	endif
@End

@SendOutChordNotes
	//# Send out chord notes based on Midi OUT Channel settings
	//# Also send out chord notes if chord pad pressed when HostStopped
	//# Basically send out chord notes when a chord changes
	chord_slot = (current_scene * 100) + (current_chord * 10)
	
	//# First turn off old chord notes
	Call @TurnOffChordNotes
	
	//# Use a standardised octave for chord notes out
	//# First remove octave and then assign
	//# Add octave to avoid C=0 issues
	chord_root = chord_bank[chord_slot]
	chord_3rd = chord_bank[chord_slot + 1]
	chord_5th = chord_bank[chord_slot + 2]
	chord_7th = chord_bank[chord_slot + 3]
	chord_bass = chord_bank[chord_slot + bass_slot]
	
	//# Raw function uses this variable
	HAR_NOTE_OCTAVE = (chords_out_octave * 12) + 24  
	
	Call @MakeChordNotesRawOctave
	if chord_bass >= 0
		chord_bass = chord_bass % 12
		chord_bass = chord_bass + HAR_NOTE_OCTAVE - 12
	endif
	
	//# Handle inversion setting for chord notes out
	chrd_inversion = chord_bank[chord_slot + inv_slot]
	if (chrd_inversion <> 0)
		Call @HandleInversionSetting //# re-define chord notes to inverted order
	endif
	
	//# Handle scene transpose
	txpose_index = scene_bank[(current_scene * sc_size) + sc_txp_slot]
	txpose_amt = txpose_array[txpose_index] //# scene txpose amount
	chord_root = chord_root + txpose_amt
	chord_3rd = chord_3rd + txpose_amt
	chord_5th = chord_5th + txpose_amt
	chord_7th	= chord_7th + txpose_amt
	if chord_bass >= 0 //# -1 is off so dont txpose
		chord_bass = chord_bass + txpose_amt
	endif
	
	//# Get per scene Midi Out channel On/Off settings
	out1_type = scene_bank[(current_scene * sc_size) + sc_och1_slot]
	out2_type = scene_bank[(current_scene * sc_size) + sc_och2_slot]
	out3_type = scene_bank[(current_scene * sc_size) + sc_och3_slot]
	out4_type = scene_bank[(current_scene * sc_size) + sc_och4_slot]
	
	//# make a dummy scale to represent chord degrees saved in cno_degrees
	chord_scale = [chord_bass, chord_root, chord_root, chord_3rd, chord_3rd, chord_5th, chord_5th, chord_7th, chord_7th]
	//# midi channes ch1-4 set in TurnOffChordNotes called above
	for i = 0 to 3 //# up to 4 notes can be sent in a mode
		ch1_degree = cno_degrees[(4 * out1_type) + i]
		ch2_degree = cno_degrees[(4 * out2_type) + i]
		ch3_degree = cno_degrees[(4 * out3_type) + i]
		ch4_degree = cno_degrees[(4 * out4_type) + i]
		Call @HumanizeVelocity
		//# send out chord notes
		if (ch1_degree >=0)
			if chord_scale[ch1_degree] > 0
				SendMIDINoteOn ch1, chord_scale[ch1_degree], velocity
				SetNoteState ch1, i, chord_scale[ch1_degree]
			endif
		endif
		if (ch2_degree >=0) 
			if chord_scale[ch2_degree] > 0
				SendMIDINoteOn ch2, chord_scale[ch2_degree], velocity
				SetNoteState ch2, i, chord_scale[ch2_degree]
			endif
		endif
		if (ch3_degree >=0) 	 
			if chord_scale[ch3_degree] > 0
				SendMIDINoteOn ch3, chord_scale[ch3_degree], velocity
				SetNoteState ch3, i, chord_scale[ch3_degree]
			endif
		endif
		if (ch4_degree >=0)
			if chord_scale[ch4_degree] > 0
				SendMIDINoteOn ch4, chord_scale[ch4_degree], velocity
				SetNoteState ch4, i, chord_scale[ch4_degree]
			endif
		endif
	endfor	
@End

@TurnOffChordNotes
	//# channels
	ch1 = midi_channels_used[9]
	ch2 = midi_channels_used[10]
	ch3 = midi_channels_used[11]
	ch4 = midi_channels_used[12]
	for i = 0 to 3
		//# stored in 1st 4 note slots (0-3) on each channel
		SendMIDINoteOff ch1, (GetNoteState ch1, i), 127
		SetNoteState ch1, i, FALSE
		
		SendMIDINoteOff ch2, (GetNoteState ch2, i), 127
		SetNoteState ch1, i, FALSE
		
		SendMIDINoteOff ch3, (GetNoteState ch3, i), 127
		SetNoteState ch1, i, FALSE
		
		SendMIDINoteOff ch4, (GetNoteState ch4, i), 127
		SetNoteState ch1, i, FALSE
	endfor
@End

@ConvertToHarmonyNotes
	//# Convert incoming midi note to a harmony note based on current chord
	//# Handles scene harmonization mode for the midi in channel also
	//# chord = [note1, note2, note3, note4, duration, inv, bass]
	//# scene = [duration, txpose, preset, mg_modes1-4]
	//# midi_in_scale_notes from selected_midi_in_root, selected_midi_in_key 
	//# [mis[0], mis[2], mis[4], mis[6]]  - chord notes
	//# [mis[1], mis[3], mis[5]] - passing notes
	//# Harm. modes: 
	//# - 0 Chord, 
	//# - 1 Round2chord, 
	//# - 2 Scene Scale, 
	//# - 3 Bass, 
	//# - 4 Root, 
	//# - 5 3rd, 
	//# - 6 5th
	chord_slot = (current_scene * 100) + (current_chord * 10)
	chord_root = chord_bank[chord_slot]
	chord_3rd = chord_bank[chord_slot+1] 
	chord_5th = chord_bank[chord_slot+2]
	chord_7th = chord_bank[chord_slot+3]
	chord_bass = chord_bank[chord_slot + bass_slot]
	
	//# Log {Converting Ch }, midi_channel, { - }, midi_note, { to Harmony}
	//# Log {Scene: }, current_scene, { Chord: }, chord_root, chord_3rd, chord_5th, chord_7th
		
	//# Outgoing harmony note is what we are looking to get here
	incoming_scale_degree = 0
	HAR_NOTE_OUT = 0
	outgoing_note_canceled = FALSE //# if chord note = -1
	
	//# What is the scene harm. mode for this channel scene array slot 4-7
	//# sc_harm_mode is set in OnMidiNoteOn
	
	//# is the incoming note a chord note or a passing note
	Call @GetIncomingNoteType //# sets var incoming_scale_degree 
	
	//# Early checks to cancel outgoing.... sch_harm_modes..
	//# -1Off 0Chord 1Round 2+NonChord 3Bass 4Root 5Third 6Fifth 7thru
	if (chord_root = -1)
		outgoing_note_canceled = TRUE //# chord setup incomplete
	elseif (incoming_scale_degree >= 3) and (chord_3rd = -1)
		outgoing_note_canceled = TRUE //# chord setup incomplete
	elseif (incoming_scale_degree >= 5) and (chord_5th = -1)
		outgoing_note_canceled = TRUE //# chord setup incomplete
	elseif (incoming_scale_degree = 7) and (chord_7th = -1) and (sc_harm_mode <> 2)
		outgoing_note_canceled = TRUE //# triads dont play 7th notes  
		//# but in +NonChord we will play it like a non_scale note
		//# Log {Chord is triad. Incoming scale degree is 7th, so no output}
	elseif(sc_harm_mode = 3) and (chord_bass = -1)
		outgoing_note_canceled = TRUE //#No bass note for Bass only mode
		Log {No bass note set for Bass only Harmonization mode}
	elseif (NOT incoming_scale_degree) and (sc_harm_mode <> 7 and sc_harm_mode <> 2)
		Log {NOT A SCALE NOTE AND SCHARMode: }, sc_harm_mode
		outgoing_note_canceled = TRUE //# Not a scale note
	elseif (NOT incoming_is_chord_note) and (sc_harm_mode <> 1 and sc_harm_mode <> 2 and sc_harm_mode <> 7) 
		//# Only Round2chord, NonChord, & Thru modes can have passing notes 
		Log {Not a chord note and mode: }, sc_harm_mode
		outgoing_note_canceled = TRUE
	elseif (sc_harm_mode = -1)
		outgoing_note_canceled = TRUE //# block notes mode
	endif

	if (NOT outgoing_note_canceled) and (sc_harm_mode <> 7) 
		//# Calc octave adj based on incoming octave and stored chord notes
		//# select chords saved? RootNote (0-11) + Intervals
		//# recorded chords saved as played and sorted. Any val
		octave_incoming_note = Div midi_note, 12
		chord_note_octave_adj = (octave_incoming_note - 3) * 12
		bass_note_octave_adj = (octave_incoming_note - 2) * 12
		if sc_harm_mode = 3
			HAR_NOTE_OCTAVE = bass_note_octave_adj + 36
		else
			HAR_NOTE_OCTAVE = chord_note_octave_adj + 36
		endif
		
		//# Remove octave but maintain ascending order
		Call @MakeChordNotesRawOctave
			
		//# Calculate a scn transpose amount
		txpose_index = scene_bank[(current_scene * sc_size) + sc_txp_slot]
		scn_txpose_amount = txpose_array[txpose_index]
	
		//# Handle single note harmony modes
		//# Positions based on root inversion, non-re-ordered chord notes
		if incoming_is_chord_note and sc_harm_mode = 3 //# Bass only
			Log {CONVERT ALL TO BASS}
			HAR_NOTE_OUT = chord_bank[chord_slot + bass_slot]
		elseif (incoming_is_chord_note and sc_harm_mode = 4) //# Root only
			Log {CONVERT ALL TO ROOT}
			HAR_NOTE_OUT = chord_root
		elseif (incoming_is_chord_note and sc_harm_mode = 5) //# 3rd only
			Log {CONVERT ALL TO 3RD}
			HAR_NOTE_OUT = chord_3rd
		elseif (incoming_is_chord_note and sc_harm_mode = 6) //# 5th only
			Log {CONVERT ALL TO 5TH}
			HAR_NOTE_OUT = chord_5th
		endif
				
		//# Re-order harmony notes for inversions so we can still play the chord with CEGB and have C as lowest note. C will now become the lowest chord note post inversion
		//# Log {old chord root: }, chord_root
		chrd_inversion = chord_bank[chord_slot + inv_slot]
		if (chrd_inversion <> 0)
			//# re-define chord notes to inverted order
			Call @HandleInversionSetting
		endif
		//# Log {new chord root: }, chord_root
		
		//# handle chord, round to chord and scn_scale modes				
		if (sc_harm_mode = 0) or (sc_harm_mode = 1) or (sc_harm_mode = 2)
			//# Log { SCALE DEGREE: }, incoming_scale_degree
			if incoming_scale_degree = 1
				HAR_NOTE_OUT = chord_root
			elseif (incoming_scale_degree = 3)
				HAR_NOTE_OUT = chord_3rd
			elseif (incoming_scale_degree = 5)
				HAR_NOTE_OUT = chord_5th
			elseif (incoming_scale_degree = 7)
				HAR_NOTE_OUT = chord_7th
			elseif (incoming_scale_degree = 2) and (sc_harm_mode = 1)
				//# passing notes get converted to chord notes in round to chord mode
				HAR_NOTE_OUT = chord_root
			elseif (incoming_scale_degree = 4) and (sc_harm_mode = 1)
				//# passing notes get converted to chord notes in round to chord mode
				HAR_NOTE_OUT = chord_3rd
			elseif (incoming_scale_degree = 6) and (sc_harm_mode = 1)
				//# passing notes get converted to chord notes in round to chord mode
				HAR_NOTE_OUT = chord_5th 
			elseif (sc_harm_mode = 2) and (incoming_scale_degree = 2)
				//# eg: D(passing note) is +2st above C(chord root)
				HAR_NOTE_OUT = chord_root + 2 
			elseif (sc_harm_mode = 2) and (incoming_scale_degree = 4)
				//# eg: F(passing note) is +1st above E(chord third)
				HAR_NOTE_OUT = chord_3rd + 1 
			elseif (sc_harm_mode = 2) and (incoming_scale_degree = 6)
				//# eg: A(passing note) is +2st above G(chord 5th)
				HAR_NOTE_OUT = chord_5th + 2
			elseif (sc_harm_mode = 2) and (non_scale_note = 1)
				//# eg: C# is +1st above chord_root
				HAR_NOTE_OUT = chord_root + 1
			elseif (sc_harm_mode = 2) and (non_scale_note = 2)
				//# eg: D# is 1st below chord_third
				HAR_NOTE_OUT = chord_3rd - 1
			elseif (sc_harm_mode = 2) and (non_scale_note = 3)
				//# eg: F# is 1st below chord_5th
				HAR_NOTE_OUT = chord_5th - 1
			elseif (sc_harm_mode = 2) and (non_scale_note = 4)
				//# eg: G# is 1st above chord_5th
				HAR_NOTE_OUT = chord_5th + 1
			elseif (sc_harm_mode = 2) and (non_scale_note = 5)
				//# eg: A# is 1st below chord_7th
				HAR_NOTE_OUT = chord_5th + 3 //# in case 7th not assigned
			elseif (sc_harm_mode <> 2) and (incoming_scale_degree = 7) and (chord_7th = -1)
				//# rare case in +NonChord but the 7th chord note not assigned we allow but nee to make a note for this
				HAR_NOTE_OUT = chord_root - 1
			endif
		endif
		
		if (HAR_NOTE_OUT > 0) 		
			//# Apply octave adj + scn transpose calculated above
			HAR_NOTE_OUT = HAR_NOTE_OUT + scn_txpose_amount 
		
			//# save calculated harmony note to locker for note off recall
			SetNoteState MIDIChannel, midi_note, HAR_NOTE_OUT
			
			//# send note out
			Call @HumanizeVelocity
			if NOT incoming_is_chord_note
				velocity = velocity_dipped
			endif
			SendMIDINoteOn MIDIChannel, HAR_NOTE_OUT, velocity  
		endif
	elseif (sc_harm_mode = 7) 
		//# ignore scn_txpose and octave adj in thru mode
		SetNoteState MIDIChannel, midi_note, midi_note
		SendMIDINoteOn MIDIChannel, midi_note, MidiVelocity
		//# Log {Midi sent through in mode 8}
	endif
			
@End

@GetIncomingNoteType
	//# midi_note set from MIDINote just before CHN is called
	incoming_note = midi_note % 12
	incoming_is_chord_note = FALSE
	non_scale_note = 0
	if incoming_note = midi_in_scale_notes[0]
		incoming_is_chord_note = TRUE
		incoming_scale_degree = 1
	elseif (incoming_note = midi_in_scale_notes[2])
		incoming_is_chord_note = TRUE
		incoming_scale_degree = 3
	elseif (incoming_note = midi_in_scale_notes[4])
		incoming_is_chord_note = TRUE
		incoming_scale_degree = 5
	elseif (incoming_note = midi_in_scale_notes[6])
		incoming_is_chord_note = TRUE
		incoming_scale_degree = 7
	elseif (incoming_note = midi_in_scale_notes[1])
		incoming_is_chord_note = FALSE
		incoming_scale_degree = 2
	elseif (incoming_note = midi_in_scale_notes[3])
		incoming_is_chord_note = FALSE
		incoming_scale_degree = 4
	elseif (incoming_note = midi_in_scale_notes[5])
		incoming_is_chord_note = FALSE
		incoming_scale_degree = 6
	elseif (incoming_note = midi_in_scale_notes[0] + 1)
		non_scale_note = 1
	elseif (incoming_note = midi_in_scale_notes[2] - 1)
		non_scale_note = 2
	elseif (incoming_note = midi_in_scale_notes[4] - 1)
		non_scale_note = 3
	elseif (incoming_note = midi_in_scale_notes[4] + 1)
		non_scale_note = 4
	elseif (incoming_note = midi_in_scale_notes[6] - 1)
		non_scale_note = 5
	endif 
@End

@HandleInversionSetting
	//# Harmony notes get re-ordered by inversion, so that the 'root' is the lowest note of the chord (say E) but not the chort root (say C) in CEG 1st inv. 
	//# Log {Converting chord notes: }, chord_root, chord_3rd, chord_5th, chord_7th
	
	//# the current inversion
	chrd_inversion = chord_bank[chord_slot + inv_slot]
	
	//# add octave in case inverting down goes below zero
	hn1 = chord_root + 12
	hn2 = chord_3rd + 12
	hn3 = chord_5th + 12
	if chord_7th >= 0
		hn4 = chord_7th + 12
	else
		hn4 = chord_7th
	endif
		
	//# re-order for inversions
	//# Log {CHORD INVERSION = }, chrd_inversion
	if chrd_inversion = 1
		harmony_notes = [hn2, hn3, hn4, hn1+12]
		if chord_7th = -1
			harmony_notes = [hn2, hn3, hn1+12, hn4]
		endif
	endif
	if chrd_inversion = 2
		harmony_notes = [hn3, hn4, hn1+12, hn2+12]
		if chord_7th = -1
			harmony_notes = [hn3, hn1+12, hn2+12, hn4]
		endif
	endif
	if chrd_inversion = 3
		harmony_notes = [hn4, hn1+12, hn2+12, hn3+12]
		if chord_7th = -1
			harmony_notes = [hn1+12, hn2+12, hn3+12, hn4]
		endif
	endif
	if chrd_inversion = 4
		harmony_notes = [hn1+12, hn2+12, hn3+12, hn4+12]
		if chord_7th = -1
			harmony_notes = [hn1+12, hn2+12, hn3+12, hn4]
		endif
	endif
	if chrd_inversion = -1
		harmony_notes = [hn4-12, hn1, hn2, hn3]
		if chord_7th = -1
			harmony_notes = [hn3-12, hn1, hn2, hn4]
		endif
	endif
	if chrd_inversion = -2
		harmony_notes = [hn3-12, hn4-12, hn1, hn2]
		if chord_7th = -1
			harmony_notes = [hn2-12, hn3-12, hn1, hn4]
		endif
	endif
	if chrd_inversion = -3
		harmony_notes = [hn2-12, hn3-12, hn4-12, hn1]
		if chord_7th = -1
			harmony_notes = [hn1-12, hn2-12, hn3-12, hn4]
		endif
	endif
	if chrd_inversion = -4
		harmony_notes = [hn1-12, hn2-12, hn3-12, hn4-12]
		if chord_7th = -1
			harmony_notes = [hn1-12, hn2-12, hn3-12, hn4]
		endif
	endif
	//# Re-define chord notes based on inverted order
	//# remove octave added above
	chord_root = harmony_notes[0] - 12
	chord_3rd = harmony_notes[1] - 12
	chord_5th = harmony_notes[2] - 12
	if chord_7th >= 0
		chord_7th = harmony_notes[3] - 12
	endif
	//# Log {Converted harmony_notes: }, chord_root, chord_3rd, chord_5th, chord_7th
@End

@MakeChordNotesRawOctave
	//# Set variabes chord_root, 3rd, 5th and 7th.
	//# updated to remove octave but maintain ascending note order
	chord_root = chord_root % 12
	chord_3rd = chord_3rd % 12
	if chord_root > chord_3rd
		chord_3rd = chord_3rd + 12
	endif
	chord_5th = chord_5th % 12
	if chord_3rd > chord_5th
		chord_5th = chord_5th + 12
	endif
	if chord_7th >= 0
		chord_7th = chord_7th % 12
		if chord_5th > chord_7th
			chord_7th = chord_7th + 12
		endif
		chord_7th = chord_7th + HAR_NOTE_OCTAVE
	else
		chord_7th = -1
	endif
	chord_root = chord_root + HAR_NOTE_OCTAVE
	chord_3rd = chord_3rd + HAR_NOTE_OCTAVE
	chord_5th = chord_5th + HAR_NOTE_OCTAVE
	//# chord_bass is always in range 0-11
@End
	
@HumanizeVelocity
	// #Velocity handling
	humanize_velocity = 80 // #50-100 Lower = more variation
		dip_velocity_pct = 60 // #50-100 Reduce velocity by %
	humanize_pct = (Random humanize_velocity, 100 ) / 100
	sinputVelocity = MidiVelocity
	if NOT MidiVelocity
		inputVelocity = 100
	endif
	velocity = RoundUp (inputVelocity * humanize_pct)
	velocity_dipped = RoundUp (velocity * dip_velocity_pct/100)
@End

@OnMidiNoteOff  
	// #handle midi notes for harmonizing note OFF
	for i = 1 to 8
		if MIDIChannel = midi_channels_used[i] and not (mode = 3)
			// #retrieve the harmony_note sent from note locker
			harmony_note = GetNoteState MIDIChannel, MIDINote  
			SendMIDINoteOff MIDIChannel, harmony_note, MIDIVelocity  
			SetNoteState MIDIChannel, MIDINote, FALSE	
		endif
	endfor
@End

@HandleRecordNotes
	Log {HANDLING RECORD NOTES TO CHORD SLOT}
	if (mode = 3) and (rec_chord_note_count <= 3)
		//# In record mode and chord selected for updating
		Log {Chord note recieved num: }, rec_chord_note_count
		
		if rec_chord_note_count = 0
			//# Recording is happening so reset the current notes
			chord_slot = (current_scene * 100) + (current_chord * 10)
			for i = 0 to 3
				Log {RESETTING CHORD SLOT }, chord_slot+i
				chord_bank[chord_slot+i] = -1
			endfor
			chord_bank[chord_slot+inv_slot] = 0 //# start new chord with no inv.
			rec_chord_notes = [-1,-1,-1,-1] //# reset array to empty
			Log {Current chord: }, current_chord
			chrd_to_label = current_chord+8
			Call @LabelChordPad //# re-label after notes reset
		endif
		
		//# Store recorded chord notes and update chord_bank and label
		rec_chord_notes[rec_chord_note_count] = MIDINote
		CopyArray rec_chord_notes, sort_list
		rec_chord_note_count = rec_chord_note_count + 1
		len_list = rec_chord_note_count
		if len_list > 1
			Call @SortList
		endif
		CopyArray sort_list, rec_chord_notes
		Call @StoreChordNotes
		chrd_to_label = current_chord+8
		Call @LabelChordPad
		Call @SetupLayout
	endif
@End

@StoreChordNotes
	//# Store the recorded notes to the chord slot
	chord_slot = (current_scene * 100) + (current_chord * 10)
	for i = 0 to 3
		if rec_chord_notes[i] >= 0
			chord_bank[chord_slot + i] = rec_chord_notes[i]
			Log {Chord note }, i, { is }, rec_chord_notes[i], { in chord slot}, chord_slot+i
		else
			chord_bank[chord_slot + i] = -1
		endif
	endfor
	if chord_bank[chord_slot + dur_slot] <= 0 //# Set a default duration
		chord_bank[chord_slot + dur_slot] = 4
	endif
@End

@ResetScene
	//# Reset scene: Duration, Txpose, Preset, modes for ch's 1-4, out ch's ON1-4, pgm_chg_msg
	scene_bank[LastPad * sc_size] = [-1,6,0,0,0,0,0,0,0,0,0,-1]
	chord_slot = (LastPad * 100)
	for c = 0 to 7
		chord_bank[(current_scene*100) + (c*10)] = [-1, -1, -1, -1, 0, 0, -1]
	endfor
	Call @SetupLayout
	Log {Scene }, LastPad +1, { reset. All chords for scene reset}
@End

@ResetChord
	chord_slot = (current_scene * 100) + ((LastPad - 8) * 10)
	//# 4 chord notes, duration, inv, bass, pattern_msg 
	chord_bank[chord_slot] = [-1,-1,-1,-1,0,0,-1,-1]
	Log {Chord }, LastPad +1, { reset}
	Call @SetupLayout
@End

@CopyPaste
	if LastPad <=7
		Log {Pasting scene to }, current_scene+1 
		LabelPads {Copied scene }, copied_scene+1, { to scene }, LastPad+1
		CopyArray scene_bank[copied_scene * sc_size], scene_bank[LastPad * sc_size], 10
		CopyArray chord_bank[copied_scene * 100], chord_bank[LastPad * 100], 100
		//# Exit copy paste
		songmode = 1
		mode=0
	elseif LastPad >= 8
		Log {pasting to chord }, LastPad-8
		LabelPads	{Copied S}, copied_scene+1, { Chord }, copied_chord+1, { to }, { S}, current_scene+1, { chord }, LastPad-7
		chord_slot_from = (copied_scene * 100) + (copied_chord * 10)
		chord_slot_to = (current_scene * 100) + ((LastPad-8) * 10)
		CopyArray chord_bank[chord_slot_from], chord_bank[chord_slot_to], 10
		//# Exit copy paste
		songmode = 2
		mode=0
	endif
	copied_scene = -1 //# reset
	copied_chord = -1
	Call @SetupLayout 
@End

@SetupKnobset0
	//# Scene settings
	knob_set = 0
	LabelKnobs {Scene }, current_scene+1, { setup}
	scn_duration = scene_bank[current_scene * sc_size]
	scn_txpose = scene_bank[(current_scene * sc_size) + sc_txp_slot]
	scn_preset = scene_bank[(current_scene * sc_size) + sc_preset_slot]
	scn_pgm_chg = scene_bank[(current_scene * sc_size) + sc_pgmchg_slot]
	LabelKnob 0, {Duration}
	LabelKnob 1, {Transpose}
	LabelKnob 2, {Preset }, scn_preset
	if scn_pgm_chg >= 0
		LabelKnob 3, {PChg }, scn_pgm_chg 
	else
		LabelKnob 3, {PChg }, {Off}
	endif
	SetKnobValue 0, TranslateScale scn_duration, 0, 32, 0, 127
	SetKnobValue 1, TranslateScale scn_txpose, 0, 12, 0, 127
	SetKnobValue 2, TranslateScale scn_preset, 1, num_sc_presets, 0, 127
	SetKnobValue 3, TranslateScale scn_pgm_chg, -1, 8, 0, 127 
@End

@SetupKnobset1
	//# Chord settings
	knob_set = 1
	LabelKnobs {Chord }, current_chord+1, { setup}
	chord_slot = (current_scene * 100) + ((current_chord) * 10)
	chrd_duration = chord_bank[chord_slot + dur_slot]
	chrd_inversion = chord_bank[chord_slot + inv_slot]
	chrd_bass = chord_bank[chord_slot + bass_slot]
	chrd_patt = chord_bank[chord_slot + patt_slot]
	if chrd_bass >= 0 //# leave -1 if not set
		chrd_bass = chord_bank[chord_slot + bass_slot] % 12
	endif
	if mode = 3
		LabelKnob 1, {REC CH }, midi_channels_used[0] + 1
		SetKnobValue 1, TranslateScale midi_channels_used[0], 0, 15, 0, 127
	else
		if chrd_patt = 16
			LabelKnob 1, {CC21 RND}
		elseif chrd_patt >= 0
			LabelKnob 1, {CC21: }, chrd_patt+1
		else
			LabelKnob 1, {CC21 Off}
		endif
		SetKnobValue 1, TranslateScale chrd_patt, -1, 16, 0, 127
	endif
	LabelKnob 0, {Duration}	
	LabelKnob 2, {Inv }, chrd_inversion
	if chrd_bass >= 0
		LabelKnob 3, {Bass }, (NoteName chrd_bass)
	else
		LabelKnob 3, {Bass }, {Off}
	endif
	SetKnobValue 0, TranslateScale chrd_duration, 0, 32, 0, 127
	SetKnobValue 2, TranslateScale chrd_inversion, -4, 4, 0, 127
	SetKnobValue 3, TranslateScale chrd_bass, -1, 11, 0, 127
@End

@SetupKnobset2
	//# Chord select settings
	knob_set = 2
	chord_slot = (current_scene * 100) + ((current_chord) * 10)
	LabelKnobs {Selecting }, {S}, current_scene+1, { Chord: }, current_chord+1
	
	//# if new chord default values from FillArray used here
	slct_chord_root = chord_bank[chord_slot] % 12
	slct_chord_inversion = chord_bank[chord_slot + inv_slot]
	slct_chord_bass_note = chord_bank[chord_slot + bass_slot] % 12
	
	//# Knob setup
	LabelKnob 0, {Root }, (NoteName slct_chord_root)
	LabelKnob 1, {Type}
	LabelKnob 2, {Inv }, slct_chord_inversion 
	LabelKnob 3, {Bass }, (NoteName slct_chord_bass_note)
	SetKnobValue 0, TranslateScale slct_chord_root, 0, 11, 0, 127
	SetKnobValue 1, TranslateScale slct_chord_type, 0, num_chord_types-1, 0, 127
	SetKnobValue 2, TranslateScale slct_chord_inversion, -4, 4, 0, 127
	SetKnobValue 3, TranslateScale slct_chord_bass_note, -1, 11, 0, 127
	//# prevent updating values not changed
	root_updated = FALSE
	type_updated = FALSE
	bass_updated = FALSE
	inv_updated = FALSE
@End

@SetupKnobset3
	//# Harmony modes: Chord only, Round2chord,  NonChord, Bass, Root, 3rd, 5th
	knob_set = 3
	LabelKnobs {S}, current_scene+1, { MIDI IN modes}
	scn_mh1_mode = scene_bank[(current_scene * sc_size) + sc_mh1_slot]
	scn_mh2_mode = scene_bank[(current_scene * sc_size) + sc_mh2_slot]
	scn_mh3_mode = scene_bank[(current_scene * sc_size) + sc_mh3_slot]
	scn_mh4_mode = scene_bank[(current_scene * sc_size) + sc_mh4_slot]
	SetKnobValue 0, TranslateScale scn_mh1_mode, -1, num_sc_mh_modes-1, 0, 127
	SetKnobValue 1, TranslateScale scn_mh2_mode, -1, num_sc_mh_modes-1, 0, 127
	SetKnobValue 2, TranslateScale scn_mh3_mode, -1, num_sc_mh_modes-1, 0, 127
	SetKnobValue 3, TranslateScale scn_mh4_mode, -1, num_sc_mh_modes-1, 0, 127
	in1ch = midi_channels_used[1]
	in2ch = midi_channels_used[2]
	in3ch = midi_channels_used[3]
	in4ch = midi_channels_used[4]
	LabelKnob 0, {Ch}, in1ch, {: }, scn_mh1_mode+1
	LabelKnob 1, {Ch}, in2ch, {: }, scn_mh2_mode+1
	LabelKnob 2, {Ch}, in3ch, {: }, scn_mh3_mode+1
	LabelKnob 3, {Ch}, in4ch, {: }, scn_mh4_mode+1
	Call @LabelSceneModesPad
	in1ch = midi_channels_used[1]
	in2ch = midi_channels_used[2]
	in3ch = midi_channels_used[3]
	in4ch = midi_channels_used[4]
	LabelKnob 0, {Ch}, in1ch+1, {: }, scn_mh1_mode+1
	LabelKnob 1, {Ch}, in2ch+1, {: }, scn_mh2_mode+1
	LabelKnob 2, {Ch}, in3ch+1, {: }, scn_mh3_mode+1
	LabelKnob 3, {Ch}, in4ch+1, {: }, scn_mh4_mode+1
@End
	
@SetupKnobset4
	//# EXT midi in channels
	knob_set = 4
	LabelKnobs {EXT Midi IN}
	SetKnobValue 0, TranslateScale midi_channels_used[1], -1, 15, 0, 127
	SetKnobValue 1, TranslateScale midi_channels_used[2], -1, 15, 0, 127
	SetKnobValue 2, TranslateScale midi_channels_used[3], -1, 15, 0, 127
	SetKnobValue 3, TranslateScale midi_channels_used[4], -1, 15, 0, 127
	Call @LabelKnobset4
	Call @LabelMidiInChannelsPadA
@End

@SetupKnobset5
	//# midi in key and scale
	knob_set = 5
	LabelKnobs {Midi IN scale}
	LabelKnob 0, {Key }, (NoteName, selected_midi_in_root)
	LabelKnob 1, (ScaleName, allowed_scales[selected_midi_in_scale])
	LabelKnob 2, { }
	LabelKnob 3, { }
	SetKnobValue 0, TranslateScale selected_midi_in_root, 0, 11, 0, 127
	SetKnobValue 1, TranslateScale selected_midi_in_scale, 0, num_scale_types-1, 0, 127
	SetKnobValue 2, 0
	SetKnobValue 3, 0
@End

@SetupKnobset6
	//# Chord construct settings
	knob_set = 6
	chord_slot = (current_scene * 100) + ((current_chord) * 10)
	LabelKnobs {Construct }, {S}, current_scene+1, { Chord: }, current_chord+1
	
	//# if new chord default values from FillArray used here
	constructed_root = chord_bank[chord_slot] % 12
	root_3rd_interval = chord_bank[chord_slot+1] - chord_bank[chord_slot]
	root_5th_interval = chord_bank[chord_slot+2] - chord_bank[chord_slot]
	root_7th_interval = chord_bank[chord_slot+3] - chord_bank[chord_slot]
	
	//# work out what knob value to assign knobs on selection on new chord pad
	if root_3rd_interval = 3
		constructed_3rd = 1
	elseif (root_3rd_interval = 4)
		constructed_3rd = 2
	elseif (root_3rd_interval > 4)
		constructed_3rd = 3
	else
		constructed_3rd = 0
	endif
	
	if root_5th_interval > 7
		constructed_5th = 2
	elseif (root_5th_interval < 7)
		constructed_5th = 0
	else
		constructed_5th = 1
	endif
	
	if root_7th_interval = 8
		constructed_7th = 1
	elseif (root_7th_interval = 9)
		constructed_7th = 2
	elseif (root_7th_interval = 10)
		constructed_7th = 3
	elseif (root_7th_interval = 11)
		constructed_7th = 4
	elseif (chord_bank[chord_slot+3] < 0)
		constructed_7th = 0
	else
		constructed_7th = 0
	endif
	
	//# Knob setup - Labelling
	LabelKnob 0, {Root }, (NoteName constructed_root)
	Call @LabelConstructed3rd
	Call @LabelConstructed5th
	Call @LabelConstructed7th
	
	SetKnobValue 0, TranslateScale constructed_root, 0, 11, 0, 127
	SetKnobValue 1, TranslateScale constructed_3rd, 0, 3, 0, 127
	SetKnobValue 2, TranslateScale constructed_5th, 0, 2, 0, 127
	SetKnobValue 3, TranslateScale constructed_7th, 0, 4, 0, 127
	//# prevent updating values not changed
	root_updated = FALSE
	3rd_updated = FALSE
	5th_updated = FALSE
	7th_updated = FALSE
@End

@SetupKnobset7
	//# midi out channels
	knob_set = 7
	LabelKnobs {CHORDS NOTE OUT}
	SetKnobValue 0, TranslateScale midi_channels_used[9], -1, 15, 0, 127
	SetKnobValue 1, TranslateScale midi_channels_used[10], -1, 15, 0, 127
	SetKnobValue 2, TranslateScale midi_channels_used[11], -1, 15, 0, 127
	SetKnobValue 3, TranslateScale midi_channels_used[12], -1, 15, 0, 127
	Call @LabelKnobset7
	Call @LabelMidiOutChannelsPad
@End

@SetupKnobset8
	//# Sequences midi in channels
	knob_set = 8
	LabelKnobs {SEQ Midi IN}
	SetKnobValue 0, TranslateScale midi_channels_used[5], -1, 15, 0, 127
	SetKnobValue 1, TranslateScale midi_channels_used[6], -1, 15, 0, 127
	SetKnobValue 2, TranslateScale midi_channels_used[7], -1, 15, 0, 127
	SetKnobValue 3, TranslateScale midi_channels_used[8], -1, 15, 0, 127
	Call @LabelKnobset8
	Call @LabelMidiInChannelsPadB
@End

@SetupKnobset9
	//# Chord Notes out styles
	knob_set = 9
	LabelKnobs {Send out...}
	kv1 = scene_bank[(current_scene * sc_size) + sc_och1_slot]
	kv2 = scene_bank[(current_scene * sc_size) + sc_och2_slot]
	kv3 = scene_bank[(current_scene * sc_size) + sc_och3_slot]
	kv4 = scene_bank[(current_scene * sc_size) + sc_och4_slot]
	SetKnobValue 0, TranslateScale kv1, 0, cno_choices, 0, 127
	SetKnobValue 1, TranslateScale kv2, 0, cno_choices, 0, 127
	SetKnobValue 2, TranslateScale kv3, 0, cno_choices, 0, 127
	SetKnobValue 3, TranslateScale kv4, 0, cno_choices, 0, 127
	Call @LabelKnobset9
	Call @LabelChordNotesOutPad
@End

@LabelKnobset4
	if midi_channels_used[1] = -1
		LabelKnob 0, {IN1 Ch: }, {off}
	else
		LabelKnob 0, {IN1 Ch: }, midi_channels_used[1]+1  
	endif
	if midi_channels_used[2] = -1
		LabelKnob 1, {IN2 Ch: }, {off}
	else
		LabelKnob 1, {IN2 Ch: }, midi_channels_used[2]+1  
	endif
	if midi_channels_used[3] = -1
		LabelKnob 2, {IN3 Ch: }, {off}
	else
		LabelKnob 2, {IN3 Ch: }, midi_channels_used[3]+1  
	endif
	if midi_channels_used[4] = -1
		LabelKnob 3, {IN4 Ch: }, {off}
	else
		LabelKnob 3, {IN4 Ch: }, midi_channels_used[4]+1  
	endif
@End


@LabelKnobset7
	if midi_channels_used[5] = -1
		LabelKnob 0, {Ch: }, {off}
	else
		LabelKnob 0, {Ch: }, midi_channels_used[9]+1
	endif
	if midi_channels_used[6] = -1
		LabelKnob 1, {Ch: }, {off}
	else
		LabelKnob 1, {Ch: }, midi_channels_used[10]+1
	endif
	if midi_channels_used[7] = -1
		LabelKnob 2, {Ch: }, {off}
	else
		LabelKnob 2,{Ch: }, midi_channels_used[11]+1
	endif
	if midi_channels_used[8] = -1
		LabelKnob 3, {Ch: }, {off}
	else
		LabelKnob 3, {Ch:}, midi_channels_used[12]+1
	endif
@End

@LabelKnobset8
	if midi_channels_used[5] = -1
		LabelKnob 0, {IN5 Ch: }, {off}
	else
		LabelKnob 0, {IN5 Ch: }, midi_channels_used[5]+1  
	endif
	if midi_channels_used[6] = -1
		LabelKnob 1, {IN6 Ch: }, {off}
	else
		LabelKnob 1, {IN6 Ch: }, midi_channels_used[6]+1  
	endif
	if midi_channels_used[7] = -1
		LabelKnob 2, {IN7 Ch: }, {off}
	else
		LabelKnob 2, {IN7 Ch: }, midi_channels_used[7]+1  
	endif
	if midi_channels_used[8] = -1
		LabelKnob 3, {IN8 Ch: }, {off}
	else
		LabelKnob 3, {IN8 Ch: }, midi_channels_used[8]+1  
	endif
@End

@LabelKnobset9
	kv1 = scene_bank[(current_scene * sc_size) + sc_och1_slot]
	kv2 = scene_bank[(current_scene * sc_size) + sc_och2_slot]
	kv3 = scene_bank[(current_scene * sc_size) + sc_och3_slot]
	kv4 = scene_bank[(current_scene * sc_size) + sc_och4_slot]
	chA = midi_channels_used[9]+1
	chB = midi_channels_used[10]+1
	chC = midi_channels_used[11]+1
	chD = midi_channels_used[12]+1
	if kv1 >= 2
		kv1_label = cno_labels[kv1]
		LabelKnob 0, {CH}, chA, { }, kv1_label
	elseif kv1 = 1
		LabelKnob 0, {CH}, chA, { Bass}
	else
		LabelKnob 0, {CH}, chA, { Off}
	endif
	
	if kv2 >= 2
		kv2_label = cno_labels[kv2]
		LabelKnob 1, {CH}, chB, { }, kv2_label
	elseif kv2 = 1
		LabelKnob 1, {CH}, chB, { Bass}
	else
		LabelKnob 1, {CH}, chB, { Off}
	endif
	
	if kv3 >= 2
		kv3_label = cno_labels[kv3]
		LabelKnob 2, {CH}, chC, { }, kv3_label
	elseif kv3 = 1
		LabelKnob 2, {CH}, chC, { Bass}
	else
		LabelKnob 2, {CH}, chC, { Off}
	endif
	
	if kv4 >= 2
		kv4_label = cno_labels[kv4]
		LabelKnob 3, {CH}, chD, { }, kv4_label
	elseif kv4 = 1
		LabelKnob 3, {CH}, chD, { Bass}
	else
		LabelKnob 3, {CH}, chD, { Off}
	endif
@End

@UpdateCurrentKnobset
	if knob_set = 0 
		Call @SetupKnobset0 //# scene settings
	elseif knob_set = 1
		Call @SetupKnobset1 //# chord settings
	elseif knob_set = 2
		Call @SetupKnobset2	//# chord select
	elseif knob_set = 3
		Call @SetupKnobset3	//# scene midi in modes (harmony modes)
	elseif knob_set = 4
		Call @SetupKnobset4	//# midi in channels
	elseif knob_set = 5
		Call @SetupKnobset5	//# midi in key scale
	elseif knob_set = 6
		Call @SetupKnobset6	//# midi construct
	elseif knob_set = 7
		Call @SetupKnobset7	//# midi out channels A
	elseif knob_set = 8
		Call @SetupKnobset8	//# midi out channels B
	elseif knob_set = 9
		Call @SetupKnobset9	//# midi out channels B
	endif
	//# On entering select mode the following need knobsets selected
	if in_mode_select
		if (mode = 8)
			Call @SetupKnobset4
		elseif (mode = 9)
			Call @SetupKnobset5
		elseif (mode = 10)
			Call @SetupKnobset7
		elseif (mode = 11)
			Call @SetupKnobset8
		elseif (mode = 12)
			Call @SetupKnobset9
		else
			//# disable knobs in_mode_select
			LabelKnobs { }
			LabelKnob 0, { }
			LabelKnob 1, { }
			LabelKnob 2, { }
			LabelKnob 3, { }
			knob_set = 99 //# dummy number to disable
		endif
	endif
	if send_cc_back_to_knobs
		Call @SendMidiCCBackToKnobs
	endif
@End

@OnKnobChange
	if knob_set = 0 
		Call @KnobChangeSet0 //# scene settings
	elseif knob_set = 1
		Call @KnobChangeSet1 //# chord settings
	elseif knob_set = 2
		Call @KnobChangeSet2	//# chord select
	elseif knob_set = 3
		Call @KnobChangeSet3	//# scene midi in modes
	elseif knob_set = 4
		Call @KnobChangeSet4	//# midi in channels
	elseif knob_set = 5
		Call @KnobChangeSet5	//# midi in scale
	elseif knob_set = 6
		Call @KnobChangeSet6	//# chord construct
	elseif knob_set = 7
		Call @KnobChangeSet7	//# Midi out channels A
	elseif knob_set = 8
		Call @KnobChangeSet8	//# Midi out channels B
	elseif knob_set = 9
		Call @KnobChangeSet9	//# Midi out channel On/Off
	endif 
@End 

@KnobChangeSet0
	//# scene settings
	if LastKnob = 0
		scn_duration = Round TranslateScale (GetKnobValue 0), 0, 127, 0, 32
		if scn_duration <> scene_bank[current_scene * sc_size] 	
			scene_bank[current_scene * sc_size] = scn_duration
			LabelKnob 0 , {Dur }, scn_duration
		endif
	endif
	if LastKnob = 1
		scn_txpose = Round TranslateScale (GetKnobValue 1), 0, 127, 0, 12
		if scn_txpose <> scene_bank[(current_scene * sc_size) + sc_txp_slot] 	
			scene_bank[(current_scene * sc_size) + sc_txp_slot] = scn_txpose
			Call @SetupLayout //# re-label all chord pads
		endif
	endif
	if LastKnob = 2
		scn_preset = Round TranslateScale (GetKnobValue 2), 0, 127, 1, num_sc_presets
		if scn_preset <> scene_bank[(current_scene * sc_size) + sc_preset_slot] 
			scene_bank[(current_scene * sc_size) + sc_preset_slot] = scn_preset
			LabelKnob 2, scn_preset
			Call @ChangeScenePreset
		endif
	endif
	if LastKnob = 3
		scn_pgm_chg = Round TranslateScale (GetKnobValue 3), 0, 127, -1, 8
		if scn_pgm_chg <> scene_bank[(current_scene * sc_size) + sc_pgmchg_slot]
			scene_bank[(current_scene * sc_size) + sc_pgmchg_slot] = scn_pgm_chg
			if scn_pgm_chg >=0
				LabelKnob 3, {PChg }, scn_pgm_chg
			else
				LabelKnob 3, {PChg }, {Off}
			endif
		endif
	endif
	scn_to_label = current_scene
	Call @LabelScenePad
@End

@KnobChangeSet1
//# chord settings
	chord_slot = (current_scene * 100) + ((current_chord) * 10)
	if LastKnob = 0
		chrd_duration = Round TranslateScale (GetKnobValue 0), 0, 127, 0, 32
		if chrd_duration <> chord_bank[chord_slot + dur_slot] 
			chord_bank[chord_slot + dur_slot] = chrd_duration
			dur_bars = Div chrd_duration, 4
			dur_beats = (chrd_duration % HostBeatsPerMeasure) * (100/HostBeatsPerMeasure)
			LabelKnob 0 , {Dur }, dur_bars, {.}, dur_beats
		endif
	endif
	if (mode = 3)
		if LastKnob = 1
			midi_channels_used[0] = Round TranslateScale (GetKnobValue 1), 0, 127, 0, 15
			LabelKnob 1, {REC CH }, midi_channels_used[0] + 1
		endif
	else
		if LastKnob = 1
			chrd_patt = Round TranslateScale (GetKnobValue 1), 0, 127, -1, 16
			if chrd_patt <> chord_bank[chord_slot + patt_slot] 
				chord_bank[chord_slot + patt_slot] = chrd_patt
				if chrd_patt = 16
					LabelKnob 1, {CC21 RND}
				elseif chrd_patt >= 0
					LabelKnob 1, {CC21: }, chrd_patt+1
				else
					LabelKnob 1, {CC21 Off}
				endif
			endif
		endif
	endif
	if LastKnob = 2
		chrd_inversion = Round TranslateScale (GetKnobValue 2), 0, 127, -4, 4
		if chrd_inversion <> chord_bank[chord_slot + inv_slot] 
			chord_bank[chord_slot + inv_slot] = chrd_inversion
			LabelKnob 2, {Inv }, chrd_inversion
		endif 
	endif
	if LastKnob = 3
		chrd_bass = Round TranslateScale (GetKnobValue 3), 0, 127, -1, 11
		if chrd_bass <> chord_bank[chord_slot + bass_slot] 
			chord_bank[chord_slot + bass_slot] = chrd_bass
			if chrd_bass >= 0
				LabelKnob 3, {Bass }, (NoteName chrd_bass)
			else
				LabelKnob 3, {Bass }, {Off}
			endif
		endif
	endif
	//# Knob 1 not used in this set
	chrd_to_label = current_chord+8
	Call @LabelChordPad
@End

@KnobChangeSet2
	bass_updated = FALSE
	inv_updated = FALSE
	if LastKnob = 0
		slct_chord_root = Round TranslateScale (GetKnobValue 0), 0, 127, 0, 11
		LabelKnob LastKnob, {Root }, (NoteName, slct_chord_root)
		root_updated = TRUE
		Call @SaveSelectedChordPad
	elseif LastKnob = 1
		slct_chord_type = Round TranslateScale (GetKnobValue 1), 0, 127, 0, num_chord_types-1
		if slct_chord_type = 0
			LabelKnob, 1, {Major}
		elseif slct_chord_type = 1
			LabelKnob, 1, {Minor}
		elseif slct_chord_type = 2
			LabelKnob, 1, {Diminished}
		elseif slct_chord_type = 3
			LabelKnob, 1, {Augmented}
		elseif slct_chord_type = 4
			LabelKnob, 1, {Sus2}
		elseif slct_chord_type = 5
			LabelKnob, 1, {Sus4}
		elseif slct_chord_type = 6
			LabelKnob, 1, {Minor 6th}
		elseif slct_chord_type = 7
			LabelKnob, 1, {Major 6th}
		elseif slct_chord_type = 8
			LabelKnob, 1, {Minor 7th}
		elseif slct_chord_type = 9
			LabelKnob, 1, {Dom 7th}
		elseif slct_chord_type = 10
			LabelKnob, 1, {Major 7th}
		endif
		type_updated = TRUE
		Call @SaveSelectedChordPad
	elseif LastKnob = 2
		slct_chord_inversion = Round TranslateScale (GetKnobValue 2), 0, 127, -4, 4
		LabelKnob LastKnob, {Inv: }, slct_chord_inversion
		inv_updated = TRUE
		Call @SaveSelectedChordPad
	else LastKnob = 3
		slct_chord_bass_note = Round TranslateScale (GetKnobValue 3), 0, 127, -1, 11
		LabelKnob LastKnob, {Bass }, (NoteName, slct_chord_bass_note)
		bass_updated = TRUE
		Call @SaveSelectedChordPad 
	endif
@End

@KnobChangeSet3
	//# scene midi IN settings
	//# Harmony modes: Chord only, Round to chord,  Scene Scale, Bass, Root, 3rd, 5th
	if LastKnob = 0
		scn_mh1_mode = Round TranslateScale (GetKnobValue 0), 0, 127, -1, num_sc_mh_modes-1
		scene_bank[(current_scene * sc_size) + sc_mh1_slot] = scn_mh1_mode
	endif
	if LastKnob = 1
		scn_mh2_mode = Round TranslateScale (GetKnobValue 1), 0, 127, -1, num_sc_mh_modes-1
		scene_bank[(current_scene * sc_size) + sc_mh2_slot] = scn_mh2_mode
	endif
	if LastKnob = 2
		scn_mh3_mode = Round TranslateScale (GetKnobValue 2), 0, 127, -1, num_sc_mh_modes-1
		scene_bank[(current_scene * sc_size) + sc_mh3_slot] = scn_mh3_mode
	endif
	if LastKnob = 3
		scn_mh4_mode = Round TranslateScale (GetKnobValue 3), 0, 127, -1, num_sc_mh_modes-1
		scene_bank[(current_scene * sc_size) + sc_mh4_slot] = scn_mh4_mode
	endif
	Call @LabelSceneModesPad
	in1ch = midi_channels_used[1]
	in2ch = midi_channels_used[2]
	in3ch = midi_channels_used[3]
	in4ch = midi_channels_used[4]
	LabelKnob 0, {Ch}, in1ch+1, {: }, scn_mh1_mode+1
	LabelKnob 1, {Ch}, in2ch+1, {: }, scn_mh2_mode+1
	LabelKnob 2, {Ch}, in3ch+1, {: }, scn_mh3_mode+1
	LabelKnob 3, {Ch}, in4ch+1, {: }, scn_mh4_mode+1
@End

@KnobChangeSet4
	//# Midi in channels
	if LastKnob = 0
		midi_channels_used[1] = Round TranslateScale (GetKnobValue 0), 0, 127, -1, 15
	endif
	if LastKnob = 1
		midi_channels_used[2] = Round TranslateScale (GetKnobValue 1), 0, 127, -1, 15
	endif
	if LastKnob = 2
		midi_channels_used[3] = Round TranslateScale (GetKnobValue 2), 0, 127, -1, 15
	endif
	if LastKnob = 3
		midi_channels_used[4] = Round TranslateScale (GetKnobValue 3), 0, 127, -1, 15
	endif
	Call @LabelMidiInChannelsPadA
	Call @LabelMidiInChannelsPadB
	Call @LabelMidiOutChannelsPad
	Call @LabelKnobset4
@End

@KnobChangeSet5
	//# Midi in scale
	if LastKnob = 0
		selected_midi_in_root = Round TranslateScale (GetKnobValue 0), 0, 127, 0, 11
		LabelKnob LastKnob, (NoteName, selected_midi_in_root)
		Call @GetMidiInScale
	endif
	if LastKnob = 1
		selected_midi_in_scale = Round TranslateScale (GetKnobValue 1), 0, 127, 0, num_scale_types-1
		LabelKnob LastKnob, (ScaleName allowed_scales[selected_midi_in_scale])
		Call @GetMidiInScale
	endif
	LabelPad 8, {  EXT MIDI  }, {   Key/Scale      }, (NoteName, selected_midi_in_root), { }, (ScaleName, allowed_scales[selected_midi_in_scale])
@End

@KnobChangeSet6
	if LastKnob = 0
		constructed_root = Round TranslateScale (GetKnobValue 0), 0, 127, 0, 11
		LabelKnob 0, {Root }, (NoteName, constructed_root)
		root_updated = TRUE
	elseif LastKnob = 1
		constructed_3rd = Round TranslateScale (GetKnobValue 1), 0, 127, 0, 3
		Call @LabelConstructed3rd
		3rd_updated = TRUE
	elseif LastKnob = 2
		constructed_5th = Round TranslateScale (GetKnobValue 2), 0, 127, 0, 2
		Call @LabelConstructed5th 
		5th_updated = TRUE
	else LastKnob = 3
		constructed_7th = Round TranslateScale (GetKnobValue 3), 0, 127, 0, 4
		Call @LabelConstructed7th
		7th_updated = TRUE 
	endif
	Call @SaveConstructedChordPad
@End

@LabelConstructed3rd
		if constructed_3rd = 0
			LabelKnob, 1, {sus2}
		elseif constructed_3rd = 1
			LabelKnob, 1, {min3 (b3)}
		elseif constructed_3rd = 2
			LabelKnob, 1, {maj3}
		elseif constructed_3rd = 3
			LabelKnob, 1, {sus4}
		endif
@End

@LabelConstructed5th
	if constructed_5th = 0
		LabelKnob, 2, {dim (b5)}
	elseif constructed_5th = 1
		LabelKnob, 2, {P5}
	elseif constructed_5th = 2
		LabelKnob, 2, {Aug (#5)}
	endif
@End

@LabelConstructed7th
	if constructed_7th = 0
		LabelKnob, 3, {None}
	elseif constructed_7th = 1
		LabelKnob, 3, {Min6 (b6)}
	elseif constructed_7th = 2
		LabelKnob, 3, {Maj6}
	elseif constructed_7th = 3
		LabelKnob, 3, {Min7 (b7)}
	elseif constructed_7th = 4
		LabelKnob, 3, {Maj7}
	endif
@End


@KnobChangeSet7
	//# Midi OUT channels
	if LastKnob = 0
		midi_channels_used[9] = Round TranslateScale (GetKnobValue 0), 0, 127, -1, 15
	endif
	if LastKnob = 1
		midi_channels_used[10] = Round TranslateScale (GetKnobValue 1), 0, 127, -1, 15
	endif
	if LastKnob = 2
		midi_channels_used[11] = Round TranslateScale (GetKnobValue 2), 0, 127, -1, 15
	endif
	if LastKnob = 3
		midi_channels_used[12] = Round TranslateScale (GetKnobValue 3), 0, 127, -1, 15
	endif
	Call @LabelMidiInChannelsPadA
	Call @LabelMidiInChannelsPadB
	Call @LabelMidiOutChannelsPad
	Call @LabelKnobset7
@End

@KnobChangeSet8
	//# Midi in channels B
	if LastKnob = 0
		midi_channels_used[5] = Round TranslateScale (GetKnobValue 0), 0, 127, -1, 15
	endif
	if LastKnob = 1
		midi_channels_used[6] = Round TranslateScale (GetKnobValue 1), 0, 127, -1, 15
	endif
	if LastKnob = 2
		midi_channels_used[7] = Round TranslateScale (GetKnobValue 2), 0, 127, -1, 15
	endif
	if LastKnob = 3
		midi_channels_used[8] = Round TranslateScale (GetKnobValue 3), 0, 127, -1, 15
	endif
	Call @LabelMidiInChannelsPadA
	Call @LabelMidiInChannelsPadB
	Call @LabelMidiOutChannelsPad
	Call @LabelKnobset8
@End

@KnobChangeSet9
	//# Chord Notes Out style
	if LastKnob = 0
		scene_bank[(current_scene * sc_size) + sc_och1_slot] = Round TranslateScale (GetKnobValue 0), 0, 127, 0, cno_choices
	endif
	if LastKnob = 1
		scene_bank[(current_scene * sc_size) + sc_och2_slot] = Round TranslateScale (GetKnobValue 1), 0, 127, 0, cno_choices
	endif
	if LastKnob = 2
		scene_bank[(current_scene * sc_size) + sc_och3_slot] = Round TranslateScale (GetKnobValue 2), 0, 127, 0, cno_choices
	endif
	if LastKnob = 3
		scene_bank[(current_scene * sc_size) + sc_och4_slot] = Round TranslateScale (GetKnobValue 3), 0, 127, 0, cno_choices
	endif
	Call @LabelChordNotesOutPad
	Call @LabelKnobset9
@End
		
@CheckMidiChannelConflict
	//# check for conflicts no recording channel list[0] or -1 settings
	midi_channel_conflict = FALSE
	for a = 1 to 12
		for b = 1 to 12
			if a <> b
				if (midi_channels_used[a] = midi_channels_used[b]) and (midi_channels_used[a] >= 0) and (a <= 8 or b <= 8)
					midi_channel_conflict = TRUE
				endif
			endif
		endfor
	endfor
@End

@LabelMidiInChannelsPadA
	Call @CheckMidiChannelConflict
	if NOT midi_channel_conflict
		LabelPad 9, {EXT MIDI    }, { Midi chs }, midi_channels_used[1]+1, {-}, midi_channels_used[2]+1, {-}, midi_channels_used[3]+1, {-}, midi_channels_used[4]+1
	else
		LabelPad 9, {EXT MIDI    }, {!CONFLICT! }, midi_channels_used[1]+1, {-}, midi_channels_used[2]+1, {-}, midi_channels_used[3]+1, {-}, midi_channels_used[4]+1
	endif
@End

@LabelSceneModesPad
	if in_mode_select
		scm1 = scene_bank[(current_scene * sc_size) + sc_mh1_slot] + 1
		scm2 = scene_bank[(current_scene * sc_size) + sc_mh2_slot] + 1
		scm3 = scene_bank[(current_scene * sc_size) + sc_mh3_slot] + 1
		scm4 = scene_bank[(current_scene * sc_size) + sc_mh4_slot] + 1
		LabelPad 10, {EXT MIDI    }, { S}, current_scene+1, { modes  }, scm1, {-}, scm2, {-}, scm3, {-}, scm4
	endif
@End

@LabelMidiInChannelsPadB
	Call @CheckMidiChannelConflict
	if NOT midi_channel_conflict
		LabelPad 11, {SEQUENCE   }, { Midi chs }, midi_channels_used[5]+1, {-}, midi_channels_used[6]+1, {-}, midi_channels_used[7]+1, {-}, midi_channels_used[8]+1
	else
		LabelPad 11, {SEQUENCE   }, {!CONFLICT! }, midi_channels_used[5]+1, {-}, midi_channels_used[6]+1, {-}, midi_channels_used[7]+1, {-}, midi_channels_used[8]+1
	endif
@End

@LabelMidiOutChannelsPad
	Call @CheckMidiChannelConflict
	if NOT midi_channel_conflict
		LabelPad 12, {CHORDS OUT   }, { Midi chs   }, midi_channels_used[9]+1, {-}, midi_channels_used[10]+1, {-}, midi_channels_used[11]+1, {-}, midi_channels_used[12]+1
	else
		LabelPad 12, {CHORDS     }, {  !CONFLICT!  }, midi_channels_used[9]+1, {-}, midi_channels_used[10]+1, {-}, midi_channels_used[11]+1, {-}, midi_channels_used[12]+1
	endif
@End

@LabelChordNotesOutPad
	o1 = scene_bank[(current_scene * sc_size) + sc_och1_slot]
	o2 = scene_bank[(current_scene * sc_size) + sc_och2_slot]
	o3 = scene_bank[(current_scene * sc_size) + sc_och3_slot]
	o4 = scene_bank[(current_scene * sc_size) + sc_och4_slot]
	LabelPad 13, {CHORDS OUT  }, {S}, current_scene+1, { modes }, o1, {-}, o2, {-}, o3, {-}, o4
@End
	
@OnShiftDown
	//# xosd
	if in_mode_select
		in_mode_select = FALSE
		LabelPads {Scene: }, current_scene+1, { Chord: }, current_chord+1
		if (mode >= 1)
			mode = 0
			songmode = 1 //# exit to scene lock
			knob_set = 1
		endif		
		Call @SetupLayout
	else
		// #Mode selection for Knobs n Pads
		in_mode_select = TRUE
		LabelPads {SETTINGS:   (shift to exit)}
		for i = 0 to (number_of_modes - 1)
			ColorPad i, col_mode_select
			LabelPad i, { } //# empty label to overwrite chord info
			if i = 0
				LatchPad i, NO
				if (songmode = 0)
					LabelPad i, {PLAYSONG: Active }
				elseif (songmode = 1)
					LabelPad i, {PLAYSONG: Scene locked}
				elseif (songmode = 2)
					LabelPad i, {PLAYSONG: Chord locked}
				else
					LabelPad i, {PLAYSONG: Disabled}
				endif
			elseif i = 1
				LatchPad i, NO
				if (NOT HostRunning) or (HostRunning and allow_mode_chg_playbk)
					LabelPad i, {+CHORDS: Select}
				endif
			elseif i = 2
				LatchPad i, NO
				if (NOT HostRunning) or (HostRunning and allow_mode_chg_playbk)
					LabelPad i, {+CHORDS: Construct}
				endif
			elseif i = 3
				LatchPad i, NO
				if (NOT HostRunning) or (HostRunning and allow_mode_chg_playbk)  
					LabelPad i, {+CHORDS: Record}
				endif
			elseif (i>=4 and i<=5) or (i=14)
				//# not in use
				LatchPad i, No
				LabelPad i, { }
			elseif i = 6
				LatchPad i, NO
				if (NOT HostRunning) or (HostRunning and allow_mode_chg_playbk)
					LabelPad i, {COPY/PASTE }
				endif
			elseif i = 7
				LatchPad i, NO
				if NOT HostRunning
					LabelPad i, { SAVE     }
				endif
			elseif i = 8
				LatchPad i, NO
			elseif i = 9
				LatchPad i, NO
				if NOT HostRunning
					Call @LabelMidiInChannelsPadA
				endif
			elseif i = 10
				LatchPad i, NO
				Call @LabelSceneModesPad	
			elseif i = 11
				LatchPad i, NO
				if NOT HostRunning
					Call @LabelMidiInChannelsPadB
				endif
			elseif i = 12
				LatchPad i, NO
				if NOT HostRunning
					Call @LabelMidiOutChannelsPad
				endif
			elseif i = 13
				LatchPad i, NO
				Call @LabelChordNotesOutPad
			elseif i = 15
				LatchPad i, NO
				if (NOT HostRunning) or (HostRunning and allow_mode_chg_playbk)
					LabelPad i, {DELETE  }
				endif
			endif
		endfor
		if NOT HostRunning
			LabelPad 8, { EXT MIDI  }, {   Key/Scale      }, (NoteName, selected_midi_in_root), { }, (ScaleName, allowed_scales[selected_midi_in_scale])
		endif
		LatchPad mode, YES
	endif
	Call @UpdateCurrentKnobset
@End

@OnShiftUp
@End

@SortList
	//# set list to sort to sort_list and len_list to # items is your list
	Log {List to sort }, sort_list[0], sort_list[1], sort_list[2], sort_list[3]
	changed = 1
	while (changed = 1)
		changed = 0
		for i = 0 to len_list - 2
		if sort_list[i] > sort_list[i+1]
				changed = 1
				tmp = sort_list[i]
				sort_list[i] = sort_list[i+1]
				sort_list[i+1] = tmp
			endif
		endfor
	endwhile
	Log {Sorted List: }, sort_list[0], sort_list[1], sort_list[2], sort_list[3]
@End

@LabelScenePad
	//# Set scn_to_label var before calling
	sc_dur = scene_bank[scn_to_label * sc_size]
	sc_txp = txpose_labels[scene_bank[(scn_to_label * sc_size) + sc_txp_slot]]
	sc_preset = scene_bank[(scn_to_label * sc_size) + sc_preset_slot]
	sc_pgchg = scene_bank[(scn_to_label * sc_size) + sc_pgmchg_slot]
	sc_txpm = sc_txp - 3
	if sc_txpm < 0
		sc_txpm = sc_txpm + 12
	endif
	if sc_pgchg >= 0
		LabelPad scn_to_label, {S}, scn_to_label+1, { [}, sc_dur, { bars]}, {    }, (NoteName sc_txp), {/}, (NoteName sc_txpm), {m(}, txpose_array[scene_bank[(scn_to_label * sc_size) + sc_txp_slot]], {st) }, {  P}, sc_preset, { PC}, sc_pgchg
	else
		LabelPad scn_to_label, {S}, scn_to_label+1, { [}, sc_dur, { bars]}, {    }, (NoteName sc_txp), {/}, (NoteName sc_txpm), {m(}, txpose_array[scene_bank[(scn_to_label * sc_size) + sc_txp_slot]], {st) }, {  P}, sc_preset, { PC}, {-}
	endif
@End

@LabelChordPad
	//# Set chrd_to_label var before calling xlcp
	chord_slot = (current_scene * 100) + ((chrd_to_label-8) * 10))
	//# txpose amount. get value stored on dial use to access array of st amounts
	txpose_index = scene_bank[(current_scene * sc_size) + sc_txp_slot]
	sta = txpose_array[txpose_index] //# scene txpose amount
	cn1 = chord_bank[chord_slot]
	cn2 = chord_bank[chord_slot + 1]
	cn3 = chord_bank[chord_slot + 2]
	cn4 = chord_bank[chord_slot + 3]
	cd = chord_bank[chord_slot + dur_slot]
	cd_bars = Div cd, 4
	lc_beats = (cd % HostBeatsPerMeasure) * (100/HostBeatsPerMeasure)
	ci = chord_bank[chord_slot + inv_slot]
	if chord_bank[chord_slot + bass_slot] >= 0
		cb = chord_bank[chord_slot + bass_slot] + 12 + sta
	else
		cb = chord_bank[chord_slot + bass_slot] //# ie -1
	endif
	
	Call @ReorderNoteLabelsForInversion
	if cn4 >= 0 //# A tetrad witha a note i cn4 
		LabelPad, chrd_to_label, {[}, cd_bars, {.}, lc_beats, { bars]}, { Inv:}, 	ci, {     Root:}, (NoteName, cn1), {     Bass:}, (NoteName, cb), {      }, (NoteName, inc[0]), (NoteName, inc[1]+sta), (NoteName, inc[2]+sta), (NoteName, inc[3]+sta)  
	else
		LabelPad, chrd_to_label, {[}, cd_bars, {.}, lc_beats, { bars]}, { Inv:}, 	ci, {     Root:}, (NoteName, cn1), {     Bass:}, (NoteName, cb), {      }, (NoteName, inc[0]+sta), (NoteName, inc[1]+sta), (NoteName, inc[2]+sta)
	endif
@End

@ReorderNoteLabelsForInversion
	//# Just re-orders the notes on the chord pad in inverted order
	inc = [] //# inverted chord notes
	if (ci = 0) or (ci = 4) or (ci = -4)
		inc = [cn1, cn2, cn3, cn4]
	elseif ci = 1
		inc = [cn2, cn3, cn4, cn1]
		if cn4 = -1
			inc = [cn2, cn3, cn1, cn4]
		endif
	elseif ci = 2
		inc = [cn3, cn4, cn1, cn2]
		if cn4 = -1
			inc = [cn3, cn1, cn2, cn4]
		endif
	elseif ci = 3
		inc = [cn4, cn1, cn2, cn3]
		if cn4 = -1
			inc = [cn1, cn2, cn3, cn4]
		endif
	elseif ci = -1
		inc = [cn4, cn1, cn2, cn3]
		if cn4 = -1
			inc = [cn3, cn1, cn2, cn4]
		endif
	elseif ci = -2
		inc = [cn3, cn4, cn1, cn2]
		if cn4 = -1
			inc = [cn2, cn3, cn1, cn4]
		endif
	elseif ci = -3
		inc = [cn2, cn3, cn4, cn1]
		if cn4 = -1
			inc = [cn1, cn2, cn3, cn4]
		endif
	endif
@End

@SetupLayout
	//#xsl setup layout pads
	if in_mode_select
		Exit
	else
		//# Setup scene pads
		for i = 0 to 7  
			if scene_bank[i * sc_size] > 0
				ColorPad i, col_scene
				scn_to_label = i
				Call @LabelScenePad
			else
				ColorPad i, col_unused
				LabelPad i, { }
			endif
			LatchPad i, NO
			if (scene_bank[i * sc_size] > 0) and (mode = 15) and NOT in_mode_select
				ColorPad i, col_del_chord
			endif
		endfor		  
		//# Setup chord pads  
		for i = 8 to 15
			chord_slot = (current_scene * 100) + ((i-8) * 10)
			LatchPad i, NO
			if chord_bank[chord_slot + dur_slot] > 0
				ColorPad i, col_chord
				chrd_to_label = i
				Call @LabelChordPad
			else
				ColorPad i, col_unused
				LabelPad i, { }
			endif
			if (mode = 3)
				ColorPad i, col_rec_chord
			elseif (mode = 15) and (chord_bank[chord_slot] > 0)
				ColorPad i, col_del_chord
			endif
		endfor
		//# Handle current scene and chord colors
		if (songmode = 0) //# Playthru no lock
			ColorPad current_scene, col_sel_scene
			ColorPad current_chord+8, col_sel_chord
		elseif (songmode = 1) //# Lock to scene
			ColorPad current_chord+8, col_sel_chord
			LatchPad current_scene, YES
		elseif (songmode = 2)
			LatchPad current_scene, YES
			LatchPad current_chord+8, YES
		elseif (mode = 3) //# REC CHORDS 
			ColorPad current_scene, loop_col //# Locked playback doesnt change
			if rec_chord_note_count = 0
				LabelPad current_chord+8, {... waiting}
			endif
			Log {REC CHORDS}
		endif
		if (mode >= 1)
			LatchPad current_scene, YES
			LatchPad current_chord+8, YES
		endif
		//# Handle pending chord and scene changes in playback
		if HostRunning and (songmode <=2)
			if chord_change_requested >= 0
				ColorPad chord_change_requested+8, col_pending
			endif
			if scene_change_requested >= 0
				ColorPad scene_change_requested, col_pending
			endif
		endif
	endif
	Call @UpdateCurrentKnobset
@End
	
@TransposeCalcArrays
	//# Creates an array to transpose using the circle of 5ths 
	//# but keeping to one octave
	FillArray txpose_array, 99, 13
	FillArray txpose_labels, 99, 13 
	txpose_index = 0
	for i = 6 to 11
		key = (i * 7) % 12
		txpose_val = key
		if key > Abs (key - 12)
			txpose_val = key - 12 
		endif
		//# Log {APos: }, i, { Key: }, (NoteName key), { TXPOSE: }, txpose_val, { Semitones: }, key, { -VE: }, key -12
		txpose_array[txpose_index] = txpose_val
		label = txpose_array[txpose_index]
		if txpose_array[txpose_index] < 0
			label = txpose_array[txpose_index] + 12
		endif
		txpose_labels[txpose_index] = label
		txpose_index = txpose_index + 1 
	endfor  
	for i = 0 to 6
		key = (i * 7) % 12
		txpose_val = key
		if key > Abs (key - 12)
			txpose_val = key - 12 
		endif
		//# Log {BPos: }, i, { Key: }, (NoteName key), { TXPOSE: }, txpose_val, { Semitones: }, key, { -VE: }, key -12 
		txpose_array[txpose_index] = txpose_val
		label = txpose_array[txpose_index]
		if txpose_array[txpose_index] < 0
			label = txpose_array[txpose_index] + 12
		endif
		txpose_labels[txpose_index] = label
		txpose_index = txpose_index + 1
	endfor
	
	//# Log {Txpose vals and Labels}
	//#for a = 0 to 12
		//# Log (NoteName txpose_labels[a]) , { val: }, txpose_array[a]
	//#endfor
@End

@ChangeScenePreset
	//# Update chords for the current scene with a set of chords
	//# Create a scene in scene_bank
	//# use arrays psd, psn, prog_durs, prog_invs, prog_bass to load data 
	//# use psn array for scale notes, use 0 in front to keep numbering sane
	//# use 1 octave of scale notes. Inversions will be calculated
	//# Call @HandleChordBankPresetUpdate and then LabelPads with scene name
	//# ionian = [2,2,1,2,2,2,1] CDEFGABC [0, 60, 62, 64, 65, 67, 69, 71, 72]
	//# dorian = [2,1,2,2,2,1,2] DEFGABCD [0, 62, 64, 65, 67, 69, 71, 72, 74]
	//# phrygian = [1,2,2,2,1,2,2] EFGABCDE [0, 64, 65, 67, 69, 71, 72, 74, 76]
	//# lydian = [2,2,2,1,2,2,1] FGABCDEF [0, 65, 67, 69, 71, 72, 74, 76, 77]
	//# mixolydian = [2,2,1,2,2,1,2] GABCDEFG [0, 67, 69, 71, 72, 74, 76, 77, 79]
	//# aeolian = [2,1,2,2,1,2,2,] ABCDEFGA [0, 69, 71, 72, 74, 76, 77, 79, 81]
	//# locrian = [1,2,2,1,2,2,2] BCDEFGAB [0, 71, 72, 74, 76, 77, 79, 81, 83]
	
	//# Default chord bank settings. Copy to preset to override
	//# scene setup. map txpose based on circle of 5ths. 
	//# scn_preset must always be setting for preset (self)
	scene_bank[current_scene * sc_size] = [8,6,scn_preset,0,0,0,0,0,0,0,0,-1]
	
	//# chord settings
	//# psd is scale degrees for each chord in the progression
	psd = [1,3,5,-1, 2,4,6,-1, 3,5,7,-1, 4,6,1,-1, 5,7,2,-1, 6,1,3,-1, 7,2,4,-1, 1,3,5,7]
	//# other settings for the 8 chord slots in this current scene
	prog_durs = [4,4,4,4,4,4,4,4]
	prog_bass = [1,2,3,4,5,6,7,1]
	prog_invs = [0,0,0,0,0,0,0,3]
	//# chord notes always stored in an ascending order. 
	//# So 461 will have an octave added to the 1. 
	//# prog_invs are applied at NoteOut. No effect on how notes stored here
				
	if scn_preset = 1
		scene_bank[current_scene * sc_size] = [4,6,scn_preset,0,0,0,0,0,0,0,0,-1]
		chord_bank[(current_scene * 100) + 0] = [60,64,67,-1,4,0,-1]
		chord_bank[(current_scene * 100) + 10] = [-1,-1,-1,-1,0,0,-1]
		chord_bank[(current_scene * 100) + 20] = [-1,-1,-1,-1,0,0,-1]
		chord_bank[(current_scene * 100) + 30] = [-1,-1,-1,-1,0,0,-1]
		chord_bank[(current_scene * 100) + 40] = [-1,-1,-1,-1,0,0,-1]
		chord_bank[(current_scene * 100) + 50] = [-1,-1,-1,-1,0,0,-1]
		chord_bank[(current_scene * 100) + 60] = [-1,-1,-1,-1,0,0,-1]
		chord_bank[(current_scene * 100) + 70] = [-1,-1,-1,-1,0,0,-1]
		LabelPads {An empty scene. Press shift to select a +CHORDS mode}
		Call @SetupLayout
	elseif scn_preset = 2
		scene_bank[current_scene * sc_size] = [4,6,scn_preset,0,0,0,0,0,0,0,0,-1]
		psn = [0, 60, 62, 64, 65, 67, 69, 71, 72]
		psd = [1,3,5,-1, 5,7,2,-1, 6,1,3,-1, 4,6,1,-1, 0,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,0,0]
		prog_durs = [4,4,4,4,0,0,0,0]
		prog_bass = [1,5,6,4,0,0,0,0]
		prog_invs = [0,-1,-1,-1,0,0,0,0]
		Call @HandleChordBankPresetUpdate
		LabelPads {Classic I-V-vi-IV progression in C Major}
	elseif scn_preset = 3
		psn = [0, 60, 62, 64, 65, 67, 69, 71, 72]
		prog_invs = [0,0,0,0,0,0,0,4]
		Call @HandleChordBankPresetUpdate
		LabelPads {C IONIAN Major diatonic chord set}
	elseif scn_preset = 4
		psn = [0, 62, 64, 65, 67, 69, 71, 72, 74]
		prog_invs = [0,0,0,0,0,0,3,4]
		Call @HandleChordBankPresetUpdate
		LabelPads {D DORIAN diatonic chord set}
	elseif scn_preset = 5
		psn = [0, 64, 65, 67, 69, 71, 72, 74, 76]
		prog_invs = [0,0,0,0,0,3,3,4]
		Call @HandleChordBankPresetUpdate
		LabelPads {E PHRYGIAN diatonic chord set}
	elseif scn_preset = 6
		psn = [0, 65, 67, 69, 71, 72, 74, 76, 77]
		prog_invs = [0,0,0,0,3,3,3,4]
		Call @HandleChordBankPresetUpdate
		LabelPads {F LYDIAN diatonic chord set}
	elseif scn_preset = 7
		psn = [0, 67, 69, 71, 72, 74, 76, 77, 79]
		prog_invs = [0,0,0,3,3,3,3,4]
		Call @HandleChordBankPresetUpdate
		LabelPads {G MIXOLYDIAN diatonic chord set}
	elseif scn_preset = 8
		psn = [0, 69, 71, 72, 74, 76, 77, 79, 81]
		prog_invs = [0,0,3,3,3,3,3,4]
		Call @HandleChordBankPresetUpdate
		LabelPads {A AEOLIAN Natural Minor diatonic chord set}
	elseif scn_preset = 9
		psn = [0, 71, 72, 74, 76, 77, 79, 81, 83]
		prog_invs = [0,3,3,3,3,3,3,4]
		Call @HandleChordBankPresetUpdate
		LabelPads {B LOCRIAN diatonic chord set}
	elseif scn_preset = 10
		scene_bank[current_scene * sc_size] = [4,6,10,0,0,0,0,0,0,0,0,-1]
		chord_bank[(current_scene * 100) + 0] = [9,12,16,-1,4,0,69]
		chord_bank[(current_scene * 100) + 10] = [11,14,17,-1,4,0,71]
		chord_bank[(current_scene * 100) + 20] = [0,4,7,-1,4,3,72]
		chord_bank[(current_scene * 100) + 30] = [2,5,9,-1,4,3,74]
		chord_bank[(current_scene * 100) + 40] = [4,8,11,-1,4,3,76]
		chord_bank[(current_scene * 100) + 50] = [5,9,12,-1,4,3,77]
		chord_bank[(current_scene * 100) + 60] = [7,10,13,-1,4,3,7]
		chord_bank[(current_scene * 100) + 70] = [9,12,16,-1,4,3,69]
		LabelPads {Minor triadic harmony (from Natural & Harmonic minor diatonic chords)} 
		Call @SetupLayout
	elseif scn_preset = 11
		scene_bank[current_scene * sc_size] = [4,6,10,0,0,0,0,0,0,0,0,-1]
		chord_bank[(current_scene * 100) + 0] = [9,12,16,19,4,0,69]
		chord_bank[(current_scene * 100) + 10] = [11,14,17,21,4,0,71]
		chord_bank[(current_scene * 100) + 20] = [0,4,7,11,4,4,72]
		chord_bank[(current_scene * 100) + 30] = [2,5,9,12,4,4,74]
		chord_bank[(current_scene * 100) + 40] = [4,8,11,14,4,4,76]
		chord_bank[(current_scene * 100) + 50] = [5,9,12,16,4,4,77]
		chord_bank[(current_scene * 100) + 60] = [7,10,13,17,4,4,7]
		chord_bank[(current_scene * 100) + 70] = [9,12,16,19,4,4,69]
		LabelPads {Diatonic 7th chords Minor (Hybrid)} 
		Call @SetupLayout
	endif
@End

@HandleChordBankPresetUpdate
	chord_slot = (current_scene * 100)
	for c = 0 to 7
		//# get from scale note array using scale degree as index
		cn1 = psn[ psd[(c*4) + 0] ]
		cn2 = psn[ psd[(c*4) + 1] ]
		cn3 = psn[ psd[(c*4) + 2] ]
		//# Log {CNs }, cn1, cn2, cn3
		if psd[(c*4) + 3] >= 0 //# 7th note is added
			cn4 = psn[ psd[(c*4) + 3] ]
		else
			cn4 = -1
		endif
		//# return scale degrees to root inversion
		if cn2 < cn1
			cn2 = cn2 + 12
			//# Log {cn2 after inv: }, cn2
		endif
		if cn3 < cn2
			cn3 = cn3 + 12
			//# Log {cn3 after inv: }, cn3
		endif
		if (cn4 >= 0) and (cn4 < cn3)
			cn4 = cn4 + 12
			//# Log {cn4 after inv: }, cn4
		endif
		chord_bank[chord_slot + (c*10) + 0] = cn1
		chord_bank[chord_slot + (c*10) + 1] = cn2
		chord_bank[chord_slot + (c*10) + 2] = cn3
		chord_bank[chord_slot + (c*10) + 3] = cn4
		chord_bank[chord_slot + (c*10) + 4] = prog_durs[c]
		chord_bank[chord_slot + (c*10) + 5] = prog_invs[c]
		chord_bank[chord_slot + (c*10) + 6] = psn[ prog_bass[c] ]
	endfor
	Call @SetupLayout
@End

@LogCurrentSceneToPresetFormat
	//# Logs current scene to a format which can be added to the preset section
	Log {======= END PRESET LOG =======}
	Log {	 Call @SetupLayout}
	Log {	 LabelPads YOUR PRESET NAME -in curly brackets!! } 
	chord_slot = (current_scene * 100)
	for c = 7 to 0
		c_loc = (chord_slot + (c*10))
		n1 = chord_bank[c_loc]
		n2 = chord_bank[c_loc + 1]
		n3 = chord_bank[c_loc + 2]
		n4 = chord_bank[c_loc + 3]
		d = chord_bank[c_loc + dur_slot]
		i = chord_bank[c_loc + inv_slot]
		b = chord_bank[c_loc + bass_slot]
		Log {	   chord_bank[(current_scene * 100) + }, , c*10, {] = [}, n1,{,}, n2,{,}, n3,{,}, n4,{,}, d,{,}, i,{,}, b, {]}
	endfor
	Log {	   scene_bank[},{current_scene * sc_size}, {] = [4,6,}, num_sc_presets+1, {,0,0,0,0,0,0,0,0,-1]}
	Log {elseif scn_preset = }, num_sc_presets+1
	Log {======= START PRESET LOG =======}
	Log {+ Make sure to change YOUR PRESET NAME and put it in curly brackets}
	Log {+ Update num_sc_presets variable to }, num_sc_presets+1,{ in @InitKnobVariables}
	Log {+ Copy this PRESET LOG to the end of @ChangeScenePreset before 'endif'}
	Log {++++++ INSTRUCTIONS FOR ADDING A PRESET +++++}
@End
