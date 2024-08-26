contributors = run_command(
  'cat', files('contributors'), check: true,
).stdout().strip()

translators = run_command(
  'cat', files('translators'), check: true,
).stdout().strip()

if get_option('flatpak')
  # start in demo mode when using flatpak through wrapper
  demo_script = files('os-installer-demo')

  install_data(demo_script,
    install_dir: get_option('bindir')
  )
endif
