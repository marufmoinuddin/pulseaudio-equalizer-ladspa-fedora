install_subdir('presets', install_dir: pkgdatadir)

install_data(appid + '.desktop',
    install_dir: join_paths(datadir, 'applications'),
)

# Install systemd user service for auto-loading
service_conf = configuration_data()
service_conf.set('bindir', bindir)

configure_file(
    input: 'pulseaudio-equalizer.service.in',
    output: 'pulseaudio-equalizer.service',
    configuration: service_conf,
    install: true,
    install_dir: join_paths(libdir, 'systemd', 'user'),
)

gnome = import('gnome')

# Compiling the resources
gnome.compile_resources(appid, appid + '.gresource.xml',
  gresource_bundle: true,
  source_dir: meson.current_build_dir(),
  install_dir: pkgdatadir,
  install: true
)

