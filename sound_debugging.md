# HDMI Audio Debugging — Raspberry Pi 5

## Symptoms

- No audio from the INSIGNIA TV's integrated speakers despite the retro-console
  playing sounds via FluidSynth
- WAV playback via `pw-play` of short files (e.g. `/usr/share/sounds/alsa/Front_Left.wav`)
  worked fine
- Longer audio produced "two tones then clicking" before falling silent
- The retro-console theme song was inaudible

## Environment

- **Hardware:** Raspberry Pi 5 Model B Rev 1.0
- **Display/speakers:** INSIGNIA TV connected via HDMI-A-2 (kernel: `vc4-hdmi-1`, ALSA card 1)
- **Audio stack:** PipeWire 1.4.2 + WirePlumber 0.5.8
- **Notable:** `pipewire-alsa` is not installed; FluidSynth uses its native PipeWire driver

## Investigation

### Step 1 — Verify the software chain

`wpctl status` while FluidSynth was running confirmed the full chain was active:

```
Streams:
    81. FluidSynth
         79. output_FR  >  MAI PCM i2s-hifi-0:playback_FR  [active]
         80. output_FL  >  MAI PCM i2s-hifi-0:playback_FL  [active]
```

FluidSynth was connecting to PipeWire and routing to the correct HDMI sink. The
problem was not a missing connection or wrong output device.

### Step 2 — Identify the XRUN

Inspecting the ALSA PCM status during playback revealed:

```
state: XRUN
avail: 32784
avail_max: 32784
buffer_size: 32768
```

`avail > buffer_size` means the entire ring buffer was empty — the HDMI audio
driver had consumed samples faster than PipeWire was supplying them. This is an
underrun (XRUN), which manifests as clicks and silence.

### Step 3 — Identify contributing factors

Three issues compounded to cause the XRUNs:

1. **HDMI clock drift.** On the Pi 5, the `vc4-hdmi` driver's audio clock runs
   slightly faster than PipeWire's nominal 48000 Hz. Over time the driver drains
   the ring buffer faster than PipeWire refills it, eventually hitting XRUN.

2. **PipeWire quantum / ALSA period mismatch.** PipeWire's default processing
   quantum was 1024 frames, but the HDMI ALSA device's period size was also 1024.
   With no headroom between them, any scheduling jitter caused the driver to read
   ahead of what PipeWire had written.

3. **Sample rate mismatch.** FluidSynth defaults to 44100 Hz; PipeWire only
   allows 48000 Hz (`clock.allowed-rates = [ 48000 ]`). PipeWire resampled in
   real time, adding CPU load and timing variability.

## Fixes

### 1. WirePlumber HDMI node config

`~/.config/wireplumber/wireplumber.conf.d/51-hdmi-fix.conf`

```
monitor.alsa.rules = [
  {
    matches = [
      { node.name = "~alsa_output.*hdmi*" }
    ]
    actions = {
      update-props = {
        api.alsa.disable-batch = true
        api.alsa.headroom      = 16384
        api.alsa.period-size   = 2048
      }
    }
  }
]
```

- `api.alsa.disable-batch = true` — disables ALSA batch mode, which can cause
  the driver to consume samples in large unpredictable chunks.
- `api.alsa.headroom = 16384` — keeps 16384 frames (~341 ms at 48 kHz) of data
  ahead of the hardware pointer, absorbing clock drift.
- `api.alsa.period-size = 2048` — doubles the period size to give PipeWire more
  time between DMA interrupts.

### 2. PipeWire quantum config

`~/.config/pipewire/pipewire.conf.d/51-hdmi-quantum.conf`

```
context.properties = {
    default.clock.quantum     = 2048
    default.clock.max-quantum = 2048
    default.clock.force-quantum = 2048
}
```

Aligns PipeWire's processing quantum with the ALSA period size (both 2048),
so each PipeWire cycle produces exactly one ALSA period of audio with no
partial writes.

### 3. FluidSynth sample rate

`src/retro_console/sound_manager.py` — added `-r 48000` to the FluidSynth
command:

```python
cmd = ["fluidsynth", "-ni", "-r", "48000"]
```

Outputs audio at PipeWire's native rate, eliminating the real-time resampling
step and its associated CPU and timing overhead.

## Verification

After applying all three fixes:

- `cat /proc/asound/card1/pcm0p/sub0/status` shows `state: RUNNING` (not `XRUN`)
  during playback
- The retro-console theme song and all sound effects play cleanly
- Settings survive reboots (all configs are file-based)
