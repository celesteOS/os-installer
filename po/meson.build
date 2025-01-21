translations = []
po_files = run_command('ls', check: true).stdout().strip()
foreach po_file : po_files.split('\n')
  if po_file.endswith('.po')
    translations += po_file.substring(0, -3)
  endif
endforeach

# create Python list
available_translations = '["' + '", "'.join(translations) + '"]'

i18n.gettext('os-installer', preset: 'glib', args: '--add-location=file')
