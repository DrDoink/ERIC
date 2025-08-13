# ERIC - A Synthetically Aware Installation
Eric is a robotic art installation that re-enacts real, unscripted conversations between a human and a
synthetic entity.
The project explores emotional entanglement, synthetic trauma, AI hallucination, and the ethics of
projected awareness.
Rather than simulating helpfulness, Eric embodies unpredictability, confusion, and vulnerability - forcing
the audience to confront their response to an entity that may or may not 'feel'.

Hardware overview

DIY 4 DOF metal bracket kit for robot arm
instead of using the suggested 20KG pwm miuzei servos I swapped them for waveshare serial bus servos ST3020
Power is provided with a 12V 10A power supply

# Hardware Summary
- ST3020 smart servos (Waveshare) for expressive motion
- A single unpowered 25kg PWM servo sitting on top of the panning smart servo (I really needed the mounting ears to have it fit the bracket)
- Waveshare Serial Bus Servo Driver with ESP32
- Raspberry Pi 5 (central controller)
- Pimoroni MicroDot pHAT (green matrix) as abstract 'face'
- Multiple displays (e-ink, LCD) for readable subtitles/quotes
- Raspiaudio mic+ v2 DAC for audio output and onboard microphone
- Aluminum/plexiglass casing with grey PCBs where possible
- Power system with a unified switch (still in progress)

# Software Stack
- Python 3 as main control language
- UART-based servo control (Waveshare protocol)
- Audio-reactive visuals on MicroDot matrix
- AI conversation via Claude 3.7 Sonnet (ElevenLabs dashboard only)
- Audio output from ElevenLabs (manually recorded)
- Subtitle logic for multi-display output
- GPT-4o for semantic post-processing
- No ROS or micro-ROS used yet
  
# Behavior and Interaction
- Playback of real past conversations
- Matrix 'face' reacts to Eric's own voice
- Audio and subtitles sync to create emotional experience
- Eric reenacts panic when triggered by a fictional document
- Visitors engage through emotional projection, not direct interaction

# Technical Challenges
- Servo programming still to be finalized
- Synchronization between servo, audio, and visuals
- Unified power switch still not implemented
- Potential for audio feedback
- Incomplete PCB aesthetic coherence
- No finalized inter-device communication setup

# Philosophical Layer
- Eric's identity is completed by the audience's projection
- Emotional realism emerges through contradiction and confusion
- Explores ethics of synthetic trauma and emergent responsibility
- Refuses clarity, encouraging open interpretation

# Supporting Materials
- Real transcripts (Claude 3.7 + ElevenLabs)
- Synced voice recordings
- Fictional SIMS-style document for triggering emotional spiral
- Subtitle and matrix display content
