#! /bin/sh

# This is an example preparation script.
# If `internet > connection_required` is enabled in the config, this script gets
# called once an internet connection is established, otherwise it's called
# immediately.

echo 'Preparation started.'

# Pretending to do something
echo 'Pretending to do something'

for i in {1..5}
do
    sleep 1
    echo -n '.'
done

echo
echo 'Preparation completed.'

exit 0