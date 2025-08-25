#!/bin/bash

# PipeWire-Compatible PulseAudio Equalizer Wrapper
# This script provides compatibility between the original pulseaudio-equalizer
# and PipeWire's PulseAudio compatibility layer

# Check if we're running with PipeWire
if systemctl --user is-active --quiet pipewire-pulse; then
    PIPEWIRE_MODE=1
    echo "Detected PipeWire with PulseAudio compatibility"
else
    PIPEWIRE_MODE=0
fi

# For PipeWire, use our working script-based approach
if [ "$PIPEWIRE_MODE" = "1" ]; then
    SCRIPT_DIR="/home/maruf/Documents/Pulseaudio-Pipewire-Mute-Issue"
    
    case "$1" in
        "enable")
            echo "Enabling LADSPA equalizer with PipeWire..."
            if [ -x "$SCRIPT_DIR/pipewire-ladspa-equalizer.sh" ]; then
                "$SCRIPT_DIR/pipewire-ladspa-equalizer.sh" load
            else
                echo "PipeWire equalizer script not found at $SCRIPT_DIR"
                exit 1
            fi
            ;;
        "disable")
            echo "Disabling LADSPA equalizer..."
            if [ -x "$SCRIPT_DIR/pipewire-ladspa-equalizer.sh" ]; then
                "$SCRIPT_DIR/pipewire-ladspa-equalizer.sh" unload
            else
                echo "PipeWire equalizer script not found at $SCRIPT_DIR"
                exit 1
            fi
            ;;
        "toggle")
            echo "Toggling LADSPA equalizer..."
            if pactl list sinks short | grep -q "ladspa_output"; then
                "$0" disable
            else
                "$0" enable
            fi
            ;;
        "status")
            echo "PipeWire LADSPA Equalizer Status:"
            if [ -x "$SCRIPT_DIR/pipewire-ladspa-equalizer.sh" ]; then
                "$SCRIPT_DIR/pipewire-ladspa-equalizer.sh" status
            else
                echo "Current sinks:"
                pactl list sinks short
            fi
            ;;
        "debug")
            echo "PipeWire LADSPA Equalizer Debug Info:"
            echo "PipeWire services:"
            systemctl --user status pipewire pipewire-pulse wireplumber --no-pager
            echo ""
            echo "Available sinks:"
            pactl list sinks short
            echo ""
            echo "LADSPA modules:"
            pactl list modules short | grep ladspa || echo "No LADSPA modules loaded"
            ;;
        "interface.getsettings"|"interface.applysettings"|"interface.resetsettings")
            echo "GUI interface commands not fully supported with PipeWire."
            echo "Use the script-based approach:"
            echo "  $SCRIPT_DIR/pipewire-ladspa-equalizer.sh load"
            echo "  $SCRIPT_DIR/eq-control.sh bass-boost"
            exit 1
            ;;
        *)
            echo "PipeWire-Compatible PulseAudio Equalizer"
            echo ""
            echo "Usage: $0 {enable|disable|toggle|status|debug}"
            echo ""
            echo "  enable     - Load LADSPA equalizer"
            echo "  disable    - Unload LADSPA equalizer"
            echo "  toggle     - Toggle equalizer on/off"
            echo "  status     - Show current status"
            echo "  debug      - Show debug information"
            echo ""
            echo "For advanced control, use:"
            echo "  $SCRIPT_DIR/pipewire-ladspa-equalizer.sh"
            echo "  $SCRIPT_DIR/eq-control.sh"
            echo ""
            ;;
    esac
    exit 0
fi

# If not PipeWire, show original error message for compatibility
echo "No PulseAudio daemon running, or not running as session daemon."
echo "No PulseAudio daemon running, or not running as session daemon."
echo "No PulseAudio daemon running, or not running as session daemon."
echo "No PulseAudio daemon running, or not running as session daemon."
echo "PulseAudio Equalizer/LADSPA Processor 4.0 (29.01.2017)"
echo "Usage: pulseaudio-equalizer [option]"
echo "WARNING: This is for internal use by the pulseaudio-equalizer-gtk interface."
echo "         Use for debugging/troubleshooting purposes only."
echo ""
echo "Options (current session):"
echo "  enable                 enable the equalizer"
echo "  disable                disable the equalizer"
echo "  toggle                 enable/disable the equalizer"
echo ""
echo "Options (persistent):"
echo "  enable-config          enable the equalizer configuration"
echo "  disable-config         disable the equalizer configuration"
echo ""
echo "Options (all):"
echo "  debug                  run equalizer diagnostics"
echo "  log                    show current equalizer log"
echo "  status                 show current equalizer status"
echo ""
echo "NOTE: PipeWire detected. For working equalizer, use the PipeWire-compatible scripts:"
echo "  /home/maruf/Documents/Pulseaudio-Pipewire-Mute-Issue/pipewire-ladspa-equalizer.sh"
