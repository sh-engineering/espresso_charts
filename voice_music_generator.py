# -*- coding: utf-8 -*-
"""
Espresso Charts — Audio Pipeline (ElevenLabs API)
====================================================
Generate voiceover and background music via the ElevenLabs API,
then mix them onto a silent chart animation MP4.

All functions use raw `requests` — no SDK dependency needed.

Setup in Colab
--------------
  from google.colab import userdata
  ELEVENLABS_API_KEY = userdata.get('ELEVENLABS_API_KEY')

Functions
---------
eListVoices           — browse available voices
eGenerateVoiceover    — text → voiceover MP3 (TTS API)
eGenerateMusic        — prompt → instrumental MP3 (Music API)
eAddVoiceover         — overlay voiceover onto video
eAddMusic             — overlay looping music onto video
eAddAudio             — overlay voiceover + music in one pass
eGetDuration          — read duration of any audio/video file
"""


# ============================================================================
# CONSTANTS
# ============================================================================

# Pre-made voice IDs (available to all accounts)
VOICES = {
    "adam":    "pNInz6obpgDQGcFmaJgB",   # American male, deep & warm
    "rachel": "21m00Tcm4TlvDq8ikWAM",   # American female, calm & clear
    "clyde":  "2EiwWnXFnvU5JabPnv8n",   # American male, war veteran
    "domi":   "AZnzlk1XvdvUeBnXmlld",   # American female, strong
    "bella":  "EXAVITQu4vr4xnSDxMaL",   # American female, soft
    "antoni": "ErXwobaYiN019PkySvjV",   # American male, professional
    "josh":   "TxGEqnHWrfWFTfGW9XjX",   # American male, deep narrator
    "sam":    "yoZ06aMxZJJ28mfd3POQ",   # American male, raspy
    "george": "JBFqnCBsd6RMkjVDRZzb",   # British male, warm narrator
}

# TTS model IDs
TTS_MODELS = {
    "v3":              "eleven_v3",               # most expressive (3k chars)
    "multilingual_v2": "eleven_multilingual_v2",  # 10k chars, 70+ languages
    "turbo_v2.5":      "eleven_turbo_v2_5",       # fast, 32 languages
    "flash_v2.5":      "eleven_flash_v2_5",       # ultra-low latency
}

# Suggested music prompts for Espresso Charts Reels
MUSIC_PRESETS = {
    "lofi_coffee": (
        "Gentle lo-fi hip-hop instrumental, soft Rhodes piano chords, "
        "warm vinyl crackle, slow tempo 75 BPM, relaxed coffee shop vibe, "
        "no vocals, ambient and minimal"
    ),
    "editorial_minimal": (
        "Minimal ambient instrumental, soft piano with subtle synth pads, "
        "calm and professional tone, 80 BPM, no percussion, "
        "suitable as background for news or data journalism"
    ),
    "upbeat_data": (
        "Light upbeat instrumental, acoustic guitar and soft percussion, "
        "positive and curious mood, 100 BPM, clean and modern, no vocals"
    ),
    "morning_news": (
        "Warm jazz instrumental, brushed drums, upright bass walking line, "
        "muted trumpet melody, 90 BPM, morning radio feel, no vocals"
    ),
}


# ============================================================================
# UTILITY
# ============================================================================
def eGetDuration(filepath):
    """Return duration in seconds of any video or audio file."""
    cmd = [
        'ffprobe', '-v', 'quiet',
        '-print_format', 'json',
        '-show_format',
        filepath
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"ffprobe failed on {filepath}: {r.stderr}")
    return float(json.loads(r.stdout)['format']['duration'])


# ============================================================================
# LIST VOICES
# ============================================================================
def eListVoices(api_key, limit=20):
    """
    Print available voices from your ElevenLabs account.

    Parameters
    ----------
    api_key : str — ElevenLabs API key
    limit   : int — max voices to show
    """
    r = requests.get(
        "https://api.elevenlabs.io/v1/voices",
        headers={"xi-api-key": api_key}
    )
    r.raise_for_status()
    voices = r.json().get("voices", [])

    print(f"{'Name':<20} {'Voice ID':<28} {'Labels'}")
    print("-" * 76)
    for v in voices[:limit]:
        labels = v.get("labels", {})
        lbl = ", ".join(f"{k}={val}" for k, val in labels.items()) if labels else ""
        print(f"{v['name']:<20} {v['voice_id']:<28} {lbl}")

    print(f"\nShowing {min(limit, len(voices))} of {len(voices)} voices")
    return voices


# ============================================================================
# GENERATE VOICEOVER (TTS API)
# ============================================================================
def eGenerateVoiceover(
    text,
    api_key,
    output_file="voiceover.mp3",
    voice_id=None,
    voice_name="george",
    model="multilingual_v2",
    stability=0.50,
    similarity_boost=0.75,
    style=0.0,
    speed=1.0,
    output_format="mp3_44100_128",
    language=None,
):
    """
    Generate voiceover audio from text via the ElevenLabs TTS API.

    Parameters
    ----------
    text            : str   — script to speak
    api_key         : str   — ElevenLabs API key
    output_file     : str   — output path (.mp3)
    voice_id        : str   — explicit voice ID (overrides voice_name)
    voice_name      : str   — shortcut from VOICES dict ("george", "rachel", etc.)
    model           : str   — model shortcut or full ID
    stability       : float — 0.0 (variable) to 1.0 (stable)
    similarity_boost: float — 0.0 to 1.0
    style           : float — 0.0 to 1.0, expressiveness (v2+ models)
    speed           : float — playback speed (0.7 to 1.3 typical)
    output_format   : str   — e.g. "mp3_44100_128", "mp3_44100_192"
    language        : str   — ISO 639-1 code to force language (e.g. "en")

    Returns
    -------
    output_file : str

    Example
    -------
    eGenerateVoiceover(
        text="Valentine's Day spending hit a record twenty-nine billion dollars.",
        api_key=ELEVENLABS_API_KEY,
        voice_name="george",
        output_file="vo.mp3"
    )
    """
    # Resolve voice ID
    if voice_id is None:
        voice_id = VOICES.get(voice_name.lower())
        if voice_id is None:
            raise ValueError(
                f"Unknown voice_name '{voice_name}'. "
                f"Use one of {list(VOICES.keys())} or pass voice_id directly."
            )

    model_id = TTS_MODELS.get(model, model)

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
    }

    payload = {
        "text": text,
        "model_id": model_id,
        "output_format": output_format,
        "voice_settings": {
            "stability": stability,
            "similarity_boost": similarity_boost,
            "style": style,
            "use_speaker_boost": True,
        },
    }

    if speed != 1.0:
        payload["voice_settings"]["speed"] = speed
    if language:
        payload["language_code"] = language

    r = requests.post(url, headers=headers, json=payload)
    if r.status_code != 200:
        raise RuntimeError(f"ElevenLabs TTS error ({r.status_code}): {r.text[:500]}")

    with open(output_file, "wb") as f:
        f.write(r.content)

    size_kb = os.path.getsize(output_file) / 1024
    dur = eGetDuration(output_file)
    print(f"✅ Voiceover saved → {output_file}  ({dur:.1f}s, {size_kb:.0f} KB, "
          f"voice={voice_name}, model={model})")
    return output_file


# ============================================================================
# GENERATE MUSIC (Music API — streaming endpoint)
# ============================================================================
def eGenerateMusic(
    api_key,
    prompt=None,
    output_file="background_music.mp3",
    duration_ms=15000,
    force_instrumental=True,
    output_format="mp3_44100_128",
    preset=None,
):
    """
    Generate background music via the ElevenLabs Music API.

    Parameters
    ----------
    prompt              : str   — text description of desired music
    api_key             : str   — ElevenLabs API key
    output_file         : str   — output path (.mp3)
    duration_ms         : int   — desired length in milliseconds (3000–600000)
    force_instrumental  : bool  — guarantee no vocals
    output_format       : str   — audio format string
    preset              : str   — key from MUSIC_PRESETS to use instead of prompt
                                  ("lofi_coffee", "editorial_minimal",
                                   "upbeat_data", "morning_news")

    Returns
    -------
    output_file : str

    Example
    -------
    eGenerateMusic(
        preset="lofi_coffee",
        api_key=ELEVENLABS_API_KEY,
        duration_ms=20000,
        output_file="bg_music.mp3"
    )
    """
    if preset is not None:
        if preset not in MUSIC_PRESETS:
            raise ValueError(
                f"Unknown preset '{preset}'. "
                f"Options: {list(MUSIC_PRESETS.keys())}"
            )
        prompt = MUSIC_PRESETS[preset]

    url = "https://api.elevenlabs.io/v1/music/stream"

    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
    }

    payload = {
        "prompt": prompt,
        "music_length_ms": duration_ms,
        "force_instrumental": force_instrumental,
        "output_format": output_format,
    }

    print(f"⏳ Generating music ({duration_ms/1000:.0f}s)... this may take 30–90 seconds.")
    r = requests.post(url, headers=headers, json=payload, stream=True)

    if r.status_code != 200:
        raise RuntimeError(f"ElevenLabs Music error ({r.status_code}): {r.text[:500]}")

    with open(output_file, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

    size_kb = os.path.getsize(output_file) / 1024
    dur = eGetDuration(output_file)
    print(f"✅ Music saved → {output_file}  ({dur:.1f}s, {size_kb:.0f} KB)")
    return output_file


# ============================================================================
# ADD VOICEOVER TO VIDEO
# ============================================================================
def eAddVoiceover(
    video_file,
    voiceover_file,
    output_file="espresso_with_vo.mp4",
    vo_volume=1.0,
    vo_delay=0.0,
    vo_fade_in=0.0,
    vo_fade_out=0.3,
):
    """
    Overlay a voiceover audio file onto a video.

    Parameters
    ----------
    video_file     : str   — input MP4 (silent)
    voiceover_file : str   — voiceover audio (mp3/wav/m4a)
    output_file    : str   — output MP4
    vo_volume      : float — volume multiplier (1.0 = original)
    vo_delay       : float — seconds to delay voiceover start
    vo_fade_in     : float — seconds of fade-in
    vo_fade_out    : float — seconds of fade-out at end of voiceover
    """
    for f in [video_file, voiceover_file]:
        if not os.path.isfile(f):
            raise FileNotFoundError(f"File not found: {f}")

    vid_dur = eGetDuration(video_file)

    vo_filters = [f"volume={vo_volume}"]
    if vo_delay > 0:
        ms = int(vo_delay * 1000)
        vo_filters.append(f"adelay={ms}|{ms}")
    if vo_fade_in > 0:
        vo_filters.append(f"afade=t=in:st=0:d={vo_fade_in}")
    if vo_fade_out > 0:
        vo_dur = eGetDuration(voiceover_file)
        fo_start = vo_dur - vo_fade_out + vo_delay
        vo_filters.append(f"afade=t=out:st={fo_start:.2f}:d={vo_fade_out}")

    vo_chain = ",".join(vo_filters)

    cmd = [
        'ffmpeg', '-y',
        '-i', video_file,
        '-i', voiceover_file,
        '-filter_complex',
        f'[1:a]{vo_chain}[vo];'
        f'[vo]apad=whole_dur={vid_dur:.2f}[aout]',
        '-map', '0:v', '-map', '[aout]',
        '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
        '-shortest', output_file
    ]

    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"ffmpeg failed:\n{r.stderr}")

    print(f"✅ Added voiceover → {output_file}")
    return output_file


# ============================================================================
# ADD MUSIC TO VIDEO
# ============================================================================
def eAddMusic(
    video_file,
    music_file,
    output_file="espresso_with_music.mp4",
    music_volume=0.15,
    fade_in=1.0,
    fade_out=2.0,
    loop=True,
):
    """
    Add background music to a video. Loops and fades automatically.

    Parameters
    ----------
    video_file   : str   — input MP4
    music_file   : str   — background music (mp3/wav/m4a)
    output_file  : str   — output MP4
    music_volume : float — volume (0.15 = 15%, sits under voiceover)
    fade_in      : float — seconds of fade-in
    fade_out     : float — seconds of fade-out at end
    loop         : bool  — loop music if shorter than video
    """
    for f in [video_file, music_file]:
        if not os.path.isfile(f):
            raise FileNotFoundError(f"File not found: {f}")

    vid_dur = eGetDuration(video_file)

    mu_filters = [f"volume={music_volume}"]
    if fade_in > 0:
        mu_filters.append(f"afade=t=in:st=0:d={fade_in}")
    if fade_out > 0:
        fo_start = vid_dur - fade_out
        mu_filters.append(f"afade=t=out:st={fo_start:.2f}:d={fade_out}")

    mu_chain = ",".join(mu_filters)
    loop_args = ['-stream_loop', '-1'] if loop else []

    cmd = [
        'ffmpeg', '-y',
        '-i', video_file,
        *loop_args, '-i', music_file,
        '-filter_complex',
        f'[1:a]{mu_chain},atrim=0:{vid_dur:.2f},asetpts=PTS-STARTPTS[music]',
        '-map', '0:v', '-map', '[music]',
        '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
        '-shortest', output_file
    ]

    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"ffmpeg failed:\n{r.stderr}")

    print(f"✅ Added background music → {output_file}")
    return output_file


# ============================================================================
# ADD VOICEOVER + MUSIC COMBINED
# ============================================================================
def eAddAudio(
    video_file,
    output_file="espresso_final.mp4",
    # --- voiceover ---
    voiceover_file=None,
    vo_volume=1.0,
    vo_delay=0.5,
    vo_fade_in=0.0,
    vo_fade_out=0.3,
    # --- music ---
    music_file=None,
    music_volume=0.12,
    music_fade_in=1.0,
    music_fade_out=2.0,
    music_loop=True,
):
    """
    Add voiceover and/or background music to a video in a single pass.

    Parameters
    ----------
    video_file     : str        — input MP4
    output_file    : str        — output MP4
    voiceover_file : str|None   — voiceover audio (skip if None)
    vo_volume      : float      — voiceover volume (1.0 = full)
    vo_delay       : float      — seconds before voiceover starts
    vo_fade_in     : float      — voiceover fade-in seconds
    vo_fade_out    : float      — voiceover fade-out seconds
    music_file     : str|None   — background music (skip if None)
    music_volume   : float      — music volume (0.12 = sits under voice)
    music_fade_in  : float      — music fade-in seconds
    music_fade_out : float      — music fade-out seconds
    music_loop     : bool       — loop music to fill video length
    """
    if voiceover_file is None and music_file is None:
        raise ValueError("Provide at least one of voiceover_file or music_file.")

    if not os.path.isfile(video_file):
        raise FileNotFoundError(f"Video not found: {video_file}")

    vid_dur = eGetDuration(video_file)

    inputs = ['-i', video_file]
    input_idx = 1
    filter_parts = []
    mix_inputs = []

    # --- Voiceover stream ---
    if voiceover_file is not None:
        if not os.path.isfile(voiceover_file):
            raise FileNotFoundError(f"Voiceover not found: {voiceover_file}")

        inputs += ['-i', voiceover_file]
        vo_idx = input_idx
        input_idx += 1

        vo_filters = [f"volume={vo_volume}"]
        if vo_delay > 0:
            ms = int(vo_delay * 1000)
            vo_filters.append(f"adelay={ms}|{ms}")
        if vo_fade_in > 0:
            vo_filters.append(f"afade=t=in:st={vo_delay:.2f}:d={vo_fade_in}")
        if vo_fade_out > 0:
            vo_dur = eGetDuration(voiceover_file)
            fo_start = vo_delay + vo_dur - vo_fade_out
            vo_filters.append(f"afade=t=out:st={fo_start:.2f}:d={vo_fade_out}")

        vo_chain = ",".join(vo_filters)
        filter_parts.append(f"[{vo_idx}:a]{vo_chain},apad=whole_dur={vid_dur:.2f}[vo]")
        mix_inputs.append("[vo]")

    # --- Music stream ---
    if music_file is not None:
        if not os.path.isfile(music_file):
            raise FileNotFoundError(f"Music not found: {music_file}")

        if music_loop:
            inputs += ['-stream_loop', '-1', '-i', music_file]
        else:
            inputs += ['-i', music_file]
        mu_idx = input_idx
        input_idx += 1

        mu_filters = [f"volume={music_volume}"]
        if music_fade_in > 0:
            mu_filters.append(f"afade=t=in:st=0:d={music_fade_in}")
        if music_fade_out > 0:
            fo_start = vid_dur - music_fade_out
            mu_filters.append(f"afade=t=out:st={fo_start:.2f}:d={music_fade_out}")

        mu_chain = ",".join(mu_filters)
        filter_parts.append(
            f"[{mu_idx}:a]{mu_chain},"
            f"atrim=0:{vid_dur:.2f},asetpts=PTS-STARTPTS[music]"
        )
        mix_inputs.append("[music]")

    # --- Mix ---
    if len(mix_inputs) == 2:
        mix_labels = "".join(mix_inputs)
        filter_parts.append(
            f"{mix_labels}amix=inputs=2:duration=first:dropout_transition=0[aout]"
        )
    else:
        single_tag = mix_inputs[0].strip("[]")
        filter_parts[-1] = filter_parts[-1].rsplit(f"[{single_tag}]", 1)[0] + "[aout]"

    filter_complex = ";".join(filter_parts)

    cmd = [
        'ffmpeg', '-y',
        *inputs,
        '-filter_complex', filter_complex,
        '-map', '0:v', '-map', '[aout]',
        '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
        '-shortest', output_file
    ]

    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"ffmpeg failed:\n{r.stderr}")

    final_dur = eGetDuration(output_file)
    parts = []
    if voiceover_file: parts.append("voiceover")
    if music_file:     parts.append("music")

    print(f"✅ Added {' + '.join(parts)} → {output_file}  ({final_dur:.1f}s)")
    return output_file
