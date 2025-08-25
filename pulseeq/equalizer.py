#!/usr/bin/env python
# -*- coding: utf-8 -*-

# PulseAudio Equalizer (PyGTK Interface)
#
# Intended for use in conjunction with pulseaudio-equalizer script
#
# Author: Conn O'Griofa <connogriofa AT gmail DOT com>
# Version: (see '/usr/pulseaudio-equalizer' script)
#

import gi
gi.check_version('3.30')
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio, GLib

import os, sys
import subprocess
import re

from pulseeq.constants import *

# Global variables for output management
global output_selected
global num_profiles
global profiles
global profile_sinks  # Store actual sink names corresponding to profiles
output_selected = 0
num_profiles = 0
profiles = []
profile_sinks = []  # New list to store sink names
# Remember the last selected output sink so we can restore it after changes
last_selected_sink = None

def GetSettings():
    global rawdata
    global rawpresets
    global ladspa_filename
    global ladspa_name
    global ladspa_label
    global preamp
    global num_ladspa_controls
    global ladspa_controls
    global ladspa_inputs
    global status
    global persistence
    global preset
    global ranges
    global presetmatch
    global clearpreset

    print('Getting settings...')

    os.system('pulseaudio-equalizer interface.getsettings')

    f = open(CONFIG_FILE, 'r')
    rawdata = f.read().split('\n')
    f.close()

    rawpresets = {}
    f = open(PRESETS_FILE, 'r')
    rawpresets = f.read().split('\n')
    f.close()
    del rawpresets[len(rawpresets) - 1]

    ladspa_filename = str(rawdata[0])
    ladspa_name = str(rawdata[1])
    ladspa_label = str(rawdata[2])
    preamp = rawdata[3]
    preset = str(rawdata[4])
    status = int(rawdata[5])
    persistence = int(rawdata[6])
    ranges = rawdata[7:9]
    num_ladspa_controls = int(rawdata[9])
    ladspa_controls = rawdata[10:10 + num_ladspa_controls]
    ladspa_inputs = rawdata[10 + num_ladspa_controls:10 + num_ladspa_controls + num_ladspa_controls]

    clearpreset = 1
    presetmatch = ''
    for i in range(len(rawpresets)):
        if rawpresets[i] == preset:
            print('Match!')
            presetmatch = 1


def ApplySettings():
    print('Applying settings...')
    f = open(CONFIG_FILE, 'w')
    del rawdata[:]
    rawdata.append(str(ladspa_filename))
    rawdata.append(str(ladspa_name))
    rawdata.append(str(ladspa_label))
    rawdata.append(str(preamp))
    rawdata.append(str(preset))
    rawdata.append(str(status))
    rawdata.append(str(persistence))
    for i in range(2):
        rawdata.append(str(ranges[i]))
    rawdata.append(str(num_ladspa_controls))
    for i in range(num_ladspa_controls):
        rawdata.append(str(ladspa_controls[i]))
    for i in range(num_ladspa_controls):
        rawdata.append(str(ladspa_inputs[i]))

    for i in rawdata:
        f.write(str(i) + '\n')
    f.close()

    os.system('pulseaudio-equalizer interface.applysettings')

    # Re-apply last selected output sink to prevent auto-switching
    try:
        global last_selected_sink
        if last_selected_sink and last_selected_sink != "default":
            # Ensure sink still exists
            chk = subprocess.run("pactl list sinks short | awk '{print $2}'", shell=True, capture_output=True, text=True)
            if chk.returncode == 0 and last_selected_sink in chk.stdout.split():
                subprocess.run(f"pulseaudio-equalizer update-output {last_selected_sink}", shell=True)
    except Exception as e:
        print(f"Warning: could not re-apply output sink: {e}")

def GetOutputDevices():
    """Get available output devices using pactl"""
    global profiles
    global profile_sinks
    global num_profiles
    
    profiles = []
    profile_sinks = []
    
    try:
        # Get sinks using pactl
        result = subprocess.run("pactl list sinks short", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        sink_name = parts[1]
                        # Skip LADSPA sinks to avoid recursion
                        if 'ladspa' not in sink_name:
                            # Get friendly name
                            desc_result = subprocess.run(
                                f"pactl list sinks | grep -A 20 'Name: {sink_name}' | grep 'Description:' | head -1",
                                shell=True, capture_output=True, text=True
                            )
                            if desc_result.returncode == 0:
                                import re
                                desc_match = re.search(r'Description: (.+)', desc_result.stdout)
                                friendly_name = desc_match.group(1) if desc_match else sink_name
                            else:
                                friendly_name = sink_name
                            
                            profiles.append(friendly_name)
                            profile_sinks.append(sink_name)  # Store the actual sink name
    
    except Exception as e:
        print(f"Error getting output devices: {e}")
        profiles = ["Default Output"]
        profile_sinks = ["default"]
    
    if not profiles:
        profiles = ["Default Output"]
        profile_sinks = ["default"]
    
    num_profiles = len(profiles)
    print(f"Found {num_profiles} output devices: {profiles}")
    print(f"Corresponding sink names: {profile_sinks}")

def ApplySettings():
    print('Applying settings...')
    f = open(CONFIG_FILE, 'w')
    del rawdata[:]
    rawdata.append(str(ladspa_filename))
    rawdata.append(str(ladspa_name))
    rawdata.append(str(ladspa_label))
    rawdata.append(str(preamp))
    rawdata.append(str(preset))
    rawdata.append(str(status))
    rawdata.append(str(persistence))
    for i in range(2):
        rawdata.append(str(ranges[i]))
    rawdata.append(str(num_ladspa_controls))
    for i in range(num_ladspa_controls):
        rawdata.append(str(ladspa_controls[i]))
    for i in range(num_ladspa_controls):
        rawdata.append(str(ladspa_inputs[i]))

    for i in rawdata:
        f.write(str(i) + '\n')
    f.close()

    os.system('pulseaudio-equalizer interface.applysettings')

    # Re-apply last selected output sink to prevent auto-switching
    try:
        global last_selected_sink
        if last_selected_sink and last_selected_sink != "default":
            chk = subprocess.run("pactl list sinks short | awk '{print $2}'", shell=True, capture_output=True, text=True)
            if chk.returncode == 0 and last_selected_sink in chk.stdout.split():
                subprocess.run(f"pulseaudio-equalizer update-output {last_selected_sink}", shell=True)
    except Exception as e:
        print(f"Warning: could not re-apply output sink: {e}")

class FrequencyLabel(Gtk.Label):
    def __init__(self, frequency=None):
        super(FrequencyLabel, self).__init__(visible=True, use_markup=True,
                                             justify=Gtk.Justification.CENTER)
        if frequency is not None:
            self.set_frequency(frequency)

    def set_frequency(self, frequency):
        frequency = float(frequency)
        suffix = 'Hz'

        if frequency > 999:
            frequency = frequency / 1000
            suffix = 'KHz'

        self.set_label('<small>{0:g}\n{1}</small>'.format(frequency, suffix))

@Gtk.Template(resource_path='/com/github/pulseaudio-equalizer-ladspa/Equalizer/ui/Equalizer.ui')
class Equalizer(Gtk.ApplicationWindow):
    __gtype_name__= "Equalizer"

    grid = Gtk.Template.Child()
    presetsbox = Gtk.Template.Child()
    outputbox = Gtk.Template.Child()

    def on_scale(self, widget, y):
        global ladspa_controls
        global preset
        global clearpreset
        newvalue = float(round(widget.get_value(), 1))
        ladspa_controls[y] = newvalue
        if clearpreset == 1:
            preset = ''
            self.presetsbox.get_child().set_text(preset)

        self.scalevalues[y].set_markup('<small>' + str(float(ladspa_controls[y])) + '\ndB</small>')

        if self.apply_event_source is not None:
            GLib.source_remove (self.apply_event_source);

        self.apply_event_source = GLib.timeout_add (500, self.on_apply_event)

    def on_apply_event(self):
        ApplySettings()
        self.apply_event_source = None
        return False

    @Gtk.Template.Callback()
    def on_presetsbox(self, widget):
        global preset
        global presetmatch
        global clearpreset
        global ladspa_filename
        global ladspa_name
        global ladspa_label
        global num_ladspa_controls
        global ladspa_controls
        global ladspa_inputs
        preset = self.presetsbox.get_child().get_text()

        self.lookup_action('remove').set_enabled(False)

        presetmatch = ''
        for i in range(len(rawpresets)):
            if rawpresets[i] == preset:
                print('Match!')
                presetmatch = 1

        if presetmatch == 1:
            if os.path.isfile(os.path.join(USER_PRESET_DIR, preset + '.preset')):
                f = open(os.path.join(USER_PRESET_DIR, preset + '.preset'), 'r')
                rawdata = f.read().split('\n')
                f.close
                self.lookup_action('remove').set_enabled(True)
            elif os.path.isfile(os.path.join(SYSTEM_PRESET_DIR, preset + '.preset')):
                f = open(os.path.join(SYSTEM_PRESET_DIR, preset + '.preset'), 'r')
                rawdata = f.read().split('\n')
                f.close
            else:
                print("Can't find %s preset" % preset)

            ladspa_filename = str(rawdata[0])
            ladspa_name = str(rawdata[1])
            ladspa_label = str(rawdata[2])
            preset = str(rawdata[4])
            num_ladspa_controls = int(rawdata[5])
            ladspa_controls = rawdata[6:6 + num_ladspa_controls]
            ladspa_inputs = rawdata[6 + num_ladspa_controls:6 + num_ladspa_controls + num_ladspa_controls]

            clearpreset = ''
            for i in range(num_ladspa_controls):
                self.scales[i].set_value(float(ladspa_controls[i]))
                self.labels[i].set_frequency(ladspa_inputs[i])
                self.scalevalues[i].set_markup('<small>' + str(float(ladspa_controls[i])) + '\ndB</small>')

            # Set preset again due to interference from scale modifications
            preset = str(rawdata[4])
            clearpreset = 1
            self.presetsbox.get_child().set_text(preset)
            # Apply settings and then ensure the selected output is retained
            ApplySettings()

            self.lookup_action('save').set_enabled(False)
        else:
            self.lookup_action('save').set_enabled(preset != '')

    @Gtk.Template.Callback()
    def on_outputbox(self, widget):
        global output_selected
        global num_profiles
        global profiles
        global profile_sinks
        global last_selected_sink

        output_selected = widget.get_active()

        if output_selected != -1 and output_selected < num_profiles:
            selected_profile = profiles[output_selected]
            selected_sink = profile_sinks[output_selected] if output_selected < len(profile_sinks) else "default"

            print(f"Output device changed to: {selected_profile} [sink: {selected_sink}]")

            # Store choice and switch the equalizer to the new output device
            last_selected_sink = selected_sink
            if selected_sink != "default":
                try:
                    result = subprocess.run(
                        f"pulseaudio-equalizer update-output {selected_sink}",
                        shell=True, capture_output=True, text=True
                    )
                    if result.returncode == 0:
                        print(f"Successfully switched equalizer to: {selected_profile}")
                        # Refresh settings to ensure GUI is up to date
                        GetSettings()
                        # Update the GUI elements
                        self.lookup_action('eqenabled').set_state(GLib.Variant('b', status))
                        for i in range(num_ladspa_controls):
                            self.scales[i].set_value(float(ladspa_controls[i]))
                            self.scalevalues[i].set_markup('<small>' + str(float(ladspa_controls[i])) + '\ndB</small>')
                    else:
                        print(f"Error switching output: {result.stderr}")
                except Exception as e:
                    print(f"Error switching equalizer output: {e}")
            else:
                print("Using default output")

    @Gtk.Template.Callback()
    def on_refresh_outputs(self, widget):
        """Refresh the output devices list"""
        GetOutputDevices()
        
        # Clear and repopulate the output combo box
        self.outputbox.remove_all()
        for profile in profiles:
            self.outputbox.append_text(profile)
        
        # Prefer previously selected sink if still available
        global last_selected_sink
        active_set = False
        if last_selected_sink and last_selected_sink in profile_sinks:
            idx = profile_sinks.index(last_selected_sink)
            if idx < num_profiles:
                self.outputbox.set_active(idx)
                active_set = True
        if not active_set and num_profiles > 0:
            self.outputbox.set_active(0)
        
        print(f"Refreshed output devices: {num_profiles} devices found")

    def on_resetsettings(self, action=None, param=None):
        print('Resetting to defaults...')
        os.system('pulseaudio-equalizer interface.resetsettings')
        GetSettings()

        self.lookup_action('eqenabled').set_state(GLib.Variant('b', status))
        Gio.Application.get_default().lookup_action('keepsettings').set_state(GLib.Variant('b', persistence))
        self.presetsbox.get_child().set_text(preset)
        for i in range(num_ladspa_controls):
            self.scales[i].set_value(float(ladspa_controls[i]))
            self.labels[i].set_frequency(ladspa_inputs[i])
            self.scalevalues[i].set_markup('<small>' + str(float(ladspa_controls[i])) + '\ndB</small>')

    def on_savepreset(self, action, param):
        global preset
        global presetmatch
        preset = self.presetsbox.get_child().get_text()
        if preset == '' or presetmatch == 1:
            print('Invalid preset name')
        else:
            f = open(os.path.join(USER_PRESET_DIR, preset + '.preset'), 'w')

            del rawdata[:]
            rawdata.append(str(ladspa_filename))
            rawdata.append(str(ladspa_name))
            rawdata.append(str(ladspa_label))
            rawdata.append('')
            rawdata.append(str(preset))
            rawdata.append(str(num_ladspa_controls))
            for i in range(num_ladspa_controls):
                rawdata.append(str(ladspa_controls[i]))
            for i in range(num_ladspa_controls):
                rawdata.append(str(ladspa_inputs[i]))

            for i in rawdata:
                f.write(str(i) + '\n')
            f.close()

            # Clear preset list from ComboBox
            self.presetsbox.remove_all()

            # Apply settings (which will save new preset as default)
            ApplySettings()

            # Refresh (and therefore, sort) preset list
            GetSettings()

            # Repopulate preset list into ComboBox
            for i in range(len(rawpresets)):
                self.presetsbox.append_text(rawpresets[i])

            action.set_enabled(False)
            self.lookup_action('remove').set_enabled(True)

    def on_eqenabled(self, action, state):
        global status
        status = int(state.get_boolean())
        ApplySettings()
        action.set_state(state)

    def on_removepreset(self, action, param):
        global preset
        os.remove(os.path.join(USER_PRESET_DIR, preset + '.preset'))

        self.presetsbox.get_child().set_text('')

        # Clear preset list from ComboBox
        self.presetsbox.remove_all()

        # Refresh (and therefore, sort) preset list
        GetSettings()

        # Repopulate preset list into ComboBox
        for i in range(len(rawpresets)):
            self.presetsbox.append_text(rawpresets[i])

        preset = ''
        # Apply settings
        ApplySettings()

        action.set_enabled(False)

    def __init__(self, *args, **kwargs):
        super(Equalizer, self).__init__(*args, **kwargs)
        GetSettings()

        self.apply_event_source = None

        # Equalizer bands
        global scale
        self.scales = {}
        self.labels = {}
        self.scalevalues = {}
        for x in range(num_ladspa_controls):
            scale = Gtk.Scale(orientation=Gtk.Orientation.VERTICAL,
                              draw_value=False, inverted=True, digits=1,
                              expand=True, visible=True)
            self.scales[x] = scale
            scale.set_range(float(ranges[0]), float(ranges[1]))
            scale.set_increments(1, 0.1)
            scale.set_size_request(35, 200)
            scale.set_value(float(ladspa_controls[x]))
            scale.connect('value-changed', self.on_scale, x)
            label = FrequencyLabel(frequency = ladspa_inputs[x])
            self.labels[x] = label
            scalevalue = Gtk.Label(visible=True, use_markup=True,
                label='<small>' + str(scale.get_value())  + '\ndB</small>')
            self.scalevalues[x] = scalevalue
            self.grid.attach(label, x, 0, 1, 1)
            self.grid.attach(scale, x, 1, 1, 2)
            self.grid.attach(scalevalue, x, 3, 1, 1)

        action = Gio.SimpleAction.new('save', None)
        action.set_enabled(False)
        action.connect('activate', self.on_savepreset)
        self.add_action(action)

        action = Gio.SimpleAction.new('remove', None)
        action.set_enabled(False)
        action.connect('activate', self.on_removepreset)
        self.add_action(action)

        self.presetsbox.get_child().set_text(preset)
        for i in range(len(rawpresets)):
            self.presetsbox.append_text(rawpresets[i])

        action = Gio.SimpleAction.new_stateful('eqenabled', None,
                                               GLib.Variant('b', status))
        action.connect('change-state', self.on_eqenabled)
        self.add_action(action)

        # Initialize output devices
        GetOutputDevices()
        for profile in profiles:
            self.outputbox.append_text(profile)
        # Prefer last selected sink on startup if available
        global last_selected_sink
        if last_selected_sink and last_selected_sink in profile_sinks:
            self.outputbox.set_active(profile_sinks.index(last_selected_sink))
        elif num_profiles > 0:
            self.outputbox.set_active(0)

        self.show()


class Application(Gtk.Application):

    def __init__(self, *args, **kwargs):
        super(Application, self).__init__(*args,
            application_id='com.github.pulseaudio-equalizer-ladspa.Equalizer',
            resource_base_path='/com/github/pulseaudio-equalizer-ladspa/Equalizer',
            **kwargs)

        self.window = None

    def do_startup(self):
        Gtk.Application.do_startup(self)
        GetSettings()

        self.window = Equalizer(application=self)

        action = Gio.SimpleAction.new('resetsettings', None)
        action.connect('activate', self.window.on_resetsettings)
        self.add_action(action)

        global persistence
        action = Gio.SimpleAction.new_stateful('keepsettings', None,
                                               GLib.Variant('b', persistence))
        action.connect('change-state', self.on_keepsettings)
        self.add_action(action)

        action = Gio.SimpleAction.new('quit', None)
        action.connect('activate', self.on_quit)
        self.add_action(action)

    def do_activate(self):
        if not self.window:
            self.window = Equalizer(application=self)

        self.window.present()

    def on_keepsettings(self, action, state):
        global persistence
        persistence = int(state.get_boolean())
        ApplySettings()
        action.set_state(state)

    def on_quit(self, action, param):
        Gio.Application.get_default().quit()
