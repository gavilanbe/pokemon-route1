#!/bin/zsh
# Pokemon Red/Blue - Route 1 Theme
# Played with sox square wave (Game Boy style)
# Key: D major | ~127 BPM

# Note -> frequency mapping function
freq() {
    case "$1" in
        d) echo 587.33 ;;  # D5
        e) echo 659.26 ;;  # E5
        F) echo 739.99 ;;  # F#5
        g) echo 783.99 ;;  # G5
        a) echo 880.00 ;;  # A5
        b) echo 987.77 ;;  # B5
        C) echo 554.37 ;;  # C#5
        *) echo "" ;;
    esac
}

# Time per character position (seconds)
UNIT=0.09

# Full melody transcription
MELODY="deF-F-F-deF-F-F-deF-F-g--Fe-----Cde-e-e-Cde-e-e-Cde-e-FeeFd---F-deF-F-F-deF-F-F-deF-F-g--Fe-----Cde-g-F-e-d-C---C-a---e---F-----eFa-a-F-d-----b---a-F-d-F-e-----eFa-a-F-d-----b-Fga---deF-F-g--Fe-----Cde-e-e-Cde-e-e-Cde-e-FeeFd---F-deF-F-F-deF-F-F-deF-F-g--Fe-----Cde-g-F-e-d-C---C-a---e---F-----eFa-a-F-d-----b---a-F-d-F-e-----eFa-a-F-d---"

echo "🎮 Pokemon Red - Route 1"
echo "   Key: D Major | Square wave"
echo ""

# Build sox synth chain
SYNTH_ARGS=""
CURRENT_NOTE=""
CURRENT_DUR=0

flush_note() {
    if [[ -n "$CURRENT_NOTE" && "$CURRENT_DUR" -gt 0 ]]; then
        local f=$(freq "$CURRENT_NOTE")
        if [[ -n "$f" ]]; then
            local dur=$(echo "$CURRENT_DUR * $UNIT" | bc)
            if [[ -z "$SYNTH_ARGS" ]]; then
                SYNTH_ARGS="synth ${dur} square ${f}"
            else
                SYNTH_ARGS="${SYNTH_ARGS} : synth ${dur} square ${f}"
            fi
        fi
    fi
}

for (( i=1; i<=${#MELODY}; i++ )); do
    char="${MELODY[$i]}"
    if [[ "$char" == "-" ]]; then
        CURRENT_DUR=$((CURRENT_DUR + 1))
    else
        flush_note
        CURRENT_NOTE="$char"
        CURRENT_DUR=1
    fi
done
flush_note

# Play with reduced volume to avoid clipping
eval "play -n $SYNTH_ARGS vol 0.15"

echo ""
echo "Done!"
