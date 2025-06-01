import numpy as np
import librosa
import json
import os


def tolist_if_array(val):
    if isinstance(val, np.ndarray):
        return val.tolist()
    elif isinstance(val, (list, tuple)):
        return [tolist_if_array(v) for v in val]
    else:
        return val

# def tolist_if_array(val):
# 	if isinstance(val, np.ndarray):
# 		return val.tolist()
# 	else:
# 		return val



def create_beatmap(y, sr):
	beatmap = {}

	mono_y = librosa.to_mono(y)
	duration = librosa.get_duration(y=mono_y, sr=sr)

	beatmap["harmonic_y"], beatmap["percussive_y"] = librosa.effects.hpss(mono_y, kernel_size=31, power=2.0)

	beatmap["plp_percussive"] = librosa.beat.plp(y=beatmap["percussive_y"], sr=sr)
	beatmap["plp_beats_percussive"] = librosa.util.localmax(beatmap["plp_percussive"])
	beatmap["beat_frames_percussive"] = np.nonzero(beatmap["plp_beats_percussive"])[0]
	beatmap["beat_times_percussive"] = librosa.frames_to_time(beatmap["beat_frames_percussive"], sr=sr)

	beatmap["plp_harmonic"] = librosa.beat.plp(y=beatmap["harmonic_y"], sr=sr)
	beatmap["plp_beats_harmonic"] = librosa.util.localmax(beatmap["plp_harmonic"])
	beatmap["beat_frames_harmonic"] = np.nonzero(beatmap["plp_beats_harmonic"])[0]
	beatmap["beat_times_harmonic"] = librosa.frames_to_time(beatmap["beat_frames_harmonic"], sr=sr)

	beatmap["beat_frames_percussive"] = beatmap["beat_frames_percussive"][beatmap["beat_frames_percussive"] < duration]
	beatmap["beat_frames_harmonic"] = beatmap["beat_frames_harmonic"][beatmap["beat_frames_harmonic"] < duration]

	beatmap["tempo"], _ = librosa.beat.beat_track(y=mono_y, sr=sr, tightness=10)

	# beatmap["kick_toggles"] = utils.detect_hardstyle_kick_toggles(mono_y, sr)

	beatmap["harmonic_amp"] = librosa.feature.rms(y=beatmap["harmonic_y"])[0]
	beatmap["percussive_amp"] = librosa.feature.rms(y=beatmap["percussive_y"])[0]
	

	return beatmap



def save_beatmap(beatmap, beatmap_path):
	beatmap = {
		"tempo": tolist_if_array(beatmap["tempo"]),
		"beat_times_percussive": tolist_if_array(beatmap["beat_times_percussive"]),
		"beat_times_harmonic": tolist_if_array(beatmap["beat_times_harmonic"]),
		"harmonic_amp": tolist_if_array(beatmap["harmonic_amp"]),
		"percussive_amp": tolist_if_array(beatmap["percussive_amp"]),
		# "kick_toggles": utils.tolist_if_array(beatmap["kick_toggles"])
	}

	with open(f"{beatmap_path}/beatmap.json", "w") as f:
		json.dump(beatmap, f)

def load_beatmap(beatmap_path):
	if os.path.isfile(beatmap_path):
		with open(beatmap_path, 'r') as f:
			beatmap = json.load(f)
		return beatmap
	else:
		raise FileNotFoundError(f"Beatmap file not found: {beatmap_path}")