from __future__ import annotations

import sys

import gi
gi.check_version('3.30')
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, Gio, GLib, Gdk

from pulseeq.pulse import (
    EqualizerState,
    get_settings,
    initialize_current_output,
    apply_settings,
    get_output_devices,
    switch_output,
)
from pulseeq.presets import load_preset, save_preset, remove_preset
from pulseeq.constants import USER_PRESET_DIR, SYSTEM_PRESET_DIR

TEMPLATE_PATH = '/com/github/pulseaudio-equalizer-ladspa/Equalizer/ui/Equalizer.ui'



class FrequencyLabel(Gtk.Label):
    def __init__(self, frequency: float | None = None, **kwargs):
        super().__init__(visible=True, use_markup=True,
                         justify=Gtk.Justification.CENTER, **kwargs)
        if frequency is not None:
            self.set_frequency(frequency)

    def set_frequency(self, frequency: float | str) -> None:
        if not frequency or frequency == '':
            self.set_label('<small>-\n</small>')
            return
        freq = float(frequency)
        suffix = 'Hz'
        if freq > 999:
            freq /= 1000
            suffix = 'KHz'
        self.set_label(f'<small>{freq:g}\n{suffix}</small>')


class Equalizer(Gtk.ApplicationWindow):
    __gtype_name__ = 'Equalizer'

    grid: Gtk.Grid = Gtk.Template.Child()
    presetsbox: Gtk.ComboBoxText = Gtk.Template.Child()
    outputbox: Gtk.ComboBoxText = Gtk.Template.Child()
    refresh_button: Gtk.Button = Gtk.Template.Child()

    def __init__(self, state: EqualizerState, **kwargs):
        cls = type(self)
        if not getattr(cls, '_template_ready', False):
            Gtk.Template(resource_path=TEMPLATE_PATH)(cls)
            cls._template_ready = True

        self._state = state
        self.apply_event_source: int | None = None
        super().__init__(**kwargs)

        self.presetsbox.connect('changed', self.on_presetsbox)
        self.outputbox.connect('changed', self.on_outputbox)
        self.refresh_button.connect('clicked', self.on_refresh_outputs)

        self._initialized = False
        get_settings(self._state)
        initialize_current_output(self._state)

        self.scales: dict[int, Gtk.Scale] = {}
        self.labels: dict[int, FrequencyLabel] = {}
        self.scalevalues: dict[int, Gtk.Label] = {}

        for x in range(self._state.num_ladspa_controls):
            scale = Gtk.Scale(
                orientation=Gtk.Orientation.VERTICAL,
                draw_value=False, inverted=True, digits=1,
                expand=True, visible=True,
            )
            self.scales[x] = scale
            scale.set_range(float(self._state.ranges[0]), float(self._state.ranges[1]))
            scale.set_increments(1, 0.1)
            scale.set_size_request(35, 200)
            scale.set_value(self._state.ladspa_controls[x])
            scale.connect('value-changed', self._on_scale, x)

            label = FrequencyLabel(frequency=self._state.ladspa_inputs[x])
            self.labels[x] = label

            scalevalue = Gtk.Label(
                visible=True, use_markup=True,
                label=f'<small>{scale.get_value():g}\ndB</small>',
            )
            self.scalevalues[x] = scalevalue

            self.grid.attach(label, x, 0, 1, 1)
            self.grid.attach(scale, x, 1, 1, 2)
            self.grid.attach(scalevalue, x, 3, 1, 1)

        action = Gio.SimpleAction.new('save', None)
        action.set_enabled(False)
        action.connect('activate', self._on_savepreset)
        self.add_action(action)

        action = Gio.SimpleAction.new('remove', None)
        action.set_enabled(False)
        action.connect('activate', self._on_removepreset)
        self.add_action(action)

        self.presetsbox.get_child().set_text(self._state.preset)
        for p in self._state.rawpresets:
            self.presetsbox.append_text(p)

        action = Gio.SimpleAction.new_stateful(
            'eqenabled', None, GLib.Variant('b', self._state.status)
        )
        action.connect('change-state', self._on_eqenabled)
        self.add_action(action)

        self._updating_output = True
        get_output_devices(self._state)
        for profile in self._state.profiles:
            self.outputbox.append_text(profile)

        if self._state.num_profiles > 0:
            selected_index = 0
            if self._state.last_selected_sink and self._state.last_selected_sink != 'default':
                for i, sink_name in enumerate(self._state.profile_sinks):
                    if sink_name == self._state.last_selected_sink:
                        selected_index = i
                        break
                else:
                    import subprocess
                    try:
                        result = subprocess.run(
                            "pactl list sinks short | grep -v ladspa",
                            shell=True, capture_output=True, text=True, timeout=10,
                        )
                        if result.returncode == 0:
                            for line in result.stdout.strip().split('\n'):
                                if 'RUNNING' in line:
                                    parts = line.split('\t')
                                    if len(parts) >= 2:
                                        running_sink = parts[1]
                                        for i, sink_name in enumerate(self._state.profile_sinks):
                                            if sink_name == running_sink:
                                                selected_index = i
                                                self._state.last_selected_sink = running_sink
                                                break
                                        break
                    except Exception as e:
                        print(f"Warning: Error selecting running device: {e}")

            self.outputbox.set_active(selected_index)

        self._initialized = True
        self._updating_output = False
        self._sync_active_sink()
        self.show()

    def _on_scale(self, widget: Gtk.Scale, index: int) -> None:
        self._state.ladspa_controls[index] = round(widget.get_value(), 1)
        if self._state.clearpreset == 1:
            self._state.preset = ''
            self.presetsbox.get_child().set_text('')

        self.scalevalues[index].set_markup(
            f'<small>{self._state.ladspa_controls[index]:g}\ndB</small>'
        )

        if self.apply_event_source is not None:
            GLib.source_remove(self.apply_event_source)

        self.apply_event_source = GLib.timeout_add(500, self._on_apply_event)

    def _on_apply_event(self) -> bool:
        apply_settings(self._state)
        self.apply_event_source = None
        return False

    def on_presetsbox(self, widget: Gtk.ComboBoxText) -> None:
        preset = self.presetsbox.get_child().get_text()
        self._state.preset = preset

        self.lookup_action('remove').set_enabled(False)

        self._state.presetmatch = ''
        for p in self._state.rawpresets:
            if p == preset:
                self._state.presetmatch = '1'

        if self._state.presetmatch == '1' and load_preset(preset, self._state):
            path = USER_PRESET_DIR / f'{preset}.preset'
            if path.is_file():
                self.lookup_action('remove').set_enabled(True)

            self._state.clearpreset = ''
            for i in range(self._state.num_ladspa_controls):
                self.scales[i].set_value(self._state.ladspa_controls[i])
                self.labels[i].set_frequency(self._state.ladspa_inputs[i])
                self.scalevalues[i].set_markup(
                    f'<small>{self._state.ladspa_controls[i]:g}\ndB</small>'
                )

            self._state.preset = preset
            self._state.clearpreset = 1
            self.presetsbox.get_child().set_text(preset)
            apply_settings(self._state)
            self.lookup_action('save').set_enabled(False)
        else:
            self.lookup_action('save').set_enabled(preset != '')

    def on_outputbox(self, widget: Gtk.ComboBoxText) -> None:
        if not self._initialized or self._updating_output:
            return
        selected_index = widget.get_active()
        if selected_index == -1 or selected_index >= self._state.num_profiles:
            return

        selected_sink = self._state.profile_sinks[selected_index] \
            if selected_index < len(self._state.profile_sinks) else 'default'
        if not selected_sink or selected_sink == 'default':
            return

        # Only switch if the sink actually differs from what the module is using
        if selected_sink == self._state.current_active_sink:
            print(f'Sink unchanged ({selected_sink}) \u2014 no switch needed')
            return

        self._state.last_selected_sink = selected_sink
        print(f'Output device changed to: {self._state.profiles[selected_index]} [sink: {selected_sink}]')

        if switch_output(self._state, selected_sink):
            get_settings(self._state)
            self.lookup_action('eqenabled').set_state(
                GLib.Variant('b', self._state.status)
            )
            for i in range(self._state.num_ladspa_controls):
                self.scales[i].set_value(self._state.ladspa_controls[i])
                self.scalevalues[i].set_markup(
                    f'<small>{self._state.ladspa_controls[i]:g}\ndB</small>'
                )

    def on_refresh_outputs(self, widget: Gtk.Widget) -> None:
        current_index = self.outputbox.get_active()
        saved_sink = None
        if 0 <= current_index < len(self._state.profile_sinks):
            saved_sink = self._state.profile_sinks[current_index]
            self._state.last_selected_sink = saved_sink

        self._updating_output = True
        self.outputbox.handler_block_by_func(self.on_outputbox)

        get_output_devices(self._state)
        self.outputbox.remove_all()
        for profile in self._state.profiles:
            self.outputbox.append_text(profile)

        selected_index = 0
        if self._state.num_profiles > 0:
            # Restore previously selected device
            if saved_sink:
                for i, sink_name in enumerate(self._state.profile_sinks):
                    if sink_name == saved_sink:
                        selected_index = i
                        break
                else:
                    print(f"Refresh: device '{saved_sink}' no longer available")

            # Fallback to current_active_sink
            if selected_index == 0 and self._state.current_active_sink:
                for i, sink_name in enumerate(self._state.profile_sinks):
                    if sink_name == self._state.current_active_sink:
                        selected_index = i
                        break

            # Last resort: find RUNNING device
            if selected_index == 0:
                import subprocess
                try:
                    result = subprocess.run(
                        "pactl list sinks short | grep -v ladspa",
                        shell=True, capture_output=True, text=True, timeout=10,
                    )
                    if result.returncode == 0:
                        for line in result.stdout.strip().split('\n'):
                            if 'RUNNING' in line:
                                parts = line.split('\t')
                                if len(parts) >= 2:
                                    running_sink = parts[1]
                                    for i, sink_name in enumerate(self._state.profile_sinks):
                                        if sink_name == running_sink:
                                            selected_index = i
                                            self._state.last_selected_sink = running_sink
                                            break
                                    break
                except Exception as e:
                    print(f"Warning: Error finding running device during refresh: {e}")

            self.outputbox.set_active(selected_index)

        self.outputbox.handler_unblock_by_func(self.on_outputbox)
        self._updating_output = False

    def _sync_active_sink(self) -> None:
        """Sync state.current_active_sink with what the LADSPA module is using."""
        import subprocess, re
        try:
            result = subprocess.run(
                "pactl list modules | grep -A 20 'module-ladspa-sink' | grep 'sink_master=' | head -1",
                shell=True, capture_output=True, text=True, timeout=10,
            )
            if result.returncode == 0 and result.stdout.strip():
                m = re.search(r'sink_master=(\S+)', result.stdout)
                if m:
                    self._state.current_active_sink = m.group(1)
                    return
        except Exception:
            pass
        self._state.current_active_sink = None

    def on_resetsettings(self, action: Gio.SimpleAction | None = None,
                         param: object = None) -> None:
        import subprocess
        subprocess.run('pulseaudio-equalizer interface.resetsettings',
                       shell=True, timeout=10)
        get_settings(self._state)

        self.lookup_action('eqenabled').set_state(
            GLib.Variant('b', self._state.status)
        )
        Gio.Application.get_default().lookup_action('keepsettings').set_state(
            GLib.Variant('b', self._state.persistence)
        )
        self.presetsbox.get_child().set_text(self._state.preset)
        for i in range(self._state.num_ladspa_controls):
            self.scales[i].set_value(self._state.ladspa_controls[i])
            self.labels[i].set_frequency(self._state.ladspa_inputs[i])
            self.scalevalues[i].set_markup(
                f'<small>{self._state.ladspa_controls[i]:g}\ndB</small>'
            )

    def _on_savepreset(self, action: Gio.SimpleAction, param: object) -> None:
        preset = self.presetsbox.get_child().get_text()
        if not preset or self._state.presetmatch == '1':
            print('Invalid preset name')
            return

        save_preset(preset, self._state)

        self.presetsbox.remove_all()
        apply_settings(self._state)
        get_settings(self._state)

        for p in self._state.rawpresets:
            self.presetsbox.append_text(p)

        action.set_enabled(False)
        self.lookup_action('remove').set_enabled(True)

    def _on_eqenabled(self, action: Gio.SimpleAction, state: GLib.Variant) -> None:
        self._state.status = int(state.get_boolean())
        apply_settings(self._state)
        action.set_state(state)

    def _on_removepreset(self, action: Gio.SimpleAction, param: object) -> None:
        remove_preset(self._state.preset)

        self.presetsbox.get_child().set_text('')
        self.presetsbox.remove_all()
        get_settings(self._state)

        for p in self._state.rawpresets:
            self.presetsbox.append_text(p)

        self._state.preset = ''
        apply_settings(self._state)
        action.set_enabled(False)


class Application(Gtk.Application):
    APP_ID = 'com.github.pulseaudio-equalizer-ladspa.Equalizer'

    def __init__(self, **kwargs):
        GLib.set_prgname(self.APP_ID)
        Gdk.set_program_class(self.APP_ID)
        super().__init__(
            application_id=self.APP_ID,
            resource_base_path='/com/github/pulseaudio-equalizer-ladspa/Equalizer',
            **kwargs,
        )
        self._state = EqualizerState()
        self._window: Equalizer | None = None

    def do_startup(self) -> None:
        Gtk.Application.do_startup(self)
        get_settings(self._state)

        self._window = Equalizer(state=self._state, application=self)

        action = Gio.SimpleAction.new('resetsettings', None)
        action.connect('activate', self._window.on_resetsettings)
        self.add_action(action)

        action = Gio.SimpleAction.new_stateful(
            'keepsettings', None, GLib.Variant('b', self._state.persistence)
        )
        action.connect('change-state', self._on_keepsettings)
        self.add_action(action)

        action = Gio.SimpleAction.new('quit', None)
        action.connect('activate', self._on_quit)
        self.add_action(action)

    def do_activate(self) -> None:
        if not self._window:
            self._window = Equalizer(state=self._state, application=self)
        self._window.present()

    def _on_keepsettings(self, action: Gio.SimpleAction, state: GLib.Variant) -> None:
        self._state.persistence = int(state.get_boolean())
        apply_settings(self._state)
        action.set_state(state)

    @staticmethod
    def _on_quit(action: Gio.SimpleAction, param: object) -> None:
        Gio.Application.get_default().quit()
