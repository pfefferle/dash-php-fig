#!/bin/sh

httrack http://www.php-fig.org \
  -O PHP-FIG.docset/Contents/Resources/Documents,cache -I0 \
  --display=2 --timeout=60 --retries=99 --sockets=7 \
  --connection-per-second=5 --max-rate=250000 \
  --keep-alive --depth=4 --mirror --robots=0 \
  --user-agent '$(httrack --version); dash-php-fig ()'
